const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { root, config, cli } = require('./lib/project.cjs');
function main() {
  if (process.argv.length > 2) throw new Error('No arguments expected; edit checks in harness.config.cjs');
  const cfg = config(), pkg = require(path.join(root, 'package.json'));
  for (const name of cfg.checks) {
    if (!/^[a-zA-Z0-9:_-]+$/.test(name) || !pkg.scripts?.[name] || name === 'check' || /check-local/.test(pkg.scripts[name])) throw new Error(`Invalid or recursive check: ${name}`);
  }
  const logs = fs.mkdtempSync(path.join(os.tmpdir(), 'harness-check-'));
  let failed = false;
  // Sequential by default: an adopting project chooses resource-safe parallelism if useful.
  for (const [index, name] of cfg.checks.entries()) {
    const log = path.join(logs, `${index}-${name.replaceAll(':', '-')}.log`);
    const fd = fs.openSync(log, 'w');
    let result;
    try { result = spawnSync(process.platform === 'win32' ? 'npm.cmd' : 'npm', ['run', name], { cwd: root, stdio: ['ignore', fd, fd], shell: process.platform === 'win32' }); }
    finally { fs.closeSync(fd); }
    const ok = result.status === 0 && !result.error;
    console.log(`${ok ? 'PASS' : 'FAIL'} ${name}`);
    if (!ok) { failed = true; console.error(result.error?.message || fs.readFileSync(log, 'utf8').split('\n').slice(-50).join('\n')); }
    else if (name === 'check:loc') console.log(fs.readFileSync(log, 'utf8')); // Keep advisories visible.
  }
  if (failed) console.error(`Logs retained: ${logs}`);
  else fs.rmSync(logs, { recursive: true });
  return failed ? 1 : 0;
}
if (require.main === module) cli(main);
