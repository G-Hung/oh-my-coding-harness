const fs = require('node:fs');
const { local, config, sourceFiles, cli } = require('./lib/project.cjs');
const countLines = source => source.length === 0 ? 0 : source.split(/\r\n|\r|\n/).length - (/\r$|\n$/.test(source) ? 1 : 0);
function main(args = process.argv.slice(2)) {
  const cfg = config();
  let strict = false;
  for (let index = 0; index < args.length; index++) {
    if (args[index] === '--strict') strict = true;
    else if (args[index] === '--max-lines') {
      const limit = Number(args[++index]);
      if (!Number.isInteger(limit) || limit < 1) throw new Error('--max-lines requires a positive integer');
      cfg.maxLines = limit;
    } else throw new Error(`Unknown option: ${args[index]}`);
  }
  const files = sourceFiles(cfg);
  const findings = files.map(file => ({ file, lines: countLines(fs.readFileSync(local(file), 'utf8')) })).filter(row => row.lines > cfg.maxLines).sort((a, b) => b.lines - a.lines);
  console.log(`Scanned ${files.length} source files; limit ${cfg.maxLines} physical lines (including comments and blanks).`);
  for (const row of findings) console.error(`${strict ? 'FAIL' : 'WARN'} ${JSON.stringify(row.file)}: ${row.lines} lines`);
  if (findings.length) console.error('Review responsibilities and cohesive extraction opportunities. Do not split just to satisfy a number. Exclusions require a documented reason.');
  return strict && findings.length ? 1 : 0;
}
if (require.main === module) cli(() => main());
module.exports = { countLines, main };
