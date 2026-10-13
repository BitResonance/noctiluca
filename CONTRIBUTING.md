# Contributing

The point of this repository is that each implementation produces the same report. Please keep that contract intact when changing behavior.

1. Check spec/LOG_FORMAT.md before changing how a log line is parsed or sorted.
2. Add an input and its expected output under fixtures/ for new behavior.
3. Apply the same change to the other language implementations.
4. Run python3 scripts/verify_outputs.py. It skips toolchains that aren't installed locally.
5. Keep runtime dependencies out unless there's a clear reason to add one.

Reports should stay deterministic: no timestamps, colors, machine-specific paths, or environment details in standard output.
