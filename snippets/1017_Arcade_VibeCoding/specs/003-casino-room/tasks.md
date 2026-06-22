# Tasks: Casino Room

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the feature scaffolding and entry points used by all later phases.

- [ ] T001 [P] Create Casino Room and casino game folders in `src/casino/scene/`, `src/casino/services/`, `src/casino/state/`, `src/casino/ui/`, `src/games/blackjack/`, and `src/games/roulette/`.
- [ ] T002 [P] Add the Casino Room scene and game module entry files in `src/casino/index.ts`, `src/casino/scene/CasinoScene.tsx`, `src/games/blackjack/index.tsx`, and `src/games/roulette/index.tsx`.
- [ ] T003 [P] Add Casino Room unit test scaffolds in `tests/unit/casinoNavigation.test.tsx`, `tests/unit/walletStorage.test.ts`, `tests/unit/blackjackLogic.test.ts`, and `tests/unit/rouletteLogic.test.ts`.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared room, wallet, and scene-transition foundations that every user story depends on.

- [ ] T004 [P] Define shared scene and wallet types in `src/casino/state/roomNavigation.ts` and `src/casino/state/wallet.ts`.
- [ ] T005 [P] Implement browser wallet persistence helpers in `src/casino/services/walletStorage.ts`.
- [ ] T006 [P] Implement local-calendar daily bonus helpers in `src/casino/services/dailyBonus.ts`.
- [ ] T007 [P] Add room-transition adapter helpers for Hub and Casino movement in `src/casino/state/roomNavigation.ts` and `src/hub/systems/interaction.ts`.
- [X] T008 Update `src/App.tsx` scene routing so the app can switch between `hub`, `casino`, `blackjack`, and `roulette` scenes.

## Phase 3: User Story 1 - Szobák közti átjárás (Priority: P1)

**Goal**: The player can move from the Arcade Hub into the Casino Room and back again using visible doors and the `E` key.

**Independent Test**: Standing near the Hub right-side door and pressing `E` opens the Casino Room; standing near the Casino left-side door and pressing `E` returns to the Hub.

- [X] T009 [P] [US1] Add the Hub casino door entity and prompt rendering in `src/hub/scene/HubScene.tsx` and `src/hub/rendering/drawHub.ts`.
- [X] T010 [P] [US1] Add the Casino Room return door entity and prompt rendering in `src/casino/scene/CasinoScene.tsx` and `src/casino/rendering/drawCasino.ts`.
- [X] T011 [US1] Wire the Hub-to-Casino and Casino-to-Hub transitions in `src/App.tsx` and `src/casino/state/roomNavigation.ts`.
- [X] T012 [P] [US1] Add room-navigation tests in `tests/unit/casinoNavigation.test.tsx` and `tests/unit/sceneTransition.test.ts`.

## Phase 4: User Story 2 - Közös pénztárca és napi bónusz (Priority: P1)

**Goal**: The Casino Room shows a persistent shared wallet that starts at 10,000 Ft for first-time players and grants a 10,000 Ft daily bonus once per calendar day.

**Independent Test**: Refreshing the browser restores the wallet balance, first-run sessions start at 10,000 Ft, and repeated same-day opens do not duplicate the daily bonus.

- [ ] T013 [P] [US2] Implement first-run wallet initialization and load/save behavior in `src/casino/services/walletStorage.ts`.
- [ ] T014 [P] [US2] Implement daily bonus eligibility and timestamp comparison in `src/casino/services/dailyBonus.ts`.
- [X] T015 [US2] Render the always-visible wallet balance HUD in `src/casino/ui/WalletHud.tsx` and mount it from `src/casino/scene/CasinoScene.tsx`.
- [ ] T016 [P] [US2] Add wallet persistence and daily bonus tests in `tests/unit/walletStorage.test.ts` and `tests/unit/dailyBonus.test.ts`.

## Phase 5: User Story 3 - Blackjack játék (Priority: P2)

**Goal**: The Casino Room Blackjack machine supports betting, Hit, Stand, Double Down, dealer draw rules, and standard payouts against the shared wallet.

**Independent Test**: A Blackjack round can be started, played to completion, and settled without leaving the Blackjack module; wallet balance changes reflect the outcome.

- [ ] T017 [P] [US3] Implement blackjack card, deck, scoring, and dealer-rule helpers in `src/games/blackjack/gameLogic.ts` and `src/games/blackjack/types.ts`.
- [X] T018 [P] [US3] Build the Blackjack machine UI, bet flow, and `Vissza a Casino Szobába` action in `src/games/blackjack/BlackjackGame.tsx` and `src/games/blackjack/index.tsx`.
- [ ] T019 [US3] Connect blackjack round settlement and wallet updates through `src/casino/services/blackjackSettlement.ts` and `src/casino/services/walletStorage.ts`.
- [X] T020 [P] [US3] Add blackjack tests for scoring, dealer behavior, double down, and payout edge cases in `tests/unit/blackjackLogic.test.ts` and `tests/unit/blackjackGame.test.tsx`.

