(function () {
  const S = window.SA;
  S.state.mapIssue = S.state.mapIssue || '';
  S.state.mapSel = S.state.mapSel || null;
  const ok = (id) => { const d = dash.data(id); return d.status === 'ok' && Array.isArray(d.data) ? d.data : null; };
  const enc = (v) => encodeURIComponent(v);

  // current per-place rows for the chosen problem
  function current() {
    const places = ok('places'), pi = ok('place_issues');
    if (!places || !pi) return null;
    const k = S.state.mapIssue;
    if (!k) return places.map((p) => ({ ...p, cn: +p.n, cneg: +p.neg }));
    const by = {};
    pi.filter((r) => r.issue === k).forEach((r) => { by[r.pid] = r; });
    return places.filter((p) => by[p.pid]).map((p) => ({ ...p, cn: +by[p.pid].n, cneg: +by[p.pid].neg }));
  }

  dash.draw('map-issue', (sel) => {
    const iss = ok('issues');
    const opts = [new Option('Minden probléma', '')];
    if (iss) iss.slice().sort((a, b) => a.title.localeCompare(b.title, 'hu')).forEach((r) => opts.push(new Option(r.title, r.id)));
    sel.replaceChildren(...opts);
    sel.value = S.state.mapIssue;
    sel.onchange = () => { S.state.mapIssue = sel.value; S.state.mapSel = null; dash.draw('map-chart'); dash.draw('map-detail'); dash.draw('map-top'); };
  });

  dash.draw('map-chart', (el) => {
    const raw = ok('basemap'), rows = current();
    if (raw && S._bmRaw !== raw) {
      S._bmRaw = raw;
      S._bm = raw.map((r) => ({ ...r, coords: String(r.coords || '').split(';').map((p) => p.split(',').map(Number)).filter((c) => c.length === 2 && Number.isFinite(c[0]) && Number.isFinite(c[1])) }));
    }
    const bm = raw ? S._bm : null;
    const st = dash.data('basemap').status;
    if (!bm || !rows) { S.failed(el, st === 'loading' ? 'loading' : dash.data('places').status); return; }
    el.replaceChildren();
    const W = Math.max(300, el.clientWidth), H = Math.round(Math.min(640, Math.max(360, W * 0.78)));
    const boundary = bm.find((r) => r.kind === 'boundary');
    const bc = boundary.coords;
    const lat0 = d3.mean(bc, (c) => c[1]) * Math.PI / 180, kx = Math.cos(lat0);
    const xs = bc.map((c) => c[0] * kx), ys = bc.map((c) => c[1]);
    const x0 = d3.min(xs), x1 = d3.max(xs), y0 = d3.min(ys), y1 = d3.max(ys);
    const pad = 12, sc = Math.min((W - 2 * pad) / (x1 - x0), (H - 2 * pad) / (y1 - y0));
    const ox = (W - sc * (x1 - x0)) / 2, oy = (H - sc * (y1 - y0)) / 2;
    const proj = (c) => [ox + (c[0] * kx - x0) * sc, oy + (y1 - c[1]) * sc];
    const lg = d3.line().x((c) => proj(c)[0]).y((c) => proj(c)[1]);
    const line = (c) => (c && c.length > 1 ? lg(c) : null);
    const poly = (c) => (c && c.length > 2 ? lg(c) + 'Z' : null);
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('height', H).attr('viewBox', `0 0 ${W} ${H}`)
      .attr('role', 'img').attr('aria-label', 'Biatorbágy térképe a problémák említéseivel; a körök mérete az említések számát, színe a negatív arányt mutatja');
    const g = svg.append('g');
    g.append('path').attr('d', poly(boundary.coords)).style('fill', 'var(--color-bg)').style('stroke', 'var(--color-fg-muted)').attr('stroke-width', 1.2);
    bm.filter((r) => r.kind === 'area' && r.coords.length > 2).forEach((r) => g.append('path').attr('d', poly(r.coords)).style('fill', 'var(--cds-chart-muted)').attr('fill-opacity', 0.18).style('stroke', 'var(--cds-chart-muted)').attr('stroke-dasharray', '3 3'));
    bm.filter((r) => r.kind === 'water' && r.coords.length > 1).forEach((r) => g.append('path').attr('d', line(r.coords)).attr('fill', 'none').style('stroke', dash.colors[0]).attr('stroke-opacity', 0.45).attr('stroke-width', 1));
    bm.filter((r) => r.kind === 'street' && r.coords.length > 1).forEach((r) => g.append('path').attr('d', line(r.coords)).attr('fill', 'none')
      .style('stroke', 'var(--cds-chart-axis)').attr('stroke-width', r.cls === 'major' ? 1.6 : r.cls === 'track' ? 0.5 : 0.8)
      .attr('stroke-dasharray', r.cls === 'track' ? '2 2' : null).attr('stroke-opacity', r.cls === 'track' ? 0.6 : 0.9));
    bm.filter((r) => r.kind === 'rail' && r.coords.length > 1).forEach((r) => g.append('path').attr('d', line(r.coords)).attr('fill', 'none').style('stroke', 'var(--color-fg-muted)').attr('stroke-width', 1.4).attr('stroke-dasharray', '6 3'));

    // highlighted streets
    const byName = {};
    bm.filter((r) => r.kind === 'street' && r.name && r.coords.length > 1).forEach((r) => { (byName[r.name] = byName[r.name] || []).push(r.coords); });
    const op = (neg) => 0.25 + 0.75 * Math.min(1, Math.max(0, neg / 100));
    rows.filter((p) => p.kind === 'utca').forEach((p) => (byName[p.name] || []).filter((c) => c.length > 1).forEach((c) => g.append('path').attr('d', line(c)).attr('fill', 'none')
      .style('stroke', 'var(--color-bad)').attr('stroke-opacity', op(p.cneg)).attr('stroke-width', 3).attr('stroke-linecap', 'round')));

    const mx = d3.max(rows, (p) => p.cn) || 1;
    const r = d3.scaleSqrt([0, mx], [0, Math.max(14, W / 28)]);
    const tp = S.tip(el);
    const sorted = rows.slice().sort((a, b) => b.cn - a.cn);
    const dots = g.append('g').selectAll('circle').data(sorted).join('circle')
      .attr('cx', (p) => proj([+p.lon, +p.lat])[0]).attr('cy', (p) => proj([+p.lon, +p.lat])[1]).attr('r', (p) => Math.max(3, r(p.cn)))
      .style('fill', 'var(--color-bad)').attr('fill-opacity', (p) => op(p.cneg) * 0.85)
      .style('stroke', (p) => (S.state.mapSel === p.pid ? 'var(--color-fg)' : 'var(--color-bg)')).attr('stroke-width', (p) => (S.state.mapSel === p.pid ? 2.5 : 1))
      .style('cursor', 'pointer')
      .on('pointermove', (e, p) => {
        const b = el.getBoundingClientRect();
        tp.show([[p.name], ['Említés', S.int(p.cn)], ['Negatív', S.pct(p.cneg)], ...(S.state.mapIssue ? [] : [['Fő témák', p.top_issues.split('; ').slice(0, 2).join(' · ')]])], e.clientX - b.left, e.clientY - b.top);
      })
      .on('pointerleave', () => tp.hide())
      .on('click', (e, p) => { S.state.mapSel = p.pid; dash.draw('map-chart'); dash.draw('map-detail'); });
    // labels for the biggest places
    const lab = g.append('g').attr('pointer-events', 'none');
    const boxes = [];
    sorted.slice(0, W < 500 ? 6 : 12).forEach((p) => {
      const [x, y] = proj([+p.lon, +p.lat]);
      const rx = Math.max(3, r(p.cn));
      const w = p.name.length * 6.3, h = 13;
      const cands = [[x + rx + 3, y + 4, 'start'], [x - rx - 3, y + 4, 'end'], [x, y - rx - 4, 'middle'], [x, y + rx + 12, 'middle']];
      for (const [lx, ly, anc] of cands) {
        const bx0 = anc === 'start' ? lx : anc === 'end' ? lx - w : lx - w / 2;
        const bb = [bx0, ly - h + 3, bx0 + w, ly + 3];
        if (bb[0] < 0 || bb[2] > W || bb[1] < 0 || bb[3] > H) continue;
        if (boxes.some((o) => !(bb[2] < o[0] || bb[0] > o[2] || bb[3] < o[1] || bb[1] > o[3]))) continue;
        boxes.push(bb);
        lab.append('text').attr('x', lx).attr('y', ly).attr('text-anchor', anc).attr('font-size', 11)
          .style('fill', 'var(--color-fg)').style('paint-order', 'stroke').style('stroke', 'var(--color-bg)').attr('stroke-width', 3).text(p.name);
        break;
      }
    });
    const zoom = d3.zoom().scaleExtent([1, 10]).translateExtent([[0, 0], [W, H]]).on('zoom', (e) => {
      S.state.mapZoom = { k: e.transform.k, x: e.transform.x, y: e.transform.y, W };
      g.attr('transform', e.transform);
      dots.attr('r', (p) => Math.max(3, r(p.cn)) / Math.sqrt(e.transform.k));
      lab.selectAll('text').attr('font-size', 11 / e.transform.k).attr('stroke-width', 3 / e.transform.k);
    });
    svg.call(zoom);
    const z = S.state.mapZoom;
    if (z && z.W === W && z.k > 1) svg.call(zoom.transform, d3.zoomIdentity.translate(z.x, z.y).scale(z.k));
    if (!rows.length) {
      svg.append('text').attr('x', W / 2).attr('y', 30).attr('text-anchor', 'middle').style('fill', 'var(--color-fg-muted)').attr('font-size', 12).text('Ehhez a problémához nincs megnevezett helyszín.');
    }
  });

  dash.draw('map-detail', (el) => {
    el.replaceChildren();
    const rows = current();
    if (!rows) return;
    const p = rows.find((x) => x.pid === S.state.mapSel);
    const mk = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
    if (!p) { el.appendChild(mk('p', 'muted', 'Kattints egy körre a részletekért. A térkép görgetéssel nagyítható, húzással mozgatható.')); return; }
    const box = mk('div', 'pb');
    box.appendChild(mk('div', 'tag', p.kind === 'utca' ? 'Utca' : p.kind === 'terület' ? 'Városrész, terület' : 'Hely'));
    box.appendChild(mk('h3', '', p.name));
    const st = mk('div', 'stats');
    const stat = (label, val, src, field, where, cls) => {
      const s = mk('span'); s.append(document.createTextNode(label + ' '));
      const b = mk('b', cls || '', val); b.dataset.source = src; b.dataset.field = field; b.dataset.where = where; s.appendChild(b); st.appendChild(s);
    };
    if (S.state.mapIssue) {
      const w = 'pid=' + enc(p.pid) + '&issue=' + enc(S.state.mapIssue);
      stat('Említés:', S.int(p.cn), 'place_issues', 'n', w);
      stat('negatív:', S.pct(p.cneg), 'place_issues', 'neg', w, 'bad');
    } else {
      stat('Problémás említés:', S.int(p.cn), 'places', 'n', 'pid=' + enc(p.pid));
      stat('negatív:', S.pct(p.cneg), 'places', 'neg', 'pid=' + enc(p.pid), 'bad');
    }
    box.appendChild(st);
    const t = mk('p'); t.append(mk('span', 'lbl2', 'Leggyakoribb problémák itt: '), document.createTextNode(p.top_issues)); box.appendChild(t);
    if (p.example_text) box.appendChild(mk('p', 'ex', 'Jellemző poszt (' + p.example_date + ', ' + S.int(+p.example_comments) + ' komment): „' + p.example_text + '”'));
    el.appendChild(box);
  });

  dash.draw('map-top', (el) => {
    el.replaceChildren();
    const rows = current();
    if (!rows) return;
    const top = rows.slice().sort((a, b) => b.cn - a.cn).slice(0, 10);
    const ol = document.createElement('ol'); ol.className = 'maplist';
    top.forEach((p) => {
      const li = document.createElement('li');
      const a = document.createElement('button'); a.type = 'button'; a.className = 'linkish'; a.textContent = p.name;
      a.addEventListener('click', () => { S.state.mapSel = p.pid; dash.draw('map-chart'); dash.draw('map-detail'); });
      const n = document.createElement('span'); n.className = 'muted';
      const nb = document.createElement('span'); nb.textContent = S.int(p.cn);
      if (S.state.mapIssue) { nb.dataset.source = 'place_issues'; nb.dataset.field = 'n'; nb.dataset.where = 'pid=' + enc(p.pid) + '&issue=' + enc(S.state.mapIssue); }
      else { nb.dataset.source = 'places'; nb.dataset.field = 'n'; nb.dataset.where = 'pid=' + enc(p.pid); }
      n.append(document.createTextNode(' '), nb, document.createTextNode(' említés, ' + S.pct(p.cneg).replace(',0%', '%') + ' negatív'));
      li.append(a, n); ol.appendChild(li);
    });
    el.appendChild(ol);
  });

  dash.draw('map-unplaced', (el) => {
    el.replaceChildren();
    const un = ok('unplaced');
    if (!un) return;
    const ul = document.createElement('ul'); ul.className = 'maplist';
    un.forEach((r) => {
      const li = document.createElement('li');
      const b = document.createElement('b'); b.textContent = r.name;
      const n = document.createElement('span'); n.className = 'muted';
      const nb = document.createElement('span'); nb.textContent = S.int(+r.n); nb.dataset.source = 'unplaced'; nb.dataset.field = 'n'; nb.dataset.where = 'name=' + enc(r.name);
      n.append(document.createTextNode(' '), nb, document.createTextNode(' említés, ' + S.pct(+r.neg).replace(',0%', '%') + ' negatív – ' + r.top_issues));
      li.append(b, n); ul.appendChild(li);
    });
    el.appendChild(ul);
  });
})();
