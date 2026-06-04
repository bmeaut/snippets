import { describe, it, expect, beforeEach } from 'vitest';
import { evaluateBet, evaluateBets, Bet } from '../../src/games/roulette/gameLogic';
import { WALLET_STORAGE_KEY } from '../../src/casino/state/wallet';
import { credit, debit, loadWallet } from '../../src/casino/services/walletStorage';

describe('Roulette payouts', () => {
  beforeEach(() => {
    localStorage.removeItem(WALLET_STORAGE_KEY);
    credit(1000);
  });

  it('pays straight 35:1 (36x total)', () => {
    const b: Bet = { type: 'straight', amount: 10, payload: 7 };
    const res = evaluateBets([b], 7);
    expect(res.totalPayout).toBe(360); // 10 * 36
  });

  it('pays color 1:1', () => {
    const b: Bet = { type: 'color', amount: 20, payload: 'red' };
    const res = evaluateBets([b], 1); // 1 is red
    expect(res.totalPayout).toBe(40);
  });

  it('matches uppercase red payloads after normalization', () => {
    const bet: Bet = { type: 'color', amount: 20, payload: 'Red' };
    expect(evaluateBet(bet, 1)).toBe(40);
  });

  it('pays range bets on the low and high outside zones', () => {
    expect(evaluateBet({ type: 'range', amount: 10, payload: 'low' }, 17)).toBe(20);
    expect(evaluateBet({ type: 'range', amount: 10, payload: 'high' }, 35)).toBe(20);
    expect(evaluateBet({ type: 'range', amount: 10, payload: 'low' }, 25)).toBe(0);
  });

  it('treats zero as a loss for all even-money bets', () => {
    const bets: Bet[] = [
      { type: 'color', amount: 10, payload: 'red' },
      { type: 'color', amount: 10, payload: 'black' },
      { type: 'parity', amount: 10, payload: 'odd' },
      { type: 'parity', amount: 10, payload: 'even' },
    ];

    for (const bet of bets) {
      expect(evaluateBet(bet, 0)).toBe(0);
    }
  });

  it('pays parity bets only on the matching odd or even outcome', () => {
    expect(evaluateBet({ type: 'parity', amount: 10, payload: 'odd' }, 3)).toBe(20);
    expect(evaluateBet({ type: 'parity', amount: 10, payload: 'even' }, 4)).toBe(20);
    expect(evaluateBet({ type: 'parity', amount: 10, payload: 'odd' }, 4)).toBe(0);
    expect(evaluateBet({ type: 'parity', amount: 10, payload: 'even' }, 3)).toBe(0);
  });

  it('handles dozen boundary values correctly', () => {
    const stake = 10;
    const cases: Array<[number, number, number]> = [
      [1, 0, 0],
      [1, 1, 30],
      [1, 12, 30],
      [1, 13, 0],
      [2, 1, 0],
      [2, 13, 30],
      [2, 24, 30],
      [2, 12, 0],
      [3, 1, 0],
      [3, 25, 30],
      [3, 36, 30],
      [3, 24, 0],
      [3, 13, 0],
    ];

    for (const [payload, winning, expected] of cases) {
      expect(evaluateBet({ type: 'dozen', amount: stake, payload }, winning)).toBe(expected);
    }
  });

  it('rejects straight bets on non-matching numbers', () => {
    expect(evaluateBet({ type: 'straight', amount: 10, payload: 7 }, 8)).toBe(0);
  });

  it('integration: deduct stake and credit payout', () => {
    // place two bets: straight 10 on 7, color black 20
    const bets: Bet[] = [
      { type: 'straight', amount: 10, payload: 7 },
      { type: 'color', amount: 20, payload: 'black' },
    ];
    const before = loadWallet();
    // deduct stake
    const totalStake = bets.reduce((s, b) => s + b.amount, 0);
    const dec = debit(totalStake);
    expect(dec.ok).toBe(true);
    const afterDebit = loadWallet();
    expect(afterDebit.balance).toBe(before.balance - totalStake);

    // winning number 7 (straight hits, color red)
    const res = evaluateBets(bets, 7);
    // straight pays 360, color loses
    expect(res.totalPayout).toBe(360);
    credit(res.totalPayout);
    const final = loadWallet();
    expect(final.balance).toBe(afterDebit.balance + 360);
  });
});
