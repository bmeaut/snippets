# Implementation Plan: Amőba Vizuális Csiszolás

**Branch**: `005-amoba-visual-polish` | **Date**: 2026-06-02 | **Spec**: [spec.md](./spec.md)

## Summary

A meglévő, funkcionálisan kész Amőba játékot vizuálisan és UX-szempontból fejlesztjük: színes jelölők, nyerési sor kiemelés, aktuális játékos jelzője, és session statisztika. A módosítások CSS/React alapúak, a canvas nem érintett. A `gameLogic.ts` egyetlen ponton bővül: egy `findWinCells` helperrel, amely visszaadja a nyerő cellák koordinátáit.

## Technical Context

**Language/Version**: TypeScript 5.x (strict)
**Primary Dependencies**: React 18, Vite, CSS modules (inline → CSS osztályok)
**Storage**: N/A (session state csak React state-ben)
**Testing**: Vitest (meglévő unit tesztek bővítése)
**Target Platform**: Böngésző (desktop)
**Performance Goals**: 30+ FPS, CSS transition animációk (nem canvas)
**Constraints**: Visszafelé kompatibilis `checkWin`, nincs localStorage

## Constitution Check

- ✅ TypeScript strict: minden új entitás (`WinResult`, `SessionStats`, `LastMove`) explicit típussal
- ✅ Modul izoláció: csak `src/games/ameoba/` érintett
- ✅ Nem töri a `GameModuleContract`-ot
- ✅ Magyar dokumentáció, angol kódnévek

## Project Structure

```text
src/games/ameoba/
├── gameLogic.ts          # findWinCells helper hozzáadása
├── AmoebaGame.tsx        # vizuális logika, session stats, last move
└── AmoebaGame.css        # (ÚJ) osztályalapú stílusok

specs/005-amoba-visual-polish/
├── spec.md
├── plan.md               # ez a fájl
└── tasks.md
```

## Phases

### Phase 1 — gameLogic.ts bővítés
`findWinCells(board, player)` hozzáadása: visszaadja a `{row, col}[]` tömböt a nyerő 4 cellával, vagy üres tömböt ha nincs győzelem. A meglévő `checkWin` érintetlen marad (belülről hívhatja `findWinCells`-t).

**Kimenet**: `findWinCells` unit teszttel igazolva, `checkWin` visszafelé kompatibilis.

### Phase 2 — Stílusos tábla és jelölők (`AmoebaGame.css`)
Új CSS fájl a következőkkel:
- `.cell` — alap cella stílus (méret, háttér, border)
- `.cell--x` — X jelölő szín (narancs/piros) és méret
- `.cell--o` — O jelölő szín (kék/cián) és méret  
- `.cell--hover` — hover kiemelés üres cellán (`:hover` + pointer cursor)
- `.cell--last` — utolsó lerakott jel enyhe kiemelése
- `.cell--win` — nyerő cella kiemelés (zöld/arany, opcionális pulzáló animáció)

**Kimenet**: A tábla stílusos, az X/O jelölők jól láthatóan különböznek.

### Phase 3 — AmoebaGame.tsx refaktor
Az inline stílusok lecserélése CSS osztályokra. Az `AmoebaGame` state kiegészítése:
- `winCells: {row:number, col:number}[]` — nyerő cellák koordinátái
- `lastMove: {row:number, col:number} | null` — utolsó lerakott jel
- `stats: SessionStats` — session statisztika

Győzelem esetén `findWinCells` meghívása és az eredmény beírása `winCells`-be. Nehézségváltáskor `stats` visszaáll.

**Kimenet**: Vizuálisan kész tábla, kiemelések működnek.

### Phase 4 — Állapotjelző sáv
A tábla felett egy kis info-sáv jelzi: "A te köröd (X)" / "AI gondolkodik..." / "X nyert!" / "Döntetlen". Az AI lépése előtt az állapot azonnal frissül, a tábla nem kattintható (`pointer-events: none`).

**Kimenet**: A játékos mindig látja kinek a köre.

### Phase 5 — Session statisztika
A topbárban (a Restart gomb mellé) kerül egy kis számlálópanel: `Gy: 0 | V: 0 | D: 0`. Meccs végén frissül. Nehézségváltáskor (`startNew(d)` hívásakor más d-vel) visszaáll.

**Kimenet**: 20 meccs után is helyes számok.

## Deliverables

- `src/games/ameoba/gameLogic.ts` — `findWinCells` hozzáadva
- `src/games/ameoba/AmoebaGame.css` — (ÚJ) stílusfájl
- `src/games/ameoba/AmoebaGame.tsx` — refaktorált, vizuálisan kész

## Risks & Mitigations

- **findWinCells és checkWin szinkronja**: A `checkWin` belülről hívja `findWinCells`-t, így nem duplikálódik a logika.
- **CSS specificity conflict**: A meglévő `styles.css` vagy `game-shell` osztályok felülírhatják. Megoldás: az amőba-specifikus osztályok egyedi prefix kapnak (`ameoba-`).
- **AI lépés közbeni kattintás**: A `currentPlayer !== 'X'` guard már megvan a kódban; vizuálisan a `pointer-events: none` erősíti meg.
