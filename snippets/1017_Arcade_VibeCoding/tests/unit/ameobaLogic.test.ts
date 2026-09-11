import { createEmptyBoard, placeMove, checkWin, isDraw, findWinCells } from '../../src/games/ameoba/gameLogic';

describe('Amoeba gameLogic', () => {
  it('detects horizontal 4-in-a-row', () => {
    const b = createEmptyBoard();
    let nb = placeMove(b, 2, 2, 'X');
    nb = placeMove(nb, 2, 3, 'X');
    nb = placeMove(nb, 2, 4, 'X');
    nb = placeMove(nb, 2, 5, 'X');
    expect(checkWin(nb, 'X')).toBe(true);
  });

  it('findWinCells returns 4 cells for horizontal win', () => {
    let b = createEmptyBoard();
    b = placeMove(b, 3, 1, 'X');
    b = placeMove(b, 3, 2, 'X');
    b = placeMove(b, 3, 3, 'X');
    b = placeMove(b, 3, 4, 'X');
    const cells = findWinCells(b, 'X');
    expect(cells).toHaveLength(4);
    expect(cells.every((c) => c.row === 3)).toBe(true);
  });

  it('findWinCells returns 4 cells for vertical win', () => {
    let b = createEmptyBoard();
    b = placeMove(b, 0, 5, 'O');
    b = placeMove(b, 1, 5, 'O');
    b = placeMove(b, 2, 5, 'O');
    b = placeMove(b, 3, 5, 'O');
    const cells = findWinCells(b, 'O');
    expect(cells).toHaveLength(4);
    expect(cells.every((c) => c.col === 5)).toBe(true);
  });

  it('findWinCells returns 4 cells for diagonal win', () => {
    let b = createEmptyBoard();
    b = placeMove(b, 0, 0, 'X');
    b = placeMove(b, 1, 1, 'X');
    b = placeMove(b, 2, 2, 'X');
    b = placeMove(b, 3, 3, 'X');
    const cells = findWinCells(b, 'X');
    expect(cells).toHaveLength(4);
  });

  it('findWinCells returns empty array when no win', () => {
    let b = createEmptyBoard();
    b = placeMove(b, 0, 0, 'X');
    b = placeMove(b, 0, 1, 'X');
    b = placeMove(b, 0, 2, 'X');
    expect(findWinCells(b, 'X')).toHaveLength(0);
  });

  it('detects draw', () => {
    // Pattern: cell(r,c) = ((c + r*2) % 4 < 2) ? 'X' : 'O'
    // Even rows: X X O O X X O O  (max 2 consecutive horizontally)
    // Odd rows:  O O X X O O X X
    // Verticals: XOXO...  Diagonals: XOOX XOOX — no 4 in any direction.
    const pattern = (r: number, c: number): 'X' | 'O' => ((c + r * 2) % 4 < 2 ? 'X' : 'O');
    let board = createEmptyBoard();
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        board = placeMove(board, r, c, pattern(r, c));
      }
    }
    expect(checkWin(board, 'X')).toBe(false);
    expect(checkWin(board, 'O')).toBe(false);
    expect(isDraw(board)).toBe(true);
  });
});
