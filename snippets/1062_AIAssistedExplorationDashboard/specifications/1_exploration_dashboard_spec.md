# Multi-Robot Exploration Dashboard — Build Spec

## 1. Purpose
Build a live monitoring dashboard for a 2-robot frontier-exploration system built on ROS 2 + Nav2.
The system source nodes are: `auction_clock`, `frontier_detection`, `frontier_selection`,
`frontier_auction`, `frontier_goal_sender`. This spec is the sole input for the build session —
it should be self-contained.

## 2. Decided Architecture
- **Platform**: Web dashboard (browser-based), talking to ROS 2 via **`rosbridge_suite`**
  (websocket bridge) + a JS client library (e.g. `roslibjs`).
  - `rosbridge_suite` is **not currently installed/running** in the user's setup — the deliverable
    must include install + launch instructions (`ros2 launch rosbridge_server rosbridge_websocket_launch.xml`,
    default port `9090`), plus the frontend connecting to `ws://localhost:9090`.
- **Scope**: Fleet view of exactly **2 robots**, namespaced `/robot1` and `/robot2`.
- **Data source**: Live ROS 2 topics only (no rosbag / replay support needed).
- **Update strategy**: Event-driven — update UI as messages arrive on each subscribed topic.
  Throttle only the map rendering to ~1 Hz to keep it smooth (data itself need not be throttled).
- **Deployment context**: Runs on the same machine/network as the robots (dev/sim setup) — no
  remote-access, auth, or NAT/firewall concerns.

## 3. Information to Display (priority order, as confirmed with user)
1. **Auction state + round id** — global, single source for both robots (see §4).
2. **Active goal / nav status per robot** — binary only: **active** vs **idle**. No richer states
   (sending/success/aborted) — those aren't published by the existing nodes and the user
   explicitly chose *not* to add new instrumentation for this.
3. **Blacklist counts per robot — as two separate counts**:
   - Goal-sender blacklist (frontier positions blacklisted after aborted Nav2 goals)
   - Auction-node local blacklist (frontier positions locally blacklisted during bid evaluation)
4. **Secondary: 2D map view** (assistant's suggestion, accepted as "whatever is suitable") —
   costmap background + frontier candidates + active goal marker + blacklist points, per robot.
   This should be a secondary/collapsible panel — the primary view is status panels/tables/numbers.

## 4. Topic Reference

### Global topics (shared, no robot namespace)
| Topic | Type | Relevant fields | Notes |
|---|---|---|---|
| `/auction_clock` | `diffrobot_interfaces/msg/AuctionClock` | `round_id` (uint32), `transition` (int8: 0=START_BIDDING, 1=START_EVALUATING), `num_robots` (uint32) | Single global clock — this is the source of truth for "auction state" shown for **both** robots, since both process the same clock message. Round 0 is a sync-only round (ignored by the auction logic). |
| `/frontier_bids` | `diffrobot_interfaces/msg/FrontierBid` | `round_id`, `robot_id`, `frontier_centroid` (geometry_msgs/Point), `score` (float), `robot_position` (geometry_msgs/Point) | Shared bidding channel; both robots' bids appear here, distinguished by `robot_id`. Optional/lower-priority table if there's room. |
| `/active_frontier` | `diffrobot_interfaces/msg/ActiveFrontier` | `header.frame_id` (empty = idle, non-empty = active), `robot_id` (string), `frontier_centroid` (geometry_msgs/Point) | Distinguish robots via `robot_id` field (e.g. `"robot1"`, `"robot2"` — namespace leading slash is stripped by the publishing node). This is the **only** source for active/idle status. |

### Per-robot topics (prefix with `/robot1/` and `/robot2/`)
| Topic (relative) | Type | Purpose for dashboard |
|---|---|---|
| `frontier_blacklist_visuals` | `visualization_msgs/Marker` (SPHERE_LIST) | Goal-sender blacklist — **count = `marker.points.size()`** |
| `local_blacklist` | `visualization_msgs/Marker` (SPHERE_LIST) | Auction-node local blacklist — **count = `marker.points.size()`** |
| `centroids` | `diffrobot_interfaces/msg/FrontierData` | Frontier candidates (`centroids`: PoseArray, `cluster_sizes`: uint32[]) — for map overlay |
| `global_costmap/costmap` | `nav_msgs/OccupancyGrid` | Map background (param-configurable topic name, default shown here) |
| `active_frontier_visual` | `visualization_msgs/Marker` | Active goal marker (sphere), for map overlay — DELETE action means goal cleared |
| `frontier_blacklist` | `geometry_msgs/PolygonStamped` | Raw polygon form of goal-sender blacklist (alternative point source to the Marker, if easier to parse) |

> Note: `frontier_cells_markers` (MarkerArray) and `frontier_centroid_markers` (Marker) also exist
> per robot for RViz visualization of raw frontier cells — not needed for this dashboard, but
> available if the map view needs finer detail later.

## 5. Layout Suggestion (not prescriptive — build session can adjust)
- **Top bar**: global auction state — current `round_id`, current `transition` (BIDDING/EVALUATING),
  `num_robots`.
- **Two side-by-side robot panels** (`robot1`, `robot2`), each showing:
  - Active/Idle status (from `/active_frontier`, filtered by `robot_id`)
  - Goal-sender blacklist count
  - Auction local blacklist count
- **Collapsible map panel** below or beside: costmap + frontier centroids + active goal + blacklist
  points, per robot (toggle between robot1/robot2, or side-by-side if performance allows).
- Optional stretch: live bid table (`/frontier_bids`) filtered to the current `round_id`.

## 6. Explicit Non-Goals / Constraints
- No new topics or code changes to the existing 5 nodes (all data must come from what's already
  published).
- No richer nav-status states (sending/success/aborted) — active/idle only.
- No rosbag replay, no remote/auth concerns, no historical persistence required (live-only).
- Not a full RViz replacement — the map view is secondary to the status panels.

## 7. Success Criteria
- [ ] Dashboard connects to ROS 2 via `rosbridge_suite` websocket without manual topic-name edits
      beyond the `/robot1` / `/robot2` namespace convention above.
- [ ] Shows current global round id + auction transition, updating live.
- [ ] Shows active/idle nav status for both robots independently, correctly filtered by `robot_id`.
- [ ] Shows two distinct, correctly-labeled blacklist counts per robot (goal-sender vs auction-local).
- [ ] Includes a working 2D map view with costmap + frontier candidates + active goal + blacklist
      points, at least for one robot at a time, refreshed at ~1 Hz without blocking the rest of the UI.
- [ ] Includes setup instructions for installing/launching `rosbridge_suite` (it is not yet
      running in the user's environment).
- [ ] All other panels update event-driven (as messages arrive), no unnecessary polling.

## 8. Open Notes for the Build Session
- `robot_id` strings are derived from ROS namespace with leading `/` stripped (e.g. namespace
  `/robot1` → `robot_id == "robot1"`), matching the `/robot1`, `/robot2` convention.
- If bid-table (stretch goal) is included, filter `/frontier_bids` by the currently-active
  `round_id` from `/auction_clock` to avoid showing stale bids from prior rounds.
- Marker point counts (`marker.points.size()`) are the correct/only way to get blacklist counts
  from the current codebase — there are no plain numeric "count" topics.
