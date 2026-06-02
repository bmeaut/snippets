# Research & Technical Decisions: Arcade Hub MVP with Snake Game

**Date**: 2026-05-12 | **Feature**: Arcade Hub MVP with Snake Game  
**Purpose**: Document technology choices, architecture patterns, and design decisions made during planning phase.

## Technology Stack Decisions

### 1. React 18+ with TypeScript (strict: true)

**Decision**: Use React 18+ for component-based UI, TypeScript with strict mode enforcement.

**Rationale**:
- React is ideal for SPA with dynamic game card switching and UI state management.
- TypeScript strict mode prevents runtime type errors—critical for game logic correctness (collision detection, scoring).
- Vite provides fast bundling and development experience.

**Alternatives Considered**:
- Vue 3 / Svelte: Both excellent but React ecosystem is wider for game-adjacent libraries and community knowledge.
- Plain JavaScript: Rejected; constitution mandates TypeScript strict mode for type safety.

**Implementation Notes**:
- `tsconfig.json` MUST have `strict: true` and `noImplicitAny: true`.
- Game logic (physics, scoring) MUST be pure functions with explicit types, not React components.

---

### 2. HTML5 Canvas 2D API (No WebGL for MVP)

**Decision**: Use native HTML5 Canvas 2D API for Snake game rendering.

**Rationale**:
- Simple 2D grid-based rendering perfect for Snake mechanics.
- No external graphics library needed; reduces dependencies and bundle size.
- Sufficient for 30+ FPS target; grid-based rendering is inherently performant.
- Canvas API is standard across all modern browsers (desktop + mobile).

**Alternatives Considered**:
- Three.js / Babylon.js: Overkill for 2D grid game; unnecessary overhead.
- Pixi.js: Good option but adds dependency; Canvas 2D sufficient.
- SVG rendering: Slower for frequent updates; Canvas better for animation frames.

**Implementation Notes**:
- Dedicated `src/shared/canvas/` module for reusable Canvas utilities.
- Separate `rendering/` folder in Snake module for game-specific drawing logic.
- Frame-by-frame updates via `requestAnimationFrame()` to maintain 60 FPS target.

---

### 3. Browser localStorage for High Score Persistence

**Decision**: Use browser `localStorage` API to persist High Score between sessions.

**Rationale**:
- Simple, zero-infrastructure persistence for MVP.
- No server needed; works offline.
- Sufficient for single-user browser-based game.

**Alternatives Considered**:
- IndexedDB: Overkill for single-value storage; localStorage simpler.
- Server-side database: Out of scope for MVP; added complexity.
- SessionStorage: Loses data on browser close; localStorage persists longer.

**Implementation Notes**:
- Storage key: `snake-high-score` (prefixed to allow multiple games).
- Encapsulate in `useHighScore()` hook for reusability across games.
- Error handling: If localStorage unavailable (private browsing), gracefully fall back to session-only score.

---

### 4. React Context for State Management

**Decision**: Use React Context API for Hub state (selected game) and game state (Snake board, score).

**Rationale**:
- Lightweight; no need for Redux complexity for MVP.
- Built into React; no additional dependencies.
- Each game module manages its own context locally, supporting isolation principle.

**Alternatives Considered**:
- Redux / Recoil: Over-engineered for MVP; added bundle size and mental overhead.
- Prop drilling: Acceptable but Context cleaner for game state across Hub and GameView layers.

**Implementation Notes**:
- Hub context: Current selected game, game loading state.
- Snake context: Game board state, snake position, apple, score, direction queue.
- Each game module exports its own provider; Hub remains agnostic.

---

### 5. Vite + TypeScript Configuration

**Decision**: Vite as bundler with TypeScript strict mode.

**Rationale**:
- Vite provides extremely fast HMR (hot module replacement) for development.
- Native TypeScript support with no additional loaders.
- Optimized production bundles via Rollup.
- Constitution specifies Vite; aligns with project standards.

**Implementation Notes**:
- `vite.config.ts`: Configure alias paths for clean imports (`@/components`, `@/games/snake`).
- `tsconfig.json`: Enforce `strict: true`, `noImplicitAny: true`, `esModuleInterop: true`.
- Build output: `dist/` folder, single entry point `index.html`.

---

### 6. Vitest for Unit Testing

**Decision**: Use Vitest for unit testing game logic.

**Rationale**:
- Vitest is Vite-native; runs in the same Vite context (same config, imports).
- Fast execution; excellent for TDD workflows.
- Compatible with React Testing Library for component tests.

**Alternatives Considered**:
- Jest: Heavier setup; slower than Vitest. Vitest is modern equivalent.
- Mocha: Less integrated with TypeScript; Vitest better.

**Implementation Notes**:
- Unit tests for: physics engine, collision detection, scoring logic, input handling.
- Component tests (React Testing Library) for: GameCard rendering, game transitions, score display.
- Test files co-located: `src/games/snake/__tests__/` folder.

---

### 7. Keyboard + Touch Input Handling

**Decision**: Unified input handler supporting both keyboard and pointer/touch events.

