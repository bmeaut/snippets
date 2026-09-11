import type { Coordinate, Direction, SnakeState } from '../../types';

export const GRID_SIZE = 20;
export const CELL_SIZE = 24;
export const SPEED_STEP = 0.06;
export const MIN_TICK_MS = 75;
export const MAX_STONES = 12;
export const GOLDEN_APPLE_INTERVAL = 7;
export const BLUE_APPLE_INTERVAL = 5;
export const GOLDEN_APPLE_TTL = 6000;
export const BLUE_APPLE_TTL = 8000;
export const SLOW_DURATION = 3000;

export const createRandomPosition = (exclude: Coordinate[]): Coordinate | null => {
  for (let i = 0; i < 200; i++) {
    const pos: Coordinate = {
      x: Math.floor(Math.random() * GRID_SIZE),
      y: Math.floor(Math.random() * GRID_SIZE),
    };
    if (!exclude.some((e) => e.x === pos.x && e.y === pos.y)) return pos;
  }
  return null;
};

export const createRandomApple = (snake: Coordinate[]): Coordinate =>
  createRandomPosition(snake) ?? { x: 0, y: 0 };

export const createInitialSnakeState = (highScore: number): SnakeState => ({
  snake: [
    { x: 10, y: 10 },
    { x: 9, y: 10 },
    { x: 8, y: 10 },
  ],
  apple: { x: 14, y: 10 },
  direction: 'right',
  pendingDirection: 'right',
  score: 0,
  highScore,
  gameOver: false,
  stones: [],
  goldenApple: null,
  blueApple: null,
  slowUntil: null,
  applesEaten: 0,
});

const isReverse = (current: Direction, next: Direction): boolean =>
  (current === 'up' && next === 'down') ||
  (current === 'down' && next === 'up') ||
  (current === 'left' && next === 'right') ||
  (current === 'right' && next === 'left');

export const updateDirection = (state: SnakeState): SnakeState => {
  if (isReverse(state.direction, state.pendingDirection)) return state;
  return { ...state, direction: state.pendingDirection };
};

export const moveSnake = (state: SnakeState, now = Date.now()): SnakeState => {
  if (state.gameOver) return state;

  const head = state.snake[0];
  const dx = state.direction === 'right' ? 1 : state.direction === 'left' ? -1 : 0;
  const dy = state.direction === 'down' ? 1 : state.direction === 'up' ? -1 : 0;

  // Portal wrap — no wall death
  const nextHead: Coordinate = {
    x: ((head.x + dx) + GRID_SIZE) % GRID_SIZE,
    y: ((head.y + dy) + GRID_SIZE) % GRID_SIZE,
  };

  const ateRegular = nextHead.x === state.apple.x && nextHead.y === state.apple.y;
  const ateGolden =
    state.goldenApple !== null &&
    nextHead.x === state.goldenApple.pos.x &&
    nextHead.y === state.goldenApple.pos.y;
  const ateBlue =
    state.blueApple !== null &&
    nextHead.x === state.blueApple.pos.x &&
    nextHead.y === state.blueApple.pos.y;
  const ateAny = ateRegular || ateGolden || ateBlue;

  const bodyToCheck = ateAny ? state.snake : state.snake.slice(0, -1);
  const hitsSelf = bodyToCheck.some((s) => s.x === nextHead.x && s.y === nextHead.y);
  const hitsStone = state.stones.some((s) => s.x === nextHead.x && s.y === nextHead.y);

  if (hitsSelf || hitsStone) return { ...state, gameOver: true };

  const newSnake = [nextHead, ...state.snake];
  if (!ateAny) newSnake.pop();

  let score = state.score;
  let applesEaten = state.applesEaten;
  if (ateRegular) { score += 1; applesEaten += 1; }
  if (ateGolden) score += 3;
  if (ateBlue) score += 1;
  const highScore = Math.max(state.highScore, score);

  // Regular apple respawn
  const baseExclude: Coordinate[] = [...newSnake, ...state.stones];
  const newApple = ateRegular
    ? (createRandomPosition(baseExclude) ?? state.apple)
    : state.apple;

  // Golden apple — timeout and eating
  let goldenApple = state.goldenApple;
  if (ateGolden) {
    goldenApple = null;
  } else if (goldenApple && now - goldenApple.spawnedAt > GOLDEN_APPLE_TTL) {
    goldenApple = null;
  }
  if (!goldenApple && ateRegular && applesEaten > 0 && applesEaten % GOLDEN_APPLE_INTERVAL === 0) {
    const pos = createRandomPosition([...baseExclude, newApple]);
    if (pos) goldenApple = { pos, spawnedAt: now };
  }

  // Blue apple — timeout, eating, slow
  let blueApple = state.blueApple;
  let slowUntil = state.slowUntil;
  if (ateBlue) {
    blueApple = null;
    slowUntil = now + SLOW_DURATION;
  } else if (blueApple && now - blueApple.spawnedAt > BLUE_APPLE_TTL) {
    blueApple = null;
  }
  if (!blueApple && ateRegular && applesEaten > 0 && applesEaten % BLUE_APPLE_INTERVAL === 0) {
    const pos = createRandomPosition([
      ...baseExclude,
      newApple,
      ...(goldenApple ? [goldenApple.pos] : []),
    ]);
    if (pos) blueApple = { pos, spawnedAt: now };
  }
  if (slowUntil !== null && now > slowUntil) slowUntil = null;

  // Stone spawn
  let stones = state.stones;
  if (ateRegular && score >= 8 && (score - 8) % 4 === 0 && stones.length < MAX_STONES) {
    const stonePos = createRandomPosition([
      ...baseExclude,
      newApple,
      ...(goldenApple ? [goldenApple.pos] : []),
      ...(blueApple ? [blueApple.pos] : []),
    ]);
    if (stonePos) stones = [...stones, stonePos];
  }

  return {
    ...state,
    snake: newSnake,
    apple: newApple,
    score,
    highScore,
    applesEaten,
    goldenApple,
    blueApple,
    slowUntil,
    stones,
  };
};

export const nextTickDelay = (score: number, slowUntil: number | null = null): number => {
  const speedBonus = Math.floor(score / 5) * SPEED_STEP;
  const ratio = Math.min(0.45, speedBonus);
  const base = Math.max(MIN_TICK_MS, Math.round(150 - 150 * ratio));
  return slowUntil !== null && Date.now() < slowUntil ? base * 2 : base;
};
