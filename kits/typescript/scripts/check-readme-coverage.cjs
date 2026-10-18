const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { root, local, config, source, cli } = require('./lib/project.cjs');
const git = args => execFileSync('git', args, { cwd: root, encoding: 'utf8' });
function readGitChangedPaths({ staged = false, base } = {}) {
  const top = git(['rev-parse', '--show-toplevel']).trim();
  if (fs.realpathSync(top) !== fs.realpathSync(root)) throw new Error('Run in a standalone project Git root after copying the kit.');
  let ref;
  if (base) {
    const commit = git(['rev-parse', '--verify', '--end-of-options', `${base}^{commit}`]).trim();
    ref = git(['merge-base', 'HEAD', commit]).trim();
  }
  const args = ['diff', '--name-status', '-z', '-M', '--diff-filter=ACMRDT'];
  if (staged) return [...new Set(parseNames(git([...args, '--cached', '--'])))];
  // Keep branch, index, and worktree changes separate, even when they cancel.
  const paths = [
    ...parseNames(git([...args, '--cached', '--'])),
    ...parseNames(git([...args, '--'])),
    ...git(['ls-files', '--others', '--exclude-standard', '-z']).split('\0').filter(Boolean),
  ];
  if (ref) paths.push(...parseNames(git([...args, `${ref}..HEAD`, '--'])));
  return [...new Set(paths)];
}
function parseNames(output) {
  const parts = output.split('\0').filter(Boolean), paths = [];
  for (let i = 0; i < parts.length;) {
    const status = parts[i++];
    paths.push(parts[i++]);
    if (/^[CR]/.test(status)) paths.push(parts[i++]);
  }
  if (paths.some(x => !x)) throw new Error('Malformed Git diff output');
  return paths;
}
function findNearestReadme(file) {
  let dir = path.posix.dirname(file);
  for (;;) {
    const candidate = path.posix.join(dir, 'README.md');
    if (fs.existsSync(local(candidate))) return candidate;
    if (dir === '.') return null;
    dir = path.posix.dirname(dir);
  }
}
function main(args = process.argv.slice(2)) {
  const options = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--staged') options.staged = true;
    else if (args[i] === '--base' && args[i + 1] && !args[i + 1].startsWith('-')) options.base = args[++i];
    else throw new Error(`Unknown or incomplete option: ${args[i]}`);
  }
  if (options.staged && options.base) throw new Error('Choose --staged or --base');
  const cfg = config(), changed = readGitChangedPaths(options);
  const groups = new Map();
  for (const file of changed.filter(file => source(file, cfg))) {
    const readme = findNearestReadme(file);
    groups.set(readme, [...(groups.get(readme) || []), file]);
  }
  console.log(`README review: ${changed.length} changed paths; ${groups.size} source areas. Advisory only.`);
  for (const [readme, files] of groups) console.log(`${readme ? JSON.stringify(readme) : 'MISSING nearby README'} (${changed.includes(readme) ? 'also changed; verify accuracy' : 'review relevance'}): ${files.map(x => JSON.stringify(x)).join(', ')}`);
  console.log('File co-change cannot establish documentation accuracy; update only when contracts or guidance changed.');
}
if (require.main === module) cli(() => main());
module.exports = { parseNames, readGitChangedPaths, findNearestReadme };
