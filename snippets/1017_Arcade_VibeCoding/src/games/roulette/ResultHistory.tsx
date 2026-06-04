import React from 'react';
import { colorOf } from './gameLogic';

const BG: Record<string, string> = {
  red:   '#ef4444',
  black: '#1f2937',
  green: '#16a34a',
};

const BORDER: Record<string, string> = {
  red:   '#f87171',
  black: '#374151',
  green: '#4ade80',
};

type Props = Readonly<{ history: number[] }>;

export default function ResultHistory({ history }: Props) {
  // Show up to 10 entries, newest first (left)
  const entries = [...history].reverse().slice(0, 10);

  return (
    <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'center' }}>
      {entries.map((n, i) => {
        const col = colorOf(n);
        return (
          <div
            key={`${i}-${n}`}
            style={{
              width: 34,
              height: 34,
              borderRadius: '50%',
              background: BG[col],
              border: `2px solid ${BORDER[col]}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontWeight: 800,
              fontSize: n >= 10 ? 11 : 13,
              boxShadow: `0 0 8px ${BG[col]}66`,
              flexShrink: 0,
              animation: i === 0 ? 'rt-badge-in 0.3s ease' : undefined,
            }}
          >
            {n}
          </div>
        );
      })}
      {/* Empty placeholder slots */}
      {Array.from({ length: Math.max(0, 10 - entries.length) }).map((_, i) => (
        <div
          key={`empty-${i}`}
          style={{
            width: 34,
            height: 34,
            borderRadius: '50%',
            border: '2px solid rgba(148,163,184,0.15)',
            flexShrink: 0,
          }}
        />
      ))}
    </div>
  );
}
