# Albert RealSense D435i Mounting — 2026-05-14

## Physical mounting (measured)
- Camera body: forward-facing, level
- Position relative to base (28 cm long, base_link at geometric center):
  - 4 cm back from front edge of base
  - 1 cm right of centerline (mounting constraint, not preference)
  - Base of camera housing ~10.5 cm above floor
  - Middle of camera ~13.5 cm above floor

## TF transform: base_link -> camera_link

| Axis | Value | Notes |
|------|-------|-------|
| x | +0.10 m | forward; base_link at geometric center, 14-4=10 |
| y | -0.01 m | ROS convention: +y=left, so right=negative |
| z | +0.135 m | base_link is on the floor (coincident with base_footprint) |
| roll/pitch/yaw | 0, 0, 0 | identity rotation; realsense driver handles optical-frame rotation downstream |

## Important context
- `base_link` is on the floor on Albert (base_link === base_footprint, identity transform)
- Wheel radius ~ 4 cm (lwheel1 at z=0.040)
- URDF contains a legacy `Camera` frame at [0.091, 0, 0.093] with 90 deg roll --
  this is from a different SKU and does NOT correspond to the realsense.
  Ignore it; consider removing from URDF later.

## DDS / domain
- All ROS 2 processes must use `ROS_DOMAIN_ID=30` to see each other
- RMW: `rmw_cyclonedds_cpp`
- Realsense container started with these env vars; `static_transform_publisher` must match

## Launch command (interim -- not yet in a launch file)

```bash
ros2 run tf2_ros static_transform_publisher \
  --x 0.10 --y -0.01 --z 0.135 \
  --roll 0 --pitch 0 --yaw 0 \
  --frame-id base_link --child-frame-id camera_link
