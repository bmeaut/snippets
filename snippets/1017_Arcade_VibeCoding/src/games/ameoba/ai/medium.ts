import type { Board, Cell } from '../gameLogic';
import { getEmptyCells, placeMove, checkWin, BOARD_SIZE } from '../gameLogic';

const DIRS = [
  [0, 1],
  [1, 0],
  [1, 1],
  [-1, 1],
] as const;

const countConsec = (board: Board, r: number, c: number, player: Cell, dr: number, dc: number): number => {
  let n = 0;
  let rr = r + dr;
  let cc = c + dc;
  while (rr >= 0 && rr < BOARD_SIZE && cc >= 0 && cc < BOARD_SIZE && board[rr][cc] === player) {
    n++;
    rr += dr;
    cc += dc;
  }
  return n;
};

// Score how valuable it is to place at (r,c) — higher is better for `me`
const scoreCell = (board: Board, r: number, c: number, me: Cell, opponent: Cell): number => {
  let score = 0;

  for (const [dr, dc] of DIRS) {
    // Offensive: how long a line would I create?
    const myFwd = countConsec(board, r, c, me, dr, dc);
    const myBwd = countConsec(board, r, c, me, -dr, -dc);
    const myLine = 1 + myFwd + myBwd;

    if (myLine >= 4) score += 100_000;
    else if (myLine === 3) score += 4_000;
    else if (myLine === 2) score += 200;
    else score += 15;

    // Defensive: how many opponent pieces does this cell interrupt?
    const oppFwd = countConsec(board, r, c, opponent, dr, dc);
    const oppBwd = countConsec(board, r, c, opponent, -dr, -dc);
    const oppThreat = oppFwd + oppBwd;

    if (oppThreat >= 3) score += 9_000;
    else if (oppThreat === 2) score += 500;
    else if (oppThreat === 1) score += 40;
  }

  // Prefer cells closer to the centre of the 8×8 board
  const centerDist = Math.abs(r - 3.5) + Math.abs(c - 3.5);
  score += Math.max(0, 30 - centerDist * 4);

  return score;
};

export const mediumAI = (board: Board, me: Cell, opponent: Cell) => {
  const empties = getEmptyCells(board);
  if (empties.length === 0) return null;

  // 1) Take an immediate win
  for (const { row, col } of empties) {
    if (checkWin(placeMove(board, row, col, me), me)) return { row, col };
  }

  // 2) Block opponent's immediate win
  for (const { row, col } of empties) {
    if (checkWin(placeMove(board, row, col, opponent), opponent)) return { row, col };
  }

  // 3) Pick the cell with the highest heuristic score
  let best = empties[0];
  let bestScore = -Infinity;
  for (const { row, col } of empties) {
    const s = scoreCell(board, row, col, me, opponent);
    if (s > bestScore) {
      bestScore = s;
      best = { row, col };
    }
  }
  return best;
};
