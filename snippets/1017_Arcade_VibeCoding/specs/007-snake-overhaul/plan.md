# Implementation Plan: Snake Overhaul

**Branch**: `007-snake-overhaul` | **Date**: 2026-06-02 | **Spec**: [spec.md](./spec.md)

## Summary

A Snake játék teljes átírása: `setTimeout` → `requestAnimationFrame`, portál falmozgás, arany/kék különleges almák, kő akadályok, vizuális redesign, magyar UI.

## Technical Context

**Language/Version**: TypeScript 5.x strict, React 18  
**Graphics**: HTML5 Canvas 2D  
**Érintett fájlok**:
- `src/games/snake/snakeLogic.ts` — logika bővítés
- `src/games/snake/SnakeGame.tsx` — rAF loop, rendering, UI
- `src/types.ts` — SnakeState bővítés

## Constitution Check

- ✅ Modul izoláció: csak `src/games/snake/` érintett
- ✅ TypeScript strict: minden új mező explicit típussal
- ✅ Meglévő unit tesztek nem törnek (snakeLogic API visszafelé kompatibilis ahol lehetséges)

## Phases

### Phase 1 — SnakeState bővítés + portál falmozgás

`src/types.ts`: SnakeState új mezői:
```ts
stones: Coordinate[]
goldenApple: { pos: Coordinate; spawnedAt: number } | null
blueApple:   { pos: Coordinate; spawnedAt: number } | null
slowUntil:   number | null
applesEaten: number
```

`snakeLogic.ts`:
- `moveSnake`: fal elérése helyett `(x + GRID_SIZE) % GRID_SIZE` wrap — nincs `hitsWall` halál
- Ütközésdetektálás: önmaga + kövek
- `createInitialSnakeState`: új mezők null/[] alapértékkel

### Phase 2 — Különleges almák logikája

`snakeLogic.ts`:
- `applesEaten` számlálás minden rendes alma evásnál
- `spawnGoldenApple(state)`: ha `applesEaten % 7 === 0 && applesEaten > 0` → arany alma spawn üres cellán
- `spawnBlueApple(state)`: ha `applesEaten % 5 === 0 && applesEaten > 0` → kék alma spawn
- Timeout ellenőrzés: `now - goldenApple.spawnedAt > 6000` → eltávolítás
- Evési logika: arany +3 pont, kék +1 pont + `slowUntil = now + 3000`
- `nextTickDelay`: ha `slowUntil > now` → delay × 2

### Phase 3 — Kő akadályok logikája

`snakeLogic.ts`:
- `spawnStone(state)`: score ≥ 8 és `(score - 8) % 4 === 0` amikor pont szerezhető → 1 új kő, max 12
- Kő spawn: random üres cella (nem kígyó, nem alma, nem másik kő)
- `moveSnake`: `hitsStone` ellenőrzés → `gameOver: true`
- `createRandomPosition(exclude: Coordinate[])`: általános helper (alma és kő spawnhoz)

### Phase 4 — requestAnimationFrame loop

`SnakeGame.tsx`:
- `tickRef` `setTimeout` → `rAF` id + `lastTickTimeRef` (utolsó logikai tick időbélyege)
- `rAF` callback: `now - lastTickTime >= currentDelay` → logikai tick futtatása
- Minden frame: canvas újrarajzolás (akár változott a state akár nem — animációkhoz)
- Lassítás: `currentDelay = slowActive ? delay * 2 : delay`

### Phase 5 — Vizuális redesign

Canvas rendering:
- `roundRect` a kígyó szegmensekhez (radius: 4px)
- Fej: világosabb zöld (#a3e635), test: sötétedő gradiens (#65a30d → #166534)
- Alma: `arc` alapú kör, narancs fill + enyhe glow (shadowBlur)
- Arany alma: sárga (#fbbf24) kör + arany glow + visszaszámláló szám a cellában
- Kék alma: cián (#38bdf8) kör + kék glow
- Kő: sötétszürke (#374151) lekerekített négyzet, enyhe textúra (belső árnyék)
- Lassítás visszaszámláló: kis ikon/szám a score panel mellett

### Phase 6 — Magyar UI + HTML overlay score

`SnakeGame.tsx`:
- Score + rekord: `<div>` overlay (nem canvas `fillText`)
- Gombok: "Vissza a Hubba", "Újraindítás"
- Game over panel: "Játék vége", "Pontszám: X", "Rekord: Y"
- Aktív lassítás jelzése a score panel mellett (pl. "🐢 2s" visszaszámláló)

## Deliverables

```text
src/types.ts                        # SnakeState bővítés
src/games/snake/snakeLogic.ts       # portál, különleges almák, kövek
src/games/snake/SnakeGame.tsx       # rAF loop, vizuális redesign, magyar UI
```

## Risks & Mitigations

- **rAF + state frissítés**: A React setState async — a logikai ticknél `useRef`-ben tárolt state-et kell olvasni (nem closure-t), különben stale state problémák lépnek fel. Megoldás: `stateRef` pattern.
- **Különleges almák egyidejűsége**: Arany és kék alma ciklusai (7 ill. 5) találkozhatnak (LCM=35). Mindkét slot egymástól független state mezőként kezelendő.
- **Kő spawn ütközés**: Ha a pálya nagyon tele van (nagy kígyó + 12 kő), a spawn loop végtelen ciklusba kerülhet. Megoldás: max 100 próba, ha nem sikerül, skip.
- **Unit tesztek**: `moveSnake` API megváltozik (portál miatt `hitsWall` eltűnik). A meglévő tesztek frissítést igényelnek.
