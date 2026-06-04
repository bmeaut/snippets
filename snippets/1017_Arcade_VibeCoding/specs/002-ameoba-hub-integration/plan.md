# Implementation Plan: Amőba (Gomoku)

## Goal
Integrate an 8x8 Amőba game into the Arcade Hub, playable vs AI with three difficulty levels, following `GameModuleContract` and including ErrorBoundary and a "Vissza a Hubba" button.

## Phases
1. Hub gép hozzáadása
   - Feladatok: placeholder entitás (kék téglalap) megjelenítése a Hub Canvas-on; interakció (`E`) hook-olása a játékmód indításához.
   - Kimenet: a Hubból elindítható a nehézségi menü.

2. Nehézségi menü és UI
   - Feladatok: modal vagy overlay képernyő létrehozása 3 gombbal (`Könnyű`, `Közepes`, `Nehéz`), választás átadása a játékmodulnak.
   - Kimenet: minden választás elindítja a játékot a megfelelő `difficulty` beállítással.

3. Játék logika (8x8 tábla)
   - Feladatok: tábla komponens, lépések kezelése, győzelem/döntetlen ellenőrző függvény (4 in-a-row), szabályok, GameState kezelése.
   - Kimenet: működő játékmotor, helyes győzelem- és döntetlen-állapotok.

4. AI algoritmusok
   - Feladatok: Easy (random), Medium (alap blokkoló logika), Hard (Minimax + alfa-béta vágás, korlátozott mélység, időlimit vagy worker támogatás).
   - Kimenet: a három difficulty viselkedése megfelel az FR-004 követelményeknek.

5. Integráció és tesztelés
   - Feladatok: Unit tesztek a `snake` játékhoz hasonlóan (`tests/unit`) a játéklogikára és AI-re; integrációs tesztek Hubból indítással; ErrorBoundary viselkedés tesztelése.
   - Kimenet: elfogadási tesztek zöldek, vizuális ellenőrzés a Hubban.

## Deliverables
- `specs/002-ameoba-hub-integration/spec.md`
- `src/games/ameoba/` mappa: `index.tsx`, `AmoebaGame.tsx`, `gameLogic.ts`, `ai/` (easy.ts, medium.ts, hard.ts)
- Unit tesztek a `tests/unit` alá

## Risks & Mitigations
- Hard AI teljesítmény probléma: korlátozott mélység + időlimit + opcionális Worker.
- Hub UI clash: izolált overlay és ErrorBoundary.

## Timeline (estimates)
- Hub integration: 1 day
- Difficulty menu + UI: 0.5 day
- Game logic: 1.5 day
- AI implementations & tuning: 2 days
- Tests and polish: 1 day

## Acceptance Criteria
- Hubból indítás, nehézségi választás, játszható 8x8 tábla, 3 AI mód, vissza a Hubba működik, kötelező ErrorBoundary implementálva.