## Phase 6: User Story 4 - Rulett játék (Priority: P3)

**Goal**: The Casino Room Roulette machine supports European wheel bets, spin resolution, and wallet settlement with the requested payout ratios.

**Independent Test**: A Roulette round can be started, resolved, and settled without leaving the Roulette module; supported bet types pay out according to the spec.

- [ ] T021 [P] [US4] Implement roulette wheel, bet validation, and payout table helpers in `src/games/roulette/gameLogic.ts` and `src/games/roulette/types.ts`.
- [X] T022 [P] [US4] Build the Roulette machine UI, bet selectors, and `Vissza a Casino Szobába` action in `src/games/roulette/RouletteGame.tsx` and `src/games/roulette/index.tsx`.
- [ ] T023 [US4] Connect roulette spin settlement and wallet updates through `src/casino/services/rouletteSettlement.ts` and `src/casino/services/walletStorage.ts`.
- [ ] T024 [P] [US4] Add roulette tests for bet validation, wheel outcomes, payout mapping, and insufficient balance handling in `tests/unit/rouletteLogic.test.ts` and `tests/unit/rouletteGame.test.tsx`.

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Stabilize the feature across all stories and validate the finished flow end to end.

- [ ] T025 [P] Update shared contract exports and game-module wiring in `src/games/blackjack/index.tsx`, `src/games/roulette/index.tsx`, and `src/casino/index.ts`.
- [ ] T026 [P] Refresh `specs/003-casino-room/quickstart.md` with the final Casino Room verification flow.
- [ ] T027 Run `npm run test`, `npm run build`, and `npm run lint` to validate the Casino Room feature end to end.

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies and can start immediately.
- Foundational (Phase 2) depends on Setup and blocks all user stories.
- User Stories (Phases 3-6) depend on Phase 2 completion.
- Polish (Phase 7) depends on the desired user stories being complete.

### User Story Dependencies

- User Story 1 (P1) depends only on the foundational room-transition helpers.
- User Story 2 (P1) depends only on the foundational wallet service.
- User Story 3 (P2) depends on the wallet service and the shared App scene routing, but not on Roulette.
- User Story 4 (P3) depends on the wallet service and the shared App scene routing, but not on Blackjack.

### Within Each User Story

- Tests are included for each story and should be written before or alongside implementation.
- Shared helpers should be implemented before the UI that consumes them.
- Each story should be validated independently before moving to the next one.

## Parallel Opportunities

- T001-T003 can run in parallel because they create different scaffolding files.
- T004-T007 can run in parallel because they touch separate foundational files.
- T009-T010 can run in parallel because Hub and Casino room rendering live in different files.
- T013-T014 can run in parallel because initialization and daily bonus logic are separate helpers.
- T017-T018 can run in parallel because blackjack logic and UI live in different files.
- T021-T022 can run in parallel because roulette logic and UI live in different files.
- T025-T026 can run in parallel because they touch different polish targets.

## Parallel Example: User Story 1

```bash
Task: "Add the Hub casino door entity and prompt rendering in src/hub/scene/HubScene.tsx and src/hub/rendering/drawHub.ts"
Task: "Add the Casino Room return door entity and prompt rendering in src/casino/scene/CasinoScene.tsx and src/casino/rendering/drawCasino.ts"
Task: "Add room-navigation tests in tests/unit/casinoNavigation.test.tsx and tests/unit/sceneTransition.test.ts"
```

## Parallel Example: User Story 3

```bash
Task: "Implement blackjack card, deck, scoring, and dealer-rule helpers in src/games/blackjack/gameLogic.ts and src/games/blackjack/types.ts"
Task: "Build the Blackjack machine UI, bet flow, and Vissza a Casino Szobába action in src/games/blackjack/BlackjackGame.tsx and src/games/blackjack/index.tsx"
Task: "Add blackjack tests for scoring, dealer behavior, double down, and payout edge cases in tests/unit/blackjackLogic.test.ts and tests/unit/blackjackGame.test.tsx"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate the Hub <-> Casino navigation independently.

### Incremental Delivery

1. Setup + Foundational establish the shared app and storage basis.
2. User Story 1 adds room navigation as the first playable slice.
3. User Story 2 adds the wallet and daily bonus that both games will use.
4. User Story 3 adds Blackjack as the first casino game.
5. User Story 4 adds Roulette as the second casino game.
6. Polish validates the whole feature with build, test, and lint checks.

## Notes

- [P] tasks can run in parallel only when they touch different files.
- Story labels map each task to the relevant user story for traceability.
- The task list is intentionally ordered so each story can be implemented and tested independently.
