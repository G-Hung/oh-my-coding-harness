const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { execFileSync, spawnSync } = require('node:child_process')
const { inspect } = require('../check-git.cjs')

const script = path.join(__dirname, '..', 'check-git.cjs')
function run(repo, ...args) {
  return execFileSync('git', ['-C', repo, ...args], { encoding: 'utf8' }).trim()
}
function put(repo, name, content) {
  fs.writeFileSync(path.join(repo, name), content)
  run(repo, 'add', name)
  run(repo, 'commit', '-qm', name)
}
function fixture(t) {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), 'git-checks-'))
  t.after(() => fs.rmSync(repo, { recursive: true, force: true }))
  run(repo, 'init', '-q')
  run(repo, 'config', 'user.email', 'fixture@example.invalid')
  run(repo, 'config', 'user.name', 'Fixture')
  put(repo, 'shared.txt', 'one\ntwo\nthree\n')
  const base = run(repo, 'rev-parse', 'HEAD')
  return { repo, base }
}
function cli(repo, base, ...extra) {
  return spawnSync(process.execPath, [script, '--repo', repo, '--base', base, ...extra], {
    encoding: 'utf8',
  })
}

test('clean independent edits pass without changing HEAD or worktree', t => {
  const { repo, base } = fixture(t)
  run(repo, 'switch', '-qc', 'peer')
  put(repo, 'peer.txt', 'peer\n')
  run(repo, 'switch', '-qc', 'target', base)
  put(repo, 'target.txt', 'target\n')
  const before = run(repo, 'rev-parse', 'HEAD')
  const result = cli(repo, base, '--peer', 'peer')
  assert.equal(result.status, 0, result.stderr)
  assert.match(result.stdout, /peer peer: clean merge/)
  assert.equal(run(repo, 'rev-parse', 'HEAD'), before)
  assert.equal(run(repo, 'status', '--porcelain'), '')
})

test('same-file overlap is reported even when merge is clean', t => {
  const { repo, base } = fixture(t)
  run(repo, 'switch', '-qc', 'peer')
  put(repo, 'shared.txt', 'peer\ntwo\nthree\n')
  run(repo, 'switch', '-qc', 'target', base)
  put(repo, 'shared.txt', 'one\ntwo\ntarget\n')
  const result = cli(repo, base, '--peer', 'peer')
  assert.equal(result.status, 0, result.stderr)
  assert.match(result.stdout, /peer peer: clean merge/)
  assert.match(result.stdout, /overlap: "shared.txt"/)
})

test('real merge conflict returns a failing status', t => {
  const { repo, base } = fixture(t)
  run(repo, 'switch', '-qc', 'peer')
  put(repo, 'shared.txt', 'peer\ntwo\nthree\n')
  run(repo, 'switch', '-qc', 'target', base)
  put(repo, 'shared.txt', 'target\ntwo\nthree\n')
  const result = cli(repo, base, '--peer', 'peer')
  assert.equal(result.status, 1)
  assert.match(result.stdout, /peer peer: CONFLICT/)
})

test('rename overlap includes the original path', t => {
  const { repo, base } = fixture(t)
  run(repo, 'switch', '-qc', 'peer')
  put(repo, 'shared.txt', 'one\npeer\nthree\n')
  run(repo, 'switch', '-qc', 'target', base)
  run(repo, 'mv', 'shared.txt', 'renamed.txt')
  run(repo, 'commit', '-qm', 'rename')
  const result = cli(repo, base, '--peer', 'peer')
  assert.equal(result.status, 0, result.stderr)
  assert.match(result.stdout, /overlap: "shared.txt"/)
})

test('bad refs and invalid arguments fail as errors', t => {
  const { repo, base } = fixture(t)
  assert.equal(cli(repo, base, '--peer', 'missing').status, 2)
  assert.equal(cli(repo, base, '--peer', '--bad').status, 2)
  assert.equal(cli(repo, base, '--peer', '-invalid').status, 2)
})

test('base conflict is checked even without peers', t => {
  const { repo, base } = fixture(t)
  run(repo, 'switch', '-qc', 'target')
  put(repo, 'shared.txt', 'target\ntwo\nthree\n')
  run(repo, 'switch', '-qc', 'base', base)
  put(repo, 'shared.txt', 'base\ntwo\nthree\n')
  const result = inspect({ repo, base: 'base', target: 'target' })
  assert.equal(result.checks[0].conflict, true)
  assert.equal(result.ok, false)
})
