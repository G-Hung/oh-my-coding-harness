"""Validate the copyable manifest and classify pinned TLC results."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

TLC_VERSION = "1.7.2"
TLC_SHA256 = "fa18543e44ed5974a85bd2c60c0dc16620ae117680ea8e693d2691999ed90b22"
TLC_URL = f"https://github.com/tlaplus/tlaplus/releases/download/v{TLC_VERSION}/tla2tools.jar"


class VerificationError(RuntimeError):
    """A verification result cannot establish the requested evidence."""


class PrerequisiteError(VerificationError):
    """A required runtime or local permission is unavailable."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contained(root: Path, name: str, *, directory: bool = False) -> Path:
    """Reject paths that escape the manifest root, including through symlinks."""
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise VerificationError("Manifest paths must be nonempty relative paths")
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise VerificationError(f"Manifest path escapes its root: {name}")
    if not (path.is_dir() if directory else path.is_file()):
        raise VerificationError(f"Missing manifest {'directory' if directory else 'file'}: {name}")
    return path


def strings(value: object, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise VerificationError(f"{label} must be a nonempty list of strings")
    return value


def identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", value):
        raise VerificationError(f"Invalid {label}")
    return value


def load_manifest(path: Path) -> tuple[dict, list[Path]]:
    """Check required inputs before running a tool or project command."""
    root = path.parent.resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise VerificationError(f"Cannot read manifest: {error}") from error
    if not isinstance(data, dict) or data.get("version") != 1:
        raise VerificationError("Manifest version must be 1")
    files = {path.resolve()}
    ids: set[str] = set()
    models = data.get("models")
    commands = data.get("conformance")
    if not isinstance(models, list) or not models:
        raise VerificationError("Manifest must contain at least one model")
    if not isinstance(commands, list) or not commands:
        raise VerificationError("Manifest must contain implementation conformance commands")
    for model in models:
        if not isinstance(model, dict):
            raise VerificationError("Model entries must be objects")
        name = identifier(model.get("id"), "model ID")
        if name in ids:
            raise VerificationError(f"Duplicate model ID: {name}")
        ids.add(name)
        directory = contained(root, model.get("directory"), directory=True)
        spec = model.get("spec")
        if not isinstance(spec, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*\.tla", spec):
            raise VerificationError("Model spec must be a TLA+ module filename")
        contained(directory, spec)
        # Include sibling modules/configurations so imported local model inputs
        # are copied and fingerprinted together. Keep external modules explicit.
        for file in directory.rglob("*"):
            if file.suffix in {".tla", ".cfg"}:
                files.add(contained(root, file.relative_to(root).as_posix()))
        for source in strings(model.get("implementation_files"), "implementation_files"):
            files.add(contained(root, source))
        checks = model.get("checks")
        if not isinstance(checks, list) or not checks:
            raise VerificationError(f"No checks for model {name}")
        check_ids: set[str] = set()
        kinds: set[str] = set()
        for check in checks:
            if not isinstance(check, dict):
                raise VerificationError("Model checks must be objects")
            config = check.get("config")
            if not isinstance(config, str) or not re.fullmatch(
                r"[A-Za-z][A-Za-z0-9_-]*\.cfg", config
            ):
                raise VerificationError("Check config must be a configuration filename")
            contained(directory, config)
            if config in check_ids:
                raise VerificationError(f"Duplicate configuration: {config}")
            check_ids.add(config)
            kind = check.get("kind")
            if kind not in {"baseline", "negative", "witness"}:
                raise VerificationError(f"Invalid check kind: {kind}")
            kinds.add(kind)
            expected = check.get("expected_invariant")
            if kind == "baseline":
                if expected is not None:
                    raise VerificationError("Baselines cannot expect an invariant violation")
            elif not isinstance(expected, str) or not re.fullmatch(
                r"[A-Za-z][A-Za-z0-9_]*", expected
            ):
                raise VerificationError("Controls and witnesses need an exact expected invariant")
        if not {"baseline", "negative"}.issubset(kinds):
            raise VerificationError("Each model needs a baseline and a negative control")
    command_ids: set[str] = set()
    for command in commands:
        if not isinstance(command, dict):
            raise VerificationError("Conformance entries must be objects")
        name = identifier(command.get("id"), "conformance ID")
        if name in command_ids:
            raise VerificationError(f"Duplicate conformance ID: {name}")
        command_ids.add(name)
        argv = strings(command.get("argv"), "argv")
        if any("{" in arg or "}" in arg for arg in argv if arg != "{python}"):
            raise VerificationError("Only the exact {python} argv placeholder is supported")
        for field in ("tests_pattern", "skips_pattern"):
            pattern = command.get(field)
            try:
                compiled = re.compile(pattern) if isinstance(pattern, str) else None
            except re.error as error:
                raise VerificationError(f"Invalid {field}: {error}") from error
            if compiled is None or "count" not in compiled.groupindex:
                raise VerificationError(f"{field} needs a named count group")
        contained(root, command.get("cwd"), directory=True)
        for source in strings(command.get("inputs"), "conformance inputs"):
            files.add(contained(root, source))
    return data, sorted(files)


def classify_conformance(output: str, command: dict) -> dict:
    """Do not accept an empty or skipped implementation suite as evidence."""
    tests = re.search(command["tests_pattern"], output)
    skips = re.search(command["skips_pattern"], output)
    try:
        count = int(tests["count"]) if tests else 0
        skipped = int(skips["count"]) if skips else 0
    except (TypeError, ValueError) as error:
        raise VerificationError("Conformance summary contains an invalid test count") from error
    if count < 1 or skipped > 0:
        raise VerificationError(
            "Conformance tests were empty, skipped, or had no recognized summary"
        )
    return {"tests": count, "skipped": skipped}


def classify_result(code: int, output: str, expected: str | None) -> dict:
    """Accept complete exploration or the exact expected counterexample."""
    counts = re.search(
        r"([\d,]+) states generated, ([\d,]+) distinct states found, "
        r"([\d,]+) states left on queue",
        output,
    )
    violations = re.findall(r"Invariant (\w+) is violated", output)
    values = [int(value.replace(",", "")) for value in counts.groups()] if counts else None
    if expected is None:
        accepted = (
            code == 0
            and "Model checking completed. No error has been found." in output
            and values is not None
            and values[0] > 0
            and values[1] > 0
            and values[2] == 0
            and not violations
        )
    else:
        accepted = (
            code == 12
            and violations == [expected]
            and "The behavior up to this point is:" in output
            and re.search(r"State 1:", output) is not None
        )
    if not accepted:
        if "SocketException" in output and "Operation not permitted" in output:
            raise PrerequisiteError("TLC needs local socket permission in this environment")
        raise VerificationError(f"TLC failed or was incomplete (exit {code})")
    return {
        "outcome": "complete" if expected is None else "expected_counterexample",
        "expected_invariant": expected,
        "distinct_states": values[1] if values else None,
        "pending_states": values[2] if values else None,
    }


def fingerprints(root: Path, paths: list[Path]) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): digest(path) for path in paths}
