export type Suit = '♠' | '♥' | '♦' | '♣';
export type Rank = 'A' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | 'J' | 'Q' | 'K';

export interface Card {
  suit: Suit;
  rank: Rank;
  isRevealed?: boolean;
  isAnimated?: boolean;
}

export function newDeck(): Card[] {
  const suits: Suit[] = ['♠', '♥', '♦', '♣'];
  const ranks: Rank[] = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
  const deck: Card[] = [];
  for (const s of suits) for (const r of ranks) deck.push({ suit: s, rank: r });
  return deck;
}

export function shuffle(deck: Card[], rnd = Math.random): Card[] {
  const d = deck.slice();
  for (let i = d.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [d[i], d[j]] = [d[j], d[i]];
  }
  return d;
}

export function drawOne(deck: Card[]): { card: Card; deck: Card[] } {
  const [card, ...rest] = deck;
  return { card, deck: rest };
}

export function cardValue(rank: Rank): number[] {
  if (rank === 'A') return [1, 11];
  if (rank === 'J' || rank === 'Q' || rank === 'K') return [10];
  return [Number.parseInt(rank, 10)];
}

export function handValues(cards: Card[]): number[] {
  let totals = [0];
  for (const c of cards) {
    const vals = cardValue(c.rank);
    const next: number[] = [];
    for (const t of totals) for (const v of vals) next.push(t + v);
    totals = Array.from(new Set(next));
  }
  // sort ascending
  return totals.sort((a, b) => a - b);
}

export function bestHandValue(cards: Card[]): number {
  const vals = handValues(cards).filter((v) => v <= 21);
  if (vals.length === 0) return Math.min(...handValues(cards));
  return Math.max(...vals);
}

export function isBust(cards: Card[]) {
  return handValues(cards).every((v) => v > 21);
}

export function isBlackjack(cards: Card[]) {
  return cards.length === 2 && handValues(cards).includes(21);
}

function resolveBlackjackResult(player: Card[], dealer: Card[]): BlackjackState['result'] {
  if (isBust(player)) return 'dealer-win';
  if (isBust(dealer)) return 'player-win';

  const playerBest = bestHandValue(player);
  const dealerBest = bestHandValue(dealer);

  if (playerBest > dealerBest) return 'player-win';
  if (playerBest < dealerBest) return 'dealer-win';
  return 'push';
}

export type PlayerRole = 'player' | 'dealer';

export interface BlackjackState {
  deck: Card[];
  playerHands: Card[][];
  activeHandIndex: number;
  handFlags: Array<{ splitAces: boolean }>;
  player: Card[];
  dealer: Card[];
  bet: number;
  status: 'betting' | 'player-turn' | 'dealer-turn' | 'settled';
  result?: 'player-win' | 'dealer-win' | 'push' | 'player-blackjack';
}

export interface SplitActionResult {
  accepted: boolean;
  reason: 'not-player-turn' | 'not-initial-hand' | 'matching-value-required' | 'insufficient-funds' | null;
  additionalBet: number;
  state: BlackjackState;
}

export interface HandPayout {
  handIndex: number;
  handValue: number;
  outcome: 'player-win' | 'dealer-win' | 'push' | 'player-blackjack';
  multiplier: number;
  payoutAmount: number;
}

export interface BetEvaluation {
  handResults: HandPayout[];
  totalPayout: number;
}

function getActivePlayerHand(state: BlackjackState): Card[] {
  return state.playerHands[state.activeHandIndex] ?? state.player;
}

function withPlayerHands(
  state: BlackjackState,
  playerHands: Card[][],
  activeHandIndex = state.activeHandIndex,
  handFlags = state.handFlags,
): BlackjackState {
  return {
    ...state,
    playerHands,
    activeHandIndex,
    handFlags,
    player: playerHands[activeHandIndex] ?? [],
  };
}

function isSplitAceHand(state: BlackjackState, handIndex = state.activeHandIndex): boolean {
  return state.handFlags[handIndex]?.splitAces ?? false;
}

function allHandsBust(playerHands: Card[][]): boolean {
  return playerHands.every((hand) => isBust(hand));
}

function advanceAfterHandComplete(state: BlackjackState, playerHands: Card[][]): BlackjackState {
  const nextHandIndex = state.activeHandIndex + 1;

  if (nextHandIndex < playerHands.length) {
    return withPlayerHands(
      {
        ...state,
        status: 'player-turn',
      },
      playerHands,
      nextHandIndex,
    );
  }

  if (allHandsBust(playerHands)) {
    return withPlayerHands(
      {
        ...state,
        status: 'settled',
        result: 'dealer-win',
      },
      playerHands,
      state.activeHandIndex,
    );
  }

  return withPlayerHands(
    {
      ...state,
      status: 'dealer-turn',
    },
    playerHands,
    state.activeHandIndex,
  );
}

function dealOpeningHands(deck: Card[]) {
  const { card: p1, deck: d1 } = drawOne(deck);
  const { card: d1c, deck: d2 } = drawOne(d1);
  const { card: p2, deck: d3 } = drawOne(d2);
  const { card: d2c, deck: d4 } = drawOne(d3);

  return {
    deck: d4,
    playerHands: [
      [
        { ...p1, isRevealed: true },
        { ...p2, isRevealed: true },
      ],
    ],
    player: [
      { ...p1, isRevealed: true },
      { ...p2, isRevealed: true },
    ],
    dealer: [
      { ...d1c, isRevealed: true },
      { ...d2c, isRevealed: false, isAnimated: true },
    ],
    handFlags: [{ splitAces: false }],
  };
}

