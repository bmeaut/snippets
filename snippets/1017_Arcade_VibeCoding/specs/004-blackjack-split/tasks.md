# Tasks: Blackjack Split

## Phase 1: Core State Refactor

**Purpose**: Replace the single player hand model with a split-ready round structure.

- [X] T001 Refactor `src/games/blackjack/gameLogic.ts` to use `playerHands: Card[][]` and `activeHandIndex` in the round state.
- [X] T002 Update `tests/unit/blackjackLogic.test.ts` to assert the new split-ready state shape while preserving the existing blackjack behavior.
- [X] T003 Keep the existing UI compiling by maintaining any temporary compatibility needed during the state transition.

## Phase 2: Split Eligibility and Wallet Validation

**Purpose**: Add split gating before any hand-duplication logic is exposed to the UI.

- [X] T004 Implement split eligibility checks for initial two-card matching values.
- [X] T005 Validate the additional split wager against the shared wallet before applying the split.
- [X] T006 Add unit tests for invalid split attempts, including insufficient funds and ineligible hands.

## Phase 3: Sequential Hand Resolution

**Purpose**: Resolve split hands one at a time and preserve the new active hand state.

- [X] T007 Implement sequential hand progression with `activeHandIndex` advancing only after the current hand finishes.
- [X] T008 Add support for per-hand resolution outcomes and aggregate round settlement.
- [X] T009 Add unit tests for sequential resolution across two split hands.

## Phase 4: Split Ace Edge Cases

**Purpose**: Enforce the stricter rules for split Aces.

- [X] T010 Implement the one-card-only rule for split Aces and auto-end the turn after the card is dealt.
- [X] T011 Treat split Ace + 10-value hands as 1:1 wins instead of natural blackjack payouts.
- [X] T012 Add unit tests for split Ace auto-end behavior and payout handling.

## Phase 5: UI Follow-up

**Purpose**: Expose split hands visually once the state model is stable.

- [X] T013 Update the Blackjack UI to render multiple hands and highlight the active one.
- [X] T014 Add UI regression tests for multi-hand rendering and active-hand indicators.

## Dependencies & Execution Order

- T001 must complete before any split-specific logic can be layered on top.
- T004-T006 depend on the new round state being available.
- T007-T012 depend on the split state and eligibility logic.
- T013-T014 are intentionally deferred until after the logic refactor stabilizes.