**Rationale**:
- Spec requires desktop (keyboard: arrow keys, WASD) and mobile (touch/pointer) support.
- Single input abstraction layer (Direction type) for game logic agnostic to input source.

**Alternatives Considered**:
- Separate keyboard and touch handlers: Duplicated code; harder to maintain.
- Game controller API: Out of scope; keyboard + touch sufficient.

**Implementation Notes**:
- `useInput()` hook: Listens to `keydown`, `pointerdown`, `touchstart` events.
- Maps physical input → Direction enum (UP, DOWN, LEFT, RIGHT).
- Handles "no reverse direction" rule: If heading right, LEFT input is ignored.

---

### 8. Module Isolation with React.ErrorBoundary

**Decision**: Use React.ErrorBoundary to catch Snake module errors and prevent Hub crash.

**Rationale**:
- Constitution Principle V mandates stability through module boundaries.
- ErrorBoundary catches React render errors in game component.
- Allows user to return to Hub if game encounters error.

**Alternatives Considered**:
- Manual try-catch: Doesn't catch React render errors; less robust.
- Suspense boundary: For async loading, but ErrorBoundary primary for error isolation.

**Implementation Notes**:
- ErrorBoundary wraps game module in `GameView.tsx`.
- Fallback UI: "Game Error" message with "Return to Hub" button.
- Error logging: Log to console or external service (future phase).

---

### 9. Responsive Design Strategy (Mobile-First)

**Decision**: CSS media queries + flexible grid layout for responsive UI.

**Rationale**:
- Spec requires 320px–4K support.
- Canvas playfield can be percentage-based (e.g., 80% of viewport width).
- Hub cards adapt from single column (mobile) to multi-column (desktop).

**Alternatives Considered**:
- Tailwind CSS: Valid option; can be added later if needed.
- CSS-in-JS (styled-components): Adds dependency; CSS modules sufficient for MVP.

**Implementation Notes**:
- CSS modules for component scoping: `Hub.module.css`, `games.module.css`.
- Breakpoints: 320px (mobile), 768px (tablet), 1024px (desktop).
- Canvas size: responsive calculation based on container width.

---

### 10. No Audio for MVP (Deferred to Phase 2)

**Decision**: Exclude audio implementation from MVP; plan infrastructure for Phase 2.

**Rationale**:
- Spec marks audio as "Out of Scope" for MVP.
- Reduces initial complexity; focus on core gameplay.
- Constitution specifies Howler.js; can be integrated in Phase 2 via dedicated audio module.

**Alternatives Considered**:
- Include basic sound effects: Would add implementation time; can be added incrementally.

**Implementation Notes**:
- Reserve `src/shared/audio/` folder structure for future Howler.js integration.
- Audio-related types and interfaces documented in contracts (Phase 1 preparation).

---

## Edge Case Resolutions

### 1. Snake Speed Increase Limits

**Decision**: Linear speed increase until frame cap of 60 FPS is reached.

**Logic**:
- Base speed: 5 grid cells per second (200ms per cell movement).
- After each 5 apples eaten: Increase speed by ~15% (capped at 60 FPS = ~16ms frame time).
- Speed formula: `baseSpeed + (applesEaten / 5) * 15%` with frame time floor.

**Testing**: Unit test to verify speed doesn't exceed frame time budget.

### 2. Input Buffer During Fast Movement

**Decision**: Use direction queue (max 2 entries) to smooth rapid consecutive inputs.

**Example**:
- Player heading RIGHT, presses UP then LEFT in quick succession.
- Queue stores [UP, LEFT]; next two frames execute both without overwrite.
- Prevents "queued" opposite direction (RIGHT → LEFT fails; dropped).

**Implementation**: `useInput()` hook maintains direction queue; physics engine dequeues on each frame.

### 3. High Score Edge Cases

**Decision**:
- First game: High Score = current score (no prior data).
- Subsequent games: High Score = max(current, previous high score).
- If localStorage unavailable: High Score remains session-only (visible but not persisted).

**Testing**: Unit test for localStorage error scenario.

---

## Performance Targets & Validation

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Hub load time | <2s (3G) | Lighthouse test |
| Snake frame rate | ≥30 FPS | Frame time monitoring hook |
| Frame time | ≤16ms (60 FPS) | Performance.now() measurements |
| Canvas render | <14ms per frame | Profiler in DevTools |
| Input latency | <50ms | Input handler timestamp + render time |
| Bundle size | <500 KB (gzipped) | Vite build analysis |

---

## Summary: No NEEDS CLARIFICATION Items

✅ All technology decisions finalized. Spec is complete; no blockers for Phase 1 design.

**Decisions Finalized**:
1. React 18 + TypeScript strict ✅
2. HTML5 Canvas 2D ✅
3. localStorage for persistence ✅
4. React Context state management ✅
5. Vite + Vitest ✅
6. Unified keyboard + touch input ✅
7. ErrorBoundary for isolation ✅
8. Responsive CSS ✅
9. Audio deferred ✅
10. Performance targets defined ✅

**Next**: Generate data-model.md and contracts/ (Phase 1).