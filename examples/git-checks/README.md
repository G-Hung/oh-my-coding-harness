# Git and lockfile checks

Copy this directory into a repository. The two scripts need Node.js 22.13+.
The Git check also needs Git 2.38+ for `merge-tree --write-tree`. The audit
check needs npm only in online mode. No package installation or hook setup is
required.

## Check local refs

Run these commands from the copied directory. Replace the example refs with
refs that exist in your repository:

```sh
node check-git.cjs --repo /path/to/repository --base origin/main --target HEAD
node check-git.cjs --repo /path/to/repository --base origin/main --target HEAD --peer origin/pr-123 --peer origin/pr-456
node --test tests/*.test.cjs
```

The command checks whether the target can merge with the base and each peer.
It also compares files changed from the base to the target and each peer.
Rename source and destination paths both count as changed. A same-file overlap
is a review signal, even if Git can merge the edits. Exit 0 means no conflict
or overlap; exit 1 means at least one; exit 2 means the check failed. A missing
ref, unrelated history, or Git error fails the check.

Refs are local snapshots. The script does not discover pull requests or fetch
new commits. To inspect open pull requests, list them explicitly with a read
query such as `gh pr list --state open --json number,headRefName --limit 100`.
If a selected PR head is missing locally, an explicit fetch such as
`git fetch origin pull/123/head:refs/remotes/origin/pr-123` creates or updates
the local ref. Then pass `--peer origin/pr-123`. Review the list cap and selected
PRs; the checker cannot claim to cover PRs it was not given. Adjust the fetch
refspec for hosts that do not expose GitHub-style pull refs.

The Git check does not change branches, the index, tracked files, or refs.
`git merge-tree --write-tree` may create unreachable objects in the local Git
object store. Git can later prune those objects. Run it on a disposable clone
if even that object-store write is unacceptable.

## Check an npm lockfile

Run from the copied directory with an npm repository:

```sh
node check-npm-audit.cjs --repo /path/to/repository --online
node check-npm-audit.cjs --repo /path/to/repository --online --level high
node check-npm-audit.cjs --repo /path/to/repository --report /path/to/audit-report.json
```

`--online` is explicit because `npm audit` contacts the configured registry.
The script includes development, optional, and peer packages from the full
lockfile. It checks the manifest against the lockfile and validates the npm
audit JSON before applying the severity threshold. The default threshold is
moderate. Exit 0 means no finding at or above the threshold; exit 1 means
blocked findings; exit 2 means invalid input or an unavailable check. It
neither installs packages nor updates the lockfile. npm may write its own cache.

`--report` evaluates an existing npm audit v2 JSON report without network
access. Generate it for the same manifest and lockfile snapshot. The JSON
format does not cryptographically bind the report to that snapshot, so use
`--online` for an authoritative current audit. A stale but well-formed clean
report cannot establish current package safety.

These scripts are standalone. Copy their tests if you change behavior after
adoption. Add their commands to an existing check gate only after confirming
the refs, npm registry, and failure policy that fit that repository.
