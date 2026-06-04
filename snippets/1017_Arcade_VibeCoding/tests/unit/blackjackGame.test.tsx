import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { BlackjackGame } from '../../src/games/blackjack/BlackjackGame';
import { WALLET_STORAGE_KEY } from '../../src/casino/state/wallet';

let handMode: 'default' | 'pair' | 'pair-second-bust' = 'default';

vi.mock('../../src/games/blackjack/gameLogic', () => {
  type Card = { rank: string; suit: '♠' | '♣' | '♥' | '♦' };
  type State = {
    deck: Card[];
    playerHands: Card[][];
    activeHandIndex: number;
    handFlags: Array<{ splitAces: boolean }>;
    player: Card[];
    dealer: Card[];
    bet: number;
    status: 'betting' | 'player-turn' | 'dealer-turn' | 'settled';
    result: 'player-win' | 'dealer-win' | 'push' | 'player-blackjack' | null;
  };

  const valueOfRank = (rank: string) => {
    if (rank === 'A') return 11;
    if (['K', 'Q', 'J'].includes(rank)) return 10;
    return Number(rank);
  };

  const handValue = (cards: Card[]) => {
    const base = cards.filter(Boolean).reduce((total, card) => total + valueOfRank(card.rank), 0);
    const aces = cards.filter((card): card is Card => Boolean(card) && card.rank === 'A').length;
    let value = base;
    while (value > 21 && aces > 0) {
      value -= 10;
    }
    return value;
  };

  const makeState = (playerHands: Card[][], dealer: Card[], deck: Card[], bet: number, status: State['status'], activeHandIndex = 0, handFlags: Array<{ splitAces: boolean }> = playerHands.map(() => ({ splitAces: false }))): State => ({
    deck,
    playerHands,
    activeHandIndex,
    handFlags,
    player: playerHands[activeHandIndex],
    dealer,
    bet,
    status,
    result: null,
  });

  const revealed = (rank: string, suit: Card['suit']) => ({ rank, suit, isRevealed: true });

  return {
    startRound: (): State => ({
      deck: [],
      playerHands: [],
      activeHandIndex: 0,
      handFlags: [],
      player: [],
      dealer: [],
      bet: 0,
      status: 'betting',
      result: null,
    }),
    placeBet: (_state: State, bet: number): State => ({
      ...makeState(
        handMode === 'pair' || handMode === 'pair-second-bust'
          ? [[revealed('8', '♠'), revealed('8', '♦')]]
          : [[revealed('10', '♠'), revealed('Q', '♦')]],
        [revealed('10', '♥'), { rank: '6', suit: '♠', isRevealed: false, isAnimated: true }],
        handMode === 'pair'
          ? [{ rank: '2', suit: '♣' }, { rank: '3', suit: '♣' }, { rank: '6', suit: '♣' }, { rank: '7', suit: '♣' }]
          : handMode === 'pair-second-bust'
            ? [{ rank: '2', suit: '♣' }, { rank: '9', suit: '♣' }, { rank: 'K', suit: '♣' }, { rank: '7', suit: '♣' }]
            : [{ rank: '2', suit: '♣' }, { rank: '6', suit: '♣' }],
        bet,
        'player-turn',
      ),
      bet,
    }),
    split: (state: State, walletBalance: number) => {
      const currentHand = state.playerHands[state.activeHandIndex] ?? [];
      const canSplit = state.status === 'player-turn' && state.playerHands.length === 1 && currentHand.length === 2 && walletBalance >= state.bet && valueOfRank(currentHand[0].rank) === valueOfRank(currentHand[1].rank);

      if (!canSplit) {
        return { accepted: false, reason: 'not-initial-hand' as const, additionalBet: 0, state };
      }

      const splitAces = currentHand[0].rank === 'A' && currentHand[1].rank === 'A';
      const playerHands = [
        [revealed(currentHand[0].rank, currentHand[0].suit), revealed(state.deck[0]?.rank ?? '2', state.deck[0]?.suit ?? '♣')],
        [revealed(currentHand[1].rank, currentHand[1].suit), revealed(state.deck[1]?.rank ?? '3', state.deck[1]?.suit ?? '♣')],
      ];

      return {
        accepted: true,
        reason: null,
        additionalBet: state.bet,
        state: makeState(playerHands, [revealed('10', '♥'), revealed('6', '♠')], state.deck.slice(2), state.bet, splitAces ? 'dealer-turn' : 'player-turn', 0, [{ splitAces }, { splitAces }]),
      };
    },
    playerHit: (state: State) => {
      if (state.status !== 'player-turn') return state;
      const nextCard = state.deck[0] ?? revealed('2', '♣');
      const updatedHand = [...state.player, revealed(nextCard.rank, nextCard.suit)];
      const playerHands = state.playerHands.map((hand, index) => (index === state.activeHandIndex ? updatedHand : hand));
      const nextState = makeState(playerHands, state.dealer, state.deck.slice(1), state.bet, state.status, state.activeHandIndex, state.handFlags);
      return handValue(updatedHand) > 21
        ? ({ ...nextState, activeHandIndex: Math.min(state.activeHandIndex + 1, playerHands.length - 1), player: playerHands[Math.min(state.activeHandIndex + 1, playerHands.length - 1)], status: state.activeHandIndex + 1 < playerHands.length ? 'player-turn' : 'dealer-turn' } as State)
        : nextState;
    },
    playerStand: (state: State): State => {
      if (state.status !== 'player-turn') return state;
      const nextIndex = state.activeHandIndex + 1;
      if (nextIndex < state.playerHands.length) {
        return { ...state, activeHandIndex: nextIndex, player: state.playerHands[nextIndex], status: 'player-turn' };
      }
      const allBust = state.playerHands.every((hand) => handValue(hand) > 21);
      if (allBust) {
        return { ...state, status: 'settled', result: 'dealer-win' };
      }
      return { ...state, status: 'dealer-turn' };
    },
    playerDoubleDown: (state: State) => {
      if (state.status !== 'player-turn') return state;
      const nextCard = state.deck[0] ?? revealed('2', '♣');
      const updatedHand = [...state.player, revealed(nextCard.rank, nextCard.suit)];
      const playerHands = state.playerHands.map((hand, index) => (index === state.activeHandIndex ? updatedHand : hand));
      const nextIndex = state.activeHandIndex + 1;
      return {
        ...state,
        deck: state.deck.slice(1),
        playerHands,
        player: updatedHand,
        activeHandIndex: nextIndex < playerHands.length ? nextIndex : state.activeHandIndex,
        status: nextIndex < playerHands.length ? 'player-turn' : 'dealer-turn',
      };
    },
    drawOne: (deck: Card[]) => ({ card: deck[0], deck: deck.slice(1) }),
    bestHandValue: (cards: Card[]) => handValue(cards),
    isBust: (cards: Card[]) => handValue(cards) > 21,
    isBlackjack: (cards: Card[]) => cards.length === 2 && handValue(cards) === 21,
    evaluateBets: (state: State) => {
      const dealerBest = handValue(state.dealer);
      const handResults = state.playerHands.map((hand, handIndex) => {
        const total = handValue(hand);
        const splitAce = state.handFlags[handIndex]?.splitAces ?? false;

        if (total > 21) return { handIndex, handValue: total, outcome: 'dealer-win' as const, multiplier: 0, payoutAmount: 0 };
        if (dealerBest > 21) return { handIndex, handValue: total, outcome: 'player-win' as const, multiplier: 2, payoutAmount: state.bet * 2 };
        if (total === dealerBest) return { handIndex, handValue: total, outcome: 'push' as const, multiplier: 1, payoutAmount: state.bet };
        if (splitAce && hand.length === 2 && total === 21) return { handIndex, handValue: total, outcome: 'player-win' as const, multiplier: 2, payoutAmount: state.bet * 2 };
        if (total === 21 && !splitAce) return { handIndex, handValue: total, outcome: 'player-blackjack' as const, multiplier: 2.5, payoutAmount: Math.round(state.bet * 2.5) };
        if (total > dealerBest) return { handIndex, handValue: total, outcome: 'player-win' as const, multiplier: 2, payoutAmount: state.bet * 2 };
        return { handIndex, handValue: total, outcome: 'dealer-win' as const, multiplier: 0, payoutAmount: 0 };
      });

      return {
        handResults,
        totalPayout: handResults.reduce((total, handResult) => total + handResult.payoutAmount, 0),
      };
    },
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
    topUpWallet: (amount = 10000) => {
      const wallet = readWallet();
      return writeWallet({ ...wallet, balance: Math.max(0, wallet.balance + Math.floor(amount)) });
    },
  };
});

