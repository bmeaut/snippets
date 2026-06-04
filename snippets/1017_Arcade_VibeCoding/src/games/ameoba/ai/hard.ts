import type { Board, Cell } from '../gameLogic';
import { getEmptyCells, placeMove, checkWin, BOARD_SIZE, WIN_LENGTH } from '../gameLogic';

const DIRS = [
  { dr: 0, dc: 1 },
  { dr: 1, dc: 0 },
  { dr: 1, dc: 1 },
  { dr: -1, dc: 1 },
] as const;

// Window-based evaluation — each 4-cell window counted exactly once, no double-counting.
const scoreBoard = (board: Board, me: Cell, opponent: Cell): number => {
  let score = 0;

  for (const { dr, dc } of DIRS) {
    for (let r = 0; r < BOARD_SIZE; r++) {
      for (let c = 0; c < BOARD_SIZE; c++) {
        const r2 = r + dr * (WIN_LENGTH - 1);
        const c2 = c + dc * (WIN_LENGTH - 1);
        if (r2 < 0 || r2 >= BOARD_SIZE || c2 < 0 || c2 >= BOARD_SIZE) continue;

        let cntMe = 0;
        let cntOpp = 0;
        for (let i = 0; i < WIN_LENGTH; i++) {
          const cell = board[r + dr * i][c + dc * i];
          if (cell === me) cntMe++;
          else if (cell === opponent) cntOpp++;
        }

        if (cntMe > 0 && cntOpp > 0) continue; // window is blocked, worthless

        if (cntMe === WIN_LENGTH) return 100_000;
        if (cntOpp === WIN_LENGTH) return -100_000;

        if (cntMe === 3) score += 1_000;
        else if (cntMe === 2) score += 80;
        else if (cntMe === 1) score += 8;

        // Penalise opponent threats more than equivalent own gains
        if (cntOpp === 3) score -= 2_000;
        else if (cntOpp === 2) score -= 120;
        else if (cntOpp === 1) score -= 8;
      }
    }
  }
  return score;
};

// Quick 1-ply heuristic score for ordering moves before the minimax tree
const scoreCellFast = (board: Board, r: number, c: number, me: Cell, opponent: Cell): number => {
  let s = 0;
  for (const { dr, dc } of DIRS) {
    let myLen = 1;
    let oppLen = 0;
    for (const sign of [1, -1] as const) {
      let rr = r + dr * sign;
      let cc = c + dc * sign;
      while (rr >= 0 && rr < BOARD_SIZE && cc >= 0 && cc < BOARD_SIZE && board[rr][cc] === me) {
        myLen++;
        rr += dr * sign;
        cc += dc * sign;
      }
      rr = r + dr * sign;
      cc = c + dc * sign;
      while (rr >= 0 && rr < BOARD_SIZE && cc >= 0 && cc < BOARD_SIZE && board[rr][cc] === opponent) {
        oppLen++;
        rr += dr * sign;
        cc += dc * sign;
      }
    }
    if (myLen >= 4) s += 100_000;
    else if (myLen === 3) s += 2_000;
    else if (myLen === 2) s += 100;
    if (oppLen >= 3) s += 5_000;
    else if (oppLen === 2) s += 300;
  }
  return s;
};

// Only consider cells within 2 squares of an existing piece
const generateCandidates = (board: Board): { row: number; col: number }[] => {
  const empties = getEmptyCells(board);
  if (empties.length === BOARD_SIZE * BOARD_SIZE) {
    return [{ row: 3, col: 3 }, { row: 3, col: 4 }, { row: 4, col: 3 }, { row: 4, col: 4 }];
  }

  const seen = new Set<string>();
  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      if (board[r][c] === '') continue;
      for (let dr = -2; dr <= 2; dr++) {
        for (let dc = -2; dc <= 2; dc++) {
          const nr = r + dr;
          const nc = c + dc;
          if (nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE && board[nr][nc] === '') {
            seen.add(`${nr},${nc}`);
          }
        }
      }
    }
  }
  return Array.from(seen).map((k) => {
    const [row, col] = k.split(',').map(Number);
    return { row, col };
  });
};

export const hardAI = (board: Board, me: Cell, opponent: Cell, maxDepth = 5, timeLimitMs = 500) => {
  const start = Date.now();
  const empties = getEmptyCells(board);

  // Immediate win
  for (const { row, col } of empties) {
    if (checkWin(placeMove(board, row, col, me), me)) return { row, col };
  }
  // Block immediate loss
  for (const { row, col } of empties) {
    if (checkWin(placeMove(board, row, col, opponent), opponent)) return { row, col };
  }

  const minimax = (
    b: Board,
    depth: number,
    alpha: number,
    beta: number,
    maximizing: boolean,
  ): { score: number; move: { row: number; col: number } | null } => {
    if (Date.now() - start > timeLimitMs) return { score: scoreBoard(b, me, opponent), move: null };
    if (depth === 0) return { score: scoreBoard(b, me, opponent), move: null };

    const candidates = generateCandidates(b);
    if (candidates.length === 0) return { score: scoreBoard(b, me, opponent), move: null };

    // Order moves by fast heuristic so alpha-beta prunes more branches
    const current = maximizing ? me : opponent;
    const other = maximizing ? opponent : me;
    candidates.sort(
      (ma, mb) => scoreCellFast(b, mb.row, mb.col, current, other) -
                  scoreCellFast(b, ma.row, ma.col, current, other),
    );

    let bestMove: { row: number; col: number } | null = null;

    if (maximizing) {
      let value = -Infinity;
      for (const { row, col } of candidates) {
        const nb = placeMove(b, row, col, me);
        if (checkWin(nb, me)) return { score: 100_000, move: { row, col } };
        const { score } = minimax(nb, depth - 1, alpha, beta, false);
        if (score > value) { value = score; bestMove = { row, col }; }
        alpha = Math.max(alpha, value);
        if (alpha >= beta) break;
      }
      return { score: value, move: bestMove };
    } else {
      let value = Infinity;
      for (const { row, col } of candidates) {
        const nb = placeMove(b, row, col, opponent);
        if (checkWin(nb, opponent)) return { score: -100_000, move: { row, col } };
        const { score } = minimax(nb, depth - 1, alpha, beta, true);
        if (score < value) { value = score; bestMove = { row, col }; }
        beta = Math.min(beta, value);
        if (alpha >= beta) break;
      }
      return { score: value, move: bestMove };
    }
  };

  const result = minimax(board, maxDepth, -Infinity, Infinity, true);
  if (result.move) return result.move;

  // Fallback: best 1-ply heuristic
  const candidates = generateCandidates(board);
  if (candidates.length === 0) return null;
  return candidates.reduce((best, cur) =>
    scoreCellFast(board, cur.row, cur.col, me, opponent) >
    scoreCellFast(board, best.row, best.col, me, opponent)
      ? cur
      : best,
  );
};
