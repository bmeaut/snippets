# Implementation Plan: Blackjack Split

**Branch**: `004-blackjack-split` | **Date**: 2026-05-31 | **Spec**: [spec.md](spec.md)

## Summary

Add Blackjack Split support to the existing casino blackjack module by refactoring the round state to support multiple player hands, sequential hand resolution, and the split-ace exception rules. The first implementation slice keeps the UI unchanged while the shared game logic and tests move to the new structure.

## Technical Context

**Language/Version**: TypeScript 5.x with `strict: true`  
**Primary Dependencies**: React 18+, Vite, Vitest, browser `localStorage` wallet service  
**Storage**: Shared wallet state already persisted in `localStorage`  
**Testing**: Vitest unit tests under `tests/unit`  
**Target Platform**: Modern desktop browsers  
**Project Type**: Single-page web application with scene-based room navigation and modular game UIs  
**Performance Goals**: Keep turn progression deterministic and avoid blocking the main UI thread  
**Constraints**: Preserve the current blackjack module boundary, do not introduce split UI until the state model is ready, and keep wallet validation aligned with the existing casino wallet service  
**Scale/Scope**: One blackjack module, one shared wallet, and one new state shape for split rounds

## Constitution Check

*GATE: Must pass before implementation and re-check after the state refactor.*

### Principle I: Strict Type Safety
**Status**: ✅ PASS — `playerHands` and `activeHandIndex` can be modeled with explicit TypeScript interfaces.

### Principle II: Complete Module Isolation
**Status**: ✅ PASS — Split logic stays inside the blackjack module and uses the shared wallet through existing service boundaries.

### Principle III: Clean Code & Consistent Documentation
**Status**: ✅ PASS — The spec and implementation notes stay in English for code and in the repository’s existing documentation style.

### Principle IV: Application Stability Through Module Boundaries
**Status**: ✅ PASS — Refactoring the round state in game logic first keeps the UI work isolated for the next phase.

**Gate Result**: ✅ ALL GATES PASS — proceed with the state refactor.

## Project Structure

### Documentation

```text
specs/004-blackjack-split/
├── spec.md
├── plan.md
├── data-model.md
└── tasks.md
```

### Source Code Impact

```text
src/games/blackjack/
├── gameLogic.ts        # Split-ready round state and hand progression
├── BlackjackGame.tsx   # UI to be updated in later phases
└── index.tsx

tests/unit/
└── blackjackLogic.test.ts
```

**Structure Decision**: Keep the split state refactor in `gameLogic.ts` first so the module can evolve to multiple hands without immediately changing the UI rendering layer.

## Phase 0: Research

### Findings

- The current blackjack logic already owns the round state and payout rules, so it is the right place to introduce split-specific hand tracking.
- The shared wallet service can continue to validate the extra split wager.
- The new state shape should support the future UI refactor by exposing both the active hand index and the list of player hands.

### Decision Log

- **Decision**: Introduce `playerHands` and `activeHandIndex` in the core round state.
  - **Rationale**: Split rounds need first-class hand sequencing instead of a single mutable player hand.
  - **Alternatives considered**: Keeping a flat hand and bolting on split metadata; rejected because it makes sequential resolution harder to reason about.

- **Decision**: Keep the UI untouched in the first implementation slice.
  - **Rationale**: The user requested a core state refactor first, and decoupling the state change from the UI reduces risk.
  - **Alternatives considered**: Refactoring UI and state together; rejected because it would widen the change set unnecessarily.

## Phase 1: Design

### Data Model Output

See [data-model.md](data-model.md) for the split-specific round state, hand model, split eligibility rules, and payout edge cases.

### Task Output

See [tasks.md](tasks.md) for the implementation order and test plan.

## Complexity Tracking

No constitution violations require justification at this stage.
