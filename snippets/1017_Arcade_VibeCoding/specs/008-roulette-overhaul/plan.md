# Implementation Plan: Rulett Overhaul

**Branch**: `008-roulette-overhaul` | **Date**: 2026-06-02 | **Spec**: [spec.md](./spec.md)

## Summary

Három párhuzamos fejlesztési szál: (1) golyó animáció Canvas/rAF-alapon a kerékhez, (2) utolsó 10 eredmény history panel, (3) Racetrack tábla új komponensként a meglévő BettingBoard mellé.

## Technical Context

**Language/Version**: TypeScript 5.x strict, React 18
**Graphics**: SVG (meglévő kerék) + Canvas overlay golyóhoz, CSS (Racetrack layout)
**Érintett fájlok**:
- `src/games/roulette/RouletteWheel.tsx` — golyó animáció hozzáadása
- `src/games/roulette/RouletteGame.tsx` — history state, toggle, golyó sync
- `src/games/roulette/RacetrackBoard.tsx` — (ÚJ) Racetrack komponens
- `src/games/roulette/gameLogic.ts` — Racetrack bet helper függvények

## Constitution Check

- ✅ Modul izoláció: csak `src/games/roulette/` érintett
- ✅ TypeScript strict: golyó state, history, NeighborCount mind explicit típus
- ✅ Meglévő BettingBoard és bet evaluation logika érintetlen

## Phases

### Phase 1 — Golyó animáció

**Megközelítés**: Canvas overlay a meglévő SVG kerék tetején (azonos méretű, `position: absolute`). A Canvas `requestAnimationFrame`-ben rajzolja a golyót, a kerék CSS transform-ja változatlan marad.

**Golyó mozgás logika** (`RouletteWheel.tsx` bővítése):
- Props: `ballTargetAngleDeg: number | null` (null = nincs animáció)
- rAF loop: `ballAngle` és `ballRadius` frissítése
  - Kezdeti szögsebesség: ~720°/s negatív irányban, exponenciális deceleration
  - `ballRadius` az utolsó 0.8s alatt csökken: `outerRimR (100)` → `pocketR (78)`
  - Végső szög = a nyerő szám szöge a kerék koordináta-rendszerében (figyelembe veszi a kerék aktuális CSS rotációját)
- Canvas egyeztetés: azonos `viewBox` transzformáció mint az SVG

**Szinkronizálás** (`RouletteGame.tsx`):
- `handleSpin`-ben: `setBallTargetAngle(winningAngle)` és `setBallSpinning(true)`
- 3s elteltével: `setBallSpinning(false)`, golyó marad a zsebben
- Auto-clear után: `setBallTargetAngle(null)`

### Phase 2 — History panel

`RouletteGame.tsx`: `history: number[]` state (max 10), `[...history.slice(-9), result]` frissítés minden pörgetés végén.

`ResultHistory.tsx` (ÚJ, kis komponens):
- 10 badge vízszintes sorban, legfrissebb bal oldalon
- Badge: kerek kis div, piros/fekete/zöld háttér, fehér szám
- Ha kevesebb mint 10 eredmény: üres helyek placeholder-rel
- Animáció: `slide-in-left` CSS animáció az új badge-re

### Phase 3 — Racetrack komponens

`RacetrackBoard.tsx` (ÚJ):

**Layout**: Ovális SVG vagy CSS flex — a 37 szám WHEEL_SEQUENCE sorrendben:
```
Felső sor (bal→jobb): 0  32 15 19  4 21  2 25 17 34  6 27 13 36 11 30  8 23
Alsó sor (jobb→bal): 10  5 24 16 33  1 20 14 31  9 22 18 29  7 28 12 35  3 26
```
(0 a bal felső sarokban, a számok az óramutató járásával mennek körbe)

**Szomszéd szelektor**: 1–4 +/- gombok, az értéket `neighborCount` state tárolja.

**Kattintás logika**: Szám kattintásra `onAddBets(bets: Bet[])` callback hívódik `2*neighborCount+1` straight téttel. A szomszédok WHEEL_SEQUENCE index alapján, wrap-around.

**Predefined gombok**:
```
Kis széria (Tiers):   6 split: [27-13, 36-11, 30-8, 23-10, 5-24, 16-33]
Nagy széria (Voisins): trio: [0-2-3], corner: [25-26-28-29], splitek: [4-7, 12-15, 18-21, 19-22, 32-35]
Árva számok (Orphelins): straight: [1], splitek: [6-9, 14-17, 17-20, 31-34]
Zéró játék (Jeu Zéro): splitek: [0-3, 12-15, 32-35], straight: [26]
```

Minden predefined bet a jelenlegi chipértékkel kerül fel (1 chip = 1 tét egység).

**Toggle** (`RouletteGame.tsx`): `boardView: 'standard' | 'racetrack'` state, gomb a két nézet között.

### Phase 4 — Magyar UI + kisebb tisztítások

- "Back to Hub" → "Vissza a Kaszinóba"
- "Mute/Unmute" → "Némítás / Hang"
- Racetrack gombok: "Kis széria", "Nagy széria", "Árva számok", "Zéró játék", "Szomszédok: N"

## Deliverables

```text
src/games/roulette/RouletteWheel.tsx     # golyó animáció Canvas overlay
src/games/roulette/RouletteGame.tsx      # history state, boardView toggle, ball sync
src/games/roulette/gameLogic.ts          # racetrack bet helpers
src/games/roulette/RacetrackBoard.tsx    # (ÚJ) Racetrack komponens
src/games/roulette/ResultHistory.tsx     # (ÚJ) History panel
```

## Risks & Mitigations

- **Golyó/kerék szinkron**: A CSS cubic-bezier és a rAF deceleration nem lesz tökéletesen szinkron. Megoldás: golyó rAF-ja a maradék idő alapján (`timeLeft / totalTime`) számol, tehát a 3s végén mindkettő pontosan megáll.
- **Canvas overlay DPR**: Az SVG és a Canvas mérete pontosan meg kell egyezzen. Megoldás: mindkettő azonos `width/height` CSS értékkel, Canvas `devicePixelRatio`-ra skálázva.
- **Predefined bet balance check**: Voisins = 9 chip → ha a játékosnak kevesebb van, ne menjen fel. Megoldás: `RouletteGame` összesíti az új téteket és ellenőriz a jelenlegi egyenleg ellen.
