const fs = require('node:fs');
const path = require('node:path');
const { root, cli } = require('./lib/project.cjs');
function summarize(parsed, top = 15, minMs = 0) {
  if (!Array.isArray(parsed.testResults) || !parsed.testResults.length) throw new Error('Profile has no suites; run test:profile first');
  const suites = [], cases = [];
  for (const suite of parsed.testResults) {
    if (typeof suite.name !== 'string' || !Number.isFinite(suite.startTime) || !Number.isFinite(suite.endTime) || suite.endTime < suite.startTime || !Array.isArray(suite.assertionResults)) throw new Error('Malformed Jest suite timing');
    const file = path.relative(root, suite.name);
    suites.push({ name: file, ms: suite.endTime - suite.startTime, status: suite.status });
    for (const test of suite.assertionResults) {
      if (test.duration == null) continue; // Skipped cases do not provide durations.
      if (!Number.isFinite(test.duration) || test.duration < 0) throw new Error('Malformed Jest case duration');
      cases.push({ name: `${file}: ${test.fullName}`, ms: test.duration, status: test.status });
    }
  }
  const select = rows => rows.filter(x => x.ms >= minMs).sort((a, b) => b.ms - a.ms).slice(0, top);
  return { suites: select(suites), cases: select(cases) };
}
function main(args = process.argv.slice(2)) {
  if (args.length > 1) throw new Error('Usage: node scripts/test-profile-summary.cjs [jest-results.json]');
  const top = Number(process.env.JEST_SLOW_TOP || 15), min = Number(process.env.JEST_SLOW_MIN_MS || 0);
  if (!Number.isInteger(top) || top < 1 || !Number.isFinite(min) || min < 0) throw new Error('Invalid JEST_SLOW_TOP or JEST_SLOW_MIN_MS');
  const input = path.resolve(root, args[0] || '.cache/jest-results.json');
  const parsed = JSON.parse(fs.readFileSync(input, 'utf8'));
  const result = summarize(parsed, top, min);
  console.log(`Profile: ${input}; modified ${fs.statSync(input).mtime.toISOString()}; reported success: ${parsed.success}`);
  for (const key of ['suites', 'cases']) {
    console.log(`Slow ${key} (top ${top}, minimum ${min}ms):`);
    for (const row of result[key]) console.log(`${row.ms}ms  ${row.status}  ${JSON.stringify(row.name)}`);
  }
  console.log('Timing is diagnostic, not a quality gate. Compare under the same environment; preserve behavioral coverage when optimizing.');
}
if (require.main === module) cli(() => main());
module.exports = { summarize };
