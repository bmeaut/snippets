# Implementation Plan: Casino Room

**Branch**: `003-casino-room` | **Date**: 2026-05-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-casino-room/spec.md`

## Summary

Add a second navigable room to the Arcade Hub: a Casino Room with a shared wallet, daily bonus persistence, and two contract-based game modules (Blackjack and European Roulette). The feature keeps the current Hub scene thin, uses `localStorage` as the wallet source of truth, and isolates each casino game behind the existing module boundary so a game failure cannot destabilize room navigation.

## Technical Context

**Language/Version**: TypeScript 5.0+ with `strict: true`  
**Primary Dependencies**: React 18+, Vite, HTML5 Canvas, browser `localStorage`  
**Storage**: Browser `localStorage` for wallet balance, first-seen timestamp, and last daily bonus timestamp  
**Testing**: Vitest, DOM-based component tests, existing unit test style under `tests/unit`  
**Target Platform**: Modern web browsers on desktop first, responsive enough for smaller viewports  
**Project Type**: Single-page web application with scene-based room navigation  
**Performance Goals**: Room transitions should feel immediate; Blackjack and Roulette resolution should not visibly block the UI; wallet UI should update synchronously after bets/payouts  
**Constraints**: Preserve the current Hub entry flow, keep game modules isolated, do not require external assets for MVP, and use a single shared wallet for both casino games  
**Scale/Scope**: Two rooms (Hub and Casino), two casino games, one persisted bankroll, and one browser session at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Strict Type Safety (TypeScript)
**Status**: ✅ PASS — Wallet, room, and round state can be described with explicit interfaces and discriminated unions.

### Principle II: Complete Module Isolation
**Status**: ✅ PASS — Blackjack and Roulette remain module boundaries with shared data only through explicit contracts and wallet service helpers.

### Principle III: Multimedia Excellence
**Status**: ✅ PASS — The feature stays within the existing Canvas + React room model and does not require new asset pipelines.

### Principle IV: Clean Code & Consistent Documentation
**Status**: ✅ PASS — Code remains English, documentation remains Hungarian, and the new docs explain the why of the room split and shared wallet.

### Principle V: Application Stability Through Module Boundaries
**Status**: ✅ PASS — Room transitions and game launches remain boundary-controlled; failures can be handled by the existing error boundary pattern.

**Gate Result**: ✅ ALL GATES PASS — proceed to Phase 0 and Phase 1 outputs.

## Project Structure

### Documentation (this feature)

```text
specs/003-casino-room/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (created separately)
```

### Source Code (repository root)

```text
src/
├── App.tsx                         # Scene switch between Hub and room/game overlays
├── components/
├── hub/                            # Existing Hub navigation and rendering
├── casino/
│   ├── scene/                      # Casino Room scene and room navigation
│   ├── state/                      # Wallet and room state models
│   ├── services/                   # localStorage wallet persistence + daily bonus logic
│   └── ui/                         # Balance HUD and return buttons
├── games/
│   ├── snake/                      # Existing game module
│   ├── ameoba/                     # Existing game module
│   ├── blackjack/                  # New casino module
│   └── roulette/                   # New casino module
└── storage.ts                      # Existing high-score storage, left intact for Snake

tests/
└── unit/                           # Room navigation, wallet, Blackjack, Roulette tests
```

**Structure Decision**: Keep the Arcade Hub as the top-level app shell, add a dedicated `src/casino/` area for shared wallet and room-state logic, and place Blackjack and Roulette in separate `src/games/*` modules so both casino games follow the same contract boundary as the existing games.

## Phase 0: Research

### Findings

- The current app already uses scene switching in `src/App.tsx`, so the casino room can be introduced without changing the top-level boot flow.
- The existing `GameModuleContract` pattern from `specs/001-arcade-hub-snake/contracts/game-module.contract.ts` is the right boundary for Blackjack and Roulette as well.
- `src/storage.ts` already shows the repo's preferred browser storage pattern: minimal wrapper, graceful fallback, and JSON-safe persistence.
- The casino wallet should be a dedicated service rather than a generic storage helper so wallet balance updates, daily bonus checks, and round settlements stay together.

### Decision Log

- **Decision**: Keep room navigation in the app/scene layer, not in the game modules.
  - **Rationale**: The casino room is a scene transition problem, not a game-logic problem.
  - **Alternatives considered**: Embedding room switching inside the game modules; rejected because it would blur module boundaries.

- **Decision**: Persist wallet data in `localStorage` as a JSON record with `balance`, `firstSeenAt`, and `lastDailyBonusAt`.
  - **Rationale**: The spec requires persistence across reloads and a daily bonus gate.
  - **Alternatives considered**: Separate keys per field; rejected because a single record is easier to validate and evolve.

- **Decision**: Evaluate the daily bonus against a local calendar-day key derived from the stored timestamp.
  - **Rationale**: The feature is day-based, not time-slice-based, and the local calendar day matches the user expectation for a daily reward.
  - **Alternatives considered**: Raw elapsed milliseconds; rejected because it can misclassify visits around midnight and time-zone changes.

- **Decision**: Implement Blackjack with a standard 52-card deck and per-round shuffle.
  - **Rationale**: The rules are standard and easy to test deterministically with seeded or stubbed shuffles.
  - **Alternatives considered**: Infinite deck or shoe-based persistence; rejected for MVP simplicity.

- **Decision**: Implement European Roulette with pockets 0-36 and standard bet resolution tables.
  - **Rationale**: The spec explicitly requires European wheel behavior and payout ratios.
  - **Alternatives considered**: American roulette; rejected because it introduces 00 and changes the house edge.

## Phase 1: Design

### Data Model Output

The feature already has a dedicated [data-model.md](data-model.md) describing:
- `SceneState` for Hub/Casino switching
- `WalletState` for persisted bankroll and daily bonus tracking
- `BlackjackRound` and `RouletteRound` for game settlement flows
- `CasinoMachine` and `RoomExit` for the visual interaction model

### Contract Output

Create concise contract docs under `specs/003-casino-room/contracts/` for:
- `game-module.contract.ts` — reuse of the existing module boundary for Blackjack and Roulette
- `wallet.contract.ts` — wallet persistence and settlement interface
- `room-navigation.contract.ts` — scene change and return-to-room callbacks

### Quickstart Output

Create [quickstart.md](quickstart.md) with:
- install/build/test commands from `package.json`
- manual verification steps for Hub -> Casino -> Hub navigation
- wallet reset and localStorage inspection notes
- smoke-test steps for Blackjack and Roulette launch/return flows

## Complexity Tracking

No constitution violations require justification.
