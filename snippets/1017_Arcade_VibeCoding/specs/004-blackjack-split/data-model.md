# Data Model: Blackjack Split

**Date**: 2026-05-31  
**Feature**: Blackjack Split  
**Purpose**: Define the round state, split eligibility, hand sequencing, and payout rules for split blackjack hands.

## Core Entities

### 1. Blackjack Round State

**Purpose**: Represents a blackjack round that can branch into multiple player hands after a split.

```typescript
type BlackjackPhase = 'betting' | 'player-turn' | 'dealer-turn' | 'settled';

interface BlackjackRound {
  betAmount: number;
  phase: BlackjackPhase;
  playerHands: Card[][];
  activeHandIndex: number;
  dealerHand: Card[];
  outcome: BlackjackOutcome | null;
  splitEligible: boolean;
  splitCount: number;
}
```

**Validation Rules**:
- `playerHands` must always contain at least one hand while the round is active.
- `activeHandIndex` must point to a valid hand index.
- `splitEligible` is true only when the active player hand has exactly two cards of matching value and no action has been taken yet.
- `splitCount` increments when the player splits and must remain consistent with the number of player hands.

---

### 2. Card State

**Purpose**: Represents a standard playing card with reveal state for suspense animations.

```typescript
interface Card {
  suit: 'clubs' | 'diamonds' | 'hearts' | 'spades';
  rank: 'A' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | 'J' | 'Q' | 'K';
  isRevealed: boolean;
  isAnimated?: boolean;
}
```

**Validation Rules**:
- Initial visible cards must start with `isRevealed: true`.
- Cards dealt during split or draw suspense may start with `isRevealed: false` and flip later.
- Aces and face cards must continue to score according to standard blackjack rules.

---

### 3. Split Eligibility

**Purpose**: Captures whether the active hand can be split.

```typescript
interface SplitEligibility {
  canSplit: boolean;
  reason: 'initial-two-cards' | 'matching-value' | 'wallet-funds' | 'already-acted' | 'aces-special-case' | null;
}
```

**Validation Rules**:
- Splitting is allowed only on the initial two cards of the active hand.
- The two cards must have the same value.
- The shared wallet must have enough balance to cover the additional wager.

---

### 4. Hand Resolution

**Purpose**: Represents the result of each split hand before the final round outcome is aggregated.

```typescript
type HandOutcome = 'pending' | 'player-win' | 'dealer-win' | 'push' | 'blackjack' | 'bust';

interface HandResolution {
  handIndex: number;
  outcome: HandOutcome;
  payoutMultiplier: number;
  finishedAt: string | null;
}
```

**Validation Rules**:
- Each hand resolves independently, in order.
- Split Ace hands auto-finish after receiving exactly one additional card.
- A split Ace + 10-value card counts as a normal 21 and pays 1:1.

---

### 5. Wallet Impact

**Purpose**: Captures the bet and payout effect of a split round on the shared wallet.

```typescript
interface WalletImpact {
  baseBet: number;
  splitBet: number;
  totalRisked: number;
  totalPayout: number;
  netDelta: number;
}
```

**Validation Rules**:
- `splitBet` must equal `baseBet`.
- `totalRisked` increases when the split is accepted.
- `netDelta` must match the combined result of both hands.

## Relationships & State Flow

```text
BlackjackRound
  -> playerHands[activeHandIndex]
  -> split eligibility check
  -> wallet validation
  -> sequential hand play
  -> hand-by-hand resolution
  -> wallet payout update
```

## Notes

- The current UI can remain on the single-hand flow until the state refactor is complete.
- Split Aces are intentionally more restrictive than normal split hands.
