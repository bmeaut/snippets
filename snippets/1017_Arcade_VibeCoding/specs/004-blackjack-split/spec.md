# Feature Specification: Blackjack Split

**Feature Branch**: `004-blackjack-split`  
**Created**: 2026-05-31  
**Status**: Draft  
**Input**: User request: "Implement the Split feature for our Blackjack game using the Spec Kit workflow."

## Business Logic

- Splitting is allowed only on the initial two cards of a player hand.
- A split is valid only when those two cards have the same value.
- Splitting requires an additional bet equal to the original bet and must be validated against the shared wallet before the split is applied.
- After a split, the two resulting hands are played sequentially:
  - Hand 1 resolves completely first.
  - Hand 2 begins only after Hand 1 has finished.
- The player must be able to complete normal blackjack actions on each split hand, subject to standard blackjack rules.
- Special rule for Aces:
  - Splitting Aces gives exactly 1 card per Ace.
  - The turn auto-ends after each split Ace receives its single card.
  - No additional Hit actions are allowed on split Ace hands.
- Special payout rule for split Ace hands:
  - A split Ace + 10-value card is treated as a normal 21, not a natural blackjack.
  - That hand pays 1:1, not 3:2.
- The game must not allow a split after the player has already Hit.
- If the player cannot cover the extra wager, the split action must be rejected and the original hand must remain unchanged.

## Architecture / State

- Refactor the blackjack player state from `playerHand: Card[]` into `playerHands: Card[][]`.
- Add `activeHandIndex: number` to track which split hand is currently being played.
- Preserve per-card reveal state so split hands can still use the existing flip animation and suspense timing.
- The UI must render multiple player hands when a split occurs.
- The UI must visually highlight the active hand so the player knows which hand is currently being resolved.
- Hand resolution and payout logic must operate per hand and then aggregate the final wallet result.
- The turn flow must prevent actions on inactive hands while the current hand is resolving.
- The state model must support special split-Ace flow without requiring extra Hit actions on those hands.

## Task Checklist

- [ ] Refactor blackjack state from a single player hand into `playerHands: Card[][]`.
- [ ] Add `activeHandIndex` tracking and update turn progression for sequential hand play.
- [ ] Implement wallet validation for the additional split bet before allowing the split.
- [ ] Add split eligibility checks so splitting is only allowed on the initial two cards with matching values.
- [ ] Implement split Ace edge-case rules: one card per Ace, auto-end, no extra Hit actions.
- [ ] Update payout logic so split Ace + 10-value hands pay 1:1 instead of 3:2.
- [ ] Update the Blackjack UI to render multiple hands and highlight the active hand.
- [ ] Preserve the existing card flip and suspense animations for split-hand draws.
- [ ] Add unit tests for split eligibility, wallet debit validation, and sequential hand resolution.
- [ ] Add unit tests for split Aces, including auto-end behavior and 1:1 payout handling.
- [ ] Add UI regression tests for multi-hand rendering and active-hand highlighting.
