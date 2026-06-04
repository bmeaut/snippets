export type Color = 'red' | 'black' | 'green';

// Authentic European wheel sequence (clockwise)
export const WHEEL_SEQUENCE: number[] = [
  0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26,
];

export function colorOf(n: number): Color {
  if (n === 0) return 'green';
  const idx = WHEEL_SEQUENCE.indexOf(n);
  if (idx === -1) return 'black';
  // alternate colors starting with index 1 = red
  return idx % 2 === 1 ? 'red' : 'black';
}

export type WinningParity = 'odd' | 'even' | 'zero';

export interface WinningProperties {
  color: Color;
  parity: WinningParity;
  dozen: 0 | 1 | 2 | 3;
}

export function getWinningProperties(winning: number): WinningProperties {
  const color = colorOf(winning);
  let parity: WinningParity = 'zero';
  if (winning !== 0) {
    parity = winning % 2 === 0 ? 'even' : 'odd';
  }

  let dozen: 0 | 1 | 2 | 3 = 0;
  if (winning >= 1 && winning <= 12) {
    dozen = 1;
  } else if (winning >= 13 && winning <= 24) {
    dozen = 2;
  } else if (winning >= 25 && winning <= 36) {
    dozen = 3;
  }

  return { color, parity, dozen };
}

export type BetType = 'color' | 'parity' | 'range' | 'dozen' | 'column' | 'straight' | 'split' | 'street' | 'corner' | 'line';

export interface Bet {
  type: BetType;
  amount: number;
  // payloads:
  // - color: 'red'|'black'
  // - parity: 'odd'|'even'
  // - range: 'low'|'high'
  // - dozen: 1|2|3
  // - column: [numbers in a 2:1 row]
  // - straight: 0..36 (number)
  // - split: [n1,n2]
  // - street: [n1,n2,n3]
  // - corner: [n1,n2,n3,n4]
  // - line: [n1..n6]
  payload: string | number | number[];
}

export function spinWheel(rng = Math.random): number {
  // 0..36 inclusive
  return Math.floor(rng() * 37);
}

function normalizePayloadText(payload: Bet['payload']) {
  return String(payload).trim().toLowerCase();
}

function normalizeNumberPayload(payload: Bet['payload']) {
  if (Array.isArray(payload)) {
    return payload
      .map(Number)
      .filter((entry) => Number.isFinite(entry));
  }

  const parsed = Number(payload);
  return Number.isFinite(parsed) ? [parsed] : [];
}

function isWinningColorBet(bet: Bet, winning: number, stake: number): number {
  if (winning === 0) return 0;
  const want = normalizePayloadText(bet.payload) as 'red' | 'black';
  return colorOf(winning) === want ? stake * 2 : 0;
}

function isWinningParityBet(bet: Bet, winning: number, stake: number): number {
  if (winning === 0) return 0;
  const want = normalizePayloadText(bet.payload) as 'odd' | 'even';

  if (want === 'odd' && winning % 2 === 1) return stake * 2;
  if (want === 'even' && winning % 2 === 0) return stake * 2;

  return 0;
}

function isWinningDozenBet(bet: Bet, winning: number, stake: number): number {
  if (winning === 0) return 0;

  const want = Number(bet.payload);
  if (want === 1 && winning >= 1 && winning <= 12) return stake * 3;
  if (want === 2 && winning >= 13 && winning <= 24) return stake * 3;
  if (want === 3 && winning >= 25 && winning <= 36) return stake * 3;

  return 0;
}

function isWinningColumnBet(bet: Bet, winning: number, stake: number): number {
  const nums = normalizeNumberPayload(bet.payload);
  return nums.includes(winning) ? stake * 3 : 0;
}

function isWinningRangeBet(bet: Bet, winning: number, stake: number): number {
  if (winning === 0) return 0;

  const want = normalizePayloadText(bet.payload) as 'low' | 'high';
  if (want === 'low' && winning >= 1 && winning <= 18) return stake * 2;
  if (want === 'high' && winning >= 19 && winning <= 36) return stake * 2;

  return 0;
}

