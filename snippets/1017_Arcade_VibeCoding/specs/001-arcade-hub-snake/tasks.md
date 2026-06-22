---
description: "Task list for Arcade Hub Canvas RPG hub rewrite"
---

# Tasks: Arcade Hub Canvas RPG + Snake

**Input**: Design documents from `/specs/001-arcade-hub-snake/`  
**Branch**: `001-arcade-hub-snake` | **Date**: 2026-05-12

**Scope Note**: This task list focuses on the new top-down Canvas Hub only. The existing Snake logic and storage are intentionally reused and should remain unchanged.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are exact and executable

---

## Phase 1: Hub Scene Foundation

**Purpose**: Create the Canvas-based room, player avatar, and placeholder machine rendering.

- [x] T001 Create `src/hub/` folder structure for scene, entities, systems, rendering, input, and hooks
- [x] T002 Define hub scene types in `src/hub/entities/player.ts` and `src/hub/entities/machine.ts`
- [x] T003 [P] Define scene transition and prompt state in `src/hub/systems/interaction.ts`
- [x] T004 Implement `src/hub/scene/HubScene.tsx` as the Canvas scene root
- [x] T005 [P] Implement `src/hub/hooks/useHubResize.ts` for responsive canvas sizing
- [x] T006 [P] Implement `src/hub/rendering/drawHub.ts` with placeholder rectangle room, player, and machine rendering
- [x] T007 Implement `src/hub/input/useHubControls.ts` for WASD / arrow movement input
- [x] T008 Implement `src/hub/systems/collision.ts` for room bounds and machine proximity checks
- [x] T009 [P] Create `src/hub/ui/InteractionPrompt.tsx` for the `[E]` hint overlay
- [x] T010 Update `src/App.tsx` to switch between `HubScene` and `SnakeGame`

**Checkpoint**: A Canvas room renders, the player moves, and the scene can switch to Snake.

---

## Phase 2: Hub Movement & Interaction

**Purpose**: Make the player walk around the room and interact with the Snake machine.

**Independent Test**: Move character, approach machine, see `[E]`, press `E`, launch Snake.

- [x] T011 [US1] Add room boundary constraints so the player cannot leave the scene
- [x] T012 [P] [US1] Add simple placeholder collision boxes for the Snake machine
- [x] T013 [US1] Show the interaction prompt only when the player enters the machine range
- [x] T014 [P] [US1] Anchor the prompt above the machine with a clear readable offset
- [x] T015 [US1] Trigger the Snake scene when `E` is pressed while in range
- [x] T016 [US1] Keep the machine inactive when the player is out of range
- [x] T017 [US1] Restore the Hub scene cleanly after Snake exits
- [x] T018 [P] [US1] Preserve Snake module behavior and storage without changing the existing contracts

**Checkpoint**: The Hub behaves like a top-down room and launches Snake through interaction.

---

## Phase 3: Scene Polish & Responsiveness

**Purpose**: Make the Hub feel like a stable Canvas scene on different screen sizes.

- [x] T019 [P] Implement room scaling so the Canvas scene adapts to the viewport
- [x] T020 [P] Ensure player and machine rectangles remain legible at mobile widths
- [x] T021 [P] Add a simple color palette for floor, wall, player, machine, and prompt states
- [x] T022 [US1] Keep the `[E]` prompt visually distinct from the room background
- [x] T023 [P] Add keyboard focus handling so the Hub can be controlled without mouse input
- [x] T024 [P] Add frame-time or render-time instrumentation for the Hub Canvas scene

**Checkpoint**: The Canvas room is responsive, readable, and stable.

---

## Phase 4: Verification & Tests

**Purpose**: Cover movement, proximity, prompt, scene switching, and Hub/Snake boundary behavior.

- [x] T025 [P] Test: player movement respects room bounds (`src/hub/__tests__/movement.test.ts`)
- [x] T026 [P] Test: collision/proximity detects machine range correctly (`src/hub/__tests__/collision.test.ts`)
- [x] T027 [US1] Test: interaction prompt appears when the player approaches the Snake machine (`src/hub/__tests__/interaction.test.tsx`)
- [x] T028 [US1] Test: pressing `E` launches the Snake scene (`src/hub/__tests__/interaction.test.tsx`)
- [x] T029 [US1] Test: returning from Snake restores the Hub scene (`src/hub/__tests__/interaction.test.tsx`)
- [x] T030 [P] Test: Hub rendering remains stable on resize (`src/hub/__tests__/resize.test.tsx`)
- [x] T031 [P] Manual acceptance test: move around the room and reach the Snake machine
- [x] T032 Manual acceptance test: see the `[E]` prompt and launch Snake from the Hub
- [x] T033 [P] Manual acceptance test: return from Snake and continue moving in the Hub

**Checkpoint**: Hub interaction flow is verified end-to-end.

---

## Phase 5: Final Validation

**Purpose**: Ensure the pivot did not alter the existing Snake game and storage behavior.

- [x] T034 Verify Snake game launch still uses the existing module entry point
- [x] T035 [P] Verify high score storage remains unchanged and still loads correctly in Snake
- [x] T036 [P] Run the full build and focused tests for the Hub rewrite
- [x] T037 Review task list status and confirm only Hub rewrite work remains open

**Checkpoint**: The pivot is complete, and the Snake/storage boundary is preserved.

---

## Dependencies & Execution Order

### Critical Path

1. **Phase 1**: Hub scene foundation
2. **Phase 2**: Movement and interaction
3. **Phase 3**: Responsiveness and polish
4. **Phase 4**: Verification and tests
5. **Phase 5**: Final validation of Snake/storage preservation

### Parallelizable Groups

- Phase 1: T003, T005, T006, T009
- Phase 2: T012, T014, T018
- Phase 3: T019, T020, T021, T023, T024
- Phase 4: T025, T026, T030, T031, T033
- Phase 5: T035, T036

---

## Success Criteria Summary

- The Hub is now a top-down Canvas room instead of a card menu.
- The player can walk around with WASD or arrow keys.
- A Snake machine exists as a rectangle placeholder.
- `[E]` appears when the player is in range.
- Pressing `E` launches the existing Snake game.
- Snake logic and storage remain untouched.
