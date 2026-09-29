# Exploration Dashboard — v4: Bug Fixes + Production-Grade UI/UX Overhaul

## 1. Purpose
Two things, in order:
- **Part A** — fix the three minor issues flagged in review of `exploration_dashboard_v3.html`.
- **Part B** — elevate the dashboard from a working prototype to a polished, production-grade
  multi-robot fleet monitoring interface, without changing what data it shows or where that data
  comes from.

**Hard constraint carried over from every prior spec in this series**: no new topics or code
changes on the 5 exploration nodes, and no ROS topics beyond what's already subscribed in v3
(`/auction_clock`, `/active_frontier`, `/frontier_bids`, `/tf`, and per-robot
`frontier_blacklist_visuals`, `local_blacklist`, `centroids`, `active_frontier_visual`,
`auction_data`, `global_costmap/costmap`, `global_costmap/costmap_updates`). Every enhancement
below — exploration progress, communication health, alerts, system metrics, fleet insights — must
be **derived client-side from data already being received**, not sourced from anything new.

## Part A — Targeted Fixes

### A1. `hist.max` goes stale on a decreasing patch
`costRGB`/`patchRaster` only ever raise `G.hist.max`, never lower it, so if the cell holding the
current max gets patched to a lower value, the displayed max overstates reality until the next
full-grid rescan.
- **Fix**: don't rescan the whole grid on every decrease (defeats the point of patching). Instead,
  when a patched cell's previous value equals the current `hist.max` *and* its new value is lower,
  set a `maxDirty` flag instead of recomputing immediately. Only recompute (scan `G.cost`, O(w·h),
  once) lazily — the next time the map panel actually needs to display `max` — and clear the flag.
  This keeps the common patch case O(1) and pays the O(w·h) cost only on the rare occasion it's
  actually needed.

### A2. Unnecessary redraw on a successful patch for a non-displayed robot
In `subscribeAll()`'s `costmap_updates` handler, a successful patch (`patchRaster(...) === null`)
sets `needsDraw = true` unconditionally, even when the patched robot isn't the currently-displayed
`mapRobot`. Harmless, but wasteful.
- **Fix**: match the failure branch's existing behavior — only set `needsDraw = true` when
  `n === mapRobot`, regardless of success or failure.

### A3. No visibility into `costmap_updates` reliability under load
There's currently no way to notice if patches silently stop arriving (e.g. dropped by rosbridge
under bandwidth pressure) short of watching the explored region visually stop advancing.
- **Fix**: fold this into Part B's Communication Health panel (§B.5) rather than a standalone
  patch — track "time since last message" per subscribed topic per robot, including
  `costmap_updates`, and surface it with an age-based freshness indicator. This gives the same
  protection as a dedicated gap-detector without needing sequence numbers the message type doesn't
  have.

### A4. Success Criteria — Part A
- [ ] `hist.max` never displays a value higher than what's actually present in `G.cost` at time of
      display (verify by patching a max cell downward and confirming the shown max updates next
      time the panel repaints).
- [ ] A patch for a robot that isn't currently displayed no longer triggers a map redraw.
- [ ] Time-since-last-message for `costmap_updates` (and other topics) is visible somewhere in the
      UI per §B.5 — see Part B for the full requirement.

## Part B — Production-Grade UI/UX Overhaul

### B.1 Design language — evolve, don't discard
The existing dark, monospace/technical aesthetic (`IBM Plex Mono` + `Archivo Narrow`, dark panel
tokens, the "signal colour = bound to an actual published marker colour" convention documented in
the CSS comments) is the right foundation for a robotics ops tool and should be **kept and
refined**, not replaced. Preserve the existing CSS custom properties
(`--ground/--panel/--panel-2/--rule/--ink/--ink-dim/--ink-faint/--bidding/--evaluating/--goal/
--blacklist/--frontier`) and their meanings. Any new colors introduced (alert severities, a
positive/success tone, extended neutral steps for the new panels) must be added as additional
tokens in the same system, and must **not** repurpose an existing token whose meaning is already
bound to a specific published marker — that invariant is load-bearing for the whole dashboard's
legibility.

