#!/usr/bin/env python3
"""NOCTILUCA: deterministic log summary and repeated-failure detector."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

LEVELS = ("DEBUG", "INFO", "WARN", "ERROR", "FATAL")


def valid_timestamp(value: str) -> bool:
    if len(value) != 20:
        return False
    if value[4] != "-" or value[7] != "-" or value[10] != "T":
        return False
    if value[13] != ":" or value[16] != ":" or value[19] != "Z":
        return False
    return all(value[i].isdigit() for i in (0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18))


def analyze(path: Path) -> str:
    level_counts: Counter[str] = Counter()
    service_counts: Counter[str] = Counter()
    failures: Counter[tuple[str, str]] = Counter()
    events = malformed = 0

    with path.open("r", encoding="utf-8") as stream:
        for raw_line in stream:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 4 or not valid_timestamp(parts[0]) or parts[1] not in LEVELS:
                malformed += 1
                continue
            timestamp, level, service = parts[:3]
            message = " ".join(parts[3:])
            if not service or not message:
                malformed += 1
                continue
            events += 1
            level_counts[level] += 1
            service_counts[service] += 1
            if level in ("ERROR", "FATAL"):
                failures[(service, message)] += 1

    lines = ["NOCTILUCA / REPORT", f"Events: {events}", f"Malformed: {malformed}", "", "LEVEL COUNTS"]
    lines.extend(f"{level}={level_counts[level]}" for level in LEVELS)
    lines.extend(["", "SERVICE COUNTS"])
    lines.extend(f"{service}={service_counts[service]}" for service in sorted(service_counts, key=lambda name: (-service_counts[name], name)))
    lines.extend(["", "REPEATED FAILURES (>=3)"])
    repeated = sorted(
        ((service, message, count) for (service, message), count in failures.items() if count >= 3),
        key=lambda item: (-item[2], item[0], item[1]),
    )
    lines.extend(f"{service} | {message} | {count}" for service, message, count in repeated)
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--listen":
        sys.stdout.write(
            "                 .      *\n"
            "                      .\n"
            "             .-\"\"\"\"-.\n"
            "          .-'  .--.  '-.\n"
            "         /   .      .   \\\n"
            "        |     .--.      |\n"
            "         \\    '----'    /\n"
            "          '-.        .-'\n"
            "             '------'\n\n"
            "       SIGNAL SOURCE: UNKNOWN\n"
            "       SOME THINGS ARE BETTER LEFT UNPARSED.\n"
        )
        return 0
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print("Usage: noctiluca.py <log-file>")
        return 0 if len(argv) == 2 else 2
    path = Path(argv[1])
    try:
        sys.stdout.write(analyze(path))
    except OSError as exc:
        print(f"noctiluca: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
