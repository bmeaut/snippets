import { WalletState, WALLET_STORAGE_KEY, makeInitialWallet, DAILY_BONUS_AMOUNT, isSameLocalDay } from '../state/wallet';

function readRaw(): WalletState | null {
  try {
    const raw = localStorage.getItem(WALLET_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (typeof parsed.balance !== 'number' || typeof parsed.firstSeenAt !== 'number') return null;
    return parsed as WalletState;
  } catch (error) {
    console.warn('Failed to read casino wallet', error);
    return null;
  }
}

export function loadWallet(): WalletState {
  const now = Date.now();
  const existing = readRaw();
  if (existing) return existing;
  const initial = makeInitialWallet(now);
  saveWallet(initial);
  return initial;
}

export function saveWallet(state: WalletState) {
  try {
    localStorage.setItem(WALLET_STORAGE_KEY, JSON.stringify(state));
  } catch (error) {
    console.warn('Failed to save casino wallet', error);
  }
}

export function credit(amount: number): WalletState {
  const w = loadWallet();
  w.balance = Math.max(0, w.balance + amount);
  saveWallet(w);
  return w;
}

export function topUpWallet(amount = 10000): WalletState {
  return credit(Math.max(0, Math.floor(amount)));
}

export function debit(amount: number): { ok: boolean; wallet: WalletState } {
  const w = loadWallet();
  if (amount <= 0) return { ok: false, wallet: w };
  if (w.balance < amount) return { ok: false, wallet: w };
  w.balance = Math.max(0, w.balance - amount);
  saveWallet(w);
  return { ok: true, wallet: w };
}

export function grantDailyBonus(): { granted: boolean; wallet: WalletState } {
  const now = Date.now();
  const w = loadWallet();
  if (w.lastDailyBonusAt && isSameLocalDay(w.lastDailyBonusAt, now)) {
    return { granted: false, wallet: w };
  }
  w.balance = Math.max(0, w.balance + DAILY_BONUS_AMOUNT);
  w.lastDailyBonusAt = now;
  saveWallet(w);
  return { granted: true, wallet: w };
}
