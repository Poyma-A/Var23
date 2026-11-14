import subprocess
import sys
import unittest
from pathlib import Path


TEST_FILE = Path(__file__).resolve()
PROJECT = TEST_FILE.parents[1]
OPTIONS = {
    "--package": "demo",
    "--repository": (
        "https://example.org"
    ),
    "--test-mode": "off",
    "--max-depth": "2",
    "--filter": "demo",
}


class CliTests(unittest.TestCase):
    def run_cli(self, overrides):
        options = OPTIONS | overrides
        command = [
            sys.executable, "main.py"
        ]
        for key, val in options.items():
            command.extend([key, val])
        return subprocess.run(
            command,
            cwd=PROJECT,
            capture_output=True,
            text=True,
        )

    def test_invalid_options(self):
        cases = [
            ("--package",
             "two words", {}),
            (
                "--repository",
                "invalid-url",
                {},
            ),
            (
                "--repository", ".",
                {"--test-mode": "on"},
            ),
            ("--test-mode",
             "maybe", {}),
            ("--max-depth", "-1", {}),
            ("--max-depth", "abc", {}),
            ("--filter", " ", {}),
        ]
        for key, val, extra in cases:
            with self.subTest(
                option=key, value=val
            ):
                args = extra.copy()
                args[key] = val
                result = self.run_cli(
                    args
                )
                self.assertEqual(
                    result.returncode, 2
                )
                self.assertIn(
                    key, result.stderr
                )
                self.assertEqual(
                    result.stdout, ""
                )
