import React, { useCallback, useEffect, useRef, useState } from 'react';
import type { SnakeState } from '../../types';
import { loadHighScore, saveHighScore } from '../../storage';
import {
  CELL_SIZE,
  GRID_SIZE,
  GOLDEN_APPLE_TTL,
  BLUE_APPLE_TTL,
  createInitialSnakeState,
  moveSnake,
  nextTickDelay,
  updateDirection,
} from './snakeLogic';

interface SnakeGameProps {
  onReturnToMenu: () => void;
}

const CANVAS_SIZE = GRID_SIZE * CELL_SIZE; // 480

function lerp(a: number, b: number, t: number): number {
  return Math.round(a + (b - a) * t);
}

function drawCanvas(ctx: CanvasRenderingContext2D, state: SnakeState, now: number): void {
  const cs = CELL_SIZE;

  // Background
  ctx.fillStyle = '#090b10';
  ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

  // Grid
  ctx.strokeStyle = 'rgba(255,255,255,0.04)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= GRID_SIZE; i++) {
    const p = i * cs;
    ctx.beginPath(); ctx.moveTo(p, 0); ctx.lineTo(p, CANVAS_SIZE); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, p); ctx.lineTo(CANVAS_SIZE, p); ctx.stroke();
  }

  // Stones
  state.stones.forEach((stone) => {
    ctx.fillStyle = '#374151';
    ctx.beginPath();
    ctx.roundRect(stone.x * cs + 2, stone.y * cs + 2, cs - 4, cs - 4, 4);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.12)';
    ctx.lineWidth = 1;
    ctx.stroke();
  });

  // Regular apple
  ctx.save();
  ctx.shadowColor = '#f97316';
  ctx.shadowBlur = 14;
  ctx.fillStyle = '#f97316';
  ctx.beginPath();
  ctx.arc(state.apple.x * cs + cs / 2, state.apple.y * cs + cs / 2, cs / 2 - 3, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // Golden apple
  if (state.goldenApple) {
    const secsLeft = Math.max(1, Math.ceil((GOLDEN_APPLE_TTL - (now - state.goldenApple.spawnedAt)) / 1000));
    const cx = state.goldenApple.pos.x * cs + cs / 2;
    const cy = state.goldenApple.pos.y * cs + cs / 2;
    ctx.save();
    ctx.shadowColor = '#fbbf24';
    ctx.shadowBlur = 18;
    ctx.fillStyle = '#fbbf24';
    ctx.beginPath();
    ctx.arc(cx, cy, cs / 2 - 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    ctx.fillStyle = '#0f172a';
    ctx.font = `bold ${Math.round(cs * 0.44)}px Inter,sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(secsLeft), cx, cy);
  }

  // Blue apple
  if (state.blueApple) {
    const secsLeft = Math.max(1, Math.ceil((BLUE_APPLE_TTL - (now - state.blueApple.spawnedAt)) / 1000));
    const cx = state.blueApple.pos.x * cs + cs / 2;
    const cy = state.blueApple.pos.y * cs + cs / 2;
    ctx.save();
    ctx.shadowColor = '#38bdf8';
    ctx.shadowBlur = 18;
    ctx.fillStyle = '#38bdf8';
    ctx.beginPath();
    ctx.arc(cx, cy, cs / 2 - 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    ctx.fillStyle = '#0f172a';
    ctx.font = `bold ${Math.round(cs * 0.44)}px Inter,sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(secsLeft), cx, cy);
  }

  // Snake
  const len = state.snake.length;
  state.snake.forEach((seg, i) => {
    const t = len > 1 ? i / (len - 1) : 0;
    // Head: #a3e635 (163,230,53) → Tail: #166534 (22,101,52)
    const color = `rgb(${lerp(163, 22, t)},${lerp(230, 101, t)},${lerp(53, 52, t)})`;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.roundRect(seg.x * cs + 2, seg.y * cs + 2, cs - 4, cs - 4, i === 0 ? 7 : 3);
    ctx.fill();
  });

  // Game over dim
  if (state.gameOver) {
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
  }
}

function dirFromKey(key: string): SnakeState['direction'] | null {
  if (key === 'ArrowUp' || key === 'w' || key === 'W') return 'up';
  if (key === 'ArrowDown' || key === 's' || key === 'S') return 'down';
  if (key === 'ArrowLeft' || key === 'a' || key === 'A') return 'left';
  if (key === 'ArrowRight' || key === 'd' || key === 'D') return 'right';
  return null;
}

