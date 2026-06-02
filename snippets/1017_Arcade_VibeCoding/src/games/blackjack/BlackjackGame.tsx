import React, { useEffect, useRef, useState } from 'react';
import type { BlackjackState, Card } from './gameLogic';
import {
  startRound,
  placeBet,
  split as splitHand,
  playerStand,
  drawOne,
  bestHandValue,
  isBust,
  isBlackjack,
  evaluateBets,
} from './gameLogic';
import { loadWallet, debit, credit, topUpWallet } from '../../casino/services/walletStorage';

type Props = Readonly<{
  onReturnToMenu?: () => void;
}>;

const CHIPS = [
  { value: 50,    color: '#3b82f6', label: '50'  },
  { value: 100,   color: '#ef4444', label: '100' },
  { value: 250,   color: '#22c55e', label: '250' },
  { value: 500,   color: '#a855f7', label: '500' },
  { value: 1000,  color: '#eab308', label: '1K'  },
  { value: 5000,  color: '#f97316', label: '5K'  },
  { value: 10000, color: '#94a3b8', label: '10K' },
] as const;

const CHIP_COLORS: Record<number, string> = Object.fromEntries(CHIPS.map(c => [c.value, c.color]));

function computeChipStack(amount: number): number[] {
  const denoms = [10000, 5000, 1000, 500, 250, 100, 50];
  const stack: number[] = [];
  let rem = amount;
  for (const d of denoms) {
    while (rem >= d && stack.length < 8) {
      stack.push(d);
      rem -= d;
    }
  }
  return stack;
}

const cardColor = (suit: Card['suit']) => (suit === '♥' || suit === '♦' ? 'red' : 'black');
const formatCardLabel = (card: Card) => `${card.rank}${card.suit}`;

const REVEAL_DELAY_MS = 450;
const DEALER_ACTION_DELAY_MS = 1100;
const DOUBLE_REVEAL_DELAY_MS = 1000;
const DOUBLE_SETTLE_DELAY_MS = 800;

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const withRevealedCard = (card: Card, isRevealed: boolean): Card => ({
  ...card,
  isRevealed,
  isAnimated: true,
});

const visibleCards = (cards: Card[]) => cards.filter((card) => card.isRevealed !== false);

function replaceActiveHand(stateToUpdate: BlackjackState, nextHand: Card[]): BlackjackState {
  const playerHands = stateToUpdate.playerHands.map((hand, index) =>
    index === stateToUpdate.activeHandIndex ? nextHand : hand,
  );
  return { ...stateToUpdate, playerHands, player: nextHand };
}

function withBlindCard(stateToUpdate: BlackjackState, card: Card, hand: 'player'): BlackjackState;
function withBlindCard(stateToUpdate: BlackjackState, card: Card, hand: 'dealer'): BlackjackState;
function withBlindCard(stateToUpdate: BlackjackState, card: Card, hand: 'player' | 'dealer'): BlackjackState {
  const hiddenCard = withRevealedCard(card, false);
  if (hand === 'player') return { ...stateToUpdate, player: [...stateToUpdate.player, hiddenCard] };
  return { ...stateToUpdate, dealer: [...stateToUpdate.dealer, hiddenCard] };
}

function settleBlackjackHand(current: BlackjackState): BlackjackState {
  const evaluation = evaluateBets(current);
  const isSplit = current.playerHands.length > 1;
  let result: BlackjackState['result'] = 'dealer-win';

  if (isSplit) {
    const totalInvested = current.bet * current.playerHands.length;
    const net = evaluation.totalPayout - totalInvested;
    if (net > 0) result = 'player-win';
    else if (net === 0) result = 'push';
    else result = 'dealer-win';
  } else if (evaluation.totalPayout > 0) {
    const allPush = evaluation.handResults.every((r) => r.outcome === 'push');
    const hasNaturalBlackjack = evaluation.handResults.some((r) => r.outcome === 'player-blackjack');
    if (allPush) result = 'push';
    else if (hasNaturalBlackjack) result = 'player-blackjack';
    else result = 'player-win';
  }

  return { ...current, status: 'settled', result };
}

