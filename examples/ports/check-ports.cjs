#!/usr/bin/env node

const { spawnSync } = require('node:child_process')

// lsof reports both IPv4 and IPv6 listeners without connecting to the app.
// TODO: choose your project's preview-port range; this range is only a default.
const DEFAULT_FROM = 3000
const DEFAULT_TO = 3100

const validateRange = (from, to) => {
  if (!Number.isInteger(from) || !Number.isInteger(to) || from < 1 || to > 65535 || from > to) {
    throw new Error('Port range must contain integers with 1 <= from <= to <= 65535.')
  }
}

const inspectPorts = ({ from = DEFAULT_FROM, to = DEFAULT_TO, run = spawnSync } = {}) => {
  validateRange(from, to)
  const result = run(
    'lsof',
    ['-nP', '-a', `-iTCP:${from}-${to}`, '-sTCP:LISTEN', '-Fpcn'],
    {
      encoding: 'utf8',
    }
  )
  if (
    result.error ||
    result.stderr?.trim() ||
    ![0, 1].includes(result.status)
  ) {
    throw new Error(
      'Unable to inspect ports. Ensure lsof is available; do not assume ports are free.'
    )
  }
  const listeners = []
  let pid
  let command
  for (const line of (result.stdout || '').split('\n').filter(Boolean)) {
    // lsof includes file-descriptor records even when -F selects p/c/n.
    if (line.startsWith('f')) continue
    if (!/^[pcn]/.test(line)) {
      throw new Error('Unexpected lsof output; cannot safely suggest a port.')
    }
    if (line.startsWith('p')) {
      pid = Number(line.slice(1))
      command = undefined
    }
    if (line.startsWith('c')) command = line.slice(1)
    if (line.startsWith('n')) {
      const port = Number(line.match(/:(\d+)$/)?.[1])
      if (
        !pid ||
        !command ||
        !Number.isInteger(port) ||
        port < from ||
        port > to
      ) {
        throw new Error(
          'Unexpected lsof listener output; cannot safely suggest a port.'
        )
      }
      if (!listeners.some(entry => entry.port === port && entry.pid === pid)) {
        listeners.push({ port, pid, command })
      }
    }
  }
  if (result.stdout?.trim() && listeners.length === 0) {
    throw new Error('Incomplete lsof output; cannot safely suggest a port.')
  }
  const occupied = new Set(listeners.map(entry => entry.port))
  const candidates = Array.from({ length: to - from + 1 }, (_, index) => from + index)
  return {
    listeners: listeners.sort((a, b) => a.port - b.port || a.pid - b.pid),
    suggestedPort: candidates.find(port => !occupied.has(port)) ?? null,
  }
}

const parseArgs = args => {
  const options = { from: DEFAULT_FROM, to: DEFAULT_TO, json: false }
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index]
    if (arg === '--json') options.json = true
    else if (arg === '--from' || arg === '--to') {
      const value = args[++index]
      if (!value || !/^\d+$/.test(value)) throw new Error(`${arg} requires a port number`)
      options[arg.slice(2)] = Number(value)
    } else throw new Error(`Unknown option: ${arg}`)
  }
  validateRange(options.from, options.to)
  return options
}

if (require.main === module) {
  try {
    const options = parseArgs(process.argv.slice(2))
    const { listeners, suggestedPort } = inspectPorts(options)
    if (options.json) console.log(JSON.stringify({ from: options.from, to: options.to, listeners, suggestedPort }))
    else {
      console.log(`Observed TCP listeners in ${options.from}–${options.to} (visibility depends on OS permissions):`)
      console.table(listeners)
      console.log(
        suggestedPort === null
          ? 'All ports are occupied. Do not stop other servers.'
          : `Suggested port: ${suggestedPort}. Snapshot only; confirm successful bind when starting.`
      )
    }
    if (suggestedPort === null) process.exitCode = 1
  } catch (error) {
    console.error(error.message)
    process.exitCode = 1
  }
}

module.exports = { inspectPorts, parseArgs }
