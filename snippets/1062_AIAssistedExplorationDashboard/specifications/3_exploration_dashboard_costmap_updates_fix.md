# Exploration Dashboard — Map Panel: Incremental Costmap Updates Fix

## 1. Purpose
Follow-up fix spec for `exploration_dashboard_v2.html`'s map panel only. Everything else
(auction clock, robot panels, bid table, pan/zoom/rotate, robot markers, goal marker sizing) is
working correctly and is **out of scope** — do not modify it.

## 2. Problem
The dashboard only subscribes to `/${n}/global_costmap/costmap` (full `nav_msgs/OccupancyGrid`).
`frontier_detection.cpp` keeps its own `costmap_buffer_` current via the paired
`<topic>_updates` topic (`map_msgs/OccupancyGridUpdate`) and only treats a full-grid message as a
one-time seed/reset. Full-grid resends only happen when Nav2 resizes the costmap, and get rarer as
the map fills in — so the dashboard's bitmap increasingly lags behind what the robot is actually
reasoning over. Visually: the live `/tf` robot marker can appear to drive through cells the map
still paints as unknown, because the dashboard's copy of the map hasn't caught up.

## 3. Required Fix

### 3.1 Subscribe to the update topic
Add, per robot: `/${n}/global_costmap/costmap_updates` (`map_msgs/OccupancyGridUpdate`).

### 3.2 Two distinct message-handling paths
- **Full grid message** → **replace** `d.raster` entirely via the existing `rasterize()` path
  (current behavior, unchanged). A full resend always fully overwrites the previous bitmap,
  including picking up any dimension/origin change from a resize.
- **Update message** → **patch** only the given rectangle into the existing bitmap:
  - If `d.raster` doesn't exist yet, drop the update (nothing to patch until the first full grid
    lands) — mirrors `frontier_detection`'s own `if (costmap_buffer_.empty()) return;` guard.
  - Bounds-check the update rectangle against the current raster's stored width/height. If it
    doesn't fit, **drop the update** — this means the grid resized server-side and the buffered
    bitmap is stale; only a fresh full-grid message can fix it. Surface this in `mapMeta` (e.g.
    "map resized, waiting for full costmap") so it's visible rather than silently wrong.
  - Composite only the patched rectangle (`putImageData` at the correct offset) — never
    re-rasterize the whole bitmap on an update.

### 3.3 Row-flip correctness
`rasterize()` writes grid row `r` to bitmap row `h-1-r` (world-y-up → screen-y-down).
`OccupancyGridUpdate.data` is row-major starting at grid row `y`, **not flipped** — same
convention as `frontier_detection`'s own patch loop. The patch code must flip rows into the
correct bitmap orientation before compositing, using the same cost classification (lethal /
inscribed / inflation / unknown / free) as `rasterize()`. Getting this wrong won't throw an error —
it will silently mirror just the patched region vertically, so this needs explicit visual
verification, not just a passing build.

### 3.4 Incremental histogram maintenance
`hist.lethal/inscribed/infl/unknown/free/max` currently only gets recomputed on a full rescan.
On each patched cell: decrement the count for its previous classification, increment for its new
one, rather than rescanning the whole grid per update message.

## 4. Non-Goals / Constraints
- No changes to pan/zoom/rotate, robot markers, goal marker, or any other panel.
- No changes to the 5 ROS nodes — `costmap_updates` is a topic Nav2 already publishes.
- Update-driven redraws must stay non-blocking and must not regress the map panel's responsiveness
  during pan/zoom gestures.

## 5. Success Criteria
- [ ] Dashboard subscribes to `costmap_updates` for each robot and visibly reflects a patch
      (previously-unknown cells becoming free/occupied) without waiting for a full-grid resend.
- [ ] A full-grid message still fully overwrites the bitmap and correctly handles a
      dimension/origin change (resize).
- [ ] An update rectangle that doesn't fit the current raster is dropped, not applied
      out-of-bounds or corrupted, and the map panel indicates staleness until the next full grid.
- [ ] Patched regions are spatially correct — no vertical mirroring or offset — verified by visual
      inspection against a known feature (e.g. a wall) that spans a patch boundary.
- [ ] `mapMeta`'s cost histogram (lethal/inscribed/inflated/unknown counts) stays accurate after a
      sequence of updates, not just after a full rescan.
- [ ] Only the patched rectangle is redrawn/recomposited per update — no full-grid
      re-rasterization triggered by an update message.
- [ ] Robot marker position (from `/tf`) and the map's explored/unknown boundary stay visually
      consistent during continuous exploration — the robot should no longer appear to be driving
      through cells the map still shows as unknown, under normal operation.
- [ ] No regression to any success criterion from the original spec or the previous map-panel fix
      (pan/zoom/rotate, wall rendering, robot markers, goal marker size).
