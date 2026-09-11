import type { HubDirection } from './player';
import type { ArcadeMachineState } from './machine';
import { movePlayerWithSlide, type RoomBounds } from '../systems/collision';

export interface NpcAppearance {
  skinTone: string;
  hairColor: string;
  jacketColor: string;
  pantsColor: string;
  isFemale: boolean;
}

export interface NpcState {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  facing: HubDirection;
  isMoving: boolean;
  animTick: number;
  vx: number;
  vy: number;
  speed: number;
  wanderTimer: number;
  appearance: NpcAppearance;
}

const APPEARANCES: NpcAppearance[] = [
  { skinTone: '#e8c49a', hairColor: '#3d2314', jacketColor: '#7c1d1d', pantsColor: '#2d2d3a', isFemale: false },
  { skinTone: '#c8845a', hairColor: '#0f0600', jacketColor: '#1e4a3f', pantsColor: '#1a1a2e', isFemale: false },
  { skinTone: '#f0d5b0', hairColor: '#c8a030', jacketColor: '#4a2878', pantsColor: '#2a2a3a', isFemale: true  },
  { skinTone: '#e8c49a', hairColor: '#8b0a0a', jacketColor: '#5c3a1e', pantsColor: '#1a2a3a', isFemale: true  },
  { skinTone: '#b87040', hairColor: '#0a0600', jacketColor: '#3a5c1e', pantsColor: '#1a1a1a', isFemale: false },
  { skinTone: '#f5e8d0', hairColor: '#2d1a0e', jacketColor: '#1a3a6a', pantsColor: '#2d2d3a', isFemale: true  },
  { skinTone: '#d4906a', hairColor: '#3d3000', jacketColor: '#7c5c1a', pantsColor: '#1a2a1a', isFemale: false },
];

const FACING_DIRS: HubDirection[] = ['up', 'down', 'left', 'right'];

const WANDER_DIRS: [number, number][] = [
  [1, 0], [-1, 0], [0, 1], [0, -1],
  [1, 1], [-1, 1], [1, -1], [-1, -1],
  [0, 0], [0, 0], // pause (weighted 2×)
];

export function createNpc(id: string, x: number, y: number, appearanceIndex: number): NpcState {
  return {
    id, x, y,
    width: 32, height: 32,
    facing: FACING_DIRS[Math.floor(Math.random() * 4)],
    isMoving: false,
    animTick: Math.random() * Math.PI * 2,
    vx: 0, vy: 0,
    speed: 48 + Math.random() * 32,
    wanderTimer: Math.random() * 1.5,
    appearance: APPEARANCES[appearanceIndex % APPEARANCES.length],
  };
}

export function updateNpc(
  npc: NpcState,
  dt: number,
  bounds: RoomBounds,
  solidMachines: ArcadeMachineState[],
): NpcState {
  let { vx, vy, wanderTimer, animTick, facing } = npc;

  wanderTimer -= dt;
  if (wanderTimer <= 0) {
    const dir = WANDER_DIRS[Math.floor(Math.random() * WANDER_DIRS.length)];
    vx = dir[0];
    vy = dir[1];
    wanderTimer = (vx === 0 && vy === 0)
      ? 0.3 + Math.random() * 0.7
      : 0.7 + Math.random() * 2.2;
  }

  const isMoving = vx !== 0 || vy !== 0;
  let ndx = vx, ndy = vy;
  if (ndx !== 0 && ndy !== 0) { ndx *= 0.7071; ndy *= 0.7071; }

  if (ndx < 0) facing = 'left';
  else if (ndx > 0) facing = 'right';
  else if (ndy < 0) facing = 'up';
  else if (ndy > 0) facing = 'down';

  animTick = isMoving ? animTick + dt * 3 : animTick * 0.82;

  const asPlayer = { x: npc.x, y: npc.y, width: npc.width, height: npc.height, facing, isMoving, animTick };
  const moved = movePlayerWithSlide(asPlayer, ndx * npc.speed * dt, ndy * npc.speed * dt, bounds, solidMachines);

  const stuck = isMoving && moved.x === npc.x && moved.y === npc.y;

  return {
    ...npc,
    x: moved.x, y: moved.y,
    facing, isMoving, animTick,
    vx: stuck ? 0 : vx,
    vy: stuck ? 0 : vy,
    wanderTimer: stuck ? 0 : wanderTimer,
  };
}

// ── Lobby NPC positions (7) ───────────────────────────────────────────────────
export function createLobbyNpcs(): NpcState[] {
  const positions: [number, number][] = [
    [150, 370], [310, 430], [500, 310], [600, 210],
    [370, 490], [660, 430], [240, 260],
  ];
  return positions.map(([x, y], i) => createNpc(`npc-hub-${i}`, x, y, i));
}

// ── Casino NPC positions (4) ──────────────────────────────────────────────────
export function createCasinoNpcs(): NpcState[] {
  const positions: [number, number][] = [
    [300, 360], [480, 450], [640, 210], [400, 270],
  ];
  return positions.map(([x, y], i) => createNpc(`npc-casino-${i}`, x, y, i + 2));
}