Bring a consistent 4/8px spacing scale across all panels (old and new), consistent corner radii,
and consistent card/section chrome so the new panels don't look bolted onto the old ones.

### B.2 Fleet-level summary strip (new)
A compact bar, above or integrated into the header, giving an at-a-glance fleet status without
opening any panel:
- Robots online / total (derived from which robots have a recent message on any topic vs. total
  configured in `ROBOTS`)
- Active alert count (see §B.4), color-coded by highest severity present
- Combined frontier candidates remaining across the fleet
- Combined blacklisted points across the fleet (both counts, or a total — your call, but don't
  hide the sender/local distinction entirely, it's diagnostically useful)
- Per-robot exploration progress (see §B.3), shown compactly (e.g. small inline bars per robot)

### B.3 Exploration progress (new, derived, per robot)
Each robot's own `global_costmap` raster already carries a full cost histogram
(`unknown/free/infl/inscribed/lethal`). Derive a simple **explored fraction** per robot:
`(free + infl + inscribed + lethal) / (unknown + free + infl + inscribed + lethal)`, expressed as
a percentage, and show it prominently on that robot's panel (e.g. a progress bar) and in the fleet
summary strip.
- **Important caveat to note directly in the UI** (tooltip or caption, not just a code comment):
  this is *this robot's own costmap's* explored fraction. If robots don't share a merged map, this
  is not fleet-wide coverage — don't imply otherwise in the copy.

### B.4 Alerts panel (new, consolidates and extends the existing single warning box)
Replace the single `clockWarn` box with a proper alerts panel/list, each entry with a severity
(info/warning/critical), a short message, and which robot(s)/topic it concerns. Derive entries
from conditions already computed or computable from existing data — no new subscriptions:
- `num_robots` (from `/auction_clock`) mismatched against `ROBOTS.length` — existing check, just
  relocated
- Map stale for a robot (`d.stale`, from §A/v3's out-of-bounds patch handling)
- Any subscribed topic silent longer than a reasonable threshold for that topic's expected cadence
  (ties into §B.5's freshness tracking — e.g. no `/auction_clock` tick in >2× the observed tick
  interval, no `/tf` for a robot in >1s, no costmap/updates activity for an unusually long time)
- rosbridge disconnected (existing `link()` states — surface as an alert too, not just the header
  dot)
- Zero frontier candidates remaining for a robot that's currently idle (mild/info-level — may
  simply mean exploration finished, phrase it that way, not as an error)

Keep alerts sorted by severity, auto-clear when the underlying condition resolves, and make the
fleet summary strip's alert count (§B.2) reflect this same list.

### B.5 Communication health panel (new)
A compact table or grid, one row per subscribed topic (grouped by robot where relevant, global
topics separate): topic name, last-message age (live-updating, e.g. "0.3s ago"), and where
meaningful an approximate message rate. Color the age cell by freshness (fresh / aging / stale)
using thresholds appropriate to that topic's normal cadence (a 1 Hz-throttled costmap and a
100ms-throttled `/tf` shouldn't share the same "stale" threshold). This is what makes §A3's fix and
the alerts panel's topic-silence entries visible and trustworthy at a glance, and it's the kind of
panel a real ops dashboard is expected to have.

### B.6 System metrics (new, lightweight)
A small panel or strip: rosbridge connection state and URL, reconnect count since page load, and
basic per-topic message rates (can reuse §B.5's data rather than duplicating logic). Keep this
honest and minimal — don't fabricate metrics (CPU, memory, network bandwidth) that aren't actually
observable from the topics in scope.

### B.7 Per-robot panel redesign
Keep all current data (active/idle, both blacklist counts, current goal) but raise the information
density and hierarchy:
- Clear primary status (active/idle) as the dominant visual element
- Goal distance: now computable client-side, since both robot pose (`/tf`) and goal position
  (`active_frontier_visual`/`active_frontier`) are already tracked — show straight-line distance
  to goal when active, this is a genuinely useful addition an operator would want
- Exploration progress (§B.3) inline
- Blacklist counts kept, but visually secondary to status/goal/progress
- A small per-robot freshness indicator (last pose update, last costmap activity) tying into §B.5
  rather than requiring a trip to the communication health panel for the basics

### B.8 Map panel — chrome polish only
Keep 100% of v3's map functionality (pan/zoom/rotate, robot markers, incremental patching,
staleness handling) untouched. Polish only the surrounding chrome: turn the flat, joined `mapMeta`
string into a small set of legible badges/stats rather than one long delimited line, and align the
toolbar (robot picker, rotate, fit, hide) with the rest of the new design system's spacing and
button styles.

### B.9 Responsive layout
Define explicit behavior at least at three widths: desktop (current multi-column fleet grid), a
tablet/narrow-desktop breakpoint (existing `@media (max-width:820px)` as a starting point, extend
it to the new panels), and a mobile-usable minimum (single column, map panel remains usable via
touch — already true for gestures, verify the new panels reflow rather than overflow).

### B.10 Interaction polish
- Consistent hover/focus states across all interactive elements (buttons, robot picker, alert
  entries) — the existing `:focus-visible` rule should extend to every new interactive element.
- Respect the existing `prefers-reduced-motion` handling for any new transitions/animations.
- Empty/loading states for every new panel (alerts, communication health, system metrics) — don't
  let them render blank or broken before the first messages arrive; mirror the existing
  "Waiting for global_costmap/costmap…" pattern already used in the map panel.

## 2. Non-Goals / Constraints
- No new ROS topics, no changes to the 5 exploration nodes.
- No fabricated metrics — everything shown must trace to a real subscribed message or a value
  derived from one.
- Map panel functionality (§B.8) is frozen — this spec is about everything around it, not the map
  logic itself.
- Existing per-topic throttle choices stay as-is (`costmap` at `MAP_HZ`, `/tf` at 100ms,
  `costmap_updates` unthrottled) unless a specific fix above says otherwise.
- Read-only viewer — still nothing is written back to ROS.

## 3. Success Criteria
**Part A** (see §A4 above) plus:
- [ ] Fleet summary strip present and accurate: online/total robots, alert count, combined
      frontier/blacklist totals, per-robot progress all match the underlying per-robot state.
- [ ] Exploration progress shown per robot and in the summary strip, computed only from each
      robot's own costmap histogram, with the "not fleet-wide coverage" caveat visible in the UI
      copy, not just in code comments.
- [ ] Alerts panel replaces the single warning box, covers at minimum: num_robots mismatch, map
      staleness, rosbridge disconnect, and topic-silence beyond a per-topic threshold; entries
      clear automatically when resolved.
- [ ] Communication health panel shows live-updating last-message age per subscribed topic, with
      freshness thresholds appropriate to each topic's own normal cadence (not one global
      threshold).
- [ ] System metrics panel shows connection state/URL/reconnect count and reuses §B.5's rate data
      — no invented metrics.
- [ ] Per-robot panels show status, live goal distance when active, exploration progress, and both
      blacklist counts, with status as the clear visual primary.
- [ ] Map panel's existing functionality (pan/zoom/rotate, markers, incremental patch handling,
      stale indicator) is unchanged in behavior — only surrounding chrome/styling touched.
- [ ] Layout is verified usable at a desktop width, a ~768–820px tablet width, and a ~375–420px
      mobile width, with no horizontal overflow or clipped controls at any of the three.
- [ ] All existing and new interactive elements have visible hover/focus states; reduced-motion
      preference is respected throughout.
- [ ] Every new panel has a defined empty/loading state and never renders blank or visually broken
      before its first data arrives.
- [ ] Color tokens: no existing signal-color token (`--bidding/--evaluating/--goal/--blacklist/
      --frontier`) is repurposed for a new meaning; new tokens are added for alert severities and
      any other new semantic colors.
- [ ] A reviewer comparing v3 and this version confirms **no data or functionality was removed** —
      every value visible in v3 is still visible here, just better organized and presented.
