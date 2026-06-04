# Implementation Plan: Arcade Hub MVP with Snake Game

**Branch**: `001-arcade-hub-snake` | **Date**: 2026-05-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-arcade-hub-snake/spec.md`

## Summary

Arcade Hub is now a top-down, 2D Canvas game room instead of a card-based menu. The player walks around the room with WASD or arrow keys, sees placeholder rectangle machines, and presses `E` near the Snake cabinet to launch the existing Snake module. The Snake game, its scoring, and storage remain unchanged; the pivot only rewrites the Hub scene and its interaction model. The architecture still emphasizes strict TypeScript typing, module isolation, and a stable scene boundary between Hub and Snake.

## Technical Context

**Language/Version**: TypeScript 5.0+ with `strict: true`, React 18.2+  
**Primary Dependencies**: 
- React 18+ (UI components)
- Vite (bundler)
- TypeScript (strict mode enforcement)
- HTML5 Canvas API (2D graphics rendering)
- localStorage API (High Score persistence)

**Storage**: Browser localStorage for Snake High Score persistence (unchanged)  
**Testing**: Vitest (unit tests), React Testing Library or DOM-based component tests, optionally Playwright for scene transitions  
**Target Platform**: Web browsers (desktop first, mobile-safe)  
**Project Type**: Single-page web application with Canvas scenes (React shell + game scenes)  
**Performance Goals**: 
- Hub Canvas scene: smooth 60 FPS target
- Snake game: ≥30 FPS sustained on standard hardware
- Frame time: ≤16ms per frame where possible
- Responsive: room and overlay scale from 320px to desktop widths

**Constraints**: 
- Keyboard input (WASD or arrow keys) for Hub movement
- `E` key launches Snake when the player is in range
- Placeholder rectangles only; no external art assets in the MVP
- Snake logic and storage remain untouched by the Hub pivot

**Scale/Scope**: 
- MVP: Canvas Hub scene + existing Snake module launch
- One playable room with one interactive machine in the first version
- Future: additional machines, NPCs, and room decorations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Strict Type Safety (TypeScript)  
**Status**: ✅ **PASS** — Spec requires TypeScript strict mode; all game logic will have explicit types, no `any` in mechanics.

### Principle II: Complete Module Isolation  
**Status**: ✅ **PASS** — Snake module is explicitly isolated; Hub loads games via contract interface; failure in Snake does not crash Hub.

### Principle III: Multimedia Excellence  
**Status**: ✅ **PASS** — HTML5 Canvas API used for graphics. Audio (Howler.js) deferred to Phase 2; MVP focuses on visual rendering.

### Principle IV: Clean Code & Consistent Documentation  
**Status**: ✅ **PASS** — Code in English (variables, functions, types), all specs and comments in Hungarian. JSDoc comments required for game module APIs.

### Principle V: Application Stability Through Module Boundaries  
**Status**: ✅ **PASS** — Hub uses React.ErrorBoundary; Snake module exports contract; invalid game states caught at boundary before execution.

**Gate Result**: ✅ **ALL GATES PASS** — No violations. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-arcade-hub-snake/
├── plan.md              # This file (implementation planning)
├── research.md          # Phase 0 output (technology decisions, architecture patterns)
├── data-model.md        # Phase 1 output (entities, state models, APIs)
├── quickstart.md        # Phase 1 output (developer quick-start guide)
├── contracts/           # Phase 1 output (module contracts and interfaces)
│   ├── game-module.contract.ts    # Game module interface contract
│   ├── hub-api.contract.ts        # Hub API contract
│   └── storage.contract.ts        # High Score storage contract
├── spec.md              # Feature specification (user stories, requirements)
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (React + TypeScript web app structure)

```text
src/
├── main.tsx                         # Application entry point
├── App.tsx                          # Scene switch between Hub and Snake
├── index.css                        # Global styles and scene shell layout
│
├── hub/
│   ├── scene/
│   │   └── HubScene.tsx             # Canvas-based top-down room
│   ├── entities/
│   │   ├── player.ts                # Player avatar state and movement
│   │   └── machine.ts               # Arcade machine placement and prompts
│   ├── systems/
│   │   ├── collision.ts             # Room bounds and proximity checks
│   │   └── interaction.ts           # E prompt and launch flow
│   ├── rendering/
│   │   └── drawHub.ts               # Placeholder rectangle rendering
│   ├── input/
│   │   └── useHubControls.ts        # WASD / arrow movement input
│   ├── hooks/
│   │   └── useHubResize.ts          # Responsive canvas sizing
│   └── __tests__/
│       ├── collision.test.ts
│       ├── interaction.test.ts
│       └── movement.test.tsx
│
├── games/
│   └── snake/                       # Existing Snake module (unchanged)
│       ├── SnakeGame.tsx
│       ├── snakeLogic.ts
│       └── index.ts
│
├── components/
│   └── ErrorBoundary.tsx            # Scene-level error isolation
│
└── storage.ts                       # High score persistence (unchanged)

tests/
└── unit/                            # Hub + integration smoke tests

public/
└── index.html                       # HTML entry point

package.json                         # Dependencies, build scripts
tsconfig.json                        # TypeScript configuration (strict: true)
vite.config.ts                       # Vite configuration
vitest.config.ts                     # Vitest test runner config
.prettierrc                          # Code formatting
.eslintrc.json                       # Linting rules
```

**Structure Decision**: Web application with scene-based Canvas Hub. The Hub lives in `src/hub/` as a top-down room, while the existing Snake module remains in `src/games/snake/` unchanged. The app shell only switches scenes and isolates failures at the boundary.

## Next Steps: Phase 0 & Phase 1

**Phase 0**: Research already complete for the pivot—no open clarifications.  
**Phase 1**: Keep the Snake contract and storage unchanged; design the Hub scene details in `data-model.md`.  
**Phase 2**: Generate a fresh `tasks.md` focused on the Canvas Hub rewrite and the Snake launch interaction.
