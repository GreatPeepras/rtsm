# Plan — live camera ingestion (cutover from replay to D435i)

**Status**: planning, not started.
**Written**: 2026-05-12, end of split-gate session.
**Context**: split-gate work shipped (`2bbd255`). Next strategic question is
how RTSM consumes Albert's live D435i feed instead of recorded sessions.

This document is the paper exercise output. No code yet. The next session
should start by reading this, doing the 10-minute Albert reconnaissance
(see "Open questions" below), then writing the shim spec.

---

## What "live" means in this system

The end-state architecture (per project design doc):

- D435i camera lives on Albert (Orin Nano).
- Albert runs ROS 2 (Humble, CycloneDDS, ROS_DOMAIN_ID=30).
- Albert publishes camera frames + nav-stack pose over ROS 2.
- Execution Jetson (Orin AGX, RTSM host) is on the same DDS domain.
- RTSM subscribes, ingests, maintains WM.
- Query API on `:8002` serves spatial lookups to the rest of the stack.

ROS 2 is already the inter-machine transport; that work is done. What is
*not* done: RTSM has no ROS 2 ingestion path. It only consumes the replay
tool's input format. That is the gap this plan addresses.

---

## What changes vs replay

Replay was deterministic, bounded, repeatable. Same frames, synthetic pose,
snapshot at end. Live introduces several things at once:

1. **Transport**: frames travel ROS 2/DDS/LAN, not disk → process.
2. **Frame selection**: producer is ~28 Hz, RTSM measured at ~0.4 fps. The
   consumer drops most frames. *Which* frames is a policy choice.
3. **Pose source**: real nav-stack pose, not `--synthetic-pose`. Pose
   noise/drift becomes a confound for spatial association.
4. **Time sync**: camera timestamp and pose timestamp must be on
   compatible clocks for TF lookup to return the right pose.
5. **Extrinsics**: camera-to-base TF must be correct, or world coordinates
   are systematically wrong.
6. **Lifecycle**: live runs indefinitely; WM grows. Forgetting/decay
   policy may need to exist where it didn't in replay.
7. **Reproducibility**: a moment in a live session cannot be reproduced
   exactly by re-walking. See "Recording" below.

---

## The plan: two milestones, not three

An earlier draft had three milestones (shim → bag-played-over-LAN → live).
The middle one was deleted: with ROS 2/DDS already verified working
between Albert and Execution Jetson, there is no separate "verify network
path" step to take. RTSM-shaped traffic doesn't behave differently than
the topics already running.

### Milestone A: RTSM speaks ROS 2

**Goal**: RTSM consumes ROS 2 topics and produces output equivalent to
replay-fed RTSM.

**Work**:
- Write a ROS 2 subscriber node on Execution Jetson.
- Subscribes to: D435i color (and depth, if RTSM uses it), TF,
  `camera_info` (or hardcode intrinsics).
- Per frame: look up pose at frame timestamp via TF, build the
  `(image, pose, timestamp)` tuple RTSM ingestion expects, hand it off.
- Frame-selection policy: drop-to-latest. ROS 2 QoS = `KEEP_LAST`
  depth 1, `BEST_EFFORT` reliability (standard sensor-data pattern).
- TF lookup policy: nearest-neighbor within ε ms, else skip frame.

**Validation**: `ros2 bag play` of synthetic or recorded input on the
same machine, compare output to replay-fed RTSM. Should match modulo
timing jitter.

**Not in scope**: Albert, live camera, real pose. Pure plumbing
verification.

### Milestone B: Live camera

**Goal**: Albert publishes live D435i + nav pose, Execution Jetson
ingests, RTSM produces sensible WM state from a real walk.

**Prerequisites**:
- Milestone A done.
- Recording-while-running in place (see below — this is non-negotiable).
- Walked-route protocol written down in advance.

**Protocol** (from prior planning, paraphrased):
- Fixed route, 5-7 objects.
- Mix of object types: one replay confirmed (e.g. picture/monitor), one
  replay confused (e.g. chair-wheels-as-"computer"), one replay missed.
- Mix of viewing geometries: at least one walk-around object, at least
  one wall-mounted single-view.
- One adversarial object: mirror, glass, or strongly occluded.
- One return visit at end: revisit 2 of the original objects to test
  re-association vs duplication.
