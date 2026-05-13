# RTSM Handoff — 2026-05-13

## TL;DR

The working memory looked broken (cross-object contamination in OIDs,
duplicate spawns of the same physical object). Root cause is upstream
of association: FramePacket.pose is never populated with real SLAM
pose, so world_from_cam runs with effective identity rotation. All
xyz_world values are camera-frame coordinates in disguise, and the
spatial gate in association is therefore non-functional.

The robot has working SLAM. It is not wired into RTSM. Wiring it in
is the highest-priority work item.

## Diagnostic evidence

Replayed dataset, 125 confirmed objects:

- z (depth axis) is 100 percent positive, 0.30m to 6.12m
  -- camera-frame z leaking through unrotated
- y is 65 percent negative, p50 = -0.08m
  -- CV-convention +y=down not remapped to world +z=up
- Object density correlates with robot dwell time, not physical
  layout (see WebGUI scatter)
- Visual audit of 10 high-hits OIDs across 5 labels: 8 contaminated,
  2 clean. Contamination = single OID containing crops of physically
  distant objects (e.g., 3D printer + cardbox + game controller all
  in one "computer" OID, despite being on opposite sides of the room)

This pattern is consistent with identity rotation + varying
translation, which fits the replay --synthetic-pose mode behavior.

## Top priority: wire SLAM into FramePacket

### Where to integrate

FramePacket is defined in rtsm/core/datamodel.py around line 131. It
already has a pose field of type Optional[PoseStamped]. PoseStamped
expects:

- t_wc      : translation, world-from-camera (T_wc)
- q_wc_xyzw : quaternion (x,y,z,w), world-from-camera

The world_from_cam(p_cam) method on FramePacket already does the
correct math: R @ p_cam + t. No changes needed to consumers. Just
populate pose at frame ingest.

### Find live ingest sites

Search for FramePacket constructors in the live ingest path. The
replay one in rtsm/tools/replay.py is intentionally synthetic --
leave it alone. The live ingest is what needs editing. To find it:

    grep -rn 'FramePacket(' rtsm/ --include=PYFILES

(Replace PYFILES with the literal star-dot-py glob; written that way
here so this heredoc does not get confused.)

### Convention checklist (do not skip)

1. Direction. SLAM must publish world-from-camera (T_wc), not
   camera-from-world. If it publishes camera-from-world, invert
   before assigning. The pose transforms a point from camera frame
   into world frame: p_world = R @ p_cam + t.

2. Frame chain. If SLAM publishes pose for base_link rather than the
   camera optical frame, compose with the static transform from
   base_link to camera_optical_frame. Common failure: forgetting
   this gives a constant offset of 50cm to 1m in object positions.

3. Axis convention mismatch. ROS REP-103 uses +x=forward, +y=left,
   +z=up. Camera optical frames use +x=right, +y=down, +z=forward.
   The static transform between them handles this -- but only if
   correctly defined in your URDF. Verify by setting a known target
   on a table and checking that xyz_world height matches the table
   height.

4. Time alignment. Pose must be queried at the frame's t_sensor_ns,
   not at "now". A 30ms misalignment at 1 m/s robot motion gives
   3cm position error per object, which is fine. A 200ms
   misalignment at fast pan gives 20cm error, which is enough to
   break the spatial gate.

### Validation procedure

After wiring, run live for ~60 seconds, then check the y/z
distributions of xyz_world. With real pose (assuming world frame
+z=up, robot ground plane near z=0):

- z should range roughly 0m to 2m (floor to ceiling), NOT exclusively
  positive 0.3m to 6m
- y distribution should be reasonable, not 65 percent negative
- Object density in WebGUI should match physical scene layout

Also run a visual audit: pull crops for 5 to 10 OIDs, check that
each OID's crops are all the same physical object. Target
contamination rate below 10 percent.

## Lower priority items

### Validated under synthetic pose, re-validate under real pose

- cos_min=0.85 shipped (was 0.90 baseline; tested 0.75, reverted to
  0.85). Real-pose data may suggest tighter or looser; do not trust
  the 0.85 choice without real-pose evidence.
- Gallery descriptor matching (commit abcc6fd). Confirm avg_hits and
  spawn-rate gains hold under real pose.
- Latency numbers from today's runs are valid; CPU-bound, not
  pose-dependent.

### Open questions deferred

- Post-hoc OID merger: not built. Decide after real-pose validation
  whether duplicate OIDs are still a problem.
- Quality floor for blurry/low-confidence observations: not
  implemented. 5 of 10 contaminated OIDs in today's audit contained
  explicit blur. Consider a blur metric or detection-confidence floor
  before inserting observations into WM.
- Detector mislabeling (e.g., painting labeled "television") is
  probably out of scope for RTSM -- it is a CLIP zero-shot issue.
  Note for the perception team.

### Things NOT to do

- Do not retune association on synthetic-pose replay. The spatial
  gate is dead in that mode; any tuning result is an artifact.
- Do not trust aggregate metrics (DIFF/SAME ratio, object count,
  avg_hits) on synthetic-pose data. They look healthy even with 80
  percent contamination.
- Do not ship a live demo without verifying the y-axis distribution
  and the visual audit per the procedure above.

## Context

The investigation is recorded in chat history (2026-05-13). Key
findings in chronological order:

1. Tuned cos_min and added gallery matching; looked good on aggregate
   metrics
2. Visual audit of cardbox cluster revealed 80 percent contamination
   across labels
3. Y-axis distribution check confirmed pose is degenerate
4. Code review confirmed world_from_cam math is correct, but
   FramePacket.pose is None or identity in practice

Current rtsm.yaml has cos_min=0.85 and match_against_gallery=true.

