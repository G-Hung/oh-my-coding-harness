const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { spawnSync } = require('node:child_process')
const { evaluate, inspect } = require('../check-npm-audit.cjs')

const script = path.join(__dirname, '..', 'check-npm-audit.cjs')
const manifest = { name: 'fixture', version: '1.0.0', devDependencies: { sample: '1.0.0' } }
const lock = { lockfileVersion: 3, packages: {
  '': { devDependencies: { sample: '1.0.0' } },
  'node_modules/sample': { version: '1.0.0' },
} }
function report(severity) {
  const counts = { info: 0, low: 0, moderate: 0, high: 0, critical: 0, total: 0 }
  const vulnerabilities = {}
  if (severity) {
    counts[severity] = 1
    counts.total = 1
    vulnerabilities.sample = { name: 'sample', severity, nodes: ['node_modules/sample'],
      via: [{ name: 'sample', severity }] }
  }
  return { auditReportVersion: 2, metadata: { vulnerabilities: counts }, vulnerabilities }
}
function fixture(t, audit) {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), 'npm-audit-check-'))
  t.after(() => fs.rmSync(repo, { recursive: true, force: true }))
  fs.writeFileSync(path.join(repo, 'package.json'), JSON.stringify(manifest))
  fs.writeFileSync(path.join(repo, 'package-lock.json'), JSON.stringify(lock))
  const reportFile = path.join(repo, 'report.json')
  fs.writeFileSync(reportFile, JSON.stringify(audit))
  return { repo, reportFile }
}

test('saved report blocks at configured severity and checks the full graph', t => {
  const { repo, reportFile } = fixture(t, report('moderate'))
  const blocked = spawnSync(process.execPath, [script, '--repo', repo, '--report', reportFile], { encoding: 'utf8' })
  assert.equal(blocked.status, 1)
  assert.match(blocked.stdout, /moderate\+ blocked: sample/)
  assert.deepEqual(evaluate(report('moderate'), manifest, lock, 'high').blocked, [])
})

test('clean report passes; malformed report and manifest mismatch fail closed', t => {
  const { repo, reportFile } = fixture(t, report())
  assert.equal(spawnSync(process.execPath, [script, '--repo', repo, '--report', reportFile]).status, 0)
  const malformed = report('low')
  malformed.vulnerabilities.sample.nodes = ['node_modules/missing']
  assert.throws(() => evaluate(malformed, manifest, lock), /Malformed audit entry/)
  const understated = report('low')
  understated.vulnerabilities.sample.via[0].severity = 'high'
  assert.throws(() => evaluate(understated, manifest, lock), /understates advisory/)
  assert.throws(() => evaluate(report(), { devDependencies: { other: '1.0.0' } }, lock), /differ/)
})

test('online mode is explicit and can use an injected npm runner', t => {
  const { repo } = fixture(t, report())
  const noMode = spawnSync(process.execPath, [script, '--repo', repo], { encoding: 'utf8' })
  assert.equal(noMode.status, 2)
  let called = 0
  const verdict = inspect({ repo, online: true, level: 'moderate' }, () => {
    called += 1
    return { status: 0, stdout: JSON.stringify(report()) }
  })
  assert.equal(called, 1)
  assert.equal(verdict.total, 0)
  assert.throws(() => inspect({ repo, online: true, level: 'moderate' }, () =>
    ({ status: 0, stdout: JSON.stringify(report('low')) })), /exit status/)
})
