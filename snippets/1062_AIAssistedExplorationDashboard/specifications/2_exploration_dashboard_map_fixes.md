# Exploration Dashboard — Map Panel Fixes

## 1. Purpose
Follow-up fix spec for the map panel of `exploration_dashboard.html` (built from
`exploration_dashboard_spec.md`). The rest of the dashboard (auction clock, robot status panels,
blacklist counts, bid table) is working correctly and is **out of scope** here — do not modify it.
This spec addresses three observed problems in the map panel only.

## 2. Root Cause Analysis (from reading the current `drawMap()` / canvas code)

### 2.1 No pan/zoom/rotate — canvas grows to match the grid instead of being a viewport
Current code sets the canvas's actual pixel buffer to the occupancy grid's cell dimensions
(`cv.width = w; cv.height = h`), then relies on CSS (`width:100%; height:auto`) to stretch that
buffer to fill the container. There is no camera/viewport concept — the canvas *is* the map, 1:1,
always fully visible, always zoomed to "fit exactly." There is no mouse/touch handling at all
(no drag, wheel, or pinch listeners), so nothing can be panned, zoomed, or rotated. This also
means every redraw on a grid-size change reshapes the element itself, which reads as the window
"auto-resizing."

### 2.2 Pixelated, thick-looking walls — two compounding causes
1. `image-rendering:pixelated` (CSS) forces nearest-neighbor scaling when the small native canvas
   buffer is stretched to fill the container — this alone produces visible blockiness.
2. The color ramp does not separate the actual lethal obstacle from the inflation cost gradient
   around it: `v>=99` is painted the same solid gray as true obstacles, and every cost value from
   1–98 (Nav2's inflation decay layer) is painted as a lightening gradient
   (`t=26+round(v*1.15)`) that visually blends into the wall. Since inflation typically extends
   several cells out from a 1-cell-wide wall, the wall reads as much thicker than it actually is.

### 2.3 Robot position markers — not found in the current source
**Note for the build session**: reading the current `subscribeAll()`, there is no subscription to
any live robot-pose source (no `/tf`, no odom, nothing populating a "robot position" marker) — the
only per-robot map overlays currently drawn are frontier candidates (green), blacklist points
(red/cyan), and the active-goal marker (blue crosshair). If a version you're looking at shows robot
dots, please locate that code and audit it against the notes below; if not, treat this as a new
addition, not a bug fix.

For continuous position, in order of preference:
- **`/tf`** (`tf2_msgs/msg/TFMessage`), transform `map` → `<robot>/base_link` (or whatever the
  per-robot base frame is under that namespace) — highest update rate, comes from the
  localization/odometry stack, not from any of the 5 custom nodes, so subscribing to it requires
  no code changes to those nodes.
  ⚠️ Frame-name inconsistency in the source: `frontier_detection.cpp` and `frontier_selection.cpp`
  look up `"map" → "base_link"`, while `frontier_goal_sender.cpp` looks up
  `"map" → "base_footprint"`. Confirm which frame each robot actually publishes before wiring this
  up, and verify TF is bridged over rosbridge in the user's setup (it can be high-volume — consider
  subscribing per-robot with a `throttle_rate` like the costmap subscription already does).
- **Fallback**: `/<robot>/auction_data` (`diffrobot_interfaces/msg/AuctionData`) already carries a
  `robot_position` field (`geometry_msgs/Point`), published by `frontier_selection`. It's a real,
  already-published topic requiring no new node code — but it only updates each time
  `frontier_selection` processes a new centroid batch (tied to costmap/frontier-detection cadence),
  not at continuous odom/TF rate. Use this only if `/tf` isn't practically available; note in the
  UI (e.g. in `mapMeta`) which source is active, since the two have very different update rates.

## 3. Required Fixes

### 3.1 Add pan, zoom, and rotate to the map viewport
- Decouple the canvas's pixel buffer from the grid's cell dimensions. Render the occupancy grid
  once per incoming message to an **offscreen canvas/bitmap** at native resolution; on every
  frame, draw that bitmap onto the visible canvas through a camera transform
  (`ctx.setTransform(scale, 0, 0, scale, offsetX, offsetY)` plus a rotation component), so
  redrawing never resizes the visible element.
- **Pan**: click-and-drag (mouse) and single-finger drag (touch) to move the view.
- **Zoom**: mouse wheel and pinch-to-zoom, zooming toward the cursor/pinch center, not the canvas
  origin.
- **Rotate**: at minimum, stepped rotation (e.g. buttons or keyboard shortcut for 0°/90°/180°/270°);
  continuous rotation is a nice-to-have if time allows.
- **Fit/reset view button**: recenters and scales so the entire occupancy grid is visible, at
  rotation 0°. This should be the default view on first load and after a robot switch.
- Camera state (pan/zoom/rotation) must **persist across data updates** — a new costmap or overlay
  message must never reset the user's current view.
- All overlays (frontier candidates, blacklist points, goal marker, robot markers) must be drawn
  through the same camera transform so they stay spatially aligned with the grid at all pan/zoom/
  rotation levels.

