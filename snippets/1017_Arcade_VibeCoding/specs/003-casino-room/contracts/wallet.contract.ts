/**
 * Wallet Contract
 *
 * Shared casino bankroll persistence and settlement interface.
 */

export interface WalletState {
  balance: number;
  firstSeenAt: string;
  lastDailyBonusAt: string | null;
}

export interface WalletService {
  load(): WalletState;
  save(state: WalletState): void;
  grantDailyBonus(currentTime: Date): WalletState;
  debit(amount: number): WalletState;
  credit(amount: number): WalletState;
}

export const validateWalletState = (state: any): state is WalletState => {
  return (
    state &&
    typeof state.balance === 'number' &&
    Number.isInteger(state.balance) &&
    state.balance >= 0 &&
    typeof state.firstSeenAt === 'string' &&
    (state.lastDailyBonusAt === null || typeof state.lastDailyBonusAt === 'string')
  );
};