- ~10s dwell per object with small head movement (multi-view-bin).
- Total session 3-5 min.
- Annotation: voice memo or terminal annotation script with timestamps.
- Snapshots: pre-session, mid-session, end pre-drain, end post-drain.
- Continuous: confirm-event log with wall-clock timestamps.

**Success criteria** (committed in writing before walking):
- Pass: each dwelt object → exactly one confirmed proto. Revisits
  accumulate hits on existing proto.
- Soft fail: one object fragments into two protos at nearby coords.
  Recoverable signal about spatial association tolerance.
- Hard fail: half the dwelt objects don\\'t confirm, or revisits
  duplicate. Triggers deeper investigation, no further live work
  until understood.

**Secondary signals**: cosine score distribution (vs replay\\'s 0.08-0.10),
frame drop rate, adversarial-object behaviour.

---

## Recording: hard prerequisite, not optional

Argument was made that "we can just re-observe; Albert never leaves the
apartment." Rejected, on the following grounds:

- **Re-observation reproduces the world, not the moment.** Weird
  behaviour at minute 4 is a property of *those specific frames and
  pose values*, not of the world. Walking again gives different frames
  and different pose noise; the bug likely won\\'t reproduce, will be
  written off as a flake, and will ship.
- **This is exactly the trap that bit us on May 11.** The tightened
  threshold patch was caught only because we had the recording and
  could rerun identical input. Without it, the diagnostic would have
  been "doesn\\'t repro today, must be transient."
- **Cost is near zero.** `ros2 bag record` on Execution Jetson,
  subscribed to the same topics RTSM consumes, runs alongside live
  operation. Rotate hourly, keep a day. A few hundred MB/min of disk.
- **Benefit is asymmetric.** Most of the time unused. The first weird
  live session it pays for itself many times over.

**Concrete ask**: one line in the ops launch script —

ros2 bag record /camera/color/image_raw /camera/depth/... /tf /tf_static


— started alongside RTSM. Topic list to be finalized after the Albert
reconnaissance below.

---

## Open questions (to resolve before writing the shim spec)

The next session should start with ~10 minutes on Albert:

1. **What does Albert publish?**
   - `ros2 topic list` on Albert (visible from Execution Jetson via DDS).
   - Specifically: color image topic name, depth topic name (if any),
     `camera_info` topic name, pose topic name (or is pose only via TF?).

2. **What\\'s the TF tree?**
   - `ros2 run tf2_tools view_frames` on Albert (or Execution Jetson).
   - Specifically: world frame name, camera optical frame name, the
     chain between them.

3. **Does RTSM use depth, or color-only?**
   - SigLIP + open-vocab detector implies color-only for perception,
     but spatial association may use depth for back-projection to world
     coords. Confirm before specifying the subscriber.

4. **What\\'s the camera-to-base extrinsic?**
   - Already calibrated for nav, presumably. Same TF, consumed by the
     shim. Confirm it\\'s correct (or that this is a known TODO).

5. **Time sync between Jetsons?**
   - chrony/NTP/PTP — what\\'s in place? Worth verifying once.

These answers feed directly into the shim spec.

---

## Suggested session sequence

1. **Display-drift fix on replay.** ~30 min. Closes loose end from
   `2bbd255`. Independent of all of the above.
2. **Albert reconnaissance.** ~10 min. Answers above.
3. **Shim spec on paper.** ~30 min. Topics, frames, TF chain, frame
   policy, injection point. Half a page.
4. **Build the shim.** Probably one full session. End state: ROS 2 →
   RTSM works, validated against `ros2 bag play`.
5. **Add bag recording to ops launch.** ~10 min. Trivial.
6. **Walked-route protocol written.** ~30 min. Route, success criteria,
   annotation method. *Before* the walk, not during.
7. **Milestone B walk.** One session.

Steps 1-6 don\\'t involve Albert in any meaningful operational sense
(reconnaissance only). Step 7 is the live walk. Two-to-three work
sessions to get from here to first live data, depending on shim size
and surprises.

---

## Things explicitly out of scope here

- Forgetting/decay policy for long-running WM. Will need attention but
  not before milestone B reveals whether it\\'s actually a problem.
- Cross-view association improvements (the card-box-x3 issue from the
  split-gate handoff). Tracked separately.
- CLIP vocabulary curation. Resident-robot relabel flow handles this
  user-side; not an RTSM-internal concern.
- Grasp pipeline integration. Per architecture doc, that\\'s not RTSM\\'s
  job at all.
