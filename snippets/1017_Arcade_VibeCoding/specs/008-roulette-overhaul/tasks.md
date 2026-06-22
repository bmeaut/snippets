# Tasks: Rulett Overhaul

## Phase 1 — Golyó animáció

- [ ] `RouletteWheel.tsx`: Canvas overlay elem hozzáadása az SVG fölé (`position: absolute`, azonos méret)
- [ ] `RouletteWheel.tsx`: Props bővítése: `ballActive: boolean`, `ballTargetAngleDeg: number`
- [ ] `RouletteWheel.tsx`: rAF loop a golyó pozíció számításhoz:
  - `ballAngle`: kezdeti gyors negatív irányú forgás, exponenciális lassítás
  - `ballRadius`: az utolsó 0.8s alatt `100 → 78` (SVG koordinátákban)
  - Végeredmény szög = `ballTargetAngleDeg` (nyerő szám szöge, kerék offsetjével korrigálva)
- [ ] `RouletteWheel.tsx`: Canvas rajzolás: fehér kör `ballRadius`-on `ballAngle` szögnél, enyhe árnyékkal
- [ ] `RouletteWheel.tsx`: Animáció leáll `ballActive === false` esetén, golyó marad az utolsó pozícióban
- [ ] `RouletteGame.tsx`: `ballActive` és `ballTargetAngleDeg` state hozzáadása
- [ ] `RouletteGame.tsx`: `handleSpin`-ben: nyerő szög kiszámítása és `ballActive: true` beállítása
- [ ] `RouletteGame.tsx`: 3s után: `ballActive: false`, golyó marad; auto-clear után: reset

Acceptance: Golyó minden pörgetésnél láthatóan a nyerő zsebben áll meg.

---

## Phase 2 — History panel

- [ ] `RouletteGame.tsx`: `history: number[]` state hozzáadása (max 10)
- [ ] `RouletteGame.tsx`: Pörgetés végén: `setHistory(prev => [...prev.slice(-9), result])`
- [ ] `ResultHistory.tsx` (ÚJ): komponens létrehozása
  - 10 db badge slot vízszintesen, legfrissebb bal oldalon
  - Badge stílus: 32px kerek div, piros (#ef4444) / fekete (#1f2937) / zöld (#16a34a) háttér, fehér szám
  - Üres slotok: halványabb placeholder karika
  - CSS `slide-in` animáció az új badge-re
- [ ] `RouletteGame.tsx`: `<ResultHistory history={history} />` elhelyezése a kerék közelében

Acceptance: 3 pörgetés után 3 badge látható helyes sorrendben és színnel.

---

## Phase 3 — Racetrack komponens

### gameLogic.ts bővítések
- [ ] `getNeighbors(number: number, count: number): number[]` — WHEEL_SEQUENCE alapján N szomszéd mindkét oldalon, wrap-around
- [ ] `getTiersBets(chipAmount: number): Bet[]` — 6 split tét
- [ ] `getVoisinsBets(chipAmount: number): Bet[]` — trio, corner, 5 split (9 chip összesen)
- [ ] `getOrphelinsBets(chipAmount: number): Bet[]` — 1 straight + 4 split (5 chip)
- [ ] `getJeuZeroBets(chipAmount: number): Bet[]` — 1 straight + 3 split (4 chip)

### RacetrackBoard.tsx (ÚJ)
- [ ] Ovális layout: felső sor és alsó sor WHEEL_SEQUENCE sorrendben (ld. plan.md)
- [ ] Szám gombok: kattintásra `onAddBets(getNeighbors + straight tétek)`
- [ ] Szomszéd szelektor: "N szomszéd" felirat, − / + gombok, 1–4 korlát
- [ ] Predefined gombok: "Kis széria", "Nagy széria", "Árva számok", "Zéró játék"
- [ ] Minden gomb kattintáskor a jelenlegi chipértékkel hívja `onAddBets`
- [ ] Hover: az érintett számok kiemelése (a predefined set összes tagja)

### RouletteGame.tsx
- [ ] `boardView: 'standard' | 'racetrack'` state hozzáadása
- [ ] Toggle gomb: "Versenypalya ↔ Standard" a board fölött
- [ ] `<RacetrackBoard>` renderelése `boardView === 'racetrack'` esetén
- [ ] `onAddBets` prop csatlakoztatása: több tét egyszerre `setBets(prev => [...prev, ...newBets])`
- [ ] Balance check: ha a tétek összege meghaladja az egyenleget, ne engedje felrakni (toast/disable)

Acceptance: Minden predefined bet helyes tétszámot és típust generál; szomszéd bet wrap-around helyes.

---

## Phase 4 — Magyar UI

- [ ] `RouletteGame.tsx`: "Back to Hub" → "Vissza a Kaszinóba"
- [ ] `RouletteGame.tsx`: "Mute/Unmute" → "Némítás" / "Hang be"
- [ ] `RouletteGame.tsx`: "European Table" → "Európai Rulett"
- [ ] `RouletteGame.tsx`: "Balance" → "Egyenleg"
- [ ] `BettingBoard.tsx`: ellenőrzés — gombok magyarok-e (Pörgetés, Törlés)

Acceptance: Minden látható szöveg magyar.

---

## Notes

- `getNeighbors(17, 2)` → WHEEL_SEQUENCE-ben 17 index=8, szomszédok: idx 6,7,8,9,10 → [2, 25, 17, 34, 6]
- Voisins hagyományos 9 chip: trio(0-2-3)×2, corner(25-26-28-29)×2, split(4-7)×1, split(12-15)×1, split(18-21)×1, split(19-22)×1, split(32-35)×1 — a `chipAmount` szorzóként funkcionál
- Racetrack layout CSS: `display: flex; flex-wrap: wrap` vagy SVG `<ellipse>`-alapú pozicionálás
- Golyó Canvas overlay: `pointer-events: none`, csak vizuális
- History komponens session-only, localStorage nem kell
