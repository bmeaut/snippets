import type { Board } from '../gameLogic';

export const easyAI = (board: Board) => {
  const empties: { row: number; col: number }[] = [];
  for (let r = 0; r < board.length; r++) {
    for (let c = 0; c < board[r].length; c++) {
      if (board[r][c] === '') empties.push({ row: r, col: c });
    }
  }
  if (empties.length === 0) return null;
  const choice = empties[Math.floor(Math.random() * empties.length)];
  return choice;
};
