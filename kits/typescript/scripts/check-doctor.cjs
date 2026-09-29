const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { root, config, sourceFiles, cli } = require('./lib/project.cjs');
function main() {
  if (process.argv.length > 2) throw new Error('No arguments expected');
  const cfg = config();
  let failed = false;
  function check(label, ok, fix) { console.log(`${ok ? 'PASS' : 'FAIL'} ${label}${ok ? '' : `: ${fix}`}`); if (!ok) failed = true; }
  const [major, minor] = process.versions.node.split('.').map(Number);
  check('Node 22.13+ or >=24', major >= 24 || (major === 22 && minor >= 13), 'activate Node 22.13+ or >=24');
  for (const name of ['tsc', 'eslint', 'jest']) check(name, fs.existsSync(path.join(root, 'node_modules/.bin', name)), 'run npm ci');
  console.log(`Source scope: ${sourceFiles(cfg).length} files`);
  const git = spawnSync('git', ['rev-parse', '--show-toplevel'], { cwd: root, encoding: 'utf8' });
  check('project Git root', git.status === 0 && path.resolve(git.stdout.trim()) === root, 'copy kit into your Git project root (or initialize your new project)');
  const hooks = spawnSync('git', ['config', '--get', 'core.hooksPath'], { cwd: root, encoding: 'utf8' });
  console.log(`Optional hooks: ${hooks.stdout?.trim() || 'not configured'}; inspect existing hooks before adopting hooks/.`);
  return failed ? 1 : 0;
}
if (require.main === module) cli(main);
