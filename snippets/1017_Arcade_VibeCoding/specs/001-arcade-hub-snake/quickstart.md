# Quick Start Guide: Arcade Hub MVP Development

**Date**: 2026-05-12 | **Feature**: Arcade Hub MVP with Snake Game  
**Audience**: Developers implementing the feature (Hungarian + English blend for docs/code balance)

---

## 🚀 Project Overview

Arcade Hub is a modular arcade game platform built with React, TypeScript, and Canvas. The MVP includes:
- **Hub Menu**: Visual game selection interface
- **Snake Game**: Classic Snake mechanics with scoring and high score tracking
- **Modularity**: Each game is completely isolated; failures don't crash the app

**Key Technologies**:
- React 18+ (UI components)
- TypeScript (strict mode)
- HTML5 Canvas (graphics)
- localStorage (score persistence)
- Vite (bundler)
- Vitest (tests)

---

## 📁 Project Structure Quick Ref

```
src/
├── main.tsx              # App entry point
├── App.tsx               # Root Hub component
├── components/           # Shared React components
│   ├── Hub.tsx
│   ├── GameCard.tsx
│   ├── GameView.tsx
│   └── ErrorBoundary.tsx
├── games/snake/          # Snake game module (isolated)
│   ├── index.ts          # Public export (game contract)
│   ├── components/       # React wrappers
│   ├── logic/            # Pure functions (physics, scoring)
│   ├── rendering/        # Canvas drawing
│   ├── input/            # Input handling
│   ├── hooks/            # Game-specific React hooks
│   ├── types/            # TypeScript types
│   └── __tests__/        # Unit tests
├── shared/               # Reusable utilities
│   ├── types/            # Global TypeScript types
│   ├── hooks/            # Generic React hooks
│   ├── utils/            # Utility functions
│   └── canvas/           # Canvas helper module
└── styles/               # CSS files (CSS modules)

specs/001-arcade-hub-snake/
├── spec.md               # User requirements & acceptance criteria
├── plan.md               # This implementation plan
├── research.md           # Technology decisions
├── data-model.md         # Entity models & state structures
├── contracts/            # Module interface contracts
└── quickstart.md         # This file
```

---

## 🎮 Key Concepts

### 1. **Hub (Main Menu)**

The Hub is the entry point—a React component showing available games as cards. Users click a card to load that game. Hub state:
- Current selected game ID (or null = showing menu)
- Game loading state
- Game error state (if module fails)

**Location**: `src/components/Hub.tsx`

**Key files**:
- `App.tsx` - Root component managing Hub vs. GameView toggle
- `Hub.tsx` - Menu UI
- `GameCard.tsx` - Individual game card component

### 2. **Snake Game Module**

Snake is an isolated module implementing the `GameModuleContract`. Everything Snake-specific lives in `src/games/snake/`.

**Game Loop**:
1. Input processing (keyboard/touch)
2. State update (physics, collision, scoring)
3. Canvas rendering
4. Repeat ~60 FPS

**Core files**:
- `logic/engine.ts` - Game loop orchestrator
- `logic/physics.ts` - Movement, collision detection
- `logic/scoring.ts` - Score calculation & high score
- `rendering/canvas.ts` - Draw to Canvas API
- `input/handler.ts` - Keyboard + touch input
- `hooks/useGameLoop.ts` - requestAnimationFrame wrapper

### 3. **Contracts (Module Boundaries)**

Games communicate with Hub **only** through well-defined contracts. This ensures isolation.

**Contract types** (in `specs/001-arcade-hub-snake/contracts/`):
- `game-module.contract.ts` - What Hub expects from every game
- `hub-api.contract.ts` - What games can call on Hub
- `storage.contract.ts` - High Score persistence interface

**Example**: When Snake game ends, it calls `hub.onGameOver(finalScore)` via HubAPI contract.

### 4. **State Management**

Uses React Context API (not Redux). Simpler for MVP.

- **Hub Context**: Selected game, loading state
- **Snake Context**: Board state, snake position, score, direction

Each game manages its own context locally → modularity.

### 5. **High Score Persistence**

High scores stored in browser `localStorage` with key: `game-{gameId}-highscore`.

**Flow**:
1. Player plays Snake → game ends
2. Snake module calls `hub.setHighScore("snake", finalScore)`
3. Hub updates localStorage
4. Next game load: HubAPI retrieves stored high score
5. Displayed on game-over screen

