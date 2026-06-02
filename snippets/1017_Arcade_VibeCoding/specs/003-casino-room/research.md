# Research: Casino Room

## Wallet Persistence

- **Decision**: Persist a single wallet record in `localStorage` with `balance`, `firstSeenAt`, and `lastDailyBonusAt`.
- **Rationale**: The casino feature needs atomic updates for bets, payouts, and bonus checks. One record avoids drift between split keys.
- **Alternatives considered**: Multiple keys for balance and timestamps; rejected because validation and migration become harder.

## Daily Bonus

- **Decision**: Compare the stored timestamp against a derived local calendar-day key before awarding the daily bonus.
- **Rationale**: A daily bonus should trigger once per user day, not once per 24-hour window from the previous login.
- **Alternatives considered**: Raw elapsed-time checks; rejected because they behave badly around midnight and time-zone changes.

## Blackjack Rules

- **Decision**: Use a standard 52-card deck, shuffle per round, and allow Hit, Stand, and Double Down only.
- **Rationale**: This is the smallest standard blackjack ruleset that satisfies the MVP and remains easy to test.
- **Alternatives considered**: Multi-deck shoes, Split, Insurance, or surrender rules; rejected for scope control.

## Dealer Logic

- **Decision**: Dealer draws until 16 and stands on 17 or higher.
- **Rationale**: The spec explicitly defines this behavior, so it should be implemented as a simple score threshold.
- **Alternatives considered**: Soft-17 special handling; rejected because the feature request did not require it.

## Roulette Rules

- **Decision**: Use European roulette with pockets 0-36 and payout mappings for red/black, even/odd, dozens, and straight-up bets.
- **Rationale**: The requested wheel and payout ratios map directly to common European roulette rules.
- **Alternatives considered**: American roulette; rejected because the rules differ and would violate the spec.

## Module Boundaries

- **Decision**: Keep Blackjack and Roulette behind the existing game-module contract and return them to the Casino Room through a dedicated back action.
- **Rationale**: The app already uses strict module boundaries for games, and the casino feature should preserve that pattern.
- **Alternatives considered**: Embedding game UI directly in the room scene; rejected because it would make the room and game logic harder to isolate and test.