import { describe, it, expect, beforeEach } from 'vitest';
import { WALLET_STORAGE_KEY, DAILY_BONUS_AMOUNT } from '../../src/casino/state/wallet';
import { loadWallet, saveWallet, grantDailyBonus, credit, debit } from '../../src/casino/services/walletStorage';

describe('Wallet Storage', () => {
  beforeEach(() => {
    localStorage.removeItem(WALLET_STORAGE_KEY);
  });

  it('initializes when none exists', () => {
    const w = loadWallet();
    expect(w).toHaveProperty('balance');
    expect(w).toHaveProperty('firstSeenAt');
    expect(w.balance).toBe(0);
  });

  it('grants daily bonus only once per day', () => {
    const first = grantDailyBonus();
    expect(first.granted).toBe(true);
    expect(first.wallet.balance).toBeGreaterThanOrEqual(DAILY_BONUS_AMOUNT);

    const second = grantDailyBonus();
    expect(second.granted).toBe(false);
  });

  it('credit and debit adjust balance', () => {
    credit(500);
    let w = loadWallet();
    expect(w.balance).toBeGreaterThanOrEqual(500);
    const res = debit(200);
    expect(res.ok).toBe(true);
    w = loadWallet();
    expect(w.balance).toBeGreaterThanOrEqual(300);
  });
});
