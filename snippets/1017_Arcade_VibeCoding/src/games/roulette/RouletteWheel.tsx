import React, { useEffect, useMemo, useState } from 'react';
import { WHEEL_SEQUENCE, colorOf } from './gameLogic';

type Props = {
  rotationDeg: number;
  durationMs: number;
  spinning: boolean;
  ballActive: boolean;
  numbers?: number[];
};

const DEFAULT_NUMBERS = WHEEL_SEQUENCE;

function sectorPath(startDeg: number, endDeg: number, innerR = 60, outerR = 100) {
  const start = (Math.PI / 180) * startDeg;
  const end = (Math.PI / 180) * endDeg;
  const x1 = Math.cos(start) * outerR;
  const y1 = Math.sin(start) * outerR;
  const x2 = Math.cos(end) * outerR;
  const y2 = Math.sin(end) * outerR;
  const x3 = Math.cos(end) * innerR;
  const y3 = Math.sin(end) * innerR;
  const x4 = Math.cos(start) * innerR;
  const y4 = Math.sin(start) * innerR;
  const large = end - start <= Math.PI ? 0 : 1;
  return `M ${x1} ${y1} A ${outerR} ${outerR} 0 ${large} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerR} ${innerR} 0 ${large} 0 ${x4} ${y4} Z`;
}

export default function RouletteWheel({
  rotationDeg,
  durationMs,
  spinning,
  ballActive,
  numbers = DEFAULT_NUMBERS,
}: Readonly<Props>) {
  const sectors = numbers.length;
  const sectorAngle = 360 / sectors;

  const items = useMemo(() => {
    return numbers.map((n, i) => {
      const angle = i * sectorAngle;
      return { n, angle, color: colorOf(n) };
    });
  }, [numbers, sectorAngle]);

  const [ballPos, setBallPos] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    if (!ballActive) {
      setBallPos(null);
      return;
    }

    // Ball starts at ~60° (upper-right) and circles CCW to -90° (top, the pointer)
    const startAngle = Math.PI / 3;          // 60° = upper-right
    const endAngle = -Math.PI / 2;           // -90° = top (where pointer is)
    const rimR = 100;                         // SVG units, outer pocket edge
    const pocketR = 80;                       // SVG units, mid-pocket
    // CCW total: 5 full rotations + arc from startAngle CCW to endAngle
    const ccwArc = ((startAngle - endAngle) + 2 * Math.PI) % (2 * Math.PI);
    const totalAngleDelta = -(5 * 2 * Math.PI + ccwArc);

    const startTime = performance.now();
    let rafId: number;

    const animate = (now: number) => {
      const t = Math.min((now - startTime) / durationMs, 1);
      const te = 1 - Math.pow(1 - t, 3); // ease-out cubic

      const angle = startAngle + totalAngleDelta * te;

      // Radius: stays at rim until 70% through, then eases into pocket
      const rt = t < 0.7 ? 0 : (t - 0.7) / 0.3;
      const r = rimR - (rimR - pocketR) * (rt * rt);

      setBallPos({ x: Math.cos(angle) * r, y: Math.sin(angle) * r });

      if (t < 1) {
        rafId = requestAnimationFrame(animate);
      }
    };

    rafId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafId);
  }, [ballActive, durationMs]);

  const wheelStyle: React.CSSProperties = {
    width: 220,
    height: 220,
    borderRadius: '50%',
    overflow: 'visible',
    transform: `rotate(${rotationDeg}deg)`,
    transition: spinning ? `transform ${durationMs}ms cubic-bezier(.22,.9,.3,1)` : 'none',
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <svg width={300} height={300} viewBox="0 0 300 300" style={{ overflow: 'visible' }}>
        <defs>
          <radialGradient id="pocketShade" cx="50%" cy="30%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.08)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0.12)" />
          </radialGradient>
          <filter id="wheelShadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="6" stdDeviation="8" floodOpacity="0.25" />
          </filter>
          <filter id="ballGlow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        <g transform="translate(150,150)">
          {/* Rotating wheel */}
          <g style={wheelStyle} filter="url(#wheelShadow)">
            <circle cx={0} cy={0} r={106} fill="#0b1220" stroke="#000" strokeWidth={2} />

            {items.map((it, idx) => {
              const start = it.angle - sectorAngle / 2;
              const end = it.angle + sectorAngle / 2;
              const path = sectorPath(start, end, 62, 100);
              const pocketColor =
                it.color === 'green' ? '#16a34a' : it.color === 'red' ? '#ef4444' : '#111827';
              const mid = ((start + end) / 2) * (Math.PI / 180);
              const lx = Math.cos(mid) * 80;
              const ly = Math.sin(mid) * 80;
              return (
                <g key={`${it.n}-${idx}`}>
                  <path d={path} fill={pocketColor} stroke="#111" strokeWidth={0.8} />
                  <path d={path} fill="url(#pocketShade)" opacity={0.12} />
                  <text
                    x={lx} y={ly + 4}
                    fill="#fff" fontSize={10} fontWeight={700} textAnchor="middle"
                    transform={`rotate(${it.angle} ${lx} ${ly})`}
                  >
                    {it.n}
                  </text>
                </g>
              );
            })}

            <circle cx={0} cy={0} r={54} fill="#0b1220" stroke="#111827" strokeWidth={3} />
            <circle cx={0} cy={0} r={36} fill="#111827" />
          </g>

          {/* Ball — fixed (not rotating with wheel) */}
          {ballPos && (
            <g filter="url(#ballGlow)">
              <circle cx={ballPos.x} cy={ballPos.y} r={6} fill="white" opacity={0.95} />
            </g>
          )}
        </g>
      </svg>
    </div>
  );
}
