export interface WalletState {
  balance: number;
  firstSeenAt: number; // timestamp
  lastDailyBonusAt?: number; // timestamp when daily bonus was last granted
}

export const WALLET_STORAGE_KEY = 'casino_wallet_v1';
export const DAILY_BONUS_AMOUNT = 10000; // 10.000 Ft

export function makeInitialWallet(now = Date.now()): WalletState {
  return {
    balance: 0,
    firstSeenAt: now,
    lastDailyBonusAt: undefined,
  };
}

export function isSameLocalDay(a: number, b: number) {
  const da = new Date(a);
  const db = new Date(b);
  return da.getFullYear() === db.getFullYear() && da.getMonth() === db.getMonth() && da.getDate() === db.getDate();
}
