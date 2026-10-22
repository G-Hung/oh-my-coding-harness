"""Check committed targets against a fresh integration branch and peer changes."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, urlparse

TIMEOUT = 120


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def transport_environment(root: Path, env: dict[str, str]) -> dict[str, str]:
    """Carry effective transport settings into the disposable repository."""
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "config",
            "--null",
            "--get-regexp",
            r"^(url\.|https?\.|credential\.|ssh\.|protocol\.|core\.(sshcommand|gitproxy)$)",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise ValueError("Cannot read Git transport configuration")
    entries = [entry.split("\n", 1) for entry in result.stdout.split("\0") if entry]
    transport = env.copy()
    # The captured settings already include system/global config and conditional
    # includes. Do not load those twice, especially multi-valued credential helpers.
    transport["GIT_CONFIG_NOSYSTEM"] = "1"
    transport["GIT_CONFIG_GLOBAL"] = os.devnull
    transport.pop("GIT_CONFIG_PARAMETERS", None)
    transport["GIT_CONFIG_COUNT"] = str(len(entries))
    for index, entry in enumerate(entries):
        transport[f"GIT_CONFIG_KEY_{index}"] = entry[0]
        transport[f"GIT_CONFIG_VALUE_{index}"] = entry[1] if len(entry) == 2 else ""
    return transport


def github_repository(remote: str) -> tuple[str, str] | None:
    """Recognize public GitHub push URLs, not the checkout's origin."""
    match = re.fullmatch(r"(?:[^@/:]+@)?github\.com:([^/]+/[^/]+?)(?:\.git)?/?", remote)
    if match:
        return "github.com", match[1]
    parsed = urlparse(remote)
    if parsed.scheme in ("https", "ssh") and parsed.hostname == "github.com":
        name = parsed.path.strip("/").removesuffix(".git")
        if re.fullmatch(r"[^/]+/[^/]+", name):
            return "github.com", name
    return None


def explicit_repository(value: str) -> tuple[str, str]:
    parts = value.strip().strip("/").split("/")
    parts[-1] = parts[-1].removesuffix(".git")
    if len(parts) not in (2, 3) or not all(parts):
        raise ValueError("--github-repo must be OWNER/REPO or HOST/OWNER/REPO")
    host = parts[0] if len(parts) == 3 else "github.com"
    return host, "/".join(parts[-2:])


