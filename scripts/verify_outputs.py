#!/usr/bin/env python3
"""Run locally available implementations against shared golden fixtures."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    (ROOT / "fixtures" / "sample.log", ROOT / "fixtures" / "sample.expected.txt"),
    (ROOT / "fixtures" / "edge_cases.log", ROOT / "fixtures" / "edge_cases.expected.txt"),
    (ROOT / "fixtures" / "empty.log", ROOT / "fixtures" / "empty.expected.txt"),
)


def available(name: str) -> bool:
    return shutil.which(name) is not None


def run(label: str, command_template: list[str], *, cwd: Path = ROOT,
        prepare: list[list[str]] | None = None) -> bool:
    try:
        for setup_command in prepare or []:
            subprocess.run(setup_command, cwd=ROOT, check=True, timeout=180)
        for input_path, expected_path in CASES:
            input_arg = str(Path(__import__("os").path.relpath(input_path, cwd)))
            command = [part.replace("{input}", input_arg) for part in command_template]
            result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, timeout=180)
            expected = expected_path.read_bytes()
            if result.stdout != expected:
                print(f"FAIL {label} / {input_path.name}: output differs from {expected_path.name}")
                sys.stdout.write(result.stdout.decode("utf-8", errors="replace"))
                sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
                return False
        command = [part.replace("{input}", "--listen") for part in command_template]
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, timeout=180)
        expected_signal = (ROOT / "fixtures" / "signal.expected.txt").read_bytes()
        if result.stdout != expected_signal:
            print(f"FAIL {label} / --listen: hidden signal output differs from signal.expected.txt")
            sys.stdout.write(result.stdout.decode("utf-8", errors="replace"))
            sys.stderr.write(result.stderr.decode("utf-8", errors="replace"))
            return False
        print(f"PASS {label}: {len(CASES)} fixtures + hidden signal")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"FAIL {label}: {exc}")
        if isinstance(exc, subprocess.CalledProcessError):
            if exc.stdout:
                sys.stdout.write(exc.stdout.decode("utf-8", errors="replace"))
            if exc.stderr:
                sys.stderr.write(exc.stderr.decode("utf-8", errors="replace"))
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("c", "rust", "go", "swift", "python", "java"),
                        help="verify only one implementation (useful in CI)")
    selected = parser.parse_args().language
    checks: list[tuple[str, str, list[str], Path, list[list[str]]]] = []

    def add(lang: str, tool: str, command: list[str], cwd: Path = ROOT,
            prepare: list[list[str]] | None = None) -> None:
        if selected is not None and selected != lang:
            return
        if available(tool):
            checks.append((lang, tool, command, cwd, prepare or []))
        else:
            print(f"SKIP {lang}: {tool} not installed")

    add("c", "cc", ["./c/noctiluca", "{input}"], prepare=[["make", "-C", "c"]])
    add("rust", "cargo", ["cargo", "run", "--quiet", "--", "{input}"], cwd=ROOT / "rust")
    add("go", "go", ["go", "run", "./cmd/noctiluca", "{input}"], cwd=ROOT / "go")
    add("swift", "swift", ["swift", "run", "--package-path", "swift", "Noctiluca", "{input}"])
    add("python", "python3", ["python3", "python/noctiluca.py", "{input}"])
    if available("javac") and available("java") and (selected is None or selected == "java"):
        checks.append(("java", "javac", ["java", "-cp", "java/out", "dev.noctiluca.Main", "{input}"], ROOT,
                       [["javac", "-d", "java/out", "java/src/main/java/dev/noctiluca/Main.java"]]))
    elif selected in (None, "java"):
        print("SKIP java: javac/java not installed")

    failures = 0
    for label, _tool, command, cwd, prepare in checks:
        if not run(label, command, cwd=cwd, prepare=prepare):
            failures += 1
    print(f"\nChecked {len(checks)} implementation(s); failures: {failures}.")
    if selected and not checks:
        return 2
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
