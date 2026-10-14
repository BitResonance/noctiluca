"""Unit tests for the privacy-conscious terminal profile."""
from __future__ import annotations

import unittest

from project_profile import collect_profile, format_profile


class ProjectProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = collect_profile(
            system="TestOS",
            release="1.2",
            machine="x86_64",
            python_version="3.12.0",
            which=lambda name: "/tool/" + name if name in {"cc", "python3"} else None,
        )

    def test_profile_mentions_project_and_six_languages(self) -> None:
        output = format_profile(self.rows)
        self.assertIn("NOCTILUCA // SYSTEM PROFILE", output)
        self.assertIn("C · Rust · Go · Swift · Python · Java", output)

    def test_environment_fields_are_injected_for_deterministic_tests(self) -> None:
        fields = dict(self.rows)
        self.assertEqual(fields["PLATFORM"], "TestOS 1.2 · x86_64")
        self.assertEqual(fields["RUNTIME"], "Python 3.12.0 (profile utility)")

    def test_toolchain_detection_is_explicit(self) -> None:
        fields = dict(self.rows)
        self.assertIn("C ✓", fields["TOOLCHAINS"])
        self.assertIn("Python ✓", fields["TOOLCHAINS"])
        self.assertIn("Rust —", fields["TOOLCHAINS"])

    def test_no_color_output_contains_no_ansi_escape(self) -> None:
        output = format_profile(self.rows, color=False)
        self.assertNotIn("\033[", output)
        self.assertTrue(output.endswith("\n"))

    def test_colored_output_wraps_header_in_ansi(self) -> None:
        output = format_profile(self.rows, color=True)
        self.assertIn("\033[1;96mNOCTILUCA // SYSTEM PROFILE\033[0m", output)

    def test_profile_does_not_include_host_identity_or_local_paths(self) -> None:
        output = format_profile(self.rows)
        self.assertNotIn("/tool/", output)
        self.assertNotIn("/home/", output)
        self.assertNotIn("HOSTNAME", output)
        self.assertNotIn("USERNAME", output)


if __name__ == "__main__":
    unittest.main()
