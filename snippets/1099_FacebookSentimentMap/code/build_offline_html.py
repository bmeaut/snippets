"""Bundle the dashboard into one offline HTML file with a small stand-in for the dash runtime.

Run from the working folder after build_dashboard_data.py:  python code/build_offline_html.py
Needs d3 v7:  npm install d3@7  (reads node_modules/d3/dist/d3.min.js)
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
D = 'data/'
OUT = 'biatorbagy_szentiment_dashboard.html'
names = ['overall', 'monthly', 'topics', 'engagement', 'threads', 'validation', 'depth', 'issues', 'issue_monthly',
         'issue_groups', 'basemap', 'places', 'place_issues', 'unplaced', 'geo_coverage']
data = {n: json.load(open(D + n + '.json')) for n in names}
page = open(os.path.join(HERE, 'web', 'index.html')).read()
page = page.replace('<meta name="dash-one-writer">', '')
mapjs = open(os.path.join(HERE, 'web', 'map.js')).read()
page = page.replace('<script src="map.js"></script>', '<script>\n' + mapjs + '\n</script>')
d3 = open('node_modules/d3/dist/d3.min.js').read()

runtime = r"""
(function () {
  const DATA = window.__DATA__;
  const calcs = {}, draws = [], onData = [];
  const store = {};
  Object.keys(DATA).forEach((k) => { store[k] = { status: 'ok', data: DATA[k] }; });
  function resolve(id) {
    if (store[id]) return store[id];
    if (calcs[id]) {
      const c = calcs[id];
      try { const v = c.fn(...c.inputs.map((i) => resolve(i).data)); store[id] = { status: 'ok', data: v }; }
      catch (e) { console.error(e); store[id] = { status: 'error', data: null }; }
      return store[id];
    }
    return { status: 'missing', data: [] };
  }
  function runDraw(d) {
    document.querySelectorAll('[data-draw="' + d.name + '"]').forEach((el) => {
      try { if (typeof d.fn === 'function') d.fn(el); else if (d.fn && d.fn.update) d.fn.update(el, d.fn.mount ? d.fn.mount(el) : undefined); }
      catch (e) { console.error('draw', d.name, e); }
    });
  }
  window.dash = {
    data: (id) => resolve(id),
    calc: (id, def) => { calcs[id] = def; },
    loader: () => {},
    onData: (fn) => { onData.push(fn); },
    draw: (name, fn) => {
      if (fn === undefined) { draws.filter((d) => d.name === name).forEach(runDraw); return; }
      draws.push({ name, fn });
    },
    colors: ['var(--series-1)', 'var(--series-2)', 'var(--series-3)', 'var(--series-4)'],
    params: () => ({}), setParams: () => {}, resetParams: () => {}, setLink: () => {}, refresh: () => {},
  };
  window.__dashStart = function () {
    onData.forEach((f) => { try { f(); } catch (e) { console.error(e); } });
    draws.forEach(runDraw);
    let t; window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(() => draws.forEach(runDraw), 150); });
  };
})();
"""

css_tokens = """
:root {
  --color-fg: #1f1e1d; --color-fg-muted: #6b6965; --color-bg: #ffffff; --color-panel: #faf9f7; --color-border-line: #e5e2dc;
  --color-ok: #3f8f5f; --color-warn: #c58a1d; --color-bad: #c2412d;
  --font-anthropic-sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; --font-anthropic-serif: Georgia, "Times New Roman", serif;
  --cds-font-size-caption: 12.5px; --cds-font-size-body: 15px; --cds-font-size-heading: 18px; --cds-font-size-title: 26px; --cds-font-weight-medium: 600;
  --cds-gap-xs: 4px; --cds-gap-sm: 8px; --cds-gap-md: 14px; --cds-gap-lg: 20px; --cds-gap-xl: 28px;
  --cds-pad-xs: 4px; --cds-pad-sm: 8px; --cds-pad-md: 12px; --cds-pad-lg: 18px; --cds-pad-xl: 24px; --cds-radius: 8px;
  --cds-chart-muted: #c9c5bd; --cds-chart-grid: #eeebe6; --cds-chart-axis: #b9b4ab; --cds-chart-reference: #8a857c; --cds-chart-status-critical: #c2412d;
  --cds-surface-popover: #ffffff; --cds-border: #ddd8cf; --cds-shadow-popover: 0 4px 16px rgba(0,0,0,.12); --cds-text-secondary: #6b6965;
  --series-1: #3b6fb6; --series-2: #c2412d; --series-3: #3f8f5f; --series-4: #8a5cb8;
}
@media (prefers-color-scheme: dark) {
  :root { --color-fg: #ecebe8; --color-fg-muted: #a9a59d; --color-bg: #1c1b1a; --color-panel: #242322; --color-border-line: #3a3835;
    --cds-chart-muted: #5b5852; --cds-chart-grid: #2e2c2a; --cds-chart-axis: #55524c; --cds-surface-popover: #2a2927; --cds-border: #44413d; --cds-text-secondary: #a9a59d; }
}
html, body { margin: 0; background: var(--color-bg); color: var(--color-fg); font-family: var(--font-anthropic-sans); }
#dash-root { max-width: 1240px; margin: 0 auto; padding: 24px 20px 48px; }
.page-title { font-family: var(--font-anthropic-serif); font-weight: 400; font-size: 28px; margin: 0 0 16px; }
.dash-select { font: inherit; padding: 4px 8px; border: 1px solid var(--color-border-line); border-radius: 6px; background: var(--color-bg); color: var(--color-fg); }
.foot { margin-top: 32px; font-size: 12px; color: var(--color-fg-muted); }
"""

html = f"""<!DOCTYPE html>
<html lang="hu"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Biatorbágyi Facebook-csoport – szentiment elemzés (2026. márc.–nov.)</title>
<style>{css_tokens}</style>
<script>{d3}</script>
<script>window.__DATA__ = {json.dumps(data, ensure_ascii=False, separators=(',', ':'))};</script>
<script>{runtime}</script>
</head><body>
<div id="dash-root">
<h1 class="page-title">Biatorbágyi Facebook-csoport – szentiment elemzés (2026. márc.–nov.)</h1>
{page}
<p class="foot">Offline, anonimizált változat (2026. november 22.): csak összesített adatokat és saját összefoglalókat tartalmaz, posztszövegeket és neveket nem. Térképadatok: © OpenStreetMap-közreműködők.</p>
</div>
<script>window.__dashStart();</script>
</body></html>"""
open(OUT, 'w').write(html)
print(len(html))