describe('blackjack game shell', () => {
  let container: HTMLDivElement;
  let root: Root;

  const dealerTotal = () => container.querySelector('.blackjack-zone--dealer .blackjack-zone__label strong')?.textContent;
  const playerTotal = () =>
    container.querySelector('.blackjack-zone--player .blackjack-zone__label strong')?.textContent
    ?? container.querySelector('.blackjack-player-hand__badge')?.textContent;
  const hiddenCardCount = () => container.querySelectorAll('[aria-label="Hidden card"]').length;
  const clickChip = (value: number) => {
    const chip = Array.from(container.querySelectorAll('button')).find(
      (b) => b.getAttribute('aria-label') === `Add ${value} Ft chip`,
    );
    chip?.click();
  };
  const clickDeal = () => {
    const dealButton = Array.from(container.querySelectorAll('button')).find((b) => b.textContent === 'Deal');
    dealButton?.click();
  };

  beforeEach(() => {
    handMode = 'default';
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

  it('reveals the dealer hole card before drawing and settles after the delay', async () => {
    act(() => {
      root.render(<BlackjackGame onReturnToMenu={() => undefined} />);
    });

    act(() => {
      clickChip(500);
    });

    act(() => {
      clickDeal();
    });

    expect(dealerTotal()).toBe('10');
    expect(container.querySelector('[aria-label="Hidden card"]')).not.toBeNull();

    act(() => {
      const standButton = Array.from(container.querySelectorAll('button')).find((button) => button.textContent === 'Stand');
      standButton?.click();
    });

    await act(async () => {
      vi.advanceTimersByTime(1099);
    });

    expect(hiddenCardCount()).toBe(1);
    expect(dealerTotal()).toBe('10');

    await act(async () => {
      vi.advanceTimersByTime(1);
    });

    expect(hiddenCardCount()).toBe(1);
    expect(dealerTotal()).toBe('16');

    await act(async () => {
      vi.advanceTimersByTime(1099);
    });

    expect(hiddenCardCount()).toBe(1);
    expect(dealerTotal()).toBe('16');

    await act(async () => {
      vi.advanceTimersByTime(1);
    });

    expect(hiddenCardCount()).toBe(0);
    expect(dealerTotal()).toBe('18');
    expect(container.textContent).toContain('You win!');
    expect(container.textContent).toContain('1,500 Ft');
  });

  it('keeps the table empty and hides game actions until the bet is placed', async () => {
    act(() => {
      root.render(<BlackjackGame onReturnToMenu={() => undefined} />);
    });

    expect(container.querySelector('.blackjack-zone--dealer')).not.toBeNull();
    expect(container.querySelector('.blackjack-zone--dealer')?.textContent?.trim()).toBe('');
    expect(container.querySelector('.blackjack-player-hand')).toBeNull();
    expect(container.querySelectorAll('[aria-label="Hidden card"]').length).toBe(0);
    expect(container.querySelector('.blackjack-bet-amount')).toBeNull();
    expect(Array.from(container.querySelectorAll('button')).map((b) => b.textContent)).toEqual(expect.arrayContaining(['Deal']));
    expect(Array.from(container.querySelectorAll('button')).map((b) => b.textContent)).not.toEqual(expect.arrayContaining(['Hit', 'Stand', 'Double', 'Split']));

    act(() => {
      clickChip(1000);
      clickChip(1000);
      clickChip(500);
    });

    expect(container.querySelector('.blackjack-bet-amount')?.textContent).toBe('2,500 Ft');

    act(() => {
      Array.from(container.querySelectorAll('button')).find((b) => b.textContent === 'Clear')?.click();
    });

    expect(container.querySelector('.blackjack-bet-amount')).toBeNull();

    act(() => {
      clickChip(250);
      clickChip(500);
    });

    act(() => {
      clickDeal();
    });

    expect(container.querySelector('.blackjack-zone--dealer')).not.toBeNull();
    expect(container.querySelector('.blackjack-player-hand')).not.toBeNull();
    expect(Array.from(container.querySelectorAll('button')).map((button) => button.textContent)).toEqual(expect.arrayContaining(['Hit', 'Stand']));
  });

  it('flips a newly hit player card after a short pause', async () => {
    act(() => {
      root.render(<BlackjackGame onReturnToMenu={() => undefined} />);
    });

    act(() => {
      clickChip(250);
      clickChip(250);
      clickChip(500);
    });

    act(() => {
      clickDeal();
    });

    act(() => {
      const hitButton = Array.from(container.querySelectorAll('button')).find((button) => button.textContent === 'Hit');
      hitButton?.click();
    });

    const doubleAfterHit = Array.from(container.querySelectorAll('button')).find((button) => button.textContent === 'Double');
    expect(doubleAfterHit).toBeUndefined();

    expect(playerTotal()).toBe('20');
    expect(hiddenCardCount()).toBe(2);

    await act(async () => {
      vi.advanceTimersByTime(449);
    });

    expect(playerTotal()).toBe('20');
    expect(hiddenCardCount()).toBe(2);

    await act(async () => {
      vi.advanceTimersByTime(1);
    });

    expect(playerTotal()).toBe('22');
    expect(hiddenCardCount()).toBe(1);
    expect(container.textContent).toContain('Dealer wins');
  });

  it('keeps the double-down card blind until the dealer finishes and then settles', async () => {
    act(() => {
      root.render(<BlackjackGame onReturnToMenu={() => undefined} />);
    });

    act(() => {
      clickChip(500);
    });

    act(() => {
      clickDeal();
    });

    act(() => {
      const doubleButton = Array.from(container.querySelectorAll('button')).find((button) => button.textContent === 'Double');
      doubleButton?.click();
    });

    expect(playerTotal()).toBe('20');
    expect(hiddenCardCount()).toBe(2);

    await act(async () => {
      vi.advanceTimersByTime(1100);
    });

    expect(hiddenCardCount()).toBe(2);
    expect(playerTotal()).toBe('20');
    expect(container.textContent).not.toContain('Result:');

    await act(async () => {
      vi.advanceTimersByTime(1100);
    });

    expect(hiddenCardCount()).toBe(1);
    expect(dealerTotal()).toBe('22');
    expect(playerTotal()).toBe('20');
    expect(container.textContent).not.toContain('Result:');

    await act(async () => {
      vi.advanceTimersByTime(1000);
    });

    expect(hiddenCardCount()).toBe(0);
    expect(playerTotal()).toBe('22');
    expect(container.textContent).not.toContain('Result:');

    await act(async () => {
      vi.advanceTimersByTime(800);
    });

    expect(container.textContent).toContain('Dealer wins');
    expect(container.textContent).toContain('0 Ft');
  });

  it('runs the dealer turn when only the last split hand busts on a hit', async () => {
    handMode = 'pair-second-bust';

    act(() => {
      root.render(<BlackjackGame onReturnToMenu={() => undefined} />);
    });

    act(() => { clickChip(500); });
    act(() => { clickDeal(); });

    const splitButton = Array.from(container.querySelectorAll('button')).find((b) => b.textContent === 'Split');
    act(() => { splitButton?.click(); });

    // stand on hand 0 → advance to hand 1
    act(() => {
      Array.from(container.querySelectorAll('button')).find((b) => b.textContent === 'Stand')?.click();
    });

    // hit on hand 1 — will bust after card reveal delay
    act(() => {
      Array.from(container.querySelectorAll('button')).find((b) => b.textContent === 'Hit')?.click();
    });

    expect(container.textContent).not.toContain('Result:');

    // card reveals → bust detected → dealer turn starts (not immediate dealer-win)
    await act(async () => { vi.advanceTimersByTime(450); });
    expect(container.textContent).not.toContain('Result:');

    // dealer hole card reveal
    await act(async () => { vi.advanceTimersByTime(1100); });
    // dealer draws extra card
    await act(async () => { vi.advanceTimersByTime(1100); });

    // hand 0 (value 10) beats the busted dealer → player-win, not dealer-win
    expect(container.textContent).toContain('You win!');
  });

  it('renders a split hand stack and highlights the active hand', async () => {
    handMode = 'pair';

    act(() => {
      root.render(<BlackjackGame onReturnToMenu={() => undefined} />);
    });

    act(() => {
      clickChip(250);
      clickChip(250);
    });

    act(() => {
      clickDeal();
    });

    const splitButton = Array.from(container.querySelectorAll('button')).find((button) => button.textContent === 'Split');
    expect(splitButton).toBeDefined();

    act(() => {
      splitButton?.click();
    });

    const splitHands = Array.from(container.querySelectorAll('.blackjack-player-hand'));
    expect(splitHands).toHaveLength(2);
    expect(splitHands[0].className).toContain('blackjack-player-hand--active');
    expect(splitHands[1].className).toContain('blackjack-player-hand--inactive');
    expect(container.querySelectorAll('.blackjack-player-hand__badge')).toHaveLength(2);
    expect(Array.from(container.querySelectorAll('button')).find((button) => button.textContent === 'Split')).toBeUndefined();
  });
});
