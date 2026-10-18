const { test } = require('node:test')
const assert = require('node:assert/strict')
const { inspectPorts, parseArgs } = require('../check-ports.cjs')

const output = stdout => () => ({ status: 0, stdout, stderr: '' })

test('deduplicates IPv4/IPv6 listeners and suggests another port', () => {
  const result = inspectPorts({ from: 4000, to: 4002,
    run: output('p123\ncnode\nf12\nn*:4000\nf13\nn[::1]:4000\np456\ncnode\nf14\nn127.0.0.1:4002\n') })
  assert.equal(result.listeners.length, 2)
  assert.equal(result.suggestedPort, 4001)
})

test('accepts no visible matches but reports a full range', () => {
  assert.equal(inspectPorts({ from: 4000, to: 4000,
    run: () => ({ status: 1, stdout: '', stderr: '' }) }).suggestedPort, 4000)
  assert.equal(inspectPorts({ from: 4000, to: 4000,
    run: output('p123\ncnode\nn*:4000\n') }).suggestedPort, null)
})

test('never suggests availability after failed or malformed inspection', () => {
  for (const run of [
    () => ({ status: 2, stdout: '', stderr: '' }),
    () => ({ status: 0, stdout: '', stderr: 'permission denied' }),
    () => ({ error: new Error('missing executable') }),
    output('not an lsof listener'), output('p123\ncnode\n'),
    output('p123\ncnode\nn*:9999\n'),
    output('p123\ncnode\nn*:4000\np456\nn*:4001\n'),
  ]) assert.throws(() => inspectPorts({ from: 4000, to: 4010, run }))
})

test('rejects bad ranges and unexpected CLI inputs', () => {
  for (const args of [['--from'], ['--from', '0'], ['--to', '65536'],
    ['--from', '5000', '--to', '4000'], ['--from', '1.2'], ['--unknown']]) {
    assert.throws(() => parseArgs(args))
  }
  assert.deepEqual(parseArgs(['--from', '4000', '--to', '4010', '--json']),
    { from: 4000, to: 4010, json: true })
})
