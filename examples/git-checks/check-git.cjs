#!/usr/bin/env node

// Check local commits only. This command never fetches, merges, or writes refs.
const { execFileSync } = require('node:child_process')

function parseArgs(args) {
  const options = { repo: process.cwd(), target: 'HEAD', peers: [] }
  const fields = { '--repo': 'repo', '--base': 'base', '--target': 'target' }
  const seen = new Set()
  for (let i = 0; i < args.length; i += 1) {
    const flag = args[i]
    if (flag === '--help') return { help: true }
    if (!(flag in fields) && flag !== '--peer') {
      throw new Error(`Unknown option: ${flag}`)
    }
    const value = args[++i]
    if (!value || value.startsWith('--')) {
      throw new Error(`Missing value for ${flag}`)
    }
    if (flag === '--peer') options.peers.push(value)
    else if (seen.has(flag)) {
      throw new Error(`Repeated option: ${flag}`)
    } else {
      seen.add(flag)
      options[fields[flag]] = value
    }
  }
  if (!options.base) throw new Error('--base is required')
  return options
}

function git(repo, args, allowed = [0]) {
  try {
    return { status: 0, output: execFileSync('git', ['-C', repo, ...args], {
      encoding: 'buffer', stdio: ['ignore', 'pipe', 'pipe'],
    }) }
  } catch (error) {
    if (Number.isInteger(error.status) && allowed.includes(error.status)) {
      return { status: error.status, output: error.stdout || Buffer.alloc(0) }
    }
    const detail = error.stderr?.toString('utf8').trim() || error.message
    throw new Error(`git ${args[0]} failed: ${detail}`)
  }
}

function commit(repo, label) {
  // Resolve names before use. SHA arguments cannot become Git options.
  const value = git(repo, ['rev-parse', '--verify', '--end-of-options', `${label}^{commit}`])
    .output.toString('utf8').trim()
  if (!/^[a-f0-9]{40,64}$/i.test(value)) throw new Error(`Invalid commit: ${label}`)
  return value
}

function changedFiles(repo, base, ref) {
  const fields = git(repo, ['diff', '--name-status', '-z', '--find-renames', `${base}...${ref}`])
    .output.toString('utf8').split('\0').filter(Boolean)
  const files = new Set()
  for (let i = 0; i < fields.length;) {
    const status = fields[i++]
    if (!/^[A-Z][0-9]*$/.test(status)) throw new Error(`Invalid Git diff status: ${status}`)
    const count = /^[RC]/.test(status) ? 2 : 1
    if (fields.length - i < count) throw new Error('Incomplete Git diff output')
    for (let j = 0; j < count; j += 1) files.add(fields[i++])
  }
  return [...files]
}

function mergeStatus(repo, left, right) {
  // A status of 1 means a content conflict. Other errors are not conflicts.
  return git(repo, ['merge-tree', '--write-tree', '--quiet', left, right], [0, 1]).status
}

function inspect({ repo, base, target = 'HEAD', peers = [] }) {
  const baseSha = commit(repo, base)
  const targetSha = commit(repo, target)
  const targetFiles = changedFiles(repo, baseSha, targetSha)
  const checks = [{ label: base, sha: baseSha, kind: 'base',
    conflict: mergeStatus(repo, baseSha, targetSha) === 1, overlap: [] }]
  for (const peer of peers) {
    const peerSha = commit(repo, peer)
    const peerFiles = new Set(changedFiles(repo, baseSha, peerSha))
    checks.push({ label: peer, sha: peerSha, kind: 'peer',
      conflict: mergeStatus(repo, peerSha, targetSha) === 1,
      overlap: targetFiles.filter(file => peerFiles.has(file)) })
  }
  return { base, baseSha, target, targetSha, targetFiles, checks,
    ok: checks.every(check => !check.conflict) }
}

function format(result) {
  const lines = [
    `Target ${result.target}: ${result.targetSha}`,
    `Base ${result.base}: ${result.baseSha}`,
  ]
  for (const check of result.checks) {
    lines.push(`${check.kind} ${check.label}: ${check.conflict ? 'CONFLICT' : 'clean merge'}`)
    for (const file of check.overlap) lines.push(`  overlap: ${JSON.stringify(file)}`)
  }
  return lines.join('\n')
}

function main(args = process.argv.slice(2)) {
  try {
    const options = parseArgs(args)
    if (options.help) {
      console.log('Usage: node check-git.cjs --base REF [--target REF] [--peer REF ...] [--repo PATH]')
      return 0
    }
    const result = inspect(options)
    console.log(format(result))
    return result.ok ? 0 : 1
  } catch (error) {
    console.error(error.message)
    return 2
  }
}

if (require.main === module) process.exitCode = main()
module.exports = { parseArgs, changedFiles, inspect, format, main }
