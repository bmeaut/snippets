import type { PlayerAvatarState, HubDirection } from '../entities/player';
import type { ArcadeMachineState } from '../entities/machine';
import type { NpcState, NpcAppearance } from '../entities/npc';

export const HUB_ROOM_WIDTH = 960;
export const HUB_ROOM_HEIGHT = 640;

const WALL = 24; // room-space wall thickness

export interface DrawHubArgs {
  canvas: HTMLCanvasElement;
  width: number;
  height: number;
  scale: number;
  player: PlayerAvatarState;
  machines: ArcadeMachineState[];
  portals: ArcadeMachineState[];
  npcs: NpcState[];
  roomType: 'hub' | 'casino';
  pulseTick: number; // elapsed seconds for animations
}

// ── Floor ────────────────────────────────────────────────────────────────────

function drawMarbleFloor(ctx: CanvasRenderingContext2D, width: number, height: number, scale: number) {
  const wallPx = WALL * scale;
  const tileSize = 48 * scale;
  const innerW = width - wallPx * 2;
  const innerH = height - wallPx * 2;
  const cols = Math.ceil(innerW / tileSize) + 1;
  const rows = Math.ceil(innerH / tileSize) + 1;

  ctx.save();
  ctx.beginPath();
  ctx.rect(wallPx, wallPx, innerW, innerH);
  ctx.clip();

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const tx = wallPx + col * tileSize;
      const ty = wallPx + row * tileSize;
      const light = (row + col) % 2 === 0;
      ctx.fillStyle = light ? '#ddd5c0' : '#282828';
      ctx.fillRect(tx, ty, tileSize, tileSize);
      ctx.strokeStyle = 'rgba(0,0,0,0.10)';
      ctx.lineWidth = 0.5;
      ctx.strokeRect(tx, ty, tileSize, tileSize);
    }
  }

  ctx.restore();
}

function drawCarpet(ctx: CanvasRenderingContext2D, cx: number, cy: number, rx: number, ry: number) {
  // Outer border
  ctx.fillStyle = '#7a1a1a';
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
  ctx.fill();
  // Inner pattern
  ctx.fillStyle = '#8b2222';
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx - 8, ry - 8, 0, 0, Math.PI * 2);
  ctx.fill();
  // Gold border
  ctx.strokeStyle = '#c8a000';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx - 2, ry - 2, 0, 0, Math.PI * 2);
  ctx.stroke();
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx - 10, ry - 10, 0, 0, Math.PI * 2);
  ctx.stroke();
}

// ── Lighting ─────────────────────────────────────────────────────────────────

