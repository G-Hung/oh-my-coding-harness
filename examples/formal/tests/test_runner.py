"""Reject incomplete evidence and exercise actual process cleanup."""

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formal_support as support
import verify

COMPLETE = (
    "Model checking completed. No error has been found.\n"
    "200 states generated, 100 distinct states found, 0 states left on queue."
)


def counterexample(invariant):
    return "\n".join(
        [
            f"Invariant {invariant} is violated",
            "The behavior up to this point is:",
            "State 1: initial",
        ]
    )


class ResultTests(unittest.TestCase):
    def test_complete_baseline(self):
        self.assertEqual(support.classify_result(0, COMPLETE, None)["distinct_states"], 100)
        self.assertEqual(
            support.classify_result(0, COMPLETE.replace("200", "2,000"), None)["pending_states"],
            0,
        )

    def test_incomplete_and_abnormal_baselines_fail(self):
        for code, output in [
            (0, ""),
            (0, COMPLETE.replace("0 states left", "1 states left")),
            (0, COMPLETE.replace("100 distinct", "0 distinct")),
            (-9, COMPLETE),
            (1, COMPLETE),
        ]:
            with (
                self.subTest(code=code, output=output),
                self.assertRaises(support.VerificationError),
            ):
                support.classify_result(code, output, None)

    def test_controls_require_exact_counterexample(self):
        self.assertEqual(
            support.classify_result(12, counterexample("Safe"), "Safe")["outcome"],
            "expected_counterexample",
        )
        for code, output in [
            (0, counterexample("Safe")),
            (1, counterexample("Safe")),
            (12, counterexample("Other")),
            (12, "Invariant Safe is violated"),
            (12, counterexample("Safe") + "\nInvariant Other is violated"),
        ]:
            with (
                self.subTest(code=code, output=output),
                self.assertRaises(support.VerificationError),
            ):
                support.classify_result(code, output, "Safe")

    def test_socket_permission_is_a_prerequisite_failure(self):
        with self.assertRaises(support.PrerequisiteError):
            support.classify_result(255, "SocketException: Operation not permitted", None)

    def test_conformance_rejects_empty_or_skipped_suites(self):
        command = {
            "tests_pattern": r"Ran (?P<count>\d+) tests",
            "skips_pattern": r"skipped=(?P<count>\d+)",
        }
        self.assertEqual(support.classify_conformance("Ran 5 tests\nOK", command)["tests"], 5)
        for output in ("", "Ran 0 tests", "Ran 5 tests\nOK (skipped=1)"):
            with self.subTest(output=output), self.assertRaises(support.VerificationError):
                support.classify_conformance(output, command)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="formal-runner-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "kit"
        shutil.copytree(
            verify.HERE, self.root, ignore=shutil.ignore_patterns(".cache", "__pycache__")
        )
        self.manifest = self.root / "python.json"
        self.jar = self.root.parent / "tool.jar"
        self.jar.write_bytes(b"fixture-tool")

    def data(self):
        return json.loads(self.manifest.read_text())

    def save(self, data):
        self.manifest.write_text(json.dumps(data))

    def run_fixture(self, execute):
        with (
            patch.object(verify, "verify_java", return_value="fixture-java"),
            patch.object(verify, "verify_tool"),
            patch.object(verify, "TLC_SHA256", support.digest(self.jar)),
            patch.object(verify, "execute", side_effect=execute),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            return verify.verify(self.manifest, "java", self.jar)

    def successful_process(self, argv, cwd, log, timeout):
        if "tlc2.TLC" not in argv:
            output = "Ran 5 tests\nOK"
            log.write_text(output)
            return 0, output
        config = argv[argv.index("-config") + 1]
        check = next(c for c in self.data()["models"][0]["checks"] if c["config"] == config)
        expected = check.get("expected_invariant")
        output = counterexample(expected) if expected else COMPLETE
        log.write_text(output)
        return (12 if expected else 0), output

    def report(self):
        return json.loads(
            next((self.root / ".cache/formal/runs").glob("*/report.json")).read_text()
        )

    def test_both_manifests_have_complete_inputs(self):
        for name in ("python.json", "typescript.json"):
            data, inputs = support.load_manifest(self.root / name)
            self.assertGreater(len(inputs), 8)
            self.assertEqual(len(data["models"][0]["checks"]), 7)

    def test_baseline_without_negative_control_is_rejected(self):
        data = self.data()
        data["models"][0]["checks"] = data["models"][0]["checks"][:1]
        self.save(data)
        with self.assertRaisesRegex(support.VerificationError, "negative control"):
            support.load_manifest(self.manifest)

    def test_missing_source_and_path_escape_fail_before_execution(self):
        for name in ("missing.py", "../outside.py"):
            data = self.data()
            data["models"][0]["implementation_files"] = [name]
            self.save(data)
            with self.subTest(name=name), self.assertRaises(support.VerificationError):
                support.load_manifest(self.manifest)

    def test_escaping_symlink_is_rejected(self):
        outside = self.root.parent / "outside.py"
        outside.write_text("outside")
        source = self.root / "python/cache.py"
        source.unlink()
        source.symlink_to(outside)
        with self.assertRaisesRegex(support.VerificationError, "escapes"):
            support.load_manifest(self.manifest)

    def test_complete_run_keeps_identity_and_logs(self):
        self.assertEqual(self.run_fixture(self.successful_process), 0)
        report = self.report()
        self.assertEqual(report["status"], "passed")
        self.assertEqual(len(report["checks"]), 8)
        self.assertEqual(report["inputs"], report["inputs_after"])
        self.assertEqual(report["checks"][-1]["tests"], 5)
        for item in report["checks"]:
            self.assertTrue((Path(report["logs"]) / item["log"]).is_file())

    def test_source_mutation_invalidates_successful_checks(self):
        def mutate(argv, cwd, log, timeout):
            result = self.successful_process(argv, cwd, log, timeout)
            if "tlc2.TLC" not in argv:
                (self.root / "python/cache.py").write_text("changed")
            return result

        self.assertEqual(self.run_fixture(mutate), 1)
        self.assertIn("stale", self.report()["error"])

    def test_model_runs_in_a_disposable_copy(self):
        paths = []

        def generated_file(argv, cwd, log, timeout):
            if "tlc2.TLC" in argv:
                paths.append(cwd)
                self.assertNotEqual(cwd, self.root / "models/fenced-cache")
                (cwd / "generated.tla").write_text("temporary trace")
            return self.successful_process(argv, cwd, log, timeout)

        self.assertEqual(self.run_fixture(generated_file), 0)
        self.assertTrue(paths)
        self.assertTrue(all(not path.exists() for path in paths))
        self.assertFalse((self.root / "models/fenced-cache/generated.tla").exists())

    def test_model_failure_preserves_log_and_stops_conformance(self):
        def wrong_violation(argv, cwd, log, timeout):
            log.write_text(counterexample("Wrong"))
            return 12, counterexample("Wrong")

        self.assertEqual(self.run_fixture(wrong_violation), 1)
        report = self.report()
        self.assertEqual(len(report["checks"]), 1)
        self.assertEqual(report["checks"][0]["status"], "failed")
        self.assertIn("Wrong", (Path(report["logs"]) / report["checks"][0]["log"]).read_text())

    def test_missing_jar_does_not_download(self):
        with patch.object(verify, "urlopen") as download:
            with self.assertRaises(support.PrerequisiteError):
                verify.verify_tool(self.root / "missing.jar")
            download.assert_not_called()

    def test_bad_cached_jar_is_not_replaced_or_downloaded(self):
        with patch.object(verify, "urlopen") as download:
            with self.assertRaisesRegex(support.VerificationError, "checksum"):
                verify.setup_tool(self.jar)
            download.assert_not_called()
        self.assertEqual(self.jar.read_bytes(), b"fixture-tool")

    def test_setup_rejects_bad_download_without_publishing_it(self):
        destination = self.root / ".cache/tool.jar"
        with patch.object(verify, "urlopen", return_value=io.BytesIO(b"wrong-bytes")):
            with self.assertRaisesRegex(support.VerificationError, "checksum"):
                verify.setup_tool(destination)
        self.assertFalse(destination.exists())

    def test_setup_publishes_verified_bytes_and_reuses_the_cache(self):
        destination = self.root / ".cache/tool.jar"
        payload = b"fixture-verified-tool"
        import hashlib

        with (
            patch.object(verify, "TLC_SHA256", hashlib.sha256(payload).hexdigest()),
            patch.object(verify, "urlopen", return_value=io.BytesIO(payload)) as download,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            verify.setup_tool(destination)
            self.assertEqual(destination.read_bytes(), payload)
            verify.setup_tool(destination)
            download.assert_called_once()

    def test_new_model_input_invalidates_successful_checks(self):
        def add_input(argv, cwd, log, timeout):
            result = self.successful_process(argv, cwd, log, timeout)
            if "tlc2.TLC" not in argv:
                (self.root / "models/fenced-cache/Extra.tla").write_text("new model input")
            return result

        self.assertEqual(self.run_fixture(add_input), 1)
        self.assertIn("stale", self.report()["error"])

    def test_old_or_missing_java_is_blocked(self):
        with patch.object(
            verify.subprocess,
            "run",
            return_value=subprocess.CompletedProcess([], 0, "", 'openjdk version "17"'),
        ):
            with self.assertRaises(support.PrerequisiteError):
                verify.verify_java("java")
        with patch.object(verify.subprocess, "run", side_effect=FileNotFoundError("java")):
            with self.assertRaises(support.PrerequisiteError):
                verify.verify_java("java")

    def test_process_timeout_retains_output(self):
        log = self.root / "process.log"
        with self.assertRaisesRegex(support.VerificationError, "timed out"):
            verify.execute(
                [sys.executable, "-c", "import time; print('started', flush=True); time.sleep(5)"],
                self.root,
                log,
                0.5,
            )
        self.assertIn("started", log.read_text())
        self.assertIn("TIMEOUT", log.read_text())

    def test_report_cannot_overwrite_source(self):
        source = self.root / "python/cache.py"
        before = source.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(verify.verify(self.manifest, "java", self.jar, source), 1)
        self.assertEqual(source.read_bytes(), before)

    def test_report_cannot_overwrite_external_project_configuration(self):
        target = self.root.parent / "package.json"
        target.write_text('{"private": true}')
        before = target.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(verify.verify(self.manifest, "java", self.jar, target), 1)
        self.assertEqual(target.read_bytes(), before)

    def test_missing_tool_has_a_blocked_report(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(verify.verify(self.manifest, "java", self.root / "missing.jar"), 1)
        self.assertEqual(self.report()["status"], "blocked")
        self.assertEqual(self.report()["checks"], [])


if __name__ == "__main__":
    unittest.main()
