import { describe, it, expect } from 'vitest';
import { evaluateBet, evaluateBets, Bet } from '../../src/games/roulette/gameLogic';

describe('Roulette advanced payouts', () => {
  it('pays split 17:1 (18x total)', () => {
    const b: Bet = { type: 'split', amount: 5, payload: [7, 10] };
    const res = evaluateBets([b], 7);
    expect(res.totalPayout).toBe(90); // 5 * 18
  });

  it('treats split as a loss when the winning number is not in the pair', () => {
    const b: Bet = { type: 'split', amount: 5, payload: [7, 10] };
    expect(evaluateBet(b, 8)).toBe(0);
  });

  it('pays street 11:1 (12x total)', () => {
    const b: Bet = { type: 'street', amount: 2, payload: [1, 2, 3] };
    const res = evaluateBets([b], 2);
    expect(res.totalPayout).toBe(24);
  });

  it('treats street as a loss off the three-number row', () => {
    const b: Bet = { type: 'street', amount: 2, payload: [1, 2, 3] };
    expect(evaluateBet(b, 4)).toBe(0);
  });

  it('pays corner 8:1 (9x total)', () => {
    const b: Bet = { type: 'corner', amount: 4, payload: [1, 2, 4, 5] };
    const res = evaluateBets([b], 5);
    expect(res.totalPayout).toBe(36);
  });

  it('treats corner as a loss when the winning number is outside the square', () => {
    const b: Bet = { type: 'corner', amount: 4, payload: [1, 2, 4, 5] };
    expect(evaluateBet(b, 3)).toBe(0);
  });

  it('pays line 5:1 (6x total)', () => {
    const b: Bet = { type: 'line', amount: 3, payload: [1, 2, 3, 4, 5, 6] };
    const res = evaluateBets([b], 6);
    expect(res.totalPayout).toBe(18);
  });

  it('treats line as a loss when the winning number is outside the six-number line', () => {
    const b: Bet = { type: 'line', amount: 3, payload: [1, 2, 3, 4, 5, 6] };
    expect(evaluateBet(b, 7)).toBe(0);
  });
});