export function startRound(shuffleFn = shuffle, rng = Math.random): BlackjackState {
  const deck = shuffleFn(newDeck(), rng);
  return {
    deck,
    playerHands: [],
    activeHandIndex: 0,
    handFlags: [],
    player: [],
    dealer: [],
    bet: 0,
    status: 'betting',
  };
}

export function placeBet(state: BlackjackState, amount: number): BlackjackState {
  if (state.status !== 'betting') return state;
  const bet = Math.max(0, Math.floor(amount));
  if (bet <= 0) return state;

  const openingHands = dealOpeningHands(state.deck);

  return {
    ...state,
    ...openingHands,
    bet,
    status: 'player-turn',
  };
}

export function split(state: BlackjackState, walletBalance: number): SplitActionResult {
  const currentHand = getActivePlayerHand(state);

  if (state.status !== 'player-turn') {
    return { accepted: false, reason: 'not-player-turn', additionalBet: 0, state };
  }

  if (state.playerHands.length !== 1 || state.activeHandIndex !== 0 || currentHand.length !== 2) {
    return { accepted: false, reason: 'not-initial-hand', additionalBet: 0, state };
  }

  if (walletBalance < state.bet) {
    return { accepted: false, reason: 'insufficient-funds', additionalBet: 0, state };
  }

  const [firstCard, secondCard] = currentHand;
  if (bestHandValue([firstCard]) !== bestHandValue([secondCard])) {
    return { accepted: false, reason: 'matching-value-required', additionalBet: 0, state };
  }

  const { card: firstDraw, deck: afterFirstDraw } = drawOne(state.deck);
  const { card: secondDraw, deck: afterSecondDraw } = drawOne(afterFirstDraw);
  const splitAces = firstCard.rank === 'A' && secondCard.rank === 'A';

  const playerHands = [
    [{ ...firstCard, isRevealed: true }, { ...firstDraw, isRevealed: true }],
    [{ ...secondCard, isRevealed: true }, { ...secondDraw, isRevealed: true }],
  ];

  const nextState = withPlayerHands(
    {
      ...state,
      deck: afterSecondDraw,
      status: splitAces ? 'dealer-turn' : 'player-turn',
    },
    playerHands,
    0,
    [{ splitAces }, { splitAces }],
  );

  return {
    accepted: true,
    reason: null,
    additionalBet: state.bet,
    state: nextState,
  };
}

export function playerHit(state: BlackjackState): BlackjackState {
  if (state.status !== 'player-turn') return state;
  if (isSplitAceHand(state)) return state;
  const { card, deck } = drawOne(state.deck);
  const currentHand = getActivePlayerHand(state);
  const updatedHand = [...currentHand, { ...card, isRevealed: true }];
  const updatedHands = state.playerHands.map((hand, index) => (index === state.activeHandIndex ? updatedHand : hand));
  const player = updatedHand;
  if (isBust(player)) {
    return advanceAfterHandComplete(withPlayerHands({ ...state, deck, player }, updatedHands), updatedHands);
  }
  return withPlayerHands({ ...state, deck, player }, updatedHands);
}

export function playerDoubleDown(state: BlackjackState): BlackjackState {
  if (state.status !== 'player-turn') return state;
  if (isSplitAceHand(state)) return state;
  // bet should be doubled by caller (wallet debit handled externally)
  const { card, deck } = drawOne(state.deck);
  const currentHand = getActivePlayerHand(state);
  const updatedHand = [...currentHand, { ...card, isRevealed: true }];
  const updatedHands = state.playerHands.map((hand, index) => (index === state.activeHandIndex ? updatedHand : hand));
  const player = updatedHand;
  // after double down player gets one card and stands
  if (isBust(player)) return advanceAfterHandComplete(withPlayerHands({ ...state, deck, player }, updatedHands), updatedHands);
  return advanceAfterHandComplete(withPlayerHands({ ...state, deck, player }, updatedHands), updatedHands);
}

export function playerStand(state: BlackjackState): BlackjackState {
  if (state.status !== 'player-turn') return state;
  return advanceAfterHandComplete(state, state.playerHands);
}

export function evaluateBets(state: BlackjackState): BetEvaluation {
  const dealerBest = isBust(state.dealer) ? -1 : bestHandValue(state.dealer);

  const handResults = state.playerHands.map((hand, handIndex) => {
    const handValue = bestHandValue(hand);
    const splitAceHand = isSplitAceHand(state, handIndex);

    if (isBust(hand)) {
      return { handIndex, handValue, outcome: 'dealer-win' as const, multiplier: 0, payoutAmount: 0 };
    }

    if (dealerBest === -1) {
      return { handIndex, handValue, outcome: 'player-win' as const, multiplier: 2, payoutAmount: state.bet * 2 };
    }

    const naturalBlackjack = isBlackjack(hand) && state.playerHands.length === 1;
    if (naturalBlackjack && !isBlackjack(state.dealer)) {
      return { handIndex, handValue, outcome: 'player-blackjack' as const, multiplier: 2.5, payoutAmount: Math.round(state.bet * 2.5) };
    }

    if (handValue > dealerBest) {
      if (splitAceHand && hand.length === 2 && handValue === 21) {
        return { handIndex, handValue, outcome: 'player-win' as const, multiplier: 2, payoutAmount: state.bet * 2 };
      }

      return { handIndex, handValue, outcome: 'player-win' as const, multiplier: 2, payoutAmount: state.bet * 2 };
    }

    if (handValue < dealerBest) {
      return { handIndex, handValue, outcome: 'dealer-win' as const, multiplier: 0, payoutAmount: 0 };
    }

    return { handIndex, handValue, outcome: 'push' as const, multiplier: 1, payoutAmount: state.bet };
  });

  return {
    handResults,
    totalPayout: handResults.reduce((total, handResult) => total + handResult.payoutAmount, 0),
  };
}