export function BlackjackGame({ onReturnToMenu }: Props) {
  const [state, setState] = useState(() => startRound());
  const [betAmount, setBetAmount] = useState(0);
  const [lastBet, setLastBet] = useState(0);
  const [balance, setBalance] = useState(() => loadWallet().balance);
  const [isDrawingCard, setIsDrawingCard] = useState(false);
  const animationTokenRef = useRef(0);

  useEffect(() => {
    setBalance(loadWallet().balance);
  }, [state.status]);

  function renderCard(card: Card) {
    const tone = cardColor(card.suit);
    const animated = card.isAnimated === true;
    const cardRevealed = card.isRevealed !== false;

    if (animated) {
      return (
        <div
          className={`blackjack-card blackjack-card--flip blackjack-card--enter ${cardRevealed ? 'blackjack-card--flip-open' : ''}`}
          aria-label={cardRevealed ? formatCardLabel(card) : 'Hidden card'}
        >
          <div className={`blackjack-card__flip-shell ${cardRevealed ? 'blackjack-card__flip-shell--revealed' : ''}`}>
            <div className="blackjack-card__face blackjack-card__face--backing" aria-hidden="true">
              <span className="blackjack-card__back-pattern" />
            </div>
            <div className={`blackjack-card__face blackjack-card__face--card blackjack-card--${tone}`}>
              <div className="blackjack-card__corner blackjack-card__corner--top">{card.rank}</div>
              <div className="blackjack-card__suit">{card.suit}</div>
              <div className="blackjack-card__corner blackjack-card__corner--bottom">{card.rank}</div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div
        className={`blackjack-card blackjack-card--${tone} blackjack-card--enter`}
        aria-label={cardRevealed ? formatCardLabel(card) : 'Hidden card'}
      >
        <div className="blackjack-card__corner blackjack-card__corner--top">{card.rank}</div>
        <div className="blackjack-card__suit">{card.suit}</div>
        <div className="blackjack-card__corner blackjack-card__corner--bottom">{card.rank}</div>
      </div>
    );
  }

  async function handleDeal() {
    const amount = Math.max(0, Math.floor(betAmount));
    const dec = debit(amount);
    if (!dec.ok) return;
    if (amount > 0) setLastBet(amount);
    const next = placeBet(state, amount);
    setState(next);
    setBalance(dec.wallet.balance);
    const playerHand = next.playerHands[0] ?? [];
    if (isBlackjack(playerHand)) {
      void runDealerTurn({ ...next, status: 'dealer-turn' });
    }
  }

  async function handleReBet() {
    if (lastBet <= 0 || lastBet > balance) return;
    animationTokenRef.current += 1;
    setIsDrawingCard(false);
    setBetAmount(lastBet);
    const amount = lastBet;
    const dec = debit(amount);
    if (!dec.ok) return;
    const next = placeBet(startRound(), amount);
    setState(next);
    setBalance(dec.wallet.balance);
    const playerHand = next.playerHands[0] ?? [];
    if (isBlackjack(playerHand)) {
      void runDealerTurn({ ...next, status: 'dealer-turn' });
    }
  }

  async function handleHit() {
    if (isDrawingCard || state.status !== 'player-turn') return;
    const token = ++animationTokenRef.current;
    setIsDrawingCard(true);
    try {
      const { card, deck } = drawOne(state.deck);
      const pendingState = replaceActiveHand(
        withBlindCard({ ...state, deck }, card, 'player'),
        [...state.player, withRevealedCard(card, false)],
      );
      setState(pendingState);
      await sleep(REVEAL_DELAY_MS);
      if (animationTokenRef.current !== token) return;
      const revealedCard = withRevealedCard(card, true);
      const revealedHand = [...pendingState.player.slice(0, -1), revealedCard];
      const revealedState = { ...replaceActiveHand(pendingState, revealedHand) };
      if (isBust(revealedState.player)) {
        const nextState = playerStand(revealedState);
        if (nextState.status === 'dealer-turn') {
          void runDealerTurn(nextState);
        } else if (nextState.status === 'player-turn') {
          setState(nextState);
        } else {
          const settled = settleBlackjackHand(nextState);
          setState(settled);
          handleSettle(settled);
        }
      } else {
        setState(revealedState);
      }
    } finally {
      if (animationTokenRef.current === token) setIsDrawingCard(false);
    }
  }

  async function runDealerTurnSequence(initialState: BlackjackState, token: number) {
    let current = initialState;
    await sleep(DEALER_ACTION_DELAY_MS);
    if (animationTokenRef.current !== token) return null;
    current = {
      ...current,
      dealer: current.dealer.map((card, index) => (index === 1 ? withRevealedCard(card, true) : card)),
    };
    setState(current);
    while (bestHandValue(current.dealer) < 17) {
      const { card, deck } = drawOne(current.deck);
      current = withBlindCard({ ...current, deck }, card, 'dealer');
      setState(current);
      await sleep(DEALER_ACTION_DELAY_MS);
      if (animationTokenRef.current !== token) return null;
      current = { ...current, dealer: [...current.dealer.slice(0, -1), withRevealedCard(card, true)] };
      setState(current);
    }
    return current;
  }

  async function runDealerTurn(next: BlackjackState) {
    const token = ++animationTokenRef.current;
    setState(next);
    setIsDrawingCard(true);
    try {
      const current = await runDealerTurnSequence(next, token);
      if (!current || animationTokenRef.current !== token) return;
      const settled = settleBlackjackHand(current);
      setState(settled);
      handleSettle(settled);
    } finally {
      if (animationTokenRef.current === token) setIsDrawingCard(false);
    }
  }

  function handleStand() {
    const next = playerStand(state);
    if (next.status === 'dealer-turn') { void runDealerTurn(next); return; }
    setState(next);
  }

  async function handleDouble() {
    if (isDrawingCard || state.status !== 'player-turn') return;
    const extra = state.bet;
    const dec = debit(extra);
    if (!dec.ok) return;

    if (state.playerHands.length > 1) {
      const token = ++animationTokenRef.current;
      const doubledState = { ...state, bet: state.bet * 2 };
      const { card, deck } = drawOne(doubledState.deck);
      const hiddenPlayerCard = withRevealedCard(card, false);
      const pendingState: BlackjackState = replaceActiveHand(
        { ...doubledState, deck, status: 'player-turn' },
        [...doubledState.player, hiddenPlayerCard],
      );
      setState(pendingState);
      setBalance(dec.wallet.balance);
      setIsDrawingCard(true);
      try {
        await sleep(REVEAL_DELAY_MS);
        if (animationTokenRef.current !== token) return;
        const revealedState: BlackjackState = replaceActiveHand(
          pendingState,
          [...pendingState.player.slice(0, -1), withRevealedCard(card, true)],
        );
        setState(revealedState);
        const nextState = playerStand(revealedState);
        if (nextState.status === 'dealer-turn') { void runDealerTurn(nextState); }
        else { setState(nextState); }
      } finally {
        if (animationTokenRef.current === token) setIsDrawingCard(false);
      }
      return;
    }

    const token = ++animationTokenRef.current;
    const doubledState = { ...state, bet: state.bet * 2 };
    const { card, deck } = drawOne(doubledState.deck);
    const hiddenPlayerCard = withRevealedCard(card, false);
    let pendingState: BlackjackState = replaceActiveHand(
      { ...doubledState, deck, status: 'dealer-turn' },
      [...doubledState.player, hiddenPlayerCard],
    );
    setState(pendingState);
    setBalance(dec.wallet.balance);
    setIsDrawingCard(true);
    try {
      if (animationTokenRef.current !== token) return;
      pendingState = await runDealerTurnSequence(pendingState, token) ?? pendingState;
      if (animationTokenRef.current !== token) return;
      await sleep(DOUBLE_REVEAL_DELAY_MS);
      if (animationTokenRef.current !== token) return;
      const revealedDoubleCard = withRevealedCard(card, true);
      const revealedState: BlackjackState = {
        ...replaceActiveHand(pendingState, [...pendingState.player.slice(0, -1), revealedDoubleCard]),
      };
      setState(revealedState);
      await sleep(DOUBLE_SETTLE_DELAY_MS);
      if (animationTokenRef.current !== token) return;
      const settled = settleBlackjackHand(revealedState);
      setState(settled);
      handleSettle(settled);
    } finally {
      if (animationTokenRef.current === token) setIsDrawingCard(false);
    }
  }

  function handleSettle(s: BlackjackState) {
    if (s.status !== 'settled') return;
    const evaluation = evaluateBets(s);
    if (evaluation.totalPayout > 0) credit(evaluation.totalPayout);
    setBalance(loadWallet().balance);
  }

  function handleSplit() {
    if (isDrawingCard || state.status !== 'player-turn') return;
    const currentHand = state.playerHands[state.activeHandIndex] ?? [];
    const sameValue = currentHand.length === 2 && bestHandValue([currentHand[0]]) === bestHandValue([currentHand[1]]);
    const canSplitNow = state.playerHands.length === 1 && state.activeHandIndex === 0 && sameValue && balance >= state.bet;
    if (!canSplitNow) return;
    const outcome = splitHand(state, balance);
    if (!outcome.accepted) return;
    const walletChange = debit(outcome.additionalBet);
    if (!walletChange.ok) return;
    setBalance(walletChange.wallet.balance);
    setState(outcome.state);
    if (outcome.state.status === 'dealer-turn') void runDealerTurn(outcome.state);
  }

  function handleNewRound() {
    animationTokenRef.current += 1;
    setIsDrawingCard(false);
    setBetAmount(0);
    setState(startRound());
  }

  function handleChipClick(value: number) {
    setBetAmount((cur) => cur + value);
  }

  function handleClearBet() {
    setBetAmount(0);
  }

  function handleDevTopUp() {
    const wallet = topUpWallet();
    setBalance(wallet.balance);
  }

  // ── Derived values ──────────────────────────────────────────────────────────
  const currentHand = state.playerHands[state.activeHandIndex] ?? state.player;
  const playerTotal = bestHandValue(visibleCards(currentHand));
  const dealerShownTotal = bestHandValue(visibleCards(state.dealer));
  const isBetting = state.status === 'betting';
  const settlementEval = state.status === 'settled' ? evaluateBets(state) : null;
  const totalPayout = settlementEval?.totalPayout ?? null;
  const splitHandResults = state.status === 'settled' && state.playerHands.length > 1 ? settlementEval?.handResults ?? null : null;
  const canDoubleDown = state.status === 'player-turn' && currentHand.length === 2;
  const canSplit =
    state.status === 'player-turn' &&
    state.playerHands.length === 1 &&
    state.activeHandIndex === 0 &&
    currentHand.length === 2 &&
    bestHandValue([currentHand[0]]) === bestHandValue([currentHand[1]]) &&
    balance >= state.bet;

  // Chip stack: betting → pending bet; playing → current bet; settled → payout
  const chipDisplayAmount = isBetting
    ? betAmount
    : state.status === 'settled' && totalPayout !== null
      ? totalPayout
      : state.bet;
  const chipStack = computeChipStack(chipDisplayAmount > 0 ? chipDisplayAmount : 0);

  const isWin = state.status === 'settled' && (state.result === 'player-win' || state.result === 'player-blackjack');
  const isPush = state.status === 'settled' && state.result === 'push';
  const isLose = state.status === 'settled' && state.result === 'dealer-win';

  const resultLabel =
    state.result === 'player-blackjack' ? 'Blackjack!' :
    state.result === 'player-win'       ? 'You win!' :
    state.result === 'push'             ? 'Push' :
    state.result === 'dealer-win'       ? 'Dealer wins' :
    null;

  // ── Card renders ────────────────────────────────────────────────────────────
  const dealerCards = state.dealer.map((card, i) => (
    <div key={`${card.rank}-${card.suit}-${i}`} style={{ position: 'relative', zIndex: i + 1 }}>
      {renderCard(card)}
    </div>
  ));

  const isSplit = state.playerHands.length > 1;

  const playerHandCards = state.playerHands.map((hand, index) => {
    const isActive = state.status === 'player-turn' && index === state.activeHandIndex;
    const handTotal = bestHandValue(visibleCards(hand));
    const handKey = hand.map((c) => `${c.rank}${c.suit}`).join('-');
    const handResult = splitHandResults?.[index] ?? null;
    const badgeModifier = handResult
      ? handResult.outcome === 'player-win' ? 'blackjack-player-hand__badge--win'
      : handResult.outcome === 'push'       ? 'blackjack-player-hand__badge--push'
      : 'blackjack-player-hand__badge--lose'
      : '';
    const badgeContent = handResult
      ? handResult.outcome === 'player-win' ? 'Win'
      : handResult.outcome === 'push'       ? 'Push'
      : 'Lose'
      : handTotal;
    return (
      <div
        key={`${index}-${handKey}`}
        className={`blackjack-player-hand ${isActive ? 'blackjack-player-hand--active' : 'blackjack-player-hand--inactive'}`}
        aria-label={`Player hand ${index + 1}`}
      >
        {isSplit && (
          <div className={`blackjack-player-hand__badge ${badgeModifier}`} aria-label={`Hand ${index + 1} score ${handTotal}`}>
            {badgeContent}
          </div>
        )}
        <div className="blackjack-player-hand__cards blackjack-cards">
          {hand.map((card, hi) => (
            <div key={`${card.rank}-${card.suit}-${hi}`} style={{ position: 'relative', zIndex: hi + 1 }}>
              {renderCard(card)}
            </div>
          ))}
        </div>
      </div>
    );
  });

  // ── Render ───────────────────────────────────────────────────────────────────
  return (
    <main className="blackjack-page blackjack-page--no-scroll">
      <button className="blackjack-back-button" onClick={onReturnToMenu}>
        ← Back
      </button>

      <section className="blackjack-table">
        <div className="blackjack-table__glow" />

        {/* Header */}
        <header className="blackjack-header">
          <div>
            <div className="blackjack-eyebrow">High Stakes Table</div>
            <h3 className="blackjack-title">Blackjack</h3>
          </div>
          <div className="blackjack-wallet">
            <span>Shared wallet</span>
            <strong>{balance.toLocaleString('en-US')} Ft</strong>
            <button type="button" className="dev-topup-button dev-topup-button--inline" onClick={handleDevTopUp}>
              Dev +10K
            </button>
          </div>
        </header>

        {/* Game area */}
        <div className="blackjack-game-area">

          {/* Dealer */}
          <section className="blackjack-zone blackjack-zone--dealer" aria-label="Dealer hand">
            {!isBetting && (
              <>
                <div className="blackjack-zone__label">
                  <span>Dealer</span>
                  <strong>{dealerShownTotal}</strong>
                </div>
                <div className="blackjack-cards">{dealerCards}</div>
              </>
            )}
          </section>

          {/* Bet spot — center of the table */}
          <div className="blackjack-bet-spot">
            <div className="blackjack-bet-circle">
              {chipStack.length > 0 && (
                <div className="blackjack-chip-stack-visual">
                  {chipStack.map((denom, i) => (
                    <div
                      key={i}
                      className="blackjack-chip-disc"
                      style={{ background: CHIP_COLORS[denom] }}
                    />
                  ))}
                </div>
              )}
              {chipStack.length === 0 && isBetting && (
                <span className="blackjack-bet-circle__hint">Bet here</span>
              )}
            </div>

            {chipDisplayAmount > 0 && (
              <span className={`blackjack-bet-amount ${isWin ? 'blackjack-bet-amount--win' : isPush ? 'blackjack-bet-amount--push' : ''}`}>
                {chipDisplayAmount.toLocaleString('en-US')} Ft
              </span>
            )}

            {resultLabel && (
              <span className={`blackjack-result-badge ${isWin ? 'blackjack-result-badge--win' : isPush ? 'blackjack-result-badge--push' : isLose ? 'blackjack-result-badge--lose' : ''}`}>
                {resultLabel}
              </span>
            )}
          </div>

          {/* Player */}
          <section className="blackjack-zone blackjack-zone--player" aria-label="Player hands">
            {!isBetting && (
              <>
                {!isSplit && (
                  <div className="blackjack-zone__label">
                    <span>Player</span>
                    <strong>{playerTotal}</strong>
                  </div>
                )}
                <div className="blackjack-player-hands__row blackjack-player-hands__row--horizontal">
                  {playerHandCards}
                </div>
              </>
            )}
          </section>
        </div>

        {/* Controls */}
        <section className="blackjack-controls">
          {isBetting ? (
            <div className="blackjack-betbox">
              <div className="blackjack-chip-row">
                {CHIPS.map(({ value, color, label }) => (
                  <button
                    key={value}
                    className="blackjack-chip"
                    style={{ '--chip-color': color } as React.CSSProperties}
                    onClick={() => handleChipClick(value)}
                    aria-label={`Add ${value} Ft chip`}
                  >
                    <span className="blackjack-chip__inner">{label}</span>
                  </button>
                ))}
              </div>
              <div className="blackjack-betbox__actions">
                <button
                  className="blackjack-button blackjack-button--gold"
                  onClick={() => void handleDeal()}
                  disabled={betAmount <= 0 || betAmount > balance}
                >
                  Deal
                </button>
                <button
                  className="blackjack-button blackjack-button--dark blackjack-button--clear"
                  onClick={handleClearBet}
                  disabled={betAmount === 0}
                >
                  Clear
                </button>
              </div>
            </div>
          ) : (
            <div className="blackjack-actions">
              {state.status === 'player-turn' && (
                <>
                  <button className="blackjack-button blackjack-button--gold" onClick={() => void handleHit()} disabled={isDrawingCard}>
                    Hit
                  </button>
                  <button className="blackjack-button blackjack-button--dark" onClick={handleStand} disabled={isDrawingCard}>
                    Stand
                  </button>
                  {canDoubleDown && (
                    <button className="blackjack-button blackjack-button--outline" onClick={() => void handleDouble()} disabled={isDrawingCard}>
                      Double
                    </button>
                  )}
                  {canSplit && (
                    <button className="blackjack-button blackjack-button--outline blackjack-button--split" onClick={handleSplit} disabled={isDrawingCard}>
                      Split
                    </button>
                  )}
                </>
              )}
              {state.status === 'dealer-turn' && (
                <p className="blackjack-dealer-thinking">Dealer is playing…</p>
              )}
              {state.status === 'settled' && (
                <>
                  <button className="blackjack-button blackjack-button--gold" onClick={handleNewRound}>
                    New Round
                  </button>
                  {lastBet > 0 && lastBet <= balance && (
                    <button className="blackjack-button blackjack-button--outline" onClick={() => void handleReBet()}>
                      Re-bet ({lastBet.toLocaleString('en-US')} Ft)
                    </button>
                  )}
                  <button className="blackjack-button blackjack-button--dark" onClick={onReturnToMenu}>
                    Back to Casino
                  </button>
                </>
              )}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
