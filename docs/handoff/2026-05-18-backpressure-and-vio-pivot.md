# 2026-05-18 — Backpressure characterization & pivot to VIO

## State

- Backpressure instrumentation complete. Data in `notes/backpressure-2026-05-18/`.
- Default `post-hz` changed from 6.0 → 2.0 (commit 38097ba).
- rtsm-dev drain rate measured at ~1–3 Hz under sustained load.
- Pipeline produces unbounded `ingest_q` growth at any sustained rate
  above ~1 Hz, but Albert's actual workload is bursty
  (move → interact → talk → move), so saturation is not a deployment concern.
- `confirmed` count plateauing during sustained input is expected behavior
  (dedup against working memory). Not a bug.

## Revised priority queue

1. ~~Backpressure instrumentation~~ ✅ 2026-05-18
2. ~~Backpressure design + impl~~ — **deprioritized**. Not needed for Albert's
   actual workload. Revisit only if usage pattern changes to sustained input.
3. **VIO — NEXT SESSION**
4. FAISS persistence in live mode
5. WM rehydration
6. Gate 2.5 (embedding re-id)
7. Gate 3 (Albert bridge)

## VIO entry notes

### Hardware: Intel RealSense D435i
- Onboard IMU (BMI055), hardware-timestamped color+depth+IR
- No native pose output (T265 had this, D435i does not)
- Need an external VIO that consumes D435i streams

### Calabi's guidance (2026-05-18)
- D435i VIO drifts initially, needs tight loop closures to self-calibrate
- Drift manifests as coordinate error on confirmed objects (not as visual
  artifacts — RTSM has no 3D mesh visualization, only coordinates+embeddings)
- RTSM's EWMA on proto-objects demotes unsupported observations, so
  drift-induced phantom detections fade with time
- ARKit on iPhone has better VIO; RTSM was originally designed against that
  baseline. D435i is a known-degraded mode that the EWMA helps absorb.

### What matters for this project
**Coordinate correctness** on confirmed objects. Not visual fidelity, not
mesh quality. "Navigate to Gerhard" must produce a pose that's actually
near Gerhard, across sessions. Everything else is downstream of that.

### Implication for stack choice
Stack choice matters less than expected. All D435i VIO options share the
drift characteristic (sensor-limited, not software-limited). Leverage is
in deployment pattern, not algorithm.

**Recommendation:** start with the lowest-setup option that publishes a TF.
Measure coordinate drift on confirmed objects over a representative session.
Move on. Don't bikeshed.

### Candidates (in increasing setup cost)
- **realsense-ros + Intel reference VIO examples** — lowest cost, unknown quality
- **VINS-Fusion (ROS2)** — well-tested with D435i, medium setup
- **ORB-SLAM3 (ROS2)** — highest quality, highest setup, has loop closure

### Calibration / warmup
Albert's ROS stack boot + LLM warmup already takes time before he's
operational. VIO loop-closure motion likely fits inside that window at
zero UX cost. **Default assumption: no explicit calibration dance needed.**
Revisit only if measured coordinate drift after boot is unacceptable for
the navigate-to-object use case.

### First-session VIO goals (suggested)
1. Get *some* VIO publishing a TF from D435i streams
2. Walk a representative route, log object coordinates over time
3. Verify confirmed-object coordinates remain stable (within nav tolerance)
   across a single session
4. Decide whether to upgrade stack or proceed to FAISS persistence

## Parked ideas

- Build baseline scene map in deliberate bursts at first deploy
  (Peep, 2026-05-18)
- Cross-reference RTSM detections against Albert's existing semantic-memory
  images (bootstrap + cross-check flavors) (Peep, 2026-05-18)
- Revisit backpressure only if workload assumption (bursty) breaks

## Methodology notes

- Subscriber-side latency measures queue-entry, not pipeline-exit. For true
  end-to-end latency, add timestamping at the rtsm-dev worker exit point.
- The `tail -n +2 | tr '\n' ' '` trick in the awk sampling was misleading —
  it appeared to print one value per run regardless of file length. Use
  `head`/`tail` with explicit row counts, or Python, for trajectory inspection.
- Locale on this machine uses comma as decimal separator (`34,1` not `34.1`).
  Some awk pipelines may sort incorrectly. Verify numeric ops if results
  look suspicious.

## Loose ends

- Untracked, should probably be versioned:
  - `scripts/backpressure-run.sh` (produced tonight's data)
  - `scripts/stats-poller.py` (polling tool used tonight)
  - `ingest/run-subscriber.sh` (example wrapper)
- Untracked, decide later:
  - `ingest/recordings/` (probably .gitignore)
  - `notes/2026-05-15-*.json` (artifacts from previous session)
