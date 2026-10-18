const { test, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync, execFileSync } = require('node:child_process');
const { countLines } = require('../scripts/check-loc.cjs');
const { parseNames } = require('../scripts/check-readme-coverage.cjs');
const { summarize } = require('../scripts/test-profile-summary.cjs');
const sandbox = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-harness-test-'));
after(() => fs.rmSync(sandbox, { recursive: true, force: true }));
function project(name, config = {}) {
  const root = path.join(sandbox, name);
  fs.mkdirSync(root);
  fs.cpSync(path.join(__dirname, '../scripts'), path.join(root, 'scripts'), { recursive: true });
  fs.mkdirSync(path.join(root, 'src'));
  fs.writeFileSync(path.join(root, 'src/example.ts'), 'export const value = 1;\n');
  fs.writeFileSync(path.join(root, 'harness.config.cjs'), `module.exports = ${JSON.stringify({ sourceRoots: ['src'], markdownRoots: ['.'], extensions: ['.ts'], exclude: [], maxLines: 1, checks: ['lint'], ...config })}`);
  return root;
}
function run(root, script, args = []) { return spawnSync(process.execPath, [path.join(root, 'scripts', script), ...args], { cwd: root, encoding: 'utf8' }); }
test('physical lines handle empty content, CRLF, CR, and final newline', () => {
  assert.equal(countLines(''), 0);
  assert.equal(countLines('a\r\nb\r\n'), 2);
  assert.equal(countLines('a\rb'), 2);
});
test('LOC is advisory by default, strict blocks; invalid and empty scopes fail', () => {
  const root = project('loc');
  fs.appendFileSync(path.join(root, 'src/example.ts'), '\n');
  assert.equal(run(root, 'check-loc.cjs').status, 0);
  assert.equal(run(root, 'check-loc.cjs', ['--strict']).status, 1);
  assert.equal(run(root, 'check-loc.cjs', ['--max-lines', 'no']).status, 1);
  fs.unlinkSync(path.join(root, 'src/example.ts'));
  assert.match(run(root, 'check-loc.cjs').stderr, /No source files/);
  assert.equal(run(project('bad-root', { sourceRoots: ['../outside'] }), 'check-loc.cjs').status, 1);
});
test('source scanning rejects symlinks instead of reading outside root', () => {
  const root = project('symlink');
  fs.symlinkSync(os.tmpdir(), path.join(root, 'src/external'));
  assert.match(run(root, 'check-loc.cjs').stderr, /Symlink/);
});
test('NUL diff parsing retains both sides of renames and unusual filenames', () => {
  assert.deepEqual(parseNames('R100\0src/old.ts\0src/new\nname.ts\0D\0src/a b.ts\0'), ['src/old.ts', 'src/new\nname.ts', 'src/a b.ts']);
});
test('README reports missing docs and unusual untracked names; invalid base fails', () => {
  const root = project('readme');
  execFileSync('git', ['init', '-q', root]);
  fs.writeFileSync(path.join(root, 'src/new\nfile.ts'), 'const n = 1;');
  const result = run(root, 'check-readme-coverage.cjs');
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /MISSING nearby README/);
  assert.match(result.stdout, /new\\nfile/);
  assert.equal(run(root, 'check-readme-coverage.cjs', ['--base', 'missing']).status, 1);
  assert.equal(run(root, 'check-readme-coverage.cjs', ['--staged', '--base', 'HEAD']).status, 1);
});
test('profile rejects empty or malformed inputs and sorts by spent time', () => {
  assert.throws(() => summarize({ testResults: [] }), /no suites/);
  const suite = (name, duration) => ({ name, startTime: 0, endTime: duration, assertionResults: [{ fullName: name, duration }] });
  const result = summarize({ testResults: [suite('/a', 10), suite('/b', 90)] }, 1);
  assert.equal(result.suites[0].ms, 90);
  assert.equal(result.cases[0].ms, 90);
  assert.throws(() => summarize({ testResults: [{ name: 'x' }] }), /Malformed/);
});
test('local gate retains logs and fails when a configured command fails', () => {
  const root = project('gate');
  fs.writeFileSync(path.join(root, 'package.json'), JSON.stringify({ scripts: { lint: 'node -e "process.exit(7)"' } }));
  const result = run(root, 'check-local.cjs');
  assert.equal(result.status, 1);
  const log = result.stderr.match(/Logs retained: (.+)/)?.[1];
  assert.ok(log && fs.existsSync(log));
  fs.rmSync(log, { recursive: true });
});
test('Markdown parser checks reference targets, skips fenced samples and rejects missing or escaping targets', () => {
  const root = project('links', { exclude: ['node_modules'] });
  fs.symlinkSync(path.join(__dirname, '../node_modules'), path.join(root, 'node_modules'));
  fs.writeFileSync(path.join(root, 'a b.md'), '# Target');
  fs.writeFileSync(path.join(root, 'README.md'), '[target][ref]\n\n[ref]: a%20b.md#unchecked\n\n```md\n[example](missing.md)\n```\n');
  const initial = run(root, 'check-links.cjs');
  assert.equal(initial.status, 0, initial.stderr);
  fs.appendFileSync(path.join(root, 'README.md'), '\n[bad](absent.md)\n[escape](../outside.md)\n');
  const result = run(root, 'check-links.cjs');
  assert.equal(result.status, 1);
  assert.match(result.stderr, /target missing/);
  assert.match(result.stderr, /escapes root/);
});

test('README with base retains staged changes cancelled by worktree and both rename paths', () => {
  const root = project('readme-base');
  const git = args => execFileSync('git', ['-c', 'user.name=Harness Test', '-c', 'user.email=test@example.invalid', '-c', 'commit.gpgsign=false', ...args], { cwd: root, encoding: 'utf8' }).trim();
  git(['init', '-q']);
  git(['add', '.']);
  git(['commit', '-qm', 'baseline']);
  const baseline = git(['rev-parse', 'HEAD']);
  const source = path.join(root, 'src/example.ts');
  const original = fs.readFileSync(source, 'utf8');
  fs.writeFileSync(source, 'export const value = 2;\n');
  git(['add', 'src/example.ts']);
  fs.writeFileSync(source, original);
  const staged = run(root, 'check-readme-coverage.cjs', ['--base', baseline]);
  assert.equal(staged.status, 0, staged.stderr);
  assert.match(staged.stdout, /src\/example.ts/);
  git(['checkout', '--', 'src/example.ts']);
  git(['mv', 'src/example.ts', 'src/renamed.ts']);
  const renamed = run(root, 'check-readme-coverage.cjs', ['--base', baseline]);
  assert.equal(renamed.status, 0, renamed.stderr);
  assert.match(renamed.stdout, /src\/example.ts/);
  assert.match(renamed.stdout, /src\/renamed.ts/);
});
