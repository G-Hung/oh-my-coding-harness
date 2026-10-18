"""Run bounded TLA+ checks and implementation tests from a copyable manifest."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen

from formal_support import (
    TLC_SHA256,
    TLC_URL,
    TLC_VERSION,
    PrerequisiteError,
    VerificationError,
    classify_conformance,
    classify_result,
    contained,
    digest,
    fingerprints,
    load_manifest,
)

HERE = Path(__file__).resolve().parent
MODEL_TIMEOUT = 60
MODEL_BUDGET = 300
CONFORMANCE_TIMEOUT = 120


def setup_tool(jar: Path) -> None:
    """Download only on explicit setup and replace only verified bytes."""
    if jar.exists():
        verify_tool(jar)
        print(f"Verified cached TLC {TLC_VERSION}")
        return
    with urlopen(TLC_URL, timeout=30) as response:
        payload = response.read()
    import hashlib

    if hashlib.sha256(payload).hexdigest() != TLC_SHA256:
        raise VerificationError("Downloaded TLC checksum mismatch")
    jar.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=jar.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(payload)
    try:
        temporary.replace(jar)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Installed verified TLC {TLC_VERSION}: {jar}")


def verify_tool(jar: Path) -> None:
    if not jar.is_file():
        raise PrerequisiteError("TLC jar is missing; run explicit setup or supply --tlc-jar")
    if digest(jar) != TLC_SHA256:
        raise VerificationError("Cached or supplied TLC checksum mismatch; no download attempted")


def verify_java(java: str) -> str:
    try:
        result = subprocess.run(
            [java, "-version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise PrerequisiteError(f"Java is unavailable: {error}") from error
    output = result.stdout + result.stderr
    version = re.search(r'version "(\d+)', output)
    if result.returncode != 0 or version is None or int(version[1]) < 21:
        raise PrerequisiteError("Java 21 or later is required")
    return output.strip()


def execute(argv: list[str], cwd: Path, log: Path, timeout: float) -> tuple[int, str]:
    """Keep process evidence even when a child times out or cannot start."""
    with log.open("w", encoding="utf-8") as stream:
        try:
            process = subprocess.Popen(
                argv,
                cwd=cwd,
                stdout=stream,
                stderr=subprocess.STDOUT,
                start_new_session=os.name == "posix",
            )
        except OSError as error:
            stream.write(f"\nUNAVAILABLE: {error}\n")
            raise PrerequisiteError(f"Cannot start {argv[0]}; see {log.name}") from error
        try:
            code = process.wait(timeout=timeout)
        except BaseException as error:
            # Kill only the group created for this command, including nested
            # test processes. On non-POSIX systems, terminate the direct child.
            try:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
            except ProcessLookupError:
                pass
            process.wait()
            if isinstance(error, subprocess.TimeoutExpired):
                stream.write(f"\nTIMEOUT after {timeout:.1f}s\n")
                raise VerificationError(f"Command timed out; see {log.name}") from error
            raise
    return code, log.read_text(encoding="utf-8", errors="replace")


def write_report(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, delete=False, encoding="utf-8"
    ) as stream:
        temporary = Path(stream.name)
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def verify(manifest: Path, java: str, jar: Path, report_path: Path | None = None) -> int:
    root = manifest.parent.resolve()
    # Reports and logs are retained for both passing and failed checks.
    runs = root / ".cache" / "formal" / "runs"
    if not runs.resolve().is_relative_to(root):
        print("FAILED: The report cache escapes the manifest root", file=sys.stderr)
        return 1
    runs.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix="run-", dir=runs))
    report = run_dir / "report.json"
    payload = {
        "schema_version": 1,
        "report_kind": "bounded-formal-verification",
        "status": "failed",
        "checks": [],
        "inputs": {},
        "tool": {"version": TLC_VERSION, "sha256": TLC_SHA256},
        "logs": str(run_dir),
    }
    paths: list[Path] = []
    before: dict[str, str] = {}
    export_report: Path | None = None
    started = time.monotonic()
    try:
        if report_path is not None:
            destination = report_path.resolve()
            if destination.is_relative_to(root) and not destination.is_relative_to(root / ".cache"):
                raise VerificationError(
                    "--report must be outside the manifest root or inside .cache"
                )
            if destination.suffix != ".json":
                raise VerificationError("--report must name a JSON report")
            if destination.exists():
                previous = json.loads(destination.read_text(encoding="utf-8"))
                if (
                    not isinstance(previous, dict)
                    or previous.get("report_kind") != payload["report_kind"]
                ):
                    raise VerificationError("--report cannot replace an unrelated existing file")
            export_report = report_path
        data, paths = load_manifest(manifest)
        # Hash the runner even when it is outside an adopted manifest directory.
        payload["runner"] = {
            "verify.py": digest(Path(__file__).resolve()),
            "formal_support.py": digest(HERE / "formal_support.py"),
        }
        before = fingerprints(root, paths)
        payload["inputs"] = before
        verify_tool(jar)
        payload["tool"]["observed_sha256"] = digest(jar)
        payload["java"] = verify_java(java)
        model_started = time.monotonic()
        for model in data["models"]:
            directory = contained(root, model["directory"], directory=True)
            for check in model["checks"]:
                name = f"{model['id']}-{Path(check['config']).stem}"
                log = run_dir / model["id"] / f"{Path(check['config']).stem}.log"
                log.parent.mkdir(parents=True, exist_ok=True)
                entry = {
                    "id": name,
                    "layer": "model",
                    "kind": check["kind"],
                    "log": log.relative_to(run_dir).as_posix(),
                    "status": "failed",
                }
                payload["checks"].append(entry)
                check_started = time.monotonic()
                try:
                    remaining = MODEL_BUDGET - (check_started - model_started)
                    if remaining <= 0:
                        raise VerificationError("Model exploration exceeded the 300-second budget")
                    # The copied directory also contains any trace files generated
                    # by TLC. Never let the checker write into model sources.
                    with tempfile.TemporaryDirectory(prefix="formal-model-") as temporary:
                        work = Path(temporary) / "model"
                        work.mkdir()
                        for source in directory.rglob("*"):
                            if source.suffix in {".tla", ".cfg"}:
                                relative = source.relative_to(directory)
                                target = work / relative
                                target.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(source, target)
                        argv = [
                            java,
                            "-Xmx512m",
                            "-XX:+UseParallelGC",
                            "-cp",
                            str(jar),
                            "tlc2.TLC",
                            "-workers",
                            "1",
                            "-metadir",
                            str(Path(temporary) / "states"),
                            "-config",
                            check["config"],
                            model["spec"],
                        ]
                        code, output = execute(argv, work, log, min(MODEL_TIMEOUT, remaining))
                    entry["exit_code"] = code
                    entry.update(classify_result(code, output, check.get("expected_invariant")))
                    entry["status"] = "passed"
                except VerificationError as error:
                    entry["status"] = (
                        "blocked" if isinstance(error, PrerequisiteError) else "failed"
                    )
                    entry["error"] = str(error)
                    raise
                finally:
                    entry["duration_seconds"] = round(time.monotonic() - check_started, 3)
                print(f"PASS {name}: {entry['outcome']}", flush=True)
        for command in data["conformance"]:
            log = run_dir / "conformance" / f"{command['id']}.log"
            log.parent.mkdir(parents=True, exist_ok=True)
            argv = [sys.executable if arg == "{python}" else arg for arg in command["argv"]]
            entry = {
                "id": command["id"],
                "layer": "implementation",
                "argv": argv,
                "log": log.relative_to(run_dir).as_posix(),
                "status": "failed",
            }
            payload["checks"].append(entry)
            check_started = time.monotonic()
            try:
                code, output = execute(
                    argv, contained(root, command["cwd"], directory=True), log, CONFORMANCE_TIMEOUT
                )
                entry["exit_code"] = code
                if code != 0:
                    raise VerificationError(f"Implementation conformance failed: {command['id']}")
                entry.update(classify_conformance(output, command))
                entry["status"] = "passed"
            except VerificationError as error:
                entry["status"] = "blocked" if isinstance(error, PrerequisiteError) else "failed"
                entry["error"] = str(error)
                raise
            finally:
                entry["duration_seconds"] = round(time.monotonic() - check_started, 3)
            print(f"PASS {command['id']}: implementation conformance", flush=True)
        if fingerprints(root, paths) != before or digest(jar) != TLC_SHA256:
            raise VerificationError("Inputs or tool changed during verification; evidence is stale")
        payload["status"] = "passed"
    except (OSError, ValueError, VerificationError, KeyboardInterrupt) as error:
        payload["status"] = "blocked" if isinstance(error, PrerequisiteError) else "failed"
        payload["error"] = str(error) or "Verification was interrupted"
        print(f"{payload['status'].upper()}: {error}", file=sys.stderr)
    finally:
        if before:
            try:
                _, after_paths = load_manifest(manifest)
                after = fingerprints(root, after_paths)
                payload["inputs_after"] = after
                if after != before:
                    payload["status"] = "failed"
                    payload["error"] = "Inputs changed during verification; evidence is stale"
                runner_after = {
                    "verify.py": digest(Path(__file__).resolve()),
                    "formal_support.py": digest(HERE / "formal_support.py"),
                }
                payload["runner_after"] = runner_after
                if runner_after != payload["runner"]:
                    payload["status"] = "failed"
                    payload["error"] = "Runner changed during verification; evidence is stale"
            except (OSError, VerificationError):
                payload["status"] = "failed"
                payload["error"] = "An input disappeared or became invalid during verification"
        payload["duration_seconds"] = round(time.monotonic() - started, 3)
        write_report(report, payload)
        if export_report is not None:
            write_report(export_report, payload)
        print(f"Report: {report}", flush=True)
    return 0 if payload["status"] == "passed" else 1


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    setup = bool(args and args[0] == "setup")
    if setup:
        args.pop(0)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tlc-jar", type=Path, default=HERE / ".cache/tla/tla2tools-v1.7.2.jar")
    if not setup:
        parser.add_argument("--manifest", type=Path, default=HERE / "python.json")
        parser.add_argument("--java", default="java")
        parser.add_argument("--report", type=Path)
    options = parser.parse_args(args)
    if setup:
        try:
            setup_tool(options.tlc_jar.resolve())
        except (OSError, VerificationError) as error:
            print(f"Setup failed: {error}", file=sys.stderr)
            return 1
        return 0
    return verify(
        options.manifest.resolve(), options.java, options.tlc_jar.resolve(), options.report
    )


if __name__ == "__main__":
    raise SystemExit(main())
