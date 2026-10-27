# NOCTILUCA

<pre>
          +--------------------+  |  NOCTILUCA // SYSTEM PROFILE
         /|                   /|  |  STYLIZED PENTERACT / 5D PROJECTION
        / |    +-------------+ |  |  ------------------------------------------
       +--+---/|------------|-+-+  |  PLATFORM     Linux · x86_64
       |  |  +-|------------|-+ |  |  LANGUAGES    C · Rust · Go · Swift · Python · Java
       |  | /  |            | | |  |  PURPOSE      Deterministic service-log summarizer
       |  +----+------------+ | |  |  INPUT        UTF-8 service logs
       | /     +-------------|-+-+  |  ANALYSIS     Severity + service aggregation
       |/      |             | /    |  TESTING      Shared golden fixtures
       +-------+-------------+/     |  DEPENDENCIES Standard libraries only
        \      |            /       |  NETWORK      Not used by the analyzer
         \     +-----------+        |  PRIVACY      No username, hostname or paths
          +----------------+        |  MODE         Verify / compare / repeat
</pre>

<p align="center">
  <strong>A deterministic log scanner, implemented six ways.</strong><br>
  One input contract. Six standard-library implementations. Reproducible output.
</p>

<p align="center">
  <a href="https://github.com/BitResonance/noctiluca/actions/workflows/ci.yml"><img src="https://github.com/BitResonance/noctiluca/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/languages-6-66d9ef" alt="Six languages">
  <img src="https://img.shields.io/badge/runtime%20dependencies-zero-a6e22e" alt="Zero third-party runtime dependencies">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-bd93f9" alt="MIT License"></a>
</p>

NOCTILUCA reads plain-text service logs and produces a compact, stable report. It counts events by severity and service, identifies malformed records, and surfaces repeated ERROR or FATAL messages. All six implementations follow the same specification and are verified against shared golden fixtures.

## See the profile in your terminal

Run the neofetch-like project/system summary:

    python3 scripts/project_profile.py

Use --no-color for logs and CI:

    python3 scripts/project_profile.py --no-color

The profile detects OS/architecture and which development toolchains are available. It intentionally does not print usernames, hostnames, absolute paths, or environment-variable values.

## What it does

- Counts valid events by severity and service.
- Skips malformed records while reporting their count.
- Groups repeated error messages by exact service/message pair.
- Keeps ordering and formatting deterministic for scripts and tests.
- Provides the same behavior in C, Rust, Go, Swift, Python, and Java.

## Example

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

## Run it

Python is enough to try the project:

    python3 python/noctiluca.py fixtures/sample.log

To verify every implementation whose toolchain is installed:

    python3 scripts/verify_outputs.py

Run tests for the terminal profile:

    python3 -m unittest discover -s scripts -p 'test_*.py'

The verifier skips languages whose toolchain is missing. GitHub Actions installs the toolchains in separate jobs and checks the same fixtures. The profile utility uses Python's standard library only.

## Implementations

| Language | Command |
|---|---|
| C | make -C c && ./c/noctiluca fixtures/sample.log |
| Rust | cargo run --manifest-path rust/Cargo.toml -- fixtures/sample.log |
| Go | cd go && go run ./cmd/noctiluca ../fixtures/sample.log |
| Swift | swift run --package-path swift Noctiluca fixtures/sample.log |
| Python | python3 python/noctiluca.py fixtures/sample.log |
| Java | javac -d java/out java/src/main/java/dev/noctiluca/Main.java && java -cp java/out dev.noctiluca.Main fixtures/sample.log |

Each implementation uses its language's standard library. The input format and output rules are documented in [spec/LOG_FORMAT.md](spec/LOG_FORMAT.md).

## Project layout

    c/         C implementation
    rust/      Rust implementation
    go/        Go implementation
    swift/     Swift implementation
    python/    Python implementation
    java/      Java implementation
    fixtures/  shared inputs and expected reports
    scripts/   cross-language verifier and terminal profile
    spec/      log format and output contract
    docs/      optional vector artwork and design notes

## Current limits

Timestamps are checked for the expected UTC shape, but not for real calendar dates. The scanner does not correlate events across time windows or infer root causes; repeated failures are counted by exact service/message pair.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes to parsing or report output should update the specification and shared fixtures before changing the implementations.

## License

MIT. See [LICENSE](LICENSE).
