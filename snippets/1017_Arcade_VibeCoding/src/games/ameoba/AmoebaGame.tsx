import React, { useEffect, useState } from 'react';
import { createEmptyBoard, BOARD_SIZE, checkWin, isDraw, placeMove, findWinCells, Board } from './gameLogic';
import { easyAI } from './ai/easy';
import { mediumAI } from './ai/medium';
import { hardAI } from './ai/hard';
import './AmoebaGame.css';

type Difficulty = 'easy' | 'medium' | 'hard' | null;

interface SessionStats {
  wins: number;
  losses: number;
  draws: number;
}

interface AmoebaGameProps {
  config?: any;
  onReturnToMenu?: () => void;
}

export function AmoebaGame({ config, onReturnToMenu }: AmoebaGameProps) {
  const [board, setBoard] = useState<Board>(() => createEmptyBoard());
  const [currentPlayer, setCurrentPlayer] = useState<'X' | 'O'>('X');
  const [winner, setWinner] = useState<'X' | 'O' | 'draw' | null>(null);
  const [difficulty, setDifficulty] = useState<Difficulty>(null);
  const [winCells, setWinCells] = useState<{ row: number; col: number }[]>([]);
  const [lastMove, setLastMove] = useState<{ row: number; col: number } | null>(null);
  const [stats, setStats] = useState<SessionStats>({ wins: 0, losses: 0, draws: 0 });

  useEffect(() => {
    if (winner) return;
    if (!difficulty) return;
    if (currentPlayer === 'O') {
      const move = (() => {
        if (difficulty === 'easy') return easyAI(board);
        if (difficulty === 'medium') return mediumAI(board, 'O', 'X');
        return hardAI(board, 'O', 'X', 5, 500);
      })();
      if (move) {
        const next = placeMove(board, move.row, move.col, 'O');
        setBoard(next);
        setLastMove({ row: move.row, col: move.col });
        if (checkWin(next, 'O')) {
          setWinCells(findWinCells(next, 'O'));
          setWinner('O');
          setStats((s) => ({ ...s, losses: s.losses + 1 }));
        } else if (isDraw(next)) {
          setWinner('draw');
          setStats((s) => ({ ...s, draws: s.draws + 1 }));
        } else {
          setCurrentPlayer('X');
        }
      }
    }
  }, [board, currentPlayer, difficulty, winner]);

  const handleCellClick = (r: number, c: number) => {
    if (winner) return;
    if (difficulty === null) return;
    if (board[r][c] !== '') return;
    if (currentPlayer !== 'X') return;
    const next = placeMove(board, r, c, 'X');
    setBoard(next);
    setLastMove({ row: r, col: c });
    if (checkWin(next, 'X')) {
      setWinCells(findWinCells(next, 'X'));
      setWinner('X');
      setStats((s) => ({ ...s, wins: s.wins + 1 }));
    } else if (isDraw(next)) {
      setWinner('draw');
      setStats((s) => ({ ...s, draws: s.draws + 1 }));
    } else {
      setCurrentPlayer('O');
    }
  };

  const startNew = (d: Difficulty) => {
    if (d !== difficulty) setStats({ wins: 0, losses: 0, draws: 0 });
    setBoard(createEmptyBoard());
    setCurrentPlayer('X');
    setWinner(null);
    setWinCells([]);
    setLastMove(null);
    setDifficulty(d);
  };

  const returnToHub = () => {
    if (onReturnToMenu) onReturnToMenu();
    if (config && typeof config.onBackToMenu === 'function') config.onBackToMenu();
  };

  const isWinCell = (r: number, c: number) => winCells.some((wc) => wc.row === r && wc.col === c);
  const isLastMove = (r: number, c: number) => lastMove?.row === r && lastMove?.col === c;
  const isClickable = !winner && difficulty !== null && currentPlayer === 'X';

  const statusText = (() => {
    if (!difficulty) return '';
    if (winner === 'X') return '🎉 Nyertél!';
    if (winner === 'O') return 'AI nyert.';
    if (winner === 'draw') return 'Döntetlen!';
    if (currentPlayer === 'X') return 'A te köröd (X)';
    return 'AI gondolkodik...';
  })();

  const statusClass = (() => {
    if (winner === 'X') return 'ameoba-status--win-player';
    if (winner === 'O') return 'ameoba-status--win-ai';
    if (winner === 'draw') return 'ameoba-status--draw';
    if (currentPlayer === 'X') return 'ameoba-status--player';
    return 'ameoba-status--ai';
  })();

  return (
    <main className="game-shell">
      <div className="game-shell__topbar">
        <button className="secondary-button" onClick={returnToHub}>
          Vissza a Hubba
        </button>
        <button className="secondary-button" onClick={() => startNew(difficulty)}>
          Restart
        </button>
        {difficulty && (
          <div className="ameoba-stats">
            Gy: <span>{stats.wins}</span> | V: <span>{stats.losses}</span> | D: <span>{stats.draws}</span>
          </div>
        )}
      </div>

      {!difficulty ? (
        <section className="game-stage" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="ameoba-difficulty">
            <span className="ameoba-difficulty__deco ameoba-difficulty__deco--x">X</span>
            <span className="ameoba-difficulty__deco ameoba-difficulty__deco--o">O</span>
            <h2 className="ameoba-difficulty__title">Válassz <span>nehézséget</span></h2>
            <div className="ameoba-difficulty__buttons">
              <button className="primary-button" onClick={() => startNew('easy')} style={{ padding: '12px 24px' }}>
                Könnyű
              </button>
              <button className="primary-button" onClick={() => startNew('medium')} style={{ padding: '12px 24px' }}>
                Közepes
              </button>
              <button className="primary-button" onClick={() => startNew('hard')} style={{ padding: '12px 24px' }}>
                Nehéz
              </button>
            </div>
          </div>
        </section>
      ) : (
        <section className="game-stage" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
          <div className={`ameoba-status ${statusClass}`}>{statusText}</div>

          <div
            className="ameoba-board"
            style={{
              gridTemplateColumns: `repeat(${BOARD_SIZE}, 48px)`,
              pointerEvents: isClickable ? 'auto' : 'none',
            }}>
            {board.map((row, r) =>
              row.map((cell, c) => {
                const win = isWinCell(r, c);
                const last = isLastMove(r, c);
                const clickable = isClickable && cell === '';
                const cls = [
                  'ameoba-cell',
                  cell === 'X' ? 'ameoba-cell--x' : '',
                  cell === 'O' ? 'ameoba-cell--o' : '',
                  win ? 'ameoba-cell--win' : '',
                  last && !win ? 'ameoba-cell--last' : '',
                  clickable ? 'ameoba-cell--clickable' : '',
                ]
                  .filter(Boolean)
                  .join(' ');

                return (
                  <div key={`${r}-${c}`} className={cls} onClick={() => handleCellClick(r, c)} role="button" aria-label={`Cella ${r} ${c}`}>
                    {cell}
                  </div>
                );
              }),
            )}
          </div>

          {winner ? (
            <div className="game-over-panel">
              <h2>{winner === 'draw' ? 'Döntetlen' : winner === 'X' ? 'Nyertél!' : 'AI nyert!'}</h2>
              <div className="game-over-panel__actions">
                <button className="primary-button" onClick={() => startNew(difficulty)}>
                  Újra
                </button>
                <button className="secondary-button" onClick={returnToHub}>
                  Vissza a Hubba
                </button>
              </div>
            </div>
          ) : null}
        </section>
      )}
    </main>
  );
}
