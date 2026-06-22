# Data Model: Amőba (Gomoku)

## Key Types (conceptual, no implementation details)

- GameState
  - `board`: 8x8 array of strings — each cell is `'X'|'O'|''` (empty)
  - `currentPlayer`: `'X'|'O'`
  - `difficulty`: `'easy'|'medium'|'hard'`
  - `moveHistory`: array of `Move`
  - `winner`: `'X'|'O'|'draw'|null`
  - `isOver`: boolean
  - `startedAt`: ISO timestamp
  - `endedAt`: ISO timestamp | null

- Move
  - `row`: number (0-7)
  - `col`: number (0-7)
  - `player`: `'X'|'O'`
  - `time`: ISO timestamp

- AIConfig
  - `difficulty`: `'easy'|'medium'|'hard'`
  - `maxDepth`: number (for Hard)
  - `timeLimitMs`: number (optional fallback)

## Storage / Persistence
- No cross-session persistence in v1. GameState kept in-memory inside module instance. If future persistence required, serialize `GameState` and `moveHistory`.

## Notes
- Keep shape minimal and serializable to allow later worker-based evaluation (transfer or message passing).
