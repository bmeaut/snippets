import { describe, expect, it } from 'vitest';
import {
  GRID_SIZE,
  createInitialSnakeState,
  createRandomPosition,
  moveSnake,
  nextTickDelay,
  updateDirection,
} from '../../src/games/snake/snakeLogic';

describe('snakeLogic', () => {
  it('moves the snake one cell in the active direction', () => {
    const state = createInitialSnakeState(0);
    expect(moveSnake(state).snake[0]).toEqual({ x: 11, y: 10 });
  });

  it('increments score when the snake eats an apple', () => {
    const state = { ...createInitialSnakeState(0), apple: { x: 11, y: 10 } };
    const next = moveSnake(state);
    expect(next.score).toBe(1);
    expect(next.snake).toHaveLength(4);
    expect(next.applesEaten).toBe(1);
  });

  it('wraps around the right wall (portal — no game over)', () => {
    const state = {
      ...createInitialSnakeState(0),
      snake: [{ x: GRID_SIZE - 1, y: 5 }, { x: GRID_SIZE - 2, y: 5 }],
      direction: 'right' as const,
      pendingDirection: 'right' as const,
      apple: { x: 0, y: 0 },
    };
    const next = moveSnake(state);
    expect(next.gameOver).toBe(false);
    expect(next.snake[0]).toEqual({ x: 0, y: 5 });
  });

  it('wraps around the top wall (portal)', () => {
    const state = {
      ...createInitialSnakeState(0),
      snake: [{ x: 5, y: 0 }, { x: 5, y: 1 }],
      direction: 'up' as const,
      pendingDirection: 'up' as const,
      apple: { x: 0, y: 0 },
    };
    const next = moveSnake(state);
    expect(next.gameOver).toBe(false);
    expect(next.snake[0]).toEqual({ x: 5, y: GRID_SIZE - 1 });
  });

  it('game over when hitting a stone', () => {
    const state = {
      ...createInitialSnakeState(0),
      snake: [{ x: 10, y: 10 }, { x: 9, y: 10 }],
      direction: 'right' as const,
      pendingDirection: 'right' as const,
      apple: { x: 0, y: 0 },
      stones: [{ x: 11, y: 10 }],
    };
    expect(moveSnake(state).gameOver).toBe(true);
  });

  it('game over when hitting self', () => {
    const state = {
      ...createInitialSnakeState(0),
      snake: [
        { x: 5, y: 5 },
        { x: 5, y: 6 },
        { x: 6, y: 6 },
        { x: 6, y: 5 },
        { x: 6, y: 4 },
      ],
      direction: 'right' as const,
      pendingDirection: 'right' as const,
      apple: { x: 0, y: 0 },
    };
    expect(moveSnake(state).gameOver).toBe(true);
  });

  it('allows moving into tail space when not eating', () => {
    const state = {
      ...createInitialSnakeState(0),
      snake: [
        { x: 10, y: 10 },
        { x: 9, y: 10 },
        { x: 8, y: 10 },
        { x: 8, y: 11 },
      ],
      direction: 'up' as const,
      pendingDirection: 'up' as const,
      apple: { x: 0, y: 0 },
    };
    const next = moveSnake(state);
    expect(next.gameOver).toBe(false);
    expect(next.snake[0]).toEqual({ x: 10, y: 9 });
  });

  it('golden apple gives 3 points', () => {
    const state = {
      ...createInitialSnakeState(0),
      snake: [{ x: 5, y: 5 }, { x: 4, y: 5 }],
      direction: 'right' as const,
      pendingDirection: 'right' as const,
      apple: { x: 0, y: 0 },
      goldenApple: { pos: { x: 6, y: 5 }, spawnedAt: Date.now() },
    };
    const next = moveSnake(state);
    expect(next.score).toBe(3);
    expect(next.goldenApple).toBeNull();
  });

  it('blue apple activates slow and gives 1 point', () => {
    const now = Date.now();
    const state = {
      ...createInitialSnakeState(0),
      snake: [{ x: 5, y: 5 }, { x: 4, y: 5 }],
      direction: 'right' as const,
      pendingDirection: 'right' as const,
      apple: { x: 0, y: 0 },
      blueApple: { pos: { x: 6, y: 5 }, spawnedAt: now },
    };
    const next = moveSnake(state, now);
    expect(next.score).toBe(1);
    expect(next.blueApple).toBeNull();
    expect(next.slowUntil).not.toBeNull();
    expect(next.slowUntil).toBeGreaterThan(now);
  });

  it('golden apple expires after TTL', () => {
    const state = {
      ...createInitialSnakeState(0),
      snake: [{ x: 5, y: 5 }, { x: 4, y: 5 }],
      direction: 'right' as const,
      pendingDirection: 'right' as const,
      apple: { x: 0, y: 0 },
      goldenApple: { pos: { x: 2, y: 2 }, spawnedAt: Date.now() - 7000 },
    };
    const next = moveSnake(state);
    expect(next.goldenApple).toBeNull();
  });

  it('stone spawns at score 8', () => {
    // Build state just before score 8
    const state = {
      ...createInitialSnakeState(0),
      score: 7,
      applesEaten: 7,
      snake: [{ x: 5, y: 5 }, { x: 4, y: 5 }],
      direction: 'right' as const,
      pendingDirection: 'right' as const,
      apple: { x: 6, y: 5 },
    };
    const next = moveSnake(state);
    expect(next.score).toBe(8);
    expect(next.stones).toHaveLength(1);
  });

  it('slow tick delay is doubled', () => {
    const now = Date.now();
    const base = nextTickDelay(0, null);
    const slow = nextTickDelay(0, now + 3000);
    expect(slow).toBe(base * 2);
  });

  it('tick delay decreases with score and stays above minimum', () => {
    expect(nextTickDelay(0)).toBeGreaterThan(nextTickDelay(5));
    expect(nextTickDelay(50)).toBeGreaterThanOrEqual(75);
  });

  it('keeps direction when reverse input buffered', () => {
    const state = {
      ...createInitialSnakeState(0),
      direction: 'right' as const,
      pendingDirection: 'left' as const,
    };
    expect(updateDirection(state).direction).toBe('right');
  });

  it('createRandomPosition avoids excluded cells', () => {
    const exclude = [{ x: 0, y: 0 }];
    for (let i = 0; i < 20; i++) {
      const pos = createRandomPosition(exclude);
      expect(pos).not.toEqual({ x: 0, y: 0 });
    }
  });
});
