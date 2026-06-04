# Tasks: UX Végső Simítások

## Phase 1 — Snake pozíció + gépfeliratok

- [ ] `machine.ts`: `createSnakeMachine` x koordinátája `728 → 520`
- [ ] `drawHub.ts`: minden gép alá felirat kirajzolása (`kind` alapján: "SNAKE" / "AMŐBA" / "KASZINÓ")
  - Stílus: `10 * scale` px betűméret, `rgba(248,250,252,0.45)` szín, középre igazítva a gép felett
  - Pozíció: `machine.x + machine.width/2` (középre), `machine.y - 10 * scale` (gép teteje fölé)

Acceptance: A hubban mind a három gép felett látható a neve; Snake és Casino ajtó közt ≥ 60 px rés.

---

## Phase 2 — [E] prompt Y-pozíció bugfix

- [ ] `HubScene.tsx`: `canvasOffsetY` számítása: `Math.max(0, (stageRef.current?.clientHeight ?? viewport.height) - viewport.height) / 2`
- [ ] `createInteractionPrompt` szignatúrájának bővítése: `canvasOffsetY: number` paraméter hozzáadása
- [ ] `interaction.ts`: `screenY: (machine.y - 16) * scale + canvasOffsetY`
- [ ] `HubScene.tsx`: `createInteractionPrompt` hívásában `canvasOffsetY` átadása
- [ ] Ha a Casino scene is hívja `createInteractionPrompt`-ot: ott is frissíteni a hívást (0 offsettel, ha a casino canvas mindig teljesen kitölti a stage-t)

Acceptance: Minden viewport-méretnél a prompt a gép canvas-pozíciójának teteje felett jelenik meg.

---

## Phase 3 — Gép-specifikus prompt szöveg

- [ ] `interaction.ts`: `createInteractionPrompt`-ban `text` meghatározása `machine.kind` és `machine.id` alapján:
  - `kind === 'snake'` → `"[E] Snake indítása"`
  - `kind === 'amoba'` → `"[E] Amőba indítása"`
  - `kind === 'door'` és `id === 'casino-door'` → `"[E] Belépés a kaszinóba"`
  - `kind === 'door'` és `id === 'casino-exit-door'` → `"[E] Vissza a hubba"`
  - egyéb → `"[E] Megnyitás"` (fallback)

Acceptance: Mind a 4 esetben a megfelelő szöveg jelenik meg.

---

## Phase 4 — Amőba difficulty screen redesign

- [ ] `AmoebaGame.css`: `.ameoba-difficulty` wrapper osztály:
  - Háttér: sötét alap (`#0f172a`), enyhe rácsháttér CSS gradienttel
  - Szegély: amőba narancs/kék enyhe glow
  - Padding, border-radius, max-width
- [ ] `AmoebaGame.css`: `.ameoba-difficulty__title` az "X vs O" vagy "Amőba" felirathoz
- [ ] `AmoebaGame.css`: `.ameoba-difficulty__deco` X és O díszek a sarokban (CSS pseudo vagy span)
- [ ] `AmoebaGame.tsx`: a difficulty section div-je `ameoba-difficulty` osztályt kap, az inline `style` prop-ok eltávolítva
- [ ] Gombok: meglévő `primary-button` marad, elrendezés `flex-column` gap-pel (egymás alatt jobban nézhet ki, de ha vízszintes jobban illik, maradhat)

Acceptance: A difficulty screen vizuálisan amőba-témájú, nincs szöveges szintleírás, a három gomb jól kattintható.

---

## Notes

- A `hub-stage` CSS-t (`place-items: center`) NEM változtatjuk — a fixet a `canvasOffsetY` számítással csináljuk, nem CSS-sel.
- A felirat (`drawHub`) a canvas-on belül rajzolódik, nem HTML overlay.
- Casino scene: `CasinoScene.tsx`-ben is ellenőrizni kell, hogy `createInteractionPrompt` hívása frissítve van-e.
