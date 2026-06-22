import React, { useState } from 'react';
import type { Bet } from './gameLogic';
import {
  WHEEL_SEQUENCE, colorOf,
  getNeighbors, getTiersBets, getVoisinsBets, getOrphelinsBets, getJeuZeroBets,
} from './gameLogic';

// ── Geometry constants ────────────────────────────────────────────────────────
const SVG_W = 580, SVG_H = 200;
const CX = 290, CY = 100;
const NUM_A = 260, NUM_B = 84;    // number-cell centres
const OA = 243, OB = 68;           // arc band outer edge
const IA = 155, IB = 30;           // arc band inner edge
const JZ_IA = 70, JZ_IB = 12;     // Jeu Zéro innermost edge

const Δ = (2 * Math.PI) / 37;
/** angle of wheel-index `i` on the oval (0 starts at left, goes clockwise) */
const θ = (i: number) => Math.PI + i * Δ;
/** boundary angle between index i and i+1 */
const boundary = (between: number) => Math.PI + between * Δ;

// Group boundary angles
const B_7_8   = boundary(7.5);
const B_10_11 = boundary(10.5);
const B_22_23 = boundary(22.5);
const B_27_28 = boundary(27.5);
// Jeu Zéro sub-section within Voisins
const B_32_33 = boundary(32.5);
const B_2_3   = boundary(2.5);

// ── SVG helpers ──────────────────────────────────────────────────────────────
type EllipsePoint = { x: number; y: number };
const pt = (rx: number, ry: number, a: number): EllipsePoint => ({
  x: CX + rx * Math.cos(a),
  y: CY + ry * Math.sin(a),
});
const fmt = ({ x, y }: EllipsePoint) => `${x.toFixed(2)} ${y.toFixed(2)}`;

/** Clockwise arc band path between two ellipses, from angle a1 → a2 */
function band(outerA: number, outerB: number, innerA: number, innerB: number,
              a1: number, a2: number): string {
  const sweep = (a2 - a1 + 2 * Math.PI) % (2 * Math.PI);
  const lg = sweep > Math.PI ? 1 : 0;
  const o1 = pt(outerA, outerB, a1), o2 = pt(outerA, outerB, a2);
  const i2 = pt(innerA, innerB, a2), i1 = pt(innerA, innerB, a1);
  return `M ${fmt(o1)} A ${outerA} ${outerB} 0 ${lg} 1 ${fmt(o2)}` +
         ` L ${fmt(i2)} A ${innerA} ${innerB} 0 ${lg} 0 ${fmt(i1)} Z`;
}

/** Label position: middle of arc, between outer and inner ellipse */
function labelPos(outerA: number, outerB: number, innerA: number, innerB: number,
                  a1: number, a2: number): EllipsePoint {
  const sweep = (a2 - a1 + 2 * Math.PI) % (2 * Math.PI);
  const mid = a1 + sweep / 2;
  return pt((outerA + innerA) / 2, (outerB + innerB) / 2, mid);
}

// ── Chip selector ─────────────────────────────────────────────────────────────
const CHIPS = [
  { value: 50,    color: '#3b82f6', label: '50'  },
  { value: 100,   color: '#ef4444', label: '100' },
  { value: 250,   color: '#22c55e', label: '250' },
  { value: 500,   color: '#a855f7', label: '500' },
  { value: 1000,  color: '#eab308', label: '1K'  },
  { value: 5000,  color: '#f97316', label: '5K'  },
  { value: 10000, color: '#94a3b8', label: '10K' },
] as const;

const NUM_BG: Record<string, string> = {
  green: '#15803d', red: '#b91c1c', black: '#1e293b',
};

// ── Highlight maps ────────────────────────────────────────────────────────────
const PRESET_NOS: Record<string, number[]> = {
  voisins:  [0,2,3,4,7,12,15,18,19,21,22,25,26,28,29,32,35],
  tiers:    [5,8,10,11,13,16,23,24,27,30,33,36],
  orphelins:[1,6,9,14,17,20,31,34],
  jeuzero:  [0,3,12,15,26,32,35],
};

// ── Component ─────────────────────────────────────────────────────────────────
type Props = Readonly<{ onAddBets: (bets: Bet[]) => void; disabled?: boolean }>;

