# Tasks: Amőba (Gomoku) Implementation

## Phase 1 — Hub gép hozzáadása
- [ ] Add blue placeholder machine in Hub Canvas (`hub/rendering/drawHub.ts` or hub scene)
- [ ] Hook `E` interaction to open Amőba difficulty menu
- [ ] Wire module entry point `src/games/ameoba/index.tsx` and lazy-load when invoked
- Acceptance: From Hub, `E` on the blue placeholder opens the difficulty screen.

## Phase 2 — Nehézségi menü
- [ ] Create overlay/modal with 3 buttons: `Könnyű`, `Közepes`, `Nehéz`
- [ ] Ensure selection passes `difficulty` to the game module
- [ ] Accessibility: keyboard focus and `Esc` to cancel
- Acceptance: Selecting a difficulty starts the game with the chosen mode.

## Phase 3 — Játék logika (8x8 tábla)
- [ ] Implement `AmoebaGame` React component and `gameLogic.ts` with: board rendering, cell click handling, move validation
- [ ] Implement `checkWin(board)` that detects 4-in-a-row in all directions
- [ ] Implement draw detection (board full, no winner)
- [ ] Add `Vissza a Hubba` button that closes game module and returns to Hub
- Acceptance: Players can place X, O alternates, win/draw detected correctly.

## Phase 4 — AI algoritmusok
- [ ] `ai/easy.ts`: random empty cell selection
- [ ] `ai/medium.ts`: detect player 2-3 in-line threats and block; otherwise random
- [ ] `ai/hard.ts`: Minimax with alpha-beta pruning, configurable `maxDepth`, time limit; fallback to simpler move if exceeds time
- [ ] Consider running `hard` AI evaluation in a Worker or with incremental timeout
- Acceptance: Each difficulty behaves per FR-004 and tests verify typical cases.

## Phase 5 — Integration, ErrorBoundary, Tests
- [ ] Wrap game module with `ErrorBoundary`
- [ ] Ensure module implements `GameModuleContract` (lifecycle hooks, close callback)
- [ ] Unit tests for `checkWin`, draw detection, AI behaviors (easy/medium/hard simplified scenarios)
- [ ] Integration test: Hub -> open game -> choose difficulty -> play minimal moves -> exit
- Acceptance: Tests pass; manual Hub validation successful.

## Notes
- File suggestions: `src/games/ameoba/index.tsx`, `AmoebaGame.tsx`, `gameLogic.ts`, `ai/easy.ts`, `ai/medium.ts`, `ai/hard.ts`.
- Keep performance budgets for Hard AI; prefer `maxDepth=4` as default and tune if needed.
