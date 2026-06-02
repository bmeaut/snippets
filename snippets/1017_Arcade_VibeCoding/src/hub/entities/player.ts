import { HUB_ROOM_HEIGHT, HUB_ROOM_WIDTH } from '../rendering/drawHub';

export type HubDirection = 'up' | 'down' | 'left' | 'right';

export interface PlayerAvatarState {
  x: number;
  y: number;
  width: number;
  height: number;
  facing: HubDirection;
  isMoving: boolean;
  animTick: number;
}

export const PLAYER_WIDTH = 32;
export const PLAYER_HEIGHT = 32;
export const PLAYER_SPEED = 140; // px/sec

export const createPlayer = (): PlayerAvatarState => ({
  x: 120,
  y: HUB_ROOM_HEIGHT / 2 - 16,
  width: PLAYER_WIDTH,
  height: PLAYER_HEIGHT,
  facing: 'right',
  isMoving: false,
  animTick: 0,
});

export type RoomSpawnSide = 'left' | 'right';


export const createRoomSpawnPlayer = (side: RoomSpawnSide): PlayerAvatarState => ({
  ...createPlayer(),
  x: side === 'left' ? 160 : HUB_ROOM_WIDTH - PLAYER_WIDTH - 200,
  y: HUB_ROOM_HEIGHT / 2 - PLAYER_HEIGHT / 2,
  facing: side === 'left' ? 'right' : 'left',
});
