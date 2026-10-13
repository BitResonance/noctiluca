# NOCTILUCA

```text
                 .       *       .       *
                        .-""""-.
                     .-'  .--.  '-.
                    /    /    \    \
                   ;    |  ()  |    ;
                    \    \    /    /
                     '-.  '--'  .-'
                        '-.__.-'

                [ SIGNAL DETECTED ]
                    NOCTILUCA
             signals in the static
```

A small command-line log scanner, implemented in six languages: C, Rust, Go, Swift, Python, and Java.

[![CI](https://github.com/BitResonance/noctiluca/actions/workflows/ci.yml/badge.svg)](https://github.com/BitResonance/noctiluca/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## What it does

NOCTILUCA reads plain-text service logs and prints a compact report. It counts events by severity and service, flags malformed records, and lists repeated `ERROR` or `FATAL` messages.

All six versions follow the same input and output rules. The verifier runs each implementation against the same sample logs and checks that the output matches the expected files exactly.

## Example

```console
$ python3 python/noctiluca.py fixtures/sample.log
NOCTILUCA / REPORT
Events: 12
Malformed: 1

LEVEL COUNTS
DEBUG=1
INFO=3
WARN=2
ERROR=5
FATAL=1

SERVICE COUNTS
auth=5
api=4
gateway=1
storage=1
worker=1

REPEATED FAILURES (>=3)
auth | invalid token signature | 3
```

## Run it

Python is enough to try the project:

```bash
python3 python/noctiluca.py fixtures/sample.log
```

To build and check every implementation available on your machine:

```bash
python3 scripts/verify_outputs.py
```

The verifier skips languages whose toolchain is not installed. The CI workflow installs each toolchain separately and runs the same checks.

## Hidden signal

There is one extra command hidden in plain sight. Try `--listen` with any implementation.

## Implementations

| Language | Command |
|---|---|
| C | `make -C c && ./c/noctiluca fixtures/sample.log` |
| Rust | `cargo run --manifest-path rust/Cargo.toml -- fixtures/sample.log` |
| Go | `cd go && go run ./cmd/noctiluca ../fixtures/sample.log` |
| Swift | `swift run --package-path swift Noctiluca fixtures/sample.log` |
| Python | `python3 python/noctiluca.py fixtures/sample.log` |
| Java | `javac -d java/out java/src/main/java/dev/noctiluca/Main.java && java -cp java/out dev.noctiluca.Main fixtures/sample.log` |

Each version uses its language's standard library. The input format and ordering rules are documented in [`spec/LOG_FORMAT.md`](spec/LOG_FORMAT.md).

## Project layout

```text
c/       C implementation
rust/    Rust implementation
go/      Go implementation
swift/   Swift implementation
python/  Python implementation
java/    Java implementation
fixtures/ shared inputs and expected reports
scripts/ cross-language verifier
spec/    log format and output rules
```

## Current limits

Timestamps are checked for the expected UTC shape, but not for real calendar dates. The scanner doesn't correlate events across time windows or infer root causes; repeated failures are counted by exact service/message pair.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Changes to parsing or report output should update the spec and shared fixtures before changing the implementations.

## License

MIT. See [`LICENSE`](LICENSE).