def open_pull_requests(root: Path, repository: tuple[str, str], base: str) -> list[dict]:
    host, name = repository
    endpoint = f"repos/{name}/pulls?state=open&base={quote(base, safe='')}&per_page=100"
    try:
        result = subprocess.run(
            ["gh", "api", "--hostname", host, "--paginate", "--slurp", endpoint],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError("Open PR query timed out after 120 seconds") from exc
    except OSError as exc:
        raise ValueError(
            "Open PR query unavailable; check gh installation and authentication"
        ) from exc
    if result.returncode:
        raise ValueError(
            "Open PR query failed; check gh support for api --paginate --slurp, "
            "authentication, and repository access"
        )
    try:
        pages = json.loads(result.stdout)
        if (
            not isinstance(pages, list)
            or not pages
            or not all(isinstance(page, list) for page in pages)
        ):
            raise ValueError("Expected paginated PR lists")
        pulls = [pull for page in pages for pull in page]
        for pull in pulls:
            if (
                not isinstance(pull["number"], int)
                or pull["base"]["ref"] != base
                or not isinstance(pull["head"]["ref"], str)
                or not re.fullmatch(r"[a-fA-F0-9]{40}|[a-fA-F0-9]{64}", pull["head"]["sha"])
            ):
                raise ValueError("Invalid PR record")
            repo = pull["head"]["repo"]
            if repo is not None and not isinstance(repo["full_name"], str):
                raise ValueError("Invalid PR source repository")
        return pulls
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Open PR query returned incomplete or invalid results") from exc


def check_remote_conflicts(
    root: Path,
    remote: str,
    targets: list[tuple[str, str | None]],
    *,
    base_ref: str | None = None,
    peers: list[str] | None = None,
    github_repo: str | None = None,
) -> None:
    """Targets pair committed object IDs with destination branch refs for self exclusion."""
    if not targets:
        return
    repository = explicit_repository(github_repo) if github_repo else github_repository(remote)
    env = os.environ.copy()
    for key in git(root, "rev-parse", "--local-env-vars").splitlines():
        if key not in ("GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT"):
            env.pop(key, None)
    local_remote = root / remote
    if local_remote.exists():
        remote = str(local_remote.resolve())
    try:
        discovery = subprocess.run(
            ["git", "ls-remote", "--symref", "--", remote],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError("Remote discovery timed out after 120 seconds") from exc
    if discovery.returncode:
        raise ValueError("Remote discovery failed; check Git transport settings and access")
    if not discovery.stdout.strip():
        if peers or base_ref or github_repo:
            raise ValueError("Remote is empty; requested integration or peer refs are unavailable")
        print("Remote is empty; no integration branch or PRs to check.", flush=True)
        return
    default = base_ref
    if default and not default.startswith("refs/heads/"):
        default = f"refs/heads/{default}"
    if not default:
        default = next(
            (
                line.split()[1]
                for line in discovery.stdout.splitlines()
                if line.startswith("ref: ") and line.split()[-1] == "HEAD"
            ),
            None,
        )
    if default is None:
        raise ValueError("Remote default branch is unavailable; set the remote HEAD or use --base")
    base_name = default.removeprefix("refs/heads/")
    pulls = open_pull_requests(root, repository, base_name) if repository else []
    env = transport_environment(root, env)
    conflicts: list[str] = []
    with tempfile.TemporaryDirectory(prefix="harness-remote-merge-") as temporary:

        def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                ["git", "--git-dir", temporary, *args],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=check,
                timeout=TIMEOUT,
            )

        def fetch(source: str, ref: str, label: str) -> str:
            try:
                run("fetch", "--quiet", "--no-tags", "--", source, ref)
            except subprocess.TimeoutExpired as exc:
                raise ValueError(f"Fetch for {label} timed out after 120 seconds") from exc
            except subprocess.CalledProcessError as exc:
                raise ValueError(f"Cannot fetch {label}; check access and retry") from exc
            return run("rev-parse", "FETCH_HEAD").stdout.strip()

        def compare(target: str, peer: str, label: str, *, overlap: bool = False) -> None:
            result = run("merge-tree", "--write-tree", target, peer, check=False)
            if result.returncode == 1:
                conflicts.append(f"{target} vs {label}:\n{result.stdout.strip()}")
            elif result.returncode:
                raise ValueError(f"Cannot compare {target} with {label}; check shared history")
            elif overlap:
                ancestor = run("merge-base", target, peer).stdout.strip()
                own = set(run("diff", "--name-only", "-z", ancestor, target).stdout.split("\0"))
                other = set(run("diff", "--name-only", "-z", ancestor, peer).stdout.split("\0"))
                common = sorted((own & other) - {""})
                if common:
                    print(f"INFO: {label} overlaps {target}: {', '.join(common)}")

        run(
            "init",
            "--bare",
            "-q",
            f"--object-format={git(root, 'rev-parse', '--show-object-format')}",
        )
        base = fetch(remote, default, default)
        for commit in dict.fromkeys(commit for commit, _ in targets):
            fetch(str(root), commit, "local target")
        proposed = next((commit for commit, branch in targets if branch == default), base)
        for commit, _ in targets:
            compare(commit, base, default)
            if proposed != base and commit != proposed:
                compare(commit, proposed, f"proposed {default}")

        for branch in peers or []:
            ref = branch if branch.startswith("refs/heads/") else f"refs/heads/{branch}"
            peer = fetch(remote, ref, f"peer branch {ref}")
            for commit, destination in targets:
                if destination != ref:
                    compare(commit, peer, f"branch {ref}", overlap=True)

        for pull in pulls:
            head = pull["head"]
            source_repo = head["repo"]["full_name"] if head["repo"] else None
            same_repository = bool(
                repository and source_repo and source_repo.casefold() == repository[1].casefold()
            )
            destination = f"refs/heads/{head['ref']}"
            relevant = [
                (commit, branch)
                for commit, branch in targets
                if not (same_repository and branch == destination)
            ]
            if not relevant:
                continue
            label = f"PR #{pull['number']} ({head['ref']})"
            peer = fetch(remote, f"refs/pull/{pull['number']}/head", label)
            if peer != head["sha"]:
                raise ValueError(f"{label} changed during the check; rerun for a fresh result")
            if same_repository:
                proposed_peer = next(
                    (commit for commit, branch in targets if branch == destination), peer
                )
                if proposed_peer != peer:
                    peer = proposed_peer
                    label = f"proposed {label}"
            for commit, _ in relevant:
                compare(commit, peer, label, overlap=True)
        if conflicts:
            raise ValueError("\n".join(["Remote merge check failed:", *conflicts]))
        print(
            f"Remote merge check passed against {default} at {base}; "
            f"queried {len(pulls)} open PRs.",
            flush=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", required=True, help="Remote name or push URL")
    parser.add_argument("--target", default="HEAD", help="Committed ref (default: HEAD)")
    parser.add_argument("--base", help="Integration branch (default: remote HEAD)")
    parser.add_argument("--peer", action="append", default=[], help="Additional remote branch")
    parser.add_argument("--github-repo", help="OWNER/REPO or HOST/OWNER/REPO for PR discovery")
    args = parser.parse_args()
    try:
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel"))
        remote = subprocess.run(
            ["git", "remote", "get-url", "--push", args.remote],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        url = remote.stdout.strip() if remote.returncode == 0 else args.remote
        commit = git(root, "rev-parse", "--verify", "--end-of-options", f"{args.target}^{{commit}}")
        branch = git(root, "rev-parse", "--symbolic-full-name", args.target)
        destination = branch if branch.startswith("refs/heads/") else None
        check_remote_conflicts(
            root,
            url,
            [(commit, destination)],
            base_ref=args.base,
            peers=args.peer,
            github_repo=args.github_repo,
        )
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Remote conflict check blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
