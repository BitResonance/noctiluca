# Log format and behavior contract

## Input format

Each non-empty, non-comment line is one event:

    <TIMESTAMP> <LEVEL> <SERVICE> <MESSAGE...>

Example:

    2026-10-13T21:00:03Z ERROR auth invalid token signature

- TIMESTAMP must match the shape YYYY-MM-DDTHH:MM:SSZ and use UTC (Z). Version 1 validates the shape, not calendar ranges.
- LEVEL is one of DEBUG, INFO, WARN, ERROR, or FATAL.
- SERVICE is a single token without whitespace.
- MESSAGE is non-empty and may contain spaces. Repeated whitespace inside a record is normalized to single spaces when parsing.
- A line whose first non-whitespace character is # is a comment. Blank lines are ignored.
- Invalid records, including unrecognized levels, increment Malformed and are skipped.

## Report contract

- Events is the number of valid records.
- Malformed is the number of invalid non-comment records.
- Level counts are always printed in this order: DEBUG, INFO, WARN, ERROR, FATAL. A missing level is printed with a count of zero.
- Service counts are sorted by count descending, then by service name ascending.
- A repeated failure is an exact (service, message) pair on ERROR or FATAL events with count greater than or equal to three.
- Repeated failures are sorted by count descending, then service ascending, then message ascending.
- Output labels and spacing are stable. Each input fixture has a corresponding expected report, and the verifier compares standard output byte-for-byte.

## Non-goals for v1

The scanner does not parse message-specific schemas, infer root cause, or determine whether a message was semantically an incident. Timestamps are validated for shape but are not used for time-window calculations.
