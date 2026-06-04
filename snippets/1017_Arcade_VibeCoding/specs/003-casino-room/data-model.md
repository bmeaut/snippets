# Data Model: Casino Room

**Date**: 2026-05-23  
**Feature**: Casino Room  
**Purpose**: Define the state, entities, and validation rules for room navigation, shared wallet handling, Blackjack, and Roulette.

## Core Entities

### 1. Scene State

**Purpose**: Represents which room is currently active and which interactive exit or machine is available.

```typescript
type SceneId = "hub" | "casino";

interface SceneState {
  currentScene: SceneId;
  activeDoorId: string | null;
  activeMachineId: string | null;
  transitionPending: boolean;
}
```

**Validation Rules**:
- `currentScene` must always be one of the known room IDs.
- `activeDoorId` is only set when the player stands near a room exit.
- `activeMachineId` is only set when the player is in range of a casino machine.
- `transitionPending` is true only while a room switch is being requested.

---

### 2. Room Geometry

**Purpose**: Describes the visible room layout, exits, and machine positions.

```typescript
interface RoomGeometry {
  roomId: SceneId;
  width: number;
  height: number;
  exits: RoomExit[];
  machines: CasinoMachine[];
}

interface RoomExit {
  id: string;
  targetScene: SceneId;
  side: "left" | "right";
  x: number;
  y: number;
  width: number;
  height: number;
}
```

**Validation Rules**:
- Each room must have at least one exit.
- The Hub room must expose a right-side exit to the Casino Room.
- The Casino Room must expose a left-side exit to the Hub.
- Exit bounds must be large enough to be interactable by the player.

---

### 3. Shared Wallet State

**Purpose**: Tracks the player's shared bankroll and daily-bonus history across sessions.

```typescript
interface WalletState {
  balance: number;
  firstSeenAt: string;
  lastDailyBonusAt: string | null;
}
```

**Validation Rules**:
- `balance` must be a non-negative integer amount in Ft.
- `firstSeenAt` is set when no wallet exists yet.
- `lastDailyBonusAt` records the last calendar date when the bonus was granted.
- The daily bonus may be applied only once per local calendar day.

---

### 4. Casino Machine State

**Purpose**: Describes a machine that the player can enter from the Casino Room.

```typescript
type CasinoMachineType = "blackjack" | "roulette";

interface CasinoMachine {
  id: string;
  type: CasinoMachineType;
  roomId: "casino";
  x: number;
  y: number;
  width: number;
  height: number;
  interactionRadius: number;
}
```

**Validation Rules**:
- `id` must be unique within the Casino Room.
- `type` determines the game module launched by the machine.
- `interactionRadius` must allow a clear `E` prompt before entry.

---

### 5. Blackjack Round State

**Purpose**: Represents a single blackjack bet and its progression.

```typescript
type BlackjackPhase = "betting" | "player-turn" | "dealer-turn" | "resolved";
type BlackjackOutcome = "player-win" | "dealer-win" | "push" | "blackjack" | "player-bust" | "dealer-bust";

interface BlackjackRound {
  betAmount: number;
  phase: BlackjackPhase;
  playerHand: Card[];
  dealerHand: Card[];
  outcome: BlackjackOutcome | null;
  canDoubleDown: boolean;
}
```

**Validation Rules**:
- `betAmount` must not exceed the current wallet balance.
- `canDoubleDown` is only true on the initial player turn.
- `playerHand` and `dealerHand` contain at least two cards after the initial deal.
- `outcome` is set only after the round is resolved.

---

### 6. Card State

**Purpose**: Represents a standard playing card used in Blackjack.

```typescript
interface Card {
  suit: "clubs" | "diamonds" | "hearts" | "spades";
  rank: "A" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10" | "J" | "Q" | "K";
  value: number;
}
```

**Validation Rules**:
- Face cards must always evaluate to 10.
- Aces must be evaluable as 1 or 11 depending on the hand.
- The round logic must be able to score the best non-busting hand.

---

### 7. Roulette Round State

**Purpose**: Represents a single roulette spin and its bet resolution.

```typescript
type RouletteBetType = "red-black" | "even-odd" | "dozen" | "straight-up";
type RouletteOutcome = "win" | "lose";

interface RouletteRound {
  betAmount: number;
  betType: RouletteBetType;
  selectedValue: string | number;
  spunNumber: number | null;
  outcome: RouletteOutcome | null;
}
```

**Validation Rules**:
- `betAmount` must not exceed the current wallet balance.
- `selectedValue` must match the bet type.
- `spunNumber` must be between 0 and 36 inclusive.
- `outcome` is determined only after the spin finishes.

---

### 8. Bet Resolution

**Purpose**: Captures the payout relationship for supported bets.

```typescript
interface BetResolution {
  wageredAmount: number;
  payoutAmount: number;
  multiplier: number;
  walletDelta: number;
}
```

**Validation Rules**:
- `walletDelta` is negative for losing bets and positive for winning bets.
- Blackjack 1:1 wins and 3:2 blackjack wins must be represented distinctly.
- Roulette payouts must map to the specified odds for each supported bet type.

## Relationships & State Flow

### Room Flow

```text
SceneState
  -> RoomGeometry
  -> RoomExit / CasinoMachine
  -> interaction via E
  -> scene transition
```

### Wallet Flow

```text
localStorage record
  -> WalletState
  -> daily bonus check
  -> wallet display
  -> bet placement / payout
```

### Blackjack Flow

```text
WalletState
  -> BlackjackRound bet
  -> deal cards
  -> player actions
  -> dealer resolution
  -> BetResolution
  -> WalletState update
```

### Roulette Flow

```text
WalletState
  -> RouletteRound bet
  -> spin outcome
  -> BetResolution
  -> WalletState update
```

## Notes

- The wallet is shared by all casino game modules.
- The daily bonus is applied before the Casino Room becomes interactive for the day.
- Placeholder visuals are sufficient for the first implementation.