---

## 🛠️ Development Workflow

### Setup

```bash
# 1. Install dependencies
npm install

# 2. Run development server
npm run dev

# 3. Browser opens http://localhost:5173

# 4. Click "Snake" card → game loads
```

### Running Tests

```bash
# Unit tests (Vitest)
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

### Building for Production

```bash
npm run build

# Output in dist/
# Deploy dist/ to web server
```

### Linting & Formatting

```bash
# Check TypeScript
npx tsc --noEmit

# Lint code
npm run lint

# Format code (Prettier)
npm run format
```

---

## 🎯 Key Implementation Guidelines

### TypeScript Strict Mode

**REQUIRED**: All game logic must have explicit types.

❌ **Bad**:
```typescript
const state: any = { score: 0 }; // NO!
```

✅ **Good**:
```typescript
interface GameState {
  score: number;
  snakeBody: Coordinate[];
}
const state: GameState = { score: 0, snakeBody: [] };
```

### Pure Functions for Game Logic

Physics, collision detection, scoring MUST be pure (no side effects).

❌ **Bad**:
```typescript
// In physics.ts
let speed = 5;
const updateSnake = () => {
  speed += 0.1; // Side effect!
  // ...
};
```

✅ **Good**:
```typescript
interface GameState {
  speed: number;
  // ...
}
const updateSnake = (state: GameState, deltaTime: number): GameState => {
  const newSpeed = calculateNewSpeed(state.applesEaten);
  return { ...state, speed: newSpeed };
};
```

### Module Isolation

Snake module is completely independent. Hub doesn't know Snake internals.

**Module exports** (via `src/games/snake/index.ts`):
```typescript
export const snakeGameModule: GameModuleContract = {
  id: "snake",
  name: "Snake",
  // ... other contract fields
  component: SnakeGame, // React component
  initialize: async (config) => { /* ... */ },
  destroy: async () => { /* ... */ },
  // ...
};
```

**Hub only knows**:
- Game ID, name, icon
- Component to render
- initialize() / destroy() lifecycle

**Hub doesn't know**:
- How physics works
- How rendering happens
- Internal game state

### Error Handling

Hub wraps game modules in ErrorBoundary. If Snake crashes, user sees error but can return to menu.

```typescript
// In GameView.tsx
<ErrorBoundary fallback={<GameError />}>
  <SnakeGame config={config} />
</ErrorBoundary>
```

---

## 📊 Game State Flow

### Initialization

```
Hub
  ↓ User clicks Snake card
  ↓ Hub.selectedGameId = "snake"
GameView (renders Snake component)
  ↓ SnakeGame component mounts
  ↓ calls snakeGameModule.initialize(config)
  ↓ Sets up Canvas, input handlers, game loop
GAME_ACTIVE
  ↓ requestAnimationFrame loop starts
  ↓ Each frame: input → update → render
```

### Game Over

```
GAME_ACTIVE
  ↓ Collision detected
  ↓ calls hub.onGameOver(finalScore)
Hub
  ↓ Updates High Score if needed
  ↓ Shows game-over screen with score & restart button
USER clicks Restart
  ↓ Game reinitializes
GAME_ACTIVE again
```

### Return to Menu

```
GAME_ACTIVE
  ↓ User clicks "Back to Menu" button
  ↓ calls hub.onBackToMenu()
Hub
  ↓ calls snakeGameModule.destroy()
  ↓ Cleans up resources (event listeners, timers, Canvas)
  ↓ Resets selectedGameId = null