export default function RacetrackBoard({ onAddBets, disabled = false }: Props) {
  const [chip, setChip] = useState<number>(100);
  const [neighbors, setNeighbors] = useState<1 | 2 | 3 | 4>(1);
  const [hoverKey, setHoverKey] = useState<string | null>(null);
  const [hoverNum, setHoverNum] = useState<number | null>(null);

  const hlNums: Set<number> = new Set(
    hoverKey
      ? PRESET_NOS[hoverKey] ?? []
      : hoverNum !== null ? getNeighbors(hoverNum, neighbors) : [],
  );

  function addBets(fn: (c: number) => Bet[]) {
    if (!disabled) onAddBets(fn(chip));
  }
  function addNeighbors(n: number) {
    if (!disabled) onAddBets(getNeighbors(n, neighbors).map(num => ({ type: 'straight' as const, amount: chip, payload: num })));
  }

  const hover = (key: string) => () => { setHoverKey(key); setHoverNum(null); };
  const unhover = () => setHoverKey(null);

  // Section fill colours
  const fill = (key: string, base: string, lit: string) =>
    hoverKey === key ? lit : base;

  const numberPositions = WHEEL_SEQUENCE.map((n, i) => ({
    n, ...pt(NUM_A, NUM_B, θ(i)),
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'center' }}>

      {/* ── SVG Racetrack ─────────────────────────────────────────────── */}
      <svg width={SVG_W} height={SVG_H + 24} viewBox={`-12 -12 ${SVG_W + 24} ${SVG_H + 24}`}>

        {/* Track background ring */}
        <ellipse cx={CX} cy={CY} rx={OA + 12} ry={OB + 12} fill="#07111e" />

        {/* ── Voisins du Zéro arc (17 numbers, left side) ── */}
        <path d={band(OA, OB, IA, IB, B_27_28, B_7_8)}
          fill={fill('voisins', '#14532d', '#166534')}
          style={{ cursor: disabled ? 'default' : 'pointer' }}
          onClick={() => addBets(getVoisinsBets)}
          onMouseEnter={hover('voisins')} onMouseLeave={unhover} />

        {/* ── Jeu Zéro inner arc (inside Voisins, 7 numbers) ── */}
        <path d={band(IA, IB, JZ_IA, JZ_IB, B_32_33, B_2_3)}
          fill={fill('jeuzero', '#15803d', '#22c55e')}
          style={{ cursor: disabled ? 'default' : 'pointer' }}
          onClick={() => addBets(getJeuZeroBets)}
          onMouseEnter={hover('jeuzero')} onMouseLeave={unhover} />

        {/* ── Orphelins arc 1 (3 numbers, idx 8-10) ── */}
        <path d={band(OA, OB, IA, IB, B_7_8, B_10_11)}
          fill={fill('orphelins', '#1e3a5f', '#1e4976')}
          style={{ cursor: disabled ? 'default' : 'pointer' }}
          onClick={() => addBets(getOrphelinsBets)}
          onMouseEnter={hover('orphelins')} onMouseLeave={unhover} />

        {/* ── Tiers du Cylindre arc (12 numbers, idx 11-22) ── */}
        <path d={band(OA, OB, IA, IB, B_10_11, B_22_23)}
          fill={fill('tiers', '#1a3a1a', '#1e4a1e')}
          style={{ cursor: disabled ? 'default' : 'pointer' }}
          onClick={() => addBets(getTiersBets)}
          onMouseEnter={hover('tiers')} onMouseLeave={unhover} />

        {/* ── Orphelins arc 2 (5 numbers, idx 23-27) ── */}
        <path d={band(OA, OB, IA, IB, B_22_23, B_27_28)}
          fill={fill('orphelins', '#1e3a5f', '#1e4976')}
          style={{ cursor: disabled ? 'default' : 'pointer' }}
          onClick={() => addBets(getOrphelinsBets)}
          onMouseEnter={hover('orphelins')} onMouseLeave={unhover} />

        {/* ── Section dividers ── */}
        {[B_7_8, B_10_11, B_22_23, B_27_28].map((a, i) => {
          const o = pt(OA, OB, a), inn = pt(IA, IB, a);
          return <line key={i} x1={o.x} y1={o.y} x2={inn.x} y2={inn.y}
            stroke="rgba(255,255,255,0.2)" strokeWidth={1} />;
        })}

        {/* ── Jeu Zéro dividers ── */}
        {[B_32_33, B_2_3].map((a, i) => {
          const o = pt(IA, IB, a), inn = pt(JZ_IA, JZ_IB, a);
          return <line key={i} x1={o.x} y1={o.y} x2={inn.x} y2={inn.y}
            stroke="rgba(255,255,255,0.15)" strokeWidth={1} />;
        })}

        {/* ── Inner and outer ellipse borders ── */}
        <ellipse cx={CX} cy={CY} rx={OA} ry={OB} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={1} />
        <ellipse cx={CX} cy={CY} rx={IA} ry={IB} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth={1} />
        <ellipse cx={CX} cy={CY} rx={JZ_IA} ry={JZ_IB} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={1} />

        {/* ── Arc labels ── */}
        {/* Voisins */}
        {(() => {
          const p = labelPos(OA, OB, IA, IB, B_27_28, B_7_8);
          return <>
            <text x={p.x} y={p.y - 7} textAnchor="middle" pointerEvents="none"
              fill="rgba(255,255,255,0.9)" fontSize={11} fontWeight="800">Nagy széria</text>
            <text x={p.x} y={p.y + 6} textAnchor="middle" pointerEvents="none"
              fill="rgba(255,255,255,0.4)" fontSize={8}>17 szám</text>
          </>;
        })()}
        {/* Tiers */}
        {(() => {
          const p = labelPos(OA, OB, IA, IB, B_10_11, B_22_23);
          return <>
            <text x={p.x} y={p.y - 7} textAnchor="middle" pointerEvents="none"
              fill="rgba(255,255,255,0.9)" fontSize={11} fontWeight="800">Kis széria</text>
            <text x={p.x} y={p.y + 6} textAnchor="middle" pointerEvents="none"
              fill="rgba(255,255,255,0.4)" fontSize={8}>12 szám</text>
          </>;
        })()}
        {/* Orphelins arc 2 (larger, show label here) */}
        {(() => {
          const p = labelPos(OA, OB, IA, IB, B_22_23, B_27_28);
          return <>
            <text x={p.x} y={p.y - 5} textAnchor="middle" pointerEvents="none"
              fill="rgba(255,255,255,0.9)" fontSize={9} fontWeight="800">Árvák</text>
          </>;
        })()}
        {/* Orphelins arc 1 (smaller) */}
        {(() => {
          const p = labelPos(OA, OB, IA, IB, B_7_8, B_10_11);
          return <text x={p.x} y={p.y + 4} textAnchor="middle" pointerEvents="none"
            fill="rgba(255,255,255,0.9)" fontSize={9} fontWeight="800">Árvák</text>;
        })()}
        {/* Jeu Zéro */}
        {(() => {
          const p = labelPos(IA, IB, JZ_IA, JZ_IB, B_32_33, B_2_3);
          return <text x={p.x} y={p.y + 4} textAnchor="middle" pointerEvents="none"
            fill="rgba(255,255,255,0.85)" fontSize={8} fontWeight="700">Zéró</text>;
        })()}

        {/* ── Number cells ── */}
        {numberPositions.map(({ n, x, y }) => {
          const lit = hlNums.has(n);
          return (
            <g key={n} transform={`translate(${x.toFixed(1)},${y.toFixed(1)})`}
              style={{ cursor: disabled ? 'default' : 'pointer' }}
              onClick={() => addNeighbors(n)}
              onMouseEnter={() => { setHoverNum(n); setHoverKey(null); }}
              onMouseLeave={() => setHoverNum(null)}>
              <rect x={-11} y={-11} width={22} height={22} rx={4}
                fill={lit ? '#fbbf24' : NUM_BG[colorOf(n)]}
                stroke={lit ? '#f59e0b' : colorOf(n) === 'black' ? 'rgba(255,255,255,0.1)' : 'none'}
                strokeWidth={lit ? 1.5 : 0.5} />
              <text textAnchor="middle" dominantBaseline="middle"
                fill={lit ? '#0f172a' : '#fff'}
                fontSize={n >= 10 ? 7.5 : 9} fontWeight="800" pointerEvents="none">
                {n}
              </text>
            </g>
          );
        })}
      </svg>

      {/* ── Neighbour + chip controls ─────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', justifyContent: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#94a3b8', fontSize: 12 }}>
          <span>Szomszéd:</span>
          <button onClick={() => setNeighbors(n => Math.max(1, n - 1) as 1|2|3|4)} disabled={neighbors <= 1} style={btnSm}>−</button>
          <span style={{ color: '#fbbf24', fontWeight: 800, minWidth: 14, textAlign: 'center' }}>{neighbors}</span>
          <button onClick={() => setNeighbors(n => Math.min(4, n + 1) as 1|2|3|4)} disabled={neighbors >= 4} style={btnSm}>+</button>
        </div>
        <div style={{ display: 'flex', gap: 5 }}>
          {CHIPS.map(c => (
            <button key={c.value} onClick={() => setChip(c.value)} disabled={disabled} style={{
              width: 32, height: 32, borderRadius: '50%',
              border: chip === c.value ? `3px solid ${c.color}` : `2px solid ${c.color}44`,
              background: chip === c.value ? `${c.color}28` : 'transparent',
              color: c.color, fontWeight: 800, fontSize: 9, cursor: disabled ? 'default' : 'pointer',
              transition: 'all 0.1s', padding: 0,
            }}>{c.label}</button>
          ))}
        </div>
      </div>
    </div>
  );
}

const btnSm: React.CSSProperties = {
  width: 22, height: 22, borderRadius: 4,
  border: '1px solid rgba(148,163,184,0.25)',
  background: 'rgba(148,163,184,0.06)',
  color: '#e2e8f0', fontWeight: 700, fontSize: 13,
  cursor: 'pointer', padding: 0, lineHeight: 1,
  display: 'flex', alignItems: 'center', justifyContent: 'center',
};
