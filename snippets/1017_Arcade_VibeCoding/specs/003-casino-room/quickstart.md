# Quickstart: Casino Room

## Prerequisites

- Node.js and npm available on the machine.
- Existing workspace dependencies installed.

## Install and Run

```bash
npm install
npm run dev
```

Open the Vite URL shown in the terminal, then:

1. Move the player to the right-side Hub exit and press `E` to enter the Casino Room.
2. Confirm the wallet balance is visible in the corner.
3. Approach the Blackjack machine, press `E`, and verify the return button brings you back to the Casino Room.
4. Approach the Roulette machine, press `E`, and verify the return button brings you back to the Casino Room.
5. Use the left-side Casino exit to return to the Hub.

## Validation Commands

```bash
npm run test
npm run build
npm run lint
```

## Wallet Checks

- Clear browser storage for the site if you need to verify first-run behavior.
- Reload the page to confirm the wallet persists between sessions.
- Reopen the game on a different local day to confirm the daily bonus is applied once.

## Notes

- The current app already follows scene-based navigation, so the casino room should appear as another room rather than a separate application.
- Blackjack and Roulette must return to the Casino Room, not directly to the Hub.