Hub (showing menu again)
```

---

## 🧪 Testing Strategy

### Unit Tests (Physics & Logic)

Test pure functions without React:

```typescript
// physics.test.ts
describe("Snake Physics", () => {
  it("should move snake forward", () => {
    const state = { snakeBody: [[5, 5]], direction: "UP" };
    const newState = moveSnake(state);
    expect(newState.snakeBody[0]).toEqual([5, 4]); // Moved up
  });

  it("should detect wall collision", () => {
    const state = { snakeBody: [[0, 0]] }; // At boundary
    const collision = checkCollision(state);
    expect(collision.hasCollision).toBe(true);
    expect(collision.type).toBe("wall");
  });
});
```

### Component Tests (React UI)

Test Hub and GameView rendering:

```typescript
// Hub.test.tsx
describe("Hub Component", () => {
  it("should render game cards", () => {
    const { getByText } = render(<Hub />);
    expect(getByText("Snake")).toBeInTheDocument();
  });

  it("should load game when card clicked", () => {
    const { getByRole } = render(<Hub />);
    fireEvent.click(getByRole("button", { name: /play/i }));
    // Verify SnakeGame component renders
  });
});
```

### Integration Tests (Future)

Full user journey with Playwright:

```typescript
// arcade-hub.e2e.ts (future)
test("User plays Snake and returns to menu", async ({ page }) => {
  await page.goto("http://localhost:5173");
  await page.click('text=Snake');
  // Game loads
  await page.press("body", "ArrowUp");
  // ... user plays ...
  await page.click('text=Back to Menu');
  // Menu shows again
});
```

---

## 🐛 Debugging Tips

### Check Game State

React DevTools:
1. Open DevTools (F12)
2. Go to React tab
3. Find `SnakeGame` component
4. Inspect props and state

### Monitor Canvas Rendering

Add performance monitoring:

```typescript
// In rendering/canvas.ts
const startTime = performance.now();
drawGameBoard(canvas, gameState);
const elapsed = performance.now() - startTime;
if (elapsed > 16) {
  console.warn(`Slow frame: ${elapsed.toFixed(2)}ms (target: 16ms)`);
}
```

### Check localStorage

Browser console:
```javascript
localStorage.getItem("game-snake-highscore")
// Output: '{"gameId":"snake","highScore":42,"lastUpdated":1234567890,"sessionCount":3}'
```

### Test Input Handling

Add debug logging:
```typescript
// In input/handler.ts
const handleKeyDown = (event: KeyboardEvent) => {
  console.log("Key pressed:", event.key);
  const direction = keyToDirection(event.key);
  console.log("Direction queued:", direction);
  // ...
};
```

---

## 📚 Additional Resources

### Files to Read First

1. **specs/001-arcade-hub-snake/spec.md** — User requirements
2. **specs/001-arcade-hub-snake/data-model.md** — Entity structures
3. **specs/001-arcade-hub-snake/contracts/game-module.contract.ts** — What games export

### Architecture Reference

- **Modularity**: See `src/games/snake/index.ts` (module export)
- **State Management**: See `src/shared/hooks/useGameLoop.ts` (animation frame hook)
- **Error Handling**: See `src/components/ErrorBoundary.tsx`
- **Canvas Rendering**: See `src/games/snake/rendering/canvas.ts`

### Constitution (Project Principles)

See `.specify/memory/constitution.md` for overarching project principles:
- Strict Type Safety (TypeScript strict mode)
- Module Isolation (games are black boxes)
- Multimedia Excellence (Canvas + Howler.js in future)
- Clean Code (English code, Hungarian docs)
- Stability Through Boundaries (ErrorBoundary pattern)

---

## ✅ Acceptance Criteria Checklist

As you implement, verify:

- [ ] Hub menu displays game cards with Play button
- [ ] Clicking Play button loads Snake game
- [ ] Snake game responds to keyboard input (arrow keys)
- [ ] Snake eats apples and grows
- [ ] Score updates correctly (1 point = 1 apple)
- [ ] Speed increases after 5 apples eaten
- [ ] Collision with wall ends game
- [ ] Collision with self ends game
- [ ] Game-over screen shows final score
- [ ] High Score persists between sessions
- [ ] "Back to Menu" button works from game
- [ ] "Restart" button works from end-game screen
- [ ] Touch input works on mobile (if testing on device)
- [ ] App < 2 seconds to load
- [ ] Game runs at 30+ FPS (check DevTools Performance)
- [ ] No `any` types in game logic
- [ ] All public functions have JSDoc comments
- [ ] TypeScript strict mode passes (`npx tsc --noEmit`)

---

## 🎉 Next Steps

1. **Setup**: Follow Setup section above
2. **Explore**: Navigate src/ folder, read component files
3. **Run Tests**: `npm run test` to verify test infrastructure works
4. **Implement**: Begin tasks from `/speckit.tasks` command
5. **Test**: Add tests as you implement features
6. **Commit**: Regular Git commits; integrate with Git hooks if needed

---

**Questions?** Refer to architecture overview or contact the project lead.

**Bug Reports?** Create issue with reproduction steps.

**Pull Requests?** Ensure TypeScript passes, tests pass, and code follows style guide.

Happy coding! 🎮