function drawChandelierGlow(
  ctx: CanvasRenderingContext2D,
  cx: number, cy: number,
  radius: number,
  width: number, height: number,
) {
  const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
  g.addColorStop(0, 'rgba(255,220,100,0.18)');
  g.addColorStop(0.6, 'rgba(255,200,80,0.06)');
  g.addColorStop(1, 'rgba(255,200,80,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, width, height);
}

// ── Walls ─────────────────────────────────────────────────────────────────────

function drawWalls(ctx: CanvasRenderingContext2D, width: number, height: number, scale: number) {
  const wallPx = WALL * scale;

  ctx.fillStyle = '#1a0f00';
  ctx.fillRect(0, 0, width, wallPx);
  ctx.fillRect(0, height - wallPx, width, wallPx);
  ctx.fillRect(0, 0, wallPx, height);
  ctx.fillRect(width - wallPx, 0, wallPx, height);

  // Inner gold trim
  ctx.strokeStyle = '#b8860b';
  ctx.lineWidth = 1.5 * scale;
  ctx.beginPath();
  ctx.moveTo(0, wallPx); ctx.lineTo(width, wallPx);
  ctx.moveTo(0, height - wallPx); ctx.lineTo(width, height - wallPx);
  ctx.moveTo(wallPx, 0); ctx.lineTo(wallPx, height);
  ctx.moveTo(width - wallPx, 0); ctx.lineTo(width - wallPx, height);
  ctx.stroke();

  // Corner accent squares
  const cs = 7 * scale;
  ctx.fillStyle = '#b8860b';
  for (const [fx, fy] of [[wallPx, wallPx], [width - wallPx, wallPx], [wallPx, height - wallPx], [width - wallPx, height - wallPx]] as const) {
    ctx.fillRect(fx - cs / 2, fy - cs / 2, cs, cs);
  }
}

// ── Decorations ───────────────────────────────────────────────────────────────

function drawPlant(ctx: CanvasRenderingContext2D, mx: number, my: number, mw: number, mh: number) {
  const cx = mx + mw / 2;
  const cy = my + mh / 2;

  // Pot
  ctx.fillStyle = '#7c3f1a';
  ctx.beginPath();
  ctx.moveTo(cx - mw * 0.35, cy + mh * 0.15);
  ctx.lineTo(cx - mw * 0.28, cy + mh * 0.45);
  ctx.lineTo(cx + mw * 0.28, cy + mh * 0.45);
  ctx.lineTo(cx + mw * 0.35, cy + mh * 0.15);
  ctx.closePath();
  ctx.fill();
  // Soil
  ctx.fillStyle = '#2d1a0a';
  ctx.beginPath();
  ctx.ellipse(cx, cy + mh * 0.16, mw * 0.3, mh * 0.1, 0, 0, Math.PI * 2);
  ctx.fill();

  // Leaves (3 ellipses)
  const leafColor = ['#1a6b1a', '#226b22', '#2d7a2d'];
  const leafOffsets: [number, number, number, number, number][] = [
    [0, -mh * 0.25, mw * 0.22, mh * 0.38, -0.3],
    [-mw * 0.2, -mh * 0.08, mw * 0.18, mh * 0.30, 0.5],
    [mw * 0.2, -mh * 0.08, mw * 0.18, mh * 0.30, -0.5],
  ];
  leafOffsets.forEach(([ox, oy, lw, lh, angle], i) => {
    ctx.fillStyle = leafColor[i];
    ctx.beginPath();
    ctx.ellipse(cx + ox, cy + oy, lw, lh, angle, 0, Math.PI * 2);
    ctx.fill();
  });
}

function drawVelvetRope(ctx: CanvasRenderingContext2D, scale: number) {
  // Decorative velvet rope near hub portal, right side
  const x1 = 680 * scale, y = 290 * scale;
  const x2 = 740 * scale;

  // Posts
  ctx.fillStyle = '#c8a000';
  for (const px of [x1, x2]) {
    ctx.fillRect(px - 3 * scale, y - 24 * scale, 6 * scale, 28 * scale);
    ctx.beginPath();
    ctx.arc(px, y - 24 * scale, 5 * scale, 0, Math.PI * 2);
    ctx.fill();
  }
  // Rope
  ctx.strokeStyle = '#8b0000';
  ctx.lineWidth = 3 * scale;
  ctx.beginPath();
  ctx.moveTo(x1, y - 16 * scale);
  ctx.bezierCurveTo(x1 + 20 * scale, y, x2 - 20 * scale, y, x2, y - 16 * scale);
  ctx.stroke();
}

// ── Portal Gate ───────────────────────────────────────────────────────────────

function drawPortal(
  ctx: CanvasRenderingContext2D,
  machine: ArcadeMachineState,
  scale: number,
  pulseTick: number,
) {
  const X = machine.x * scale;
  const Y = machine.y * scale;
  const W = machine.width * scale;
  const H = machine.height * scale;
  const pw = 14 * scale; // pillar width
  const archCy = Y + 44 * scale; // arch center Y
  const archR = W / 2;

  // Left pillar
  ctx.fillStyle = '#3d2808';
  ctx.beginPath();
  ctx.roundRect(X, archCy, pw, H - 44 * scale, [0, 0, 3 * scale, 3 * scale]);
  ctx.fill();
  // Right pillar
  ctx.beginPath();
  ctx.roundRect(X + W - pw, archCy, pw, H - 44 * scale, [0, 0, 3 * scale, 3 * scale]);
  ctx.fill();

  // Arch crown (solid semicircle)
  const archCx = X + W / 2;
  ctx.fillStyle = '#3d2808';
  ctx.beginPath();
  ctx.arc(archCx, archCy, archR, Math.PI, 0);
  ctx.lineTo(X + W, archCy);
  ctx.lineTo(X, archCy);
  ctx.closePath();
  ctx.fill();

  // Gold trim on pillars
  ctx.strokeStyle = '#c8a000';
  ctx.lineWidth = 1.5 * scale;
  ctx.strokeRect(X, archCy, pw, H - 44 * scale);
  ctx.strokeRect(X + W - pw, archCy, pw, H - 44 * scale);

  // Gold arch border
  ctx.lineWidth = 2 * scale;
  ctx.beginPath();
  ctx.arc(archCx, archCy, archR - 1 * scale, Math.PI, 0);
  ctx.stroke();

  // Inner arch glow
  const innerR = archR - pw - 2 * scale;
  if (innerR > 0) {
    const ag = ctx.createRadialGradient(archCx, archCy, 0, archCx, archCy, innerR);
    ag.addColorStop(0, 'rgba(255,200,80,0.10)');
    ag.addColorStop(1, 'rgba(255,200,80,0)');
    ctx.fillStyle = ag;
    ctx.beginPath();
    ctx.arc(archCx, archCy, innerR, Math.PI, 0);
    ctx.lineTo(X + W - pw - 2 * scale, archCy);
    ctx.lineTo(X + pw + 2 * scale, archCy);
    ctx.closePath();
    ctx.fill();
  }

  // Pulsing threshold glow at bottom
  const pulse = 0.13 + 0.07 * Math.sin(pulseTick * 2.5);
  const tg = ctx.createLinearGradient(X, Y + H - 36 * scale, X, Y + H + 4 * scale);
  tg.addColorStop(0, `rgba(255,210,60,${pulse})`);
  tg.addColorStop(1, `rgba(255,210,60,0)`);
  ctx.fillStyle = tg;
  ctx.fillRect(X + pw, Y + H - 36 * scale, W - pw * 2, 40 * scale);

  // Highlight dots on arch
  ctx.fillStyle = 'rgba(255,245,180,0.75)';
  for (let i = 0; i <= 4; i++) {
    const angle = Math.PI + (i / 4) * Math.PI;
    const hx = archCx + Math.cos(angle) * (archR - 3 * scale);
    const hy = archCy + Math.sin(angle) * (archR - 3 * scale);
    ctx.beginPath();
    ctx.arc(hx, hy, 1.5 * scale, 0, Math.PI * 2);
    ctx.fill();
  }

  // Label above arch
  if (machine.label) {
    ctx.font = `bold ${Math.round(10 * scale)}px Georgia, "Times New Roman", serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#d4a000';
    ctx.fillText(machine.label, archCx, Y + 18 * scale);
  }
}

// ── Arcade Machines ───────────────────────────────────────────────────────────

function drawArcadeMachine(
  ctx: CanvasRenderingContext2D,
  machine: ArcadeMachineState,
  scale: number,
) {
  const X = machine.x * scale;
  const Y = machine.y * scale;
  const W = machine.width * scale;
  const H = machine.height * scale;
  const sc = scale;

  const label = machine.id === 'snake-machine' ? 'SNAKE' : 'AMŐBA';
  const screenColor = machine.screenColor ?? '#22d3ee';

  // Shadow
  ctx.fillStyle = 'rgba(0,0,0,0.28)';
  ctx.beginPath();
  ctx.roundRect(X + 4 * sc, Y + 6 * sc, W, H, 4 * sc);
  ctx.fill();

  // Cabinet body (tapered top)
  ctx.fillStyle = '#2a1608';
  ctx.beginPath();
  ctx.moveTo(X + 6 * sc, Y + H);
  ctx.lineTo(X, Y + H);
  ctx.lineTo(X + 8 * sc, Y + 28 * sc); // top-left corner
  ctx.lineTo(X + W - 8 * sc, Y + 28 * sc); // top-right corner
  ctx.lineTo(X + W, Y + H);
  ctx.lineTo(X + W - 6 * sc, Y + H);
  ctx.closePath();
  ctx.fill();

  // Marquee (top panel)
  ctx.fillStyle = '#1a0f00';
  ctx.beginPath();
  ctx.roundRect(X + 4 * sc, Y + 2 * sc, W - 8 * sc, 28 * sc, [4 * sc, 4 * sc, 0, 0]);
  ctx.fill();
  // Marquee grid lines
  ctx.strokeStyle = 'rgba(255,255,255,0.08)';
  ctx.lineWidth = 0.5 * sc;
  for (let i = 1; i < 5; i++) {
    const lx = X + 4 * sc + (W - 8 * sc) * (i / 5);
    ctx.beginPath(); ctx.moveTo(lx, Y + 2 * sc); ctx.lineTo(lx, Y + 30 * sc); ctx.stroke();
  }
  // Marquee label
  ctx.font = `bold ${Math.round(8 * sc)}px "Segoe UI", Arial, sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = screenColor;
  ctx.fillText(label, X + W / 2, Y + 16 * sc);

  // Screen bezel
  ctx.fillStyle = '#111';
  ctx.beginPath();
  ctx.roundRect(X + 8 * sc, Y + 32 * sc, W - 16 * sc, 40 * sc, 2 * sc);
  ctx.fill();
  // Screen glow
  const sg = ctx.createRadialGradient(
    X + W / 2, Y + 52 * sc, 0,
    X + W / 2, Y + 52 * sc, 22 * sc,
  );
  sg.addColorStop(0, screenColor + 'cc');
  sg.addColorStop(0.6, screenColor + '55');
  sg.addColorStop(1, screenColor + '00');
  ctx.fillStyle = sg;
  ctx.beginPath();
  ctx.roundRect(X + 10 * sc, Y + 34 * sc, W - 20 * sc, 36 * sc, 1 * sc);
  ctx.fill();

  // Control panel
  ctx.fillStyle = '#1a0d04';
  ctx.beginPath();
  ctx.moveTo(X, Y + H - 30 * sc);
  ctx.lineTo(X + W, Y + H - 30 * sc);
  ctx.lineTo(X + W - 6 * sc, Y + H);
  ctx.lineTo(X + 6 * sc, Y + H);
  ctx.closePath();
  ctx.fill();

  // Joystick
  const jx = X + 18 * sc, jy = Y + H - 18 * sc;
  ctx.fillStyle = '#555';
  ctx.beginPath(); ctx.arc(jx, jy + 3 * sc, 5 * sc, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#333';
  ctx.beginPath(); ctx.arc(jx, jy, 4 * sc, 0, Math.PI * 2); ctx.fill();

  // Buttons
  const btnColors = ['#e53e3e', '#ecc94b', '#38a169'];
  for (let i = 0; i < 3; i++) {
    ctx.fillStyle = btnColors[i];
    ctx.beginPath();
    ctx.arc(X + (38 + i * 10) * sc, Y + H - 16 * sc, 3.5 * sc, 0, Math.PI * 2);
    ctx.fill();
  }

  // Gold edge trim
  ctx.strokeStyle = '#6b3a00';
  ctx.lineWidth = 1 * sc;
  ctx.strokeRect(X + 4 * sc, Y + 2 * sc, W - 8 * sc, H - 2 * sc);
}

// ── Casino Terminals ──────────────────────────────────────────────────────────

function drawCasinoTerminal(
  ctx: CanvasRenderingContext2D,
  machine: ArcadeMachineState,
  scale: number,
) {
  const X = machine.x * scale;
  const Y = machine.y * scale;
  const W = machine.width * scale;
  const H = machine.height * scale;
  const sc = scale;
  const screenColor = machine.screenColor ?? '#ef4444';
  const label = machine.label ?? 'CASINO';

  // Table felt surface under terminal
  ctx.fillStyle = '#0f4a2a';
  ctx.beginPath();
  ctx.ellipse(X + W / 2, Y + H + 10 * sc, W * 0.75, 14 * sc, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#c8a000';
  ctx.lineWidth = 1 * sc;
  ctx.beginPath();
  ctx.ellipse(X + W / 2, Y + H + 10 * sc, W * 0.75 - 2 * sc, 12 * sc, 0, 0, Math.PI * 2);
  ctx.stroke();

  // Shadow
  ctx.fillStyle = 'rgba(0,0,0,0.25)';
  ctx.beginPath();
  ctx.roundRect(X + 3 * sc, Y + 4 * sc, W, H, 4 * sc);
  ctx.fill();

  // Stand / base
  ctx.fillStyle = '#1a1a1a';
  ctx.beginPath();
  ctx.roundRect(X + W * 0.3, Y + H - 14 * sc, W * 0.4, 14 * sc, 2 * sc);
  ctx.fill();
  ctx.fillStyle = '#2a2a2a';
  ctx.beginPath();
  ctx.roundRect(X + W * 0.15, Y + H - 6 * sc, W * 0.7, 6 * sc, 3 * sc);
  ctx.fill();

  // Monitor frame
  ctx.fillStyle = '#111';
  ctx.beginPath();
  ctx.roundRect(X, Y, W, H - 10 * sc, 5 * sc);
  ctx.fill();

  // Screen
  const screenGrad = ctx.createLinearGradient(X + 3 * sc, Y + 3 * sc, X + 3 * sc, Y + H - 20 * sc);
  screenGrad.addColorStop(0, screenColor + 'bb');
  screenGrad.addColorStop(1, screenColor + '44');
  ctx.fillStyle = screenGrad;
  ctx.beginPath();
  ctx.roundRect(X + 4 * sc, Y + 4 * sc, W - 8 * sc, H - 22 * sc, 3 * sc);
  ctx.fill();

  // Gold accent bar at bottom of screen
  ctx.fillStyle = '#b8860b';
  ctx.fillRect(X + 4 * sc, Y + H - 22 * sc, W - 8 * sc, 5 * sc);

  // Label on screen
  ctx.font = `bold ${Math.round(7 * sc)}px "Segoe UI", Arial, sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = '#fff';
  ctx.fillText(label, X + W / 2, Y + (H - 22 * sc) / 2);
}

// ── Shared human figure renderer ──────────────────────────────────────────────

const PLAYER_APPEARANCE: NpcAppearance = {
  skinTone: '#e8c49a',
  hairColor: '#3d2314',
  jacketColor: '#1e3a5f',
  pantsColor: '#2d2d3a',
  isFemale: false,
};

function drawHumanFigure(
  ctx: CanvasRenderingContext2D,
  cx: number, cy: number,
  facing: HubDirection,
  isMoving: boolean,
  animTick: number,
  scale: number,
  appearance: NpcAppearance,
) {
  const s = scale;
  const legSwing = isMoving ? Math.sin(animTick * Math.PI * 2) * 5 * s : 0;
  const bodyBob  = isMoving ? Math.abs(Math.sin(animTick * Math.PI * 2)) * 0.8 * s : 0;
  const cyHead   = cy - 11 * s - bodyBob;
  const cyHair   = cy - 14 * s - bodyBob;

  // Shadow
  ctx.fillStyle = 'rgba(0,0,0,0.28)';
  ctx.beginPath();
  ctx.ellipse(cx + 1 * s, cy + 12 * s, 13 * s, 7 * s, 0, 0, Math.PI * 2);
  ctx.fill();

  // Legs
  ctx.fillStyle = appearance.pantsColor;
  ctx.beginPath();
  ctx.ellipse(cx - 4 * s, cy + 9 * s - bodyBob + legSwing, 3.5 * s, 5 * s, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.ellipse(cx + 4 * s, cy + 9 * s - bodyBob - legSwing, 3.5 * s, 5 * s, 0, 0, Math.PI * 2);
  ctx.fill();

  // Body / jacket
  ctx.fillStyle = appearance.jacketColor;
  ctx.beginPath();
  ctx.roundRect(cx - 8 * s, cy - 6 * s - bodyBob, 16 * s, 17 * s, 3 * s);
  ctx.fill();

  // Shirt strip
  ctx.fillStyle = '#f0f0f0';
  ctx.fillRect(cx - 2.5 * s, cy - 6 * s - bodyBob, 5 * s, 9 * s);

  // Head
  ctx.fillStyle = appearance.skinTone;
  ctx.beginPath();
  ctx.ellipse(cx, cyHead, 9 * s, 10 * s, 0, 0, Math.PI * 2);
  ctx.fill();

  // Hair — female: wider 240° arc covering sides; male: top half
  ctx.fillStyle = appearance.hairColor;
  ctx.beginPath();
  if (appearance.isFemale) {
    ctx.arc(cx, cyHair, 9 * s, Math.PI * 5 / 6, Math.PI / 6, false);
  } else {
    ctx.arc(cx, cyHair, 9 * s, Math.PI, 0, false);
  }
  ctx.closePath();
  ctx.fill();

  // Eyes (shift toward facing direction)
  let eyeDx = 0, eyeDy = 0;
  if (facing === 'up')   eyeDy = -3.5 * s;
  else if (facing === 'down')  eyeDy = 1.5 * s;
  else if (facing === 'left')  eyeDx = -2.5 * s;
  else                         eyeDx = 2.5 * s;

  ctx.fillStyle = '#1a1a2e';
  ctx.beginPath();
  ctx.arc(cx - 2.5 * s + eyeDx, cyHead + eyeDy, 1.4 * s, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(cx + 2.5 * s + eyeDx, cyHead + eyeDy, 1.4 * s, 0, Math.PI * 2);
  ctx.fill();
}

function drawPlayer(ctx: CanvasRenderingContext2D, player: PlayerAvatarState, scale: number) {
  const cx = (player.x + player.width / 2) * scale;
  const cy = (player.y + player.height / 2) * scale;
  drawHumanFigure(ctx, cx, cy, player.facing, player.isMoving, player.animTick, scale, PLAYER_APPEARANCE);
}

function drawNpc(ctx: CanvasRenderingContext2D, npc: NpcState, scale: number) {
  const cx = (npc.x + npc.width / 2) * scale;
  const cy = (npc.y + npc.height / 2) * scale;
  drawHumanFigure(ctx, cx, cy, npc.facing, npc.isMoving, npc.animTick, scale, npc.appearance);
}

// ── Interaction prompt label (drawn on canvas) ────────────────────────────────

function drawMachineLabels(
  ctx: CanvasRenderingContext2D,
  machines: ArcadeMachineState[],
  scale: number,
) {
  const labels: Record<string, string> = {
    'snake-machine': 'SNAKE',
    'amoba-machine': 'AMŐBA',
    'casino-roulette-terminal': 'RULETT',
    'casino-blackjack-terminal': 'BLACKJACK',
  };
  for (const m of machines) {
    if (m.kind === 'plant' || m.kind === 'portal') continue;
    const txt = labels[m.id];
    if (!txt) continue;
    const cx = (m.x + m.width / 2) * scale;
    const cy = (m.y - 8) * scale;
    ctx.font = `bold ${Math.round(9 * scale)}px "Segoe UI", Arial, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.fillStyle = 'rgba(255,255,255,0.45)';
    ctx.fillText(txt, cx, cy);
  }
}

// ── Main draw ─────────────────────────────────────────────────────────────────

export const drawHub = ({
  canvas, width, height, scale,
  player, machines, portals, npcs, roomType, pulseTick,
}: DrawHubArgs): void => {
  let ctx: CanvasRenderingContext2D | null = null;
  try { ctx = canvas.getContext('2d'); } catch { return; }
  if (!ctx) return;

  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);

  // 1. Marble floor
  drawMarbleFloor(ctx, width, height, scale);

  // 2. Casino carpet
  if (roomType === 'casino') {
    drawCarpet(ctx, width / 2, height / 2, 200 * scale, 120 * scale);
  }

  // 3. Chandelier glow(s)
  if (roomType === 'hub') {
    drawChandelierGlow(ctx, width * 0.45, height * 0.35, 200 * scale, width, height);
    drawChandelierGlow(ctx, width * 0.25, height * 0.65, 140 * scale, width, height);
  } else {
    drawChandelierGlow(ctx, width / 2, height / 2, 230 * scale, width, height);
    drawChandelierGlow(ctx, width * 0.7, height * 0.3, 130 * scale, width, height);
  }

  // 4. Walls (on top of floor)
  drawWalls(ctx, width, height, scale);

  // 5. Velvet rope (hub only)
  if (roomType === 'hub') {
    drawVelvetRope(ctx, scale);
  }

  // 6. Portals
  for (const portal of portals) {
    drawPortal(ctx, portal, scale, pulseTick);
  }

  // 7. Machines (sorted by y for depth)
  const sorted = [...machines].sort((a, b) => (a.y + a.height) - (b.y + b.height));
  for (const m of sorted) {
    const X = m.x * scale, Y = m.y * scale, W = m.width * scale, H = m.height * scale;
    if (m.kind === 'plant') {
      drawPlant(ctx, X, Y, W, H);
    } else if (m.kind === 'snake' || m.kind === 'amoba') {
      drawArcadeMachine(ctx, m, scale);
    } else if (m.kind === 'casino') {
      drawCasinoTerminal(ctx, m, scale);
    }
  }

  // 8. Characters — depth-sorted by bottom edge (higher y drawn on top)
  type CharEntry = { bottomY: number; draw: () => void };
  const chars: CharEntry[] = [
    ...npcs.map((npc) => ({
      bottomY: npc.y + npc.height,
      draw: () => drawNpc(ctx, npc, scale),
    })),
    {
      bottomY: player.y + player.height,
      draw: () => drawPlayer(ctx, player, scale),
    },
  ];
  chars.sort((a, b) => a.bottomY - b.bottomY);
  for (const c of chars) c.draw();
};
