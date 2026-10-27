#!/usr/bin/env python3
"""Print a privacy-conscious neofetch-style profile for NOCTILUCA.

The report intentionally avoids usernames, hostnames, absolute paths, and
environment-variable values. The ASCII art is a stylized penteract-like
projection: an artistic 2D sketch of a five-dimensional hypercube.
"""
from __future__ import annotations

import argparse
import platform
import shutil
import sys
from collections.abc import Callable, Sequence

ASCII_ART: tuple[str, ...] = (
    "          +--------------------+",
    "         /|                   /|",
    "        / |    +-------------+ |",
    "       +--+---/|------------|-+-+",
    "       |  |  +-|------------|-+ |",
    "       |  | /  |            | | |",
    "       |  +----+------------+ | |",
    "       | /     +-------------|-+-+",
    "       |/      |             | /",
    "       +-------+-------------+/",
    "        \\      |            /",
    "         \\     +-----------+",
    "          +----------------+",
)

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

    Detection is limited to OS/architecture and whether tool commands exist
    on PATH. Tool paths are never printed.
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
        ("LANGUAGES", "C · Rust · Go · Swift · Python · Java"),
        ("PURPOSE", "Deterministic service-log summarizer"),
        ("INPUT", "UTF-8 line-oriented service logs"),
        ("ANALYSIS", "Severity counts · service totals · repeated failures"),
        ("DEPENDENCIES", "Standard library per implementation"),
        ("TOOLCHAINS", "  ".join(available)),
        ("NETWORK", "Not used by the analyzer"),
        ("PRIVACY", "No username, hostname, or local paths displayed"),
    ]


def format_profile(rows: Sequence[tuple[str, str]], *, color: bool = False) -> str:
    """Render an ASCII hypercube alongside project/system details."""
    def paint(value: str, code: str) -> str:
        return f"\033[{code}m{value}\033[0m" if color else value

    label_width = max(len(label) for label, _ in rows)
    info_lines = [
        paint("NOCTILUCA // SYSTEM PROFILE", "1;96"),
        paint("STYLIZED PENTERACT / 5D PROJECTION", "95"),
        paint("-" * 42, "90"),
    ]
    info_lines.extend(
        f"{paint(label.ljust(label_width), '96')}  {value}"
        for label, value in rows
    )
    info_lines.extend([
        paint("-" * 42, "90"),
        paint("LOCAL ANALYZER / DETERMINISTIC OUTPUT", "94"),
    ])

    art_width = max(len(line) for line in ASCII_ART)
    height = max(len(ASCII_ART), len(info_lines))
    lines: list[str] = []
    for index in range(height):
        art = ASCII_ART[index] if index < len(ASCII_ART) else ""
        left = paint(art.ljust(art_width), "96")
        right = info_lines[index] if index < len(info_lines) else ""
        lines.append(f"{left}  {paint('|', '90')}  {right}")
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
