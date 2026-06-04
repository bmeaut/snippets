export type GameId = 'snake';

export type Direction = 'up' | 'down' | 'left' | 'right';

export type GameScreen =
  | { mode: 'hub' }
  | { mode: 'game'; gameId: GameId };

export interface GameCardDefinition {
  id: GameId;
  title: string;
  description: string;
  accent: string;
}

export interface Coordinate {
  x: number;
  y: number;
}

export interface SnakeState {
  snake: Coordinate[];
  apple: Coordinate;
  direction: Direction;
  pendingDirection: Direction;
  score: number;
  highScore: number;
  gameOver: boolean;
  stones: Coordinate[];
  goldenApple: { pos: Coordinate; spawnedAt: number } | null;
  blueApple: { pos: Coordinate; spawnedAt: number } | null;
  slowUntil: number | null;
  applesEaten: number;
}
