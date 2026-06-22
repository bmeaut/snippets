import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { RouletteGame } from '../../src/games/roulette/RouletteGame';
import { WALLET_STORAGE_KEY } from '../../src/casino/state/wallet';

vi.mock('../../src/games/roulette/gameLogic', async () => {
  const actual = await vi.importActual<typeof import('../../src/games/roulette/gameLogic')>('../../src/games/roulette/gameLogic');

  return {
    ...actual,
    spinWheel: vi.fn(() => 32),
  };
});

vi.mock('../../src/casino/services/walletStorage', async () => {
  const readWallet = () => {
    const raw = localStorage.getItem(WALLET_STORAGE_KEY);
    if (!raw) {
      return { balance: 1000, firstSeenAt: Date.now() };
    }

    return JSON.parse(raw) as { balance: number; firstSeenAt: number };
  };

  const writeWallet = (wallet: { balance: number; firstSeenAt: number }) => {
    localStorage.setItem(WALLET_STORAGE_KEY, JSON.stringify(wallet));
    return wallet;
  };

  return {
    loadWallet: () => readWallet(),
    credit: (amount: number) => {
      const wallet = readWallet();
      return writeWallet({ ...wallet, balance: Math.max(0, wallet.balance + amount) });
    },
    debit: (amount: number) => {
      const wallet = readWallet();

      if (amount <= 0 || wallet.balance < amount) {
        return { ok: false, wallet };
      }

      return { ok: true, wallet: writeWallet({ ...wallet, balance: Math.max(0, wallet.balance - amount) }) };
    },
    saveWallet: (nextWallet: typeof wallet) => {
      writeWallet(nextWallet);
    },
    topUpWallet: (amount = 10000) => {
      const wallet = readWallet();
      return writeWallet({ ...wallet, balance: Math.max(0, wallet.balance + Math.floor(amount)) });
    },
  };
});

describe('roulette game shell', () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    localStorage.removeItem(WALLET_STORAGE_KEY);
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
    vi.useFakeTimers();
  });

  afterEach(() => {
    act(() => {
      vi.runOnlyPendingTimers();
      root.unmount();
    });
    vi.useRealTimers();
    container.remove();
  });

  it('mounts without throwing', () => {
    act(() => {
      root.render(<RouletteGame onReturnToMenu={() => undefined} />);
    });

    expect(container.textContent).toContain('Roulette');
  });

  it('credits the wallet after a winning red bet resolves', async () => {
    act(() => {
      root.render(<RouletteGame onReturnToMenu={() => undefined} />);
    });

    act(() => {
      const redButton = Array.from(container.querySelectorAll('button')).find((button) => button.textContent === 'RED');
      redButton?.click();
    });

    act(() => {
      const spinButton = Array.from(container.querySelectorAll('button')).find((button) => button.textContent === 'Spin');
      spinButton?.click();
    });

    await act(async () => {
      vi.advanceTimersByTime(3000);
    });

    expect(container.textContent).toContain('1100 Ft');
    expect(container.textContent).toContain('Payout credited');
  });
});