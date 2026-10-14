#!/usr/bin/env python3
"""Print a neofetch-inspired profile for the NOCTILUCA project.

The report intentionally avoids usernames, hostnames, absolute paths, and
environment-variable values. It reports the current OS/architecture and which
development toolchains appear to be available on PATH.
"""
from __future__ import annotations

import argparse
import platform
import shutil
import sys
from collections.abc import Callable, Sequence

TOOLCHAINS: tuple[tuple[str, str], ...] = (
    ("C", "cc"),
    ("Rust", "cargo"),
    ("Go", "go"),
    ("Swift", "swift"),
    ("Python", "python3"),
    ("Java", "javac"),
)


def collect_profile(
    *,
    system: str | None = None,
    release: str | None = None,
    machine: str | None = None,
    python_version: str | None = None,
    which: Callable[[str], str | None] | None = None,
) -> list[tuple[str, str]]:
    """Collect a predictable, privacy-conscious project profile.

    Parameters are injectable so the formatter can be tested without depending
    on the machine running the tests.
    """
    find_tool = which or shutil.which
    system_name = system if system is not None else platform.system()
    release_name = release if release is not None else platform.release()
    machine_name = machine if machine is not None else platform.machine()
    py_version = python_version if python_version is not None else platform.python_version()

    available = [
        f"{label} {'✓' if find_tool(command) else '—'}"
        for label, command in TOOLCHAINS
    ]

    return [
        ("PLATFORM", f"{system_name} {release_name} · {machine_name}".strip()),
        ("RUNTIME", f"Python {py_version} (profile utility)"),
        ("PURPOSE", "Deterministic service-log summarizer"),
        ("LANGUAGES", "C · Rust · Go · Swift · Python · Java"),
        ("INPUT", "UTF-8 line-oriented service logs"),
        ("ANALYSIS", "Severity counts · service totals · repeated failures"),
        ("DEPENDENCIES", "Standard library per implementation"),
        ("NETWORK", "Not used by the analyzer"),
        ("TOOLCHAINS", "  ".join(available)),
        ("PRIVACY", "No username, hostname, or local paths displayed"),
    ]


def format_profile(rows: Sequence[tuple[str, str]], *, color: bool = False) -> str:
    """Format rows as a compact terminal profile."""
    def paint(value: str, code: str) -> str:
        return f"\033[{code}m{value}\033[0m" if color else value

    label_width = max(len(label) for label, _ in rows)
    lines = [
        paint("NOCTILUCA // SYSTEM PROFILE", "1;96"),
        paint("─" * 66, "90"),
    ]
    for label, value in rows:
        lines.append(f"{paint(label.ljust(label_width), '96')}  {value}")
    lines.extend([
        paint("─" * 66, "90"),
        paint("LOCAL TOOL / SHARED CONTRACT / REPRODUCIBLE OUTPUT", "94"),
    ])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="disable ANSI colors (recommended for CI and log capture)",
    )
    args = parser.parse_args(argv)
    use_color = sys.stdout.isatty() and not args.no_color
    print(format_profile(collect_profile(), color=use_color), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