export function SnakeGame({ onReturnToMenu }: SnakeGameProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const stateRef = useRef<SnakeState>(createInitialSnakeState(loadHighScore()));
  const rafRef = useRef<number>(0);
  const lastTickRef = useRef<number>(0);
  const pointerStartRef = useRef<{ x: number; y: number } | null>(null);

  const [displayState, setDisplayState] = useState<SnakeState>(() => {
    const s = createInitialSnakeState(loadHighScore());
    stateRef.current = s;
    return s;
  });

  // Keyboard input
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const dir = dirFromKey(e.key);
      if (!dir) return;
      setDisplayState((prev) => {
        const next = { ...prev, pendingDirection: dir };
        stateRef.current = next;
        return next;
      });
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  // Single rAF loop — draw every frame, tick at intervals
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const DPR = window.devicePixelRatio || 1;
    canvas.width = CANVAS_SIZE * DPR;
    canvas.height = CANVAS_SIZE * DPR;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

    lastTickRef.current = Date.now();

    const loop = () => {
      const now = Date.now();
      const s = stateRef.current;

      drawCanvas(ctx, s, now);

      if (!s.gameOver) {
        const delay = nextTickDelay(s.score, s.slowUntil);
        if (now - lastTickRef.current >= delay) {
          lastTickRef.current = now;
          setDisplayState((prev) => {
            const next = updateDirection(moveSnake(prev, now));
            stateRef.current = next;
            if (next.gameOver) saveHighScore(next.highScore);
            return next;
          });
        }
      }

      rafRef.current = requestAnimationFrame(loop);
    };

    rafRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafRef.current);
  }, []); // single mount — never recreated

  const restart = useCallback(() => {
    const s = createInitialSnakeState(loadHighScore());
    stateRef.current = s;
    lastTickRef.current = Date.now();
    setDisplayState(s);
  }, []);

  // Swipe
  const handlePointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    pointerStartRef.current = { x: e.clientX, y: e.clientY };
  };
  const handlePointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const start = pointerStartRef.current;
    pointerStartRef.current = null;
    if (!start) return;
    const dx = e.clientX - start.x;
    const dy = e.clientY - start.y;
    if (Math.max(Math.abs(dx), Math.abs(dy)) < 20) return;
    const dir: SnakeState['direction'] =
      Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : dy > 0 ? 'down' : 'up';
    setDisplayState((prev) => {
      const next = { ...prev, pendingDirection: dir };
      stateRef.current = next;
      return next;
    });
  };

  const slowActive = displayState.slowUntil !== null && Date.now() < displayState.slowUntil;

  return (
    <main className="game-shell">
      <div className="game-shell__topbar">
        <button className="secondary-button" onClick={onReturnToMenu}>
          Vissza a Hubba
        </button>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center', fontSize: 14, color: '#e2e8f0' }}>
          <span>Pontszám: <strong style={{ color: '#f97316' }}>{displayState.score}</strong></span>
          <span>Rekord: <strong style={{ color: '#38bdf8' }}>{displayState.highScore}</strong></span>
          {slowActive && <span title="Lassítás aktív" style={{ fontSize: 18 }}>🐢</span>}
        </div>
        <button className="secondary-button" onClick={restart}>
          Újraindítás
        </button>
      </div>

      <section className="game-stage">
        <canvas
          ref={canvasRef}
          className="game-canvas"
          aria-label="Snake játéktábla"
          style={{
            maxHeight: '85vh',
            maxWidth: '100%',
            aspectRatio: '1 / 1',
            objectFit: 'contain',
            margin: '0 auto',
            display: 'block',
          }}
          onPointerDown={handlePointerDown}
          onPointerUp={handlePointerUp}
        />
        {displayState.gameOver && (
          <div className="game-over-panel">
            <h2>Játék vége</h2>
            <p>Pontszám: {displayState.score}</p>
            <p>Rekord: {displayState.highScore}</p>
            <div className="game-over-panel__actions">
              <button className="primary-button" onClick={restart}>
                Újraindítás
              </button>
              <button className="secondary-button" onClick={onReturnToMenu}>
                Vissza a Hubba
              </button>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
