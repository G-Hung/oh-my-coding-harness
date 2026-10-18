const fs = require('node:fs');
const { spawnSync } = require('node:child_process');
const { root, local, cli } = require('./lib/project.cjs');
function main() {
  if (process.argv.length > 2) throw new Error('No arguments expected');
  fs.mkdirSync(local('.cache'), { recursive: true });
  const output = local('.cache/jest-results.json');
  // Do not leave a previous successful profile available when the next invocation fails.
  fs.rmSync(output, { force: true });
  const result = spawnSync(process.execPath, [require.resolve('jest/bin/jest'), '--runInBand', '--json', `--outputFile=${output}`], { cwd: root, stdio: 'inherit' });
  if (result.error) throw result.error;
  return typeof result.status === 'number' ? result.status : 1;
}
if (require.main === module) cli(main);
