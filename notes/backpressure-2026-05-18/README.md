# Backpressure Instrumentation — 2026-05-18

Open Item #1 from the 2026-05-17 handoff. Goal: characterize POST
latency and queue dynamics at varying subscriber-side rates on a
live feed from Albert.

## What's measured

- Per-frame subscriber timing CSV (one row per `_emit` call)
- 1 Hz poll of `rtsm-dev` `/stats` (queue depth + counters)

## Run protocol

For each rate in {6.0, 3.0, 1.5}:

1. Camera container running on Albert (6 Hz, unchanged).
2. `./scripts/backpressure-run.sh <rate>` on Execution Jetson.
3. Walk Albert through apartment ~3-5 minutes, similar path each
   time. Try to revisit similar object clusters across runs.
4. Ctrl-C to stop. Two CSVs land in `run-<rate>Hz-<ts>/`.

## Analysis (separate script, written after first run)

`./scripts/analyze-backpressure.py run-*Hz-*/` produces a
per-rate table of p50/p95/p99 post latency, fail/skip rates,
and queue saturation behavior.

## Caveats

- `t_capture_ns` is Albert's clock; `t_received_ns` and later are
  Execution clock. Don't subtract across machines without grain
  of salt.
- Subscriber-side decimation only — camera still publishes 6 Hz.
  If 3 Hz wins, follow-up session rebuilds camera at 3 Hz to
  realize Albert-side gains (see "Two-stage rate-reduction" in
  session handoff).
- Today's load profile is "early-life" (lots of novel detections).
  Steady-state (after Items #2, #3, Gate 2.5) will be lower.
