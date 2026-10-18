#!/usr/bin/env node

const fs = require('node:fs')
const path = require('node:path')
const { spawnSync } = require('node:child_process')

const LEVELS = ['info', 'low', 'moderate', 'high', 'critical']
const object = value => value && typeof value === 'object' && !Array.isArray(value)

function parseArgs(args) {
  const options = { repo: process.cwd(), level: 'moderate' }
  const seen = new Set()
  for (let i = 0; i < args.length; i += 1) {
    const flag = args[i]
    if (flag === '--help') return { help: true }
    if (flag === '--online') {
      if (options.online) throw new Error('Repeated --online')
      options.online = true
      continue
    }
    if (!['--repo', '--report', '--level'].includes(flag)) throw new Error(`Unknown option: ${flag}`)
    const value = args[++i]
    if (!value || value.startsWith('--') || seen.has(flag)) {
      throw new Error(`Invalid value for ${flag}`)
    }
    seen.add(flag)
    options[flag.slice(2)] = value
  }
  if (!LEVELS.includes(options.level)) throw new Error(`Invalid severity level: ${options.level}`)
  if (Boolean(options.online) === Boolean(options.report)) {
    throw new Error('Choose exactly one of --report FILE or --online')
  }
  return options
}

function validateManifestLock(manifest, lock) {
  if (!object(manifest) || !object(lock) || !object(lock.packages) ||
      !object(lock.packages['']) || ![2, 3].includes(lock.lockfileVersion)) {
    throw new Error('Invalid package manifest or lockfile')
  }
  for (const section of ['dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies']) {
    const declared = manifest[section] || {}
    const locked = lock.packages[''][section] || {}
    if (!object(declared) || !object(locked) ||
        Object.keys(declared).length !== Object.keys(locked).length ||
        Object.entries(declared).some(([name, range]) => typeof range !== 'string' || locked[name] !== range)) {
      throw new Error(`Manifest and lockfile differ: ${section}`)
    }
  }
}

function evaluate(report, manifest, lock, level = 'moderate') {
  if (!LEVELS.includes(level)) throw new Error(`Invalid severity level: ${level}`)
  validateManifestLock(manifest, lock)
  if (!object(report) || report.error || report.auditReportVersion !== 2 ||
      !object(report.vulnerabilities) || !object(report.metadata?.vulnerabilities)) {
    throw new Error('Invalid npm audit report')
  }
  const counts = report.metadata.vulnerabilities
  const actual = Object.fromEntries(LEVELS.map(name => [name, 0]))
  for (const [name, item] of Object.entries(report.vulnerabilities)) {
    if (!object(item) || item.name !== name || !LEVELS.includes(item.severity) ||
        !Array.isArray(item.nodes) || item.nodes.length === 0 ||
        item.nodes.some(node => typeof node !== 'string' || !object(lock.packages[node])) ||
        !Array.isArray(item.via) || item.via.length === 0 ||
        item.via.some(via => typeof via === 'string'
          ? !object(report.vulnerabilities[via])
          : !object(via) || via.name !== name || !LEVELS.includes(via.severity))) {
      throw new Error(`Malformed audit entry: ${name}`)
    }
    for (const via of item.via) {
      const severity = typeof via === 'string' ? report.vulnerabilities[via].severity : via.severity
      if (LEVELS.indexOf(severity) > LEVELS.indexOf(item.severity)) {
        throw new Error(`Audit severity understates advisory: ${name}`)
      }
    }
    actual[item.severity] += 1
  }
  const entries = Object.entries(report.vulnerabilities)
  if (counts.total !== entries.length || LEVELS.some(name => counts[name] !== actual[name])) {
    throw new Error('Audit counts do not match entries')
  }
  const blocked = entries.filter(([, item]) => LEVELS.indexOf(item.severity) >= LEVELS.indexOf(level))
  return { blocked: blocked.map(([name]) => name), total: entries.length, level }
}

function runNpm(repo) {
  const args = ['audit', '--audit-level=info', '--json', '--package-lock-only', '--include=dev', '--include=optional', '--include=peer']
  const result = spawnSync('npm', args, { cwd: repo, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 })
  if (result.error || result.signal || ![0, 1].includes(result.status)) {
    throw new Error(`npm audit failed: ${result.error?.message || result.stderr || result.signal || result.status}`)
  }
  return result
}

function inspect(options, npmRunner = runNpm) {
  const manifest = JSON.parse(fs.readFileSync(path.join(options.repo, 'package.json'), 'utf8'))
  const lock = JSON.parse(fs.readFileSync(path.join(options.repo, 'package-lock.json'), 'utf8'))
  const result = options.online ? npmRunner(options.repo) : null
  const report = JSON.parse(result ? result.stdout : fs.readFileSync(options.report, 'utf8'))
  const verdict = evaluate(report, manifest, lock, options.level)
  if (result && result.status !== (verdict.total > 0 ? 1 : 0)) {
    // The explicit info threshold makes every finding a nonzero npm status.
    throw new Error('npm audit exit status does not match its report')
  }
  return verdict
}

function main(args = process.argv.slice(2)) {
  try {
    const options = parseArgs(args)
    if (options.help) {
      console.log('Usage: node check-npm-audit.cjs [--repo PATH] [--level SEVERITY] (--report FILE | --online)')
      return 0
    }
    const result = inspect(options)
    console.log(`Audit: ${result.total} findings; ${result.level}+ blocked: ${result.blocked.join(', ') || 'none'}`)
    return result.blocked.length ? 1 : 0
  } catch (error) {
    console.error(error.message)
    return 2
  }
}

if (require.main === module) process.exitCode = main()
module.exports = { parseArgs, validateManifestLock, evaluate, inspect, main }
