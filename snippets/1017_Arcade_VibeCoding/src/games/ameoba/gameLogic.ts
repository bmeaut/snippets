export type Cell = 'X' | 'O' | '';
export type Board = Cell[][];
export type Move = { row: number; col: number; player: Cell };

export const BOARD_SIZE = 8;
export const WIN_LENGTH = 4;

export const createEmptyBoard = (): Board => Array.from({ length: BOARD_SIZE }, () => Array.from({ length: BOARD_SIZE }, () => ''));

export const cloneBoard = (board: Board): Board => board.map((r) => r.slice());

export const getEmptyCells = (board: Board) => {
  const out: { row: number; col: number }[] = [];
  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      if (board[r][c] === '') out.push({ row: r, col: c });
    }
  }
  return out;
};

export const placeMove = (board: Board, row: number, col: number, player: Cell): Board => {
  if (board[row][col] !== '') return board;
  const next = cloneBoard(board);
  next[row][col] = player;
  return next;
};

const DIRS = [
  { dr: 0, dc: 1 },
  { dr: 1, dc: 0 },
  { dr: 1, dc: 1 },
  { dr: -1, dc: 1 },
] as const;

export const findWinCells = (board: Board, player: Cell): { row: number; col: number }[] => {
  if (player === '') return [];
  const N = BOARD_SIZE;
  const L = WIN_LENGTH;

  for (let r = 0; r < N; r++) {
    for (let c = 0; c < N; c++) {
      if (board[r][c] !== player) continue;
      for (const { dr, dc } of DIRS) {
        const cells: { row: number; col: number }[] = [{ row: r, col: c }];
        let rr = r + dr;
        let cc = c + dc;
        while (rr >= 0 && rr < N && cc >= 0 && cc < N && board[rr][cc] === player) {
          cells.push({ row: rr, col: cc });
          if (cells.length >= L) return cells;
          rr += dr;
          cc += dc;
        }
      }
    }
  }
  return [];
};

export const checkWin = (board: Board, player: Cell): boolean => findWinCells(board, player).length > 0;

export const isDraw = (board: Board): boolean => getEmptyCells(board).length === 0 && !checkWin(board, 'X') && !checkWin(board, 'O');
