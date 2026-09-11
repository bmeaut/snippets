import type { ArcadeMachineState } from '../entities/machine';
import type { PlayerAvatarState } from '../entities/player';

export interface RoomBounds {
  width: number;
  height: number;
}

const WALL = 24;

export const clamp = (value: number, minimum: number, maximum: number): number =>
  Math.max(minimum, Math.min(value, maximum));

export const isInsideRoom = (player: PlayerAvatarState, bounds: RoomBounds): boolean =>
  player.x >= WALL &&
  player.y >= WALL &&
  player.x + player.width <= bounds.width - WALL &&
  player.y + player.height <= bounds.height - WALL;

export const clampPlayerToRoom = (
  player: PlayerAvatarState,
  bounds: RoomBounds,
): PlayerAvatarState => ({
  ...player,
  x: clamp(player.x, WALL, bounds.width - player.width - WALL),
  y: clamp(player.y, WALL, bounds.height - player.height - WALL),
});

function overlapsRect(
  px: number, py: number, pw: number, ph: number,
  mx: number, my: number, mw: number, mh: number,
): boolean {
  return px < mx + mw && px + pw > mx && py < my + mh && py + ph > my;
}

export const movePlayerWithSlide = (
  player: PlayerAvatarState,
  dx: number,
  dy: number,
  bounds: RoomBounds,
  solidMachines: ArcadeMachineState[],
): PlayerAvatarState => {
  const { x, y, width, height } = player;

  // Try X axis
  let nextX = x + dx;
  const xClamped = clamp(nextX, WALL, bounds.width - width - WALL);
  const xBlocked =
    xClamped !== nextX ||
    solidMachines.some((m) => m.isSolid && overlapsRect(xClamped, y, width, height, m.x, m.y, m.width, m.height));
  const resolvedX = xBlocked ? x : xClamped;

  // Try Y axis
  let nextY = y + dy;
  const yClamped = clamp(nextY, WALL, bounds.height - height - WALL);
  const yBlocked =
    yClamped !== nextY ||
    solidMachines.some((m) => m.isSolid && overlapsRect(resolvedX, yClamped, width, height, m.x, m.y, m.width, m.height));
  const resolvedY = yBlocked ? y : yClamped;

  return { ...player, x: resolvedX, y: resolvedY };
};

export const intersectsMachine = (
  player: PlayerAvatarState,
  machine: ArcadeMachineState,
): boolean => {
  const playerCenterX = player.x + player.width / 2;
  const playerCenterY = player.y + player.height / 2;
  const machineCenterX = machine.x + machine.width / 2;
  const machineCenterY = machine.y + machine.height / 2;
  const distance = Math.hypot(machineCenterX - playerCenterX, machineCenterY - playerCenterY);
  return distance <= machine.interactionRadius;
};
