import React, { useMemo, useState } from 'react';
import type { Bet } from './gameLogic';
import { colorOf } from './gameLogic';

const CHIPS = [
  { value: 50,    color: '#3b82f6', label: '50'  },
  { value: 100,   color: '#ef4444', label: '100' },
  { value: 250,   color: '#22c55e', label: '250' },
  { value: 500,   color: '#a855f7', label: '500' },
  { value: 1000,  color: '#eab308', label: '1K'  },
  { value: 5000,  color: '#f97316', label: '5K'  },
  { value: 10000, color: '#94a3b8', label: '10K' },
] as const;

// Grid: row 0 = top (3,6,9..36), row 1 = middle (2,5..35), row 2 = bottom (1,4..34)
const NUMBER_ROWS = [
  [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
  [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
  [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
] as const;

const NUMBER_POS: Record<number, { row: number; col: number }> = {};
for (let r = 0; r < NUMBER_ROWS.length; r++) {
  for (let c = 0; c < NUMBER_ROWS[r].length; c++) {
    NUMBER_POS[NUMBER_ROWS[r][c]] = { row: r, col: c };
  }
}

function chipColorFor(amount: number): string {
  if (amount >= 10000) return '#94a3b8';
  if (amount >= 5000)  return '#f97316';
  if (amount >= 1000)  return '#eab308';
  if (amount >= 500)   return '#a855f7';
  if (amount >= 250)   return '#22c55e';
  if (amount >= 100)   return '#ef4444';
  return '#3b82f6';
}

function fmtAmt(n: number): string {
  if (n >= 10000) return `${n / 1000}K`;
  if (n >= 1000)  return `${n / 1000}K`;
  return String(n);
}

function betKey(bet: Omit<Bet, 'amount'>): string {
  if (bet.type === 'column' && Array.isArray(bet.payload)) {
    // identify column by its minimum number
    const min = Math.min(...(bet.payload as number[]));
    return `column-${min}`;
  }
  if (Array.isArray(bet.payload)) {
    return `${bet.type}-${[...(bet.payload as number[])].sort((a, b) => a - b).join('_')}`;
  }
  return `${bet.type}-${bet.payload}`;
}

// Position of a chip inside the number grid (as 0..1 fraction of width/height)
function chipPos(bet: Omit<Bet, 'amount'>): { x: number; y: number } | null {
  const COLS = 12, ROWS = 3;
  if (bet.type === 'straight' && typeof bet.payload === 'number' && bet.payload >= 1) {
    const p = NUMBER_POS[bet.payload];
    return p ? { x: (p.col + 0.5) / COLS, y: (p.row + 0.5) / ROWS } : null;
  }
  if (Array.isArray(bet.payload) && (bet.type === 'split' || bet.type === 'corner' || bet.type === 'street')) {
    const positions = (bet.payload as number[]).map(n => NUMBER_POS[n]).filter(Boolean);
    if (!positions.length) return null;
    const avgCol = positions.reduce((s, p) => s + p.col, 0) / positions.length;
    const avgRow = positions.reduce((s, p) => s + p.row, 0) / positions.length;
    return { x: (avgCol + 0.5) / COLS, y: (avgRow + 0.5) / ROWS };
  }
  return null;
}

type HoverBet = Omit<Bet, 'amount'> | null;

type Props = Readonly<{
  bets: Bet[];
  onAddBet: (bet: Bet) => void;
  onClearBets: () => void;
  onSpin: () => void;
  onReBet?: () => void;
  disabled?: boolean;
  totalStake?: number;
}>;

export default function BettingBoard({ bets, onAddBet, onClearBets, onSpin, onReBet, disabled = false, totalStake = 0 }: Props) {
  const [selectedChip, setSelectedChip] = useState<number>(100);
  const [hover, setHover] = useState<{ bet: HoverBet; x?: number; y?: number } | null>(null);

  // Map betKey → total amount for chip display
  const chipMap = useMemo(() => {
    const m = new Map<string, number>();
    for (const b of bets) {
      const k = betKey(b);
      m.set(k, (m.get(k) ?? 0) + b.amount);
    }
    return m;
  }, [bets]);

  // Non-straight chips to render as overlays on number grid
  const overlayChips = useMemo(() => {
    const seen = new Set<string>();
    const result: { key: string; x: number; y: number; amount: number }[] = [];
    for (const b of bets) {
      if (b.type === 'straight') continue;
      const pos = chipPos(b);
      if (!pos) continue;
      const k = betKey(b);
      if (seen.has(k)) continue;
      seen.add(k);
      result.push({ key: k, x: pos.x, y: pos.y, amount: chipMap.get(k) ?? 0 });
    }
    return result;
  }, [bets, chipMap]);

  function place(bet: Omit<Bet, 'amount'>) {
    if (disabled) return;
    onAddBet({ ...bet, amount: selectedChip });
  }

  function handleNumberClick(number: number, row: number, col: number, e: React.MouseEvent<HTMLDivElement>) {
    if (disabled) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const rx = (e.clientX - rect.left) / rect.width;
    const ry = (e.clientY - rect.top) / rect.height;
    const E = 0.3;
    const right  = rx > 1 - E && col < 11;
    const bottom = ry > 1 - E && row < 2;

    if (right && bottom) {
      const nums = [NUMBER_ROWS[row][col], NUMBER_ROWS[row][col + 1],
                    NUMBER_ROWS[row + 1][col], NUMBER_ROWS[row + 1][col + 1]].sort((a, b) => a - b);
      place({ type: 'corner', payload: nums });
    } else if (right) {
      place({ type: 'split', payload: [number, NUMBER_ROWS[row][col + 1]].sort((a, b) => a - b) });
    } else if (bottom) {
      place({ type: 'split', payload: [number, NUMBER_ROWS[row + 1][col]].sort((a, b) => a - b) });
    } else {
      place({ type: 'straight', payload: number });
    }
  }

  function handleNumberMouseMove(number: number, row: number, col: number, e: React.MouseEvent<HTMLDivElement>) {
    if (disabled) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const rx = (e.clientX - rect.left) / rect.width;
    const ry = (e.clientY - rect.top) / rect.height;
    const E = 0.3;
    const right  = rx > 1 - E && col < 11;
    const bottom = ry > 1 - E && row < 2;
    const COLS = 12, ROWS = 3;

    if (right && bottom) {
      setHover({ bet: { type: 'corner', payload: [] }, x: (col + 1) / COLS, y: (row + 1) / ROWS });
    } else if (right) {
      setHover({ bet: { type: 'split',  payload: [] }, x: (col + 1) / COLS, y: (row + 0.5) / ROWS });
    } else if (bottom) {
      setHover({ bet: { type: 'split',  payload: [] }, x: (col + 0.5) / COLS, y: (row + 1) / ROWS });
    } else {
      setHover({ bet: { type: 'straight', payload: number }, x: (col + 0.5) / COLS, y: (row + 0.5) / ROWS });
    }
  }

  const OUTSIDE_ZONES: { label: string; type: Bet['type']; payload: string; cls?: string }[] = [
    { label: '1–18', type: 'range',  payload: 'low'            },
    { label: 'Even', type: 'parity', payload: 'even'           },
    { label: 'Red',  type: 'color',  payload: 'red',  cls: 'red'   },
    { label: 'Black',type: 'color',  payload: 'black',cls: 'black' },
    { label: 'Odd',  type: 'parity', payload: 'odd'            },
    { label: '19–36',type: 'range',  payload: 'high'           },
  ];

  return (
    <div className="rl-board">
      {/* ── Main grid ─────────────────────────────────────────────────── */}
      <div className="rl-layout">

        {/* 0 */}
        <div className="rl-zero">
          <div
            className="rl-cell rl-cell--green"
            onClick={() => place({ type: 'straight', payload: 0 })}
            onMouseEnter={() => setHover(null)}
            role="button" tabIndex={0}
          >
            <span className="rl-cell__num">0</span>
            {(chipMap.get('straight-0') ?? 0) > 0 && (
              <span className="rl-chip-disc" style={{ background: chipColorFor(chipMap.get('straight-0')!) }}>
                {fmtAmt(chipMap.get('straight-0')!)}
              </span>
            )}
          </div>
        </div>

        {/* Number grid */}
        <div
          className="rl-numbers"
          onMouseLeave={() => setHover(null)}
        >
          {NUMBER_ROWS.map((row, ri) =>
            row.map((num, ci) => {
              const color = colorOf(num);
              const k = `straight-${num}`;
              const amt = chipMap.get(k) ?? 0;
              return (
                <div
                  key={num}
                  className={`rl-cell rl-cell--${color}`}
                  style={{ gridColumn: ci + 1, gridRow: ri + 1 }}
                  role="button" tabIndex={0}
                  onClick={e => handleNumberClick(num, ri, ci, e)}
                  onMouseMove={e => handleNumberMouseMove(num, ri, ci, e)}
                >
                  <span className="rl-cell__num">{num}</span>
                  {amt > 0 && (
                    <span className="rl-chip-disc" style={{ background: chipColorFor(amt) }}>
                      {fmtAmt(amt)}
                    </span>
                  )}
                </div>
              );
            })
          )}

          {/* Split / corner chip overlays */}
          {overlayChips.map(oc => (
            <div
              key={oc.key}
              className="rl-chip-disc rl-chip-disc--overlay"
              style={{ left: `${oc.x * 100}%`, top: `${oc.y * 100}%`, background: chipColorFor(oc.amount) }}
            >
              {fmtAmt(oc.amount)}
            </div>
          ))}

          {/* Hover preview chip */}
          {hover && hover.x !== undefined && !disabled && (
            <div
              className="rl-chip-disc rl-chip-disc--overlay rl-chip-disc--preview"
              style={{ left: `${hover.x! * 100}%`, top: `${hover.y! * 100}%`, background: chipColorFor(selectedChip) }}
            >
              {fmtAmt(selectedChip)}
            </div>
          )}
        </div>

        {/* 2:1 column buttons */}
        <div className="rl-col-btns">
          {NUMBER_ROWS.map((row, ri) => {
            const k = `column-${Math.min(...row)}`;
            const amt = chipMap.get(k) ?? 0;
            return (
              <div
                key={ri}
                className="rl-cell rl-cell--col21"
                role="button" tabIndex={0}
                onClick={() => place({ type: 'column', payload: [...row] })}
                onMouseEnter={() => setHover(null)}
              >
                {amt > 0 && (
                  <span className="rl-chip-disc" style={{ background: chipColorFor(amt) }}>{fmtAmt(amt)}</span>
                )}
                <span className="rl-cell__num">2:1</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Dozens ────────────────────────────────────────────────────── */}
      <div className="rl-dozens">
        {([{ label: '1st 12', payload: 1 }, { label: '2nd 12', payload: 2 }, { label: '3rd 12', payload: 3 }] as const).map(z => {
          const k = `dozen-${z.payload}`;
          const amt = chipMap.get(k) ?? 0;
          return (
            <div key={k} className="rl-cell rl-cell--outside" role="button" tabIndex={0}
              onClick={() => place({ type: 'dozen', payload: z.payload })}>
              {amt > 0 && <span className="rl-chip-disc" style={{ background: chipColorFor(amt) }}>{fmtAmt(amt)}</span>}
              <span className="rl-cell__num">{z.label}</span>
            </div>
          );
        })}
      </div>

      {/* ── Outside row ───────────────────────────────────────────────── */}
      <div className="rl-outside">
        {OUTSIDE_ZONES.map(z => {
          const k = `${z.type}-${z.payload}`;
          const amt = chipMap.get(k) ?? 0;
          return (
            <div key={k}
              className={`rl-cell rl-cell--outside${z.cls ? ` rl-cell--${z.cls}` : ''}`}
              role="button" tabIndex={0}
              onClick={() => place({ type: z.type, payload: z.payload })}
            >
              {amt > 0 && <span className="rl-chip-disc" style={{ background: chipColorFor(amt) }}>{fmtAmt(amt)}</span>}
              <span className="rl-cell__num">{z.label}</span>
            </div>
          );
        })}
      </div>

      {/* ── Chip selector ─────────────────────────────────────────────── */}
      <div className="rl-chip-row">
        {CHIPS.map(chip => (
          <button
            key={chip.value}
            className={`rl-chip-btn${selectedChip === chip.value ? ' rl-chip-btn--active' : ''}`}
            style={{ '--chip-color': chip.color } as React.CSSProperties}
            onClick={() => setSelectedChip(chip.value)}
            disabled={disabled}
            aria-label={`Select ${chip.label} Ft chip`}
          >
            <span className="rl-chip-btn__label">{chip.label}</span>
          </button>
        ))}
      </div>

      {/* ── Actions ───────────────────────────────────────────────────── */}
      <div className="rl-actions">
        <span className="rl-stake">Tét: {totalStake.toLocaleString('en-US')} Ft</span>
        <button className="rl-btn rl-btn--spin" onClick={onSpin} disabled={disabled || totalStake <= 0}>
          {disabled ? 'Forog…' : 'Pörgetés'}
        </button>
        {onReBet && (
          <button className="rl-btn rl-btn--rebet" onClick={onReBet} disabled={disabled}>
            Újra tét
          </button>
        )}
        <button className="rl-btn rl-btn--clear" onClick={onClearBets} disabled={disabled || totalStake <= 0}>
          Töröl
        </button>
      </div>
    </div>
  );
}