### 3.2 Clean up the occupancy grid rendering
- Turn off `image-rendering:pixelated`; enable canvas smoothing
  (`ctx.imageSmoothingEnabled = true`, `imageSmoothingQuality = 'high'`) on the camera-transformed
  draw so scaling looks smooth rather than blocky.
- Scale the offscreen bitmap's backing resolution by `window.devicePixelRatio` for crispness on
  high-DPI displays.
- Separate true obstacles from the inflation gradient in the color ramp:
  - Treat only the actual lethal value (cost `100`, i.e. adjust the current `v>=99` cutoff to the
    correct lethal threshold — confirm against the costmap's actual cost convention) as the solid
    "wall" color.
  - Render the inflation gradient (cost `1–98`) much more subtly — significantly lower
    opacity/blend into the background — so it reads as a soft cost hint, not as part of the wall.
    Confirm the exact cutoff/opacity curve looks right against a real costmap before finalizing.
  - Keep unknown space (`-1`) as-is; it wasn't part of the complaint.

### 3.3 Add distinguishable, continuously-updating robot markers
- Subscribe to a live position source per §2.3 and draw one marker per robot on the map.
- Each robot gets a **visually distinct marker** — different shape and/or color per robot (not
  just two identical dots). Suggest reusing/extending the existing per-robot signal-color
  convention already in the CSS (`--goal`, etc.) or introducing two new distinct marker colors, one
  per robot, plus a heading indicator (e.g. an arrowhead/wedge) if orientation is available from
  the chosen source.
- Marker updates must track the source topic's actual rate — don't throttle robot markers down to
  the map's 1 Hz redraw *unless* the position source itself is that slow; if using the
  `auction_data.robot_position` fallback, say so in `mapMeta` so the update cadence isn't a
  surprise.
- Add a legend entry for the robot markers (currently the legend only covers frontier/goal/
  blacklist/lethal/unknown).

### 3.4 Shrink the goal marker
- The current goal marker (circle + crosshair) is sized from grid resolution
  (`rad = max(2, round(0.15/res))`, then multiplied up to `rad*2.4` / `rad*3.4`), which — combined
  with the canvas-stretching bug in §2.1 — makes it dominate the view.
- Once §3.1's camera transform is in place, size the goal marker (and ideally all point markers:
  frontier candidates, blacklist points) in **fixed screen-space pixels** (e.g. goal ring radius
  ~6–8px, crosshair arm length ~10–12px on screen) rather than in grid/resolution units, so it
  stays a sensible, legible size at any zoom level instead of growing/shrinking with map scale.

## 4. Non-Goals / Constraints (unchanged from original spec)
- No changes outside the map panel.
- No new topics/instrumentation on the 5 custom nodes themselves — `/tf` and `/odom`-style topics
  are standard Nav2 stack outputs already published independently of those nodes, so subscribing to
  them from the dashboard is in scope; adding a publisher to any of the 5 nodes is not.
- Keep the map panel's ~1 Hz costmap redraw non-blocking (per the original spec) — the new
  pan/zoom/rotate and marker rendering must not regress this.

## 5. Success Criteria
- [ ] Full occupancy grid, at any size, can be viewed via a "fit/reset view" control that frames
      the whole grid.
- [ ] User can zoom in/out (wheel + pinch) and pan (drag) smoothly, independent of incoming data
      updates — the view never snaps back or resizes when a new costmap/overlay message arrives.
- [ ] User can rotate the view (minimum: stepped 90° increments).
- [ ] Grid renders without visible pixelation/blockiness at typical zoom levels; walls visually
      match the actual lethal-cell footprint rather than including the inflation halo as if it
      were solid wall.
- [ ] Each robot is shown on the map with a marker that is visually distinguishable from the other
      robot (shape and/or color) and from all other markers (frontier/goal/blacklist).
- [ ] Robot markers update at the rate of whichever live position source was chosen — no
      dashboard-side throttling below that source's natural rate — and the chosen source/rate is
      visible or documented in the UI.
- [ ] Goal marker is visibly smaller, legible, and does not dominate the view at default zoom.
- [ ] All existing map overlays (frontier candidates, both blacklist point sets) still render
      correctly, aligned with the grid, under the new pan/zoom/rotate transform.
- [ ] Legend updated to include the new robot marker(s).
- [ ] No regression to any success criterion in the original `exploration_dashboard_spec.md`
      (auction clock, per-robot status, blacklist counts, bid table, event-driven updates,
      rosbridge setup instructions).

## 6. Open Notes for the Build Session
- Confirm the real Nav2 lethal-cost threshold used in this setup before hardcoding a new cutoff —
  don't assume `100` without checking the actual costmap config/values coming through.
- Confirm which TF frame (`base_link` vs `base_footprint`) each robot namespace actually publishes
  before wiring up robot-position tracking; the existing nodes are inconsistent with each other on
  this (see §2.3).
- If `/tf` proves too heavy to bridge live, document that decision and the fallback used
  (`auction_data.robot_position`) directly in the dashboard UI, not just in code comments, so it's
  clear to anyone watching the map why robot movement may look stepped rather than continuous.
