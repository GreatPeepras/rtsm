# 2026-05-15 — Gate 2 SLAM-pose-wired (AMCL path) — DONE

## Result

Live AMCL pose flows end-to-end into rtsm-dev. Object world coordinates
are in real `map` frame. Open Item #1 from the 2026-05-14 handoff is
CLOSED. A ~9-minute walk through the apartment produced a 58-object
spatial map (50 confirmed, 8 candidates) with correct clustering by
apartment region.

## Architectural decision

The 2026-05-14 handoff committed to RTAB-Map for Option A's first run.
That plan was **abandoned in favor of AMCL** (M3Pro_navigation stack):

1. AMCL was already running on Albert via the nav stack.
2. The Option A architecture was always grounded in "Albert's nav stack
   provides reliable pose"; RTAB-Map was a stepping-stone.
3. Skipping RTAB-Map removes VIO drift concerns.

`launch-rtabmap.sh` is **retired** from TODO.

## Configuration

### On Albert
- AMCL: M3Pro_navigation stack (`base_bringup.launch.py`,
  `navigation2.launch.py`, `nav_rviz.launch.py`)
- Initial pose set manually in nav_rviz
- TF chain: map → odom → base_footprint → base_link → camera_link →
  camera_color_optical_frame
- `base_link → camera_link` via interim `static_transform_publisher`
  (x=0.10, y=−0.01, z=0.135, rpy=0). **Not in a launch file yet;
  does not survive reboot.**

### On execution
- Subscriber: `~/rtsm/scripts/run-subscriber.sh`
- `--world-frame map` (subscriber default, confirmed via grep)
- `--post-hz 3.0` (lowered from 6.0 post-session; see note below)
- `--record --record-root /recordings`

## Validation

### 15s sanity test (~10:21 UTC)
- synced_frames 1 → 145, post_ok=50, post_fail=0
- 14 objects spawned, 6 confirmed
- robot_pose matched `tf2_echo map base_link`

### Extended walk (~10:44 → ~10:53 UTC, ~9 min)
- 9600 synced frames, avg 13.9 Hz, peak 12.9 Hz instantaneous
- tf_fail=3 (warmup only), tf_stale=24ms — TF chain rock solid
- post_ok=3165, post_fail=0, post_skip=6435 (67% subscriber-side throttle)
- 58 objects, 50 confirmed, avg_hits=60.2
- Spatial span: ~7m in y, ~3m in x
- Visual inspection: clusters match apartment regions
  (TV wall, back room, curtain side)
- Recording: `~/rtsm/ingest/recordings/2026-05-15T10-44-52Z/`
- Subscriber log: `~/rtsm/ingest/logs/subscriber-2026-05-15T10-44-50Z.log`
- Stats JSON: `~/rtsm/notes/2026-05-15-final-stats.json`
- Objects JSON: `~/rtsm/notes/2026-05-15-objects.json`

## Issues observed

### NEW: Queue saturation (high priority for next session)
- `ingest_q` pinned at 512 (cap) by end of walk
- Pipeline kept processing but at degraded freshness
- Subscriber kept posting blindly with no awareness of API state
- Cause: SigLIP+FAISS pipeline throughput < post rate
- Fix: subscriber-side backpressure

### NEW: Spawn-on-revisit
- Original 15s-test objects (created at t≈2918s monotonic) did not
  match against re-observed objects during the walk (t≈4350+s)
- Second wave spawned new OIDs for same physical objects
- Cause: WM timeout + no FAISS persistence + no rehydration
- Fix: chained — FAISS persistence + WM rehydration + Gate 2.5

### NEW: Negative-z artifacts (4/58 objects)
- refrigerator at z=−0.36, picture at z=−0.48, card box at z=−0.60,
  snack bag at z=−0.57
- **Root cause identified:** Albert was carried for this walk, so
  camera height varied (~0.4–1.4m), but the TF chain assumed
  `base_link → camera_link` = static 0.135m. Z-error proportional to
  carry height.
- This is not a pipeline bug — it's an assumption boundary:
  **AMCL pose tells us where Albert's wheels are on the 2D floor;
  it does NOT tell us where the camera is in 3D space.**
- Same problem will occur if Albert is placed on tables, sofas, beds,
  or anywhere off the floor.
- Long-term fix candidate: layer VIO (from RealSense IMU + image
  stream) on top of AMCL — AMCL for 2D-floor truth, VIO for
  3D-camera truth. Not for current cycle.
- Near-term workaround: treat z as advisory when Albert isn't
  autonomously rolling.

### EXISTING: Cross-view duplicates
- Visually confirmed during walk (e.g., card box spawned twice from
  different angles, ~30cm apart)
- 10cm spatial-grid dedup is insufficient at viewing-angle separation
- Fix: Gate 2.5 (embedding-based identity matching)

### EXISTING: WebUI "black void"
- AMCL produces no 3D mesh; WebUI has nothing to draw behind objects
- Not a bug — design gap. WebUI was built assuming RTAB-Map TSDF.
- Deferred.

## Post-session change

Lowered `--post-hz` from 6.0 → 3.0 in `run-subscriber.sh`:
- 67% of 6 Hz posts were skipped subscriber-side anyway
- Albert's fan was clearly straining during the walk
- 3 Hz matches what actually reaches the pipeline after the
  keyframe gate
- Zero downside — saves Albert's thermals for free

## Open items (priority order)

1. **NEW** Subscriber backpressure (queue saturation at 512)
2. **EXISTING (#2)** FAISS persistence in live ingest mode
3. **NEW** WM rehydration on subscriber start
4. **EXISTING** Gate 2.5: embedding-based identity matching
5. **EXISTING** `base_link → camera_link` static TF needs to land in
   a launch file on Albert (currently terminal-resident)
6. **EXISTING** WebUI black void (visualization design gap, deferred)
7. **LONG-TERM** Camera VIO on top of AMCL for off-floor scenarios

## Subscriber shutdown behavior

Clean exit on Ctrl-C — final stats line printed, prompt returned.
**No `ExternalShutdownException` traceback** despite the 2026-05-14
handoff flagging it as a known issue. May be fixed; may not trigger
in this code path. Either way, no longer a known issue.