function isWinningNumberGroupBet(bet: Bet, winning: number, stake: number, payoutMultiplier: number) {
  const nums = normalizeNumberPayload(bet.payload);
  return nums.includes(winning) ? stake * payoutMultiplier : 0;
}

function isWinningStraightBet(bet: Bet, winning: number, stake: number): number {
  const want = Number(bet.payload);
  return want === winning ? stake * 36 : 0;
}

export function evaluateBet(bet: Bet, winning: number): number {
  const stake = Math.floor(bet.amount);
  if (stake <= 0) return 0;

  switch (bet.type) {
    case 'color':
      return isWinningColorBet(bet, winning, stake);
    case 'parity':
      return isWinningParityBet(bet, winning, stake);
    case 'range':
      return isWinningRangeBet(bet, winning, stake);
    case 'dozen':
      return isWinningDozenBet(bet, winning, stake);
    case 'column':
      return isWinningColumnBet(bet, winning, stake);
    case 'split':
      return isWinningNumberGroupBet(bet, winning, stake, 18);
    case 'street':
      return isWinningNumberGroupBet(bet, winning, stake, 12);
    case 'corner':
      return isWinningNumberGroupBet(bet, winning, stake, 9);
    case 'line':
      return isWinningNumberGroupBet(bet, winning, stake, 6);
    case 'straight':
      return isWinningStraightBet(bet, winning, stake);
    default:
      return 0;
  }
}

export function evaluateBets(bets: Bet[], winning: number) {
  let totalPayout = 0;
  for (const b of bets) {
    totalPayout += evaluateBet(b, winning);
  }
  return { winning, totalPayout };
}

// ── Racetrack helpers ────────────────────────────────────────────────────────

export function getNeighbors(number: number, count: number): number[] {
  const idx = WHEEL_SEQUENCE.indexOf(number);
  if (idx === -1) return [number];
  const result: number[] = [];
  for (let i = -count; i <= count; i++) {
    result.push(WHEEL_SEQUENCE[((idx + i) + WHEEL_SEQUENCE.length) % WHEEL_SEQUENCE.length]);
  }
  return result;
}

// Tiers du Cylindre — 6 splits (12 numbers, 5/8 section of wheel opposite zero)
export function getTiersBets(chip: number): Bet[] {
  return [
    { type: 'split', amount: chip, payload: [5, 8] },
    { type: 'split', amount: chip, payload: [10, 11] },
    { type: 'split', amount: chip, payload: [13, 16] },
    { type: 'split', amount: chip, payload: [23, 24] },
    { type: 'split', amount: chip, payload: [27, 30] },
    { type: 'split', amount: chip, payload: [33, 36] },
  ];
}

// Voisins du Zéro — 9 chips (17 numbers around zero)
export function getVoisinsBets(chip: number): Bet[] {
  return [
    { type: 'street', amount: chip * 2, payload: [0, 2, 3] },   // trio, 2 chips
    { type: 'split',  amount: chip,     payload: [4, 7] },
    { type: 'split',  amount: chip,     payload: [12, 15] },
    { type: 'split',  amount: chip,     payload: [18, 21] },
    { type: 'split',  amount: chip,     payload: [19, 22] },
    { type: 'corner', amount: chip * 2, payload: [25, 26, 28, 29] }, // corner, 2 chips
    { type: 'split',  amount: chip,     payload: [32, 35] },
  ];
}

// Orphelins — 5 chips (8 numbers not covered by Tiers or Voisins)
export function getOrphelinsBets(chip: number): Bet[] {
  return [
    { type: 'straight', amount: chip, payload: 1 },
    { type: 'split',    amount: chip, payload: [6, 9] },
    { type: 'split',    amount: chip, payload: [14, 17] },
    { type: 'split',    amount: chip, payload: [17, 20] },
    { type: 'split',    amount: chip, payload: [31, 34] },
  ];
}

// Jeu Zéro — 4 chips (7 numbers near zero)
export function getJeuZeroBets(chip: number): Bet[] {
  return [
    { type: 'split',    amount: chip, payload: [0, 3] },
    { type: 'split',    amount: chip, payload: [12, 15] },
    { type: 'straight', amount: chip, payload: 26 },
    { type: 'split',    amount: chip, payload: [32, 35] },
  ];
}
