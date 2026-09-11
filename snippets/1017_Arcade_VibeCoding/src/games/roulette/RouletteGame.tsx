import React, { useEffect, useState } from 'react';
import BettingBoard from './BettingBoard';
import RacetrackBoard from './RacetrackBoard';
import ResultHistory from './ResultHistory';
import { spinWheel, Bet, WHEEL_SEQUENCE, evaluateBet, evaluateBets, getWinningProperties } from './gameLogic';
import RouletteWheel from './RouletteWheel';
import { loadWallet, debit, saveWallet, topUpWallet } from '../../casino/services/walletStorage';

type Props = Readonly<{
  onReturnToMenu?: () => void;
}>;

type BoardView = 'standard' | 'racetrack';

export function RouletteGame({ onReturnToMenu }: Props) {
  const [bets, setBets] = useState<({ bet: Bet; payout?: number })[]>([]);
  const [lastBets, setLastBets] = useState<Bet[]>([]);
  const [result, setResult] = useState<number | null>(null);
  const [payout, setPayout] = useState(0);
  const [balance, setBalance] = useState(() => loadWallet().balance);
  const [spinning, setSpinning] = useState(false);
  const [muted, setMuted] = useState(false);
  const [wheelRotation, setWheelRotation] = useState(0);
  const [wheelDuration, setWheelDuration] = useState(3000);
  const [ballActive, setBallActive] = useState(false);
  const [history, setHistory] = useState<number[]>([]);
  const [boardView, setBoardView] = useState<BoardView>('standard');
  const spinDurationMs = 3000;

  useEffect(() => {
    setBalance(loadWallet().balance);
  }, []);

  function handleAddBet(bet: Bet) {
    setBets((current) => [...current, { bet }]);
  }

  function handleAddBets(newBets: Bet[]) {
    setBets((current) => [...current, ...newBets.map((bet) => ({ bet }))]);
  }

  function totalStake() {
    return bets.reduce((sum, entry) => sum + entry.bet.amount, 0);
  }

  function cloneBetSnapshot(entries: typeof bets) {
    return entries.map((entry) => ({
      bet: {
        ...entry.bet,
        payload: Array.isArray(entry.bet.payload) ? [...entry.bet.payload] : entry.bet.payload,
      },
      payout: entry.payout,
    }));
  }

  function getBetKey(entry: { bet: Bet; payout?: number }) {
    const p = entry.bet.payload;
    return `${entry.bet.type}-${Array.isArray(p) ? p.join(',') : String(p)}-${entry.bet.amount}-${entry.payout ?? 'pending'}`;
  }

  function handleReBet() {
    if (lastBets.length === 0 || spinning) return;
    setBets(lastBets.map((bet) => ({ bet })));
  }

  function handleSpin() {
    const stake = totalStake();
    if (stake <= 0) return;
    const dec = debit(stake);
    if (!dec.ok) return;
    setLastBets(bets.map((e) => ({
      ...e.bet,
      payload: Array.isArray(e.bet.payload) ? [...e.bet.payload] : e.bet.payload,
    })));
    const betSnapshot = cloneBetSnapshot(bets);

    setBalance((prev) => Math.max(0, prev - stake));

    const winningNumber = spinWheel();
    const wheelIndex = WHEEL_SEQUENCE.indexOf(winningNumber);
    const sectorAngle = 360 / WHEEL_SEQUENCE.length;
    const fullSpins = 3600;
    const pointerOffset = -90;
    const targetRotation = pointerOffset - wheelIndex * sectorAngle;

    setWheelDuration(spinDurationMs);
    setWheelRotation((prev) => prev + fullSpins + targetRotation - (prev % 360));
    setSpinning(true);
    setBallActive(true);

    // Tick sound
    let audioCtx: AudioContext | null = null;
    let tickTimer: number | null = null;
    if (!muted) {
      const Ctor = globalThis.AudioContext || (globalThis as any).webkitAudioContext;
      if (Ctor) audioCtx = new Ctor();
      if (audioCtx) {
        let interval = 120;
        const playTick = () => {
          if (!audioCtx) return;
          const o = audioCtx.createOscillator();
          const g = audioCtx.createGain();
          o.type = 'square'; o.frequency.value = 1200;
          g.gain.value = 0.0015;
          o.connect(g); g.connect(audioCtx.destination);
          o.start(); setTimeout(() => o.stop(), 40);
        };
        tickTimer = globalThis.setInterval(playTick, interval);
      }
    }

    setTimeout(() => {
      if (tickTimer) clearInterval(tickTimer);
      if (!muted && audioCtx) {
        const clack = audioCtx.createOscillator();
        const g2 = audioCtx.createGain();
        clack.type = 'sine'; clack.frequency.value = 880;
        g2.gain.value = 0.0015;
        clack.connect(g2); g2.connect(audioCtx.destination);
        clack.start(); setTimeout(() => clack.stop(), 220);
      }

      const settlement = evaluateBets(betSnapshot.map((e) => e.bet), winningNumber);
      const evaluated = betSnapshot.map((entry) => ({
        ...entry,
        payout: evaluateBet(entry.bet, winningNumber),
      }));

      if (settlement.totalPayout > 0) {
        const w = loadWallet();
        saveWallet({ ...w, balance: Math.max(0, w.balance + settlement.totalPayout) });
        setBalance((prev) => prev + settlement.totalPayout);
      }

      setBets(evaluated as any);
      setPayout(settlement.totalPayout);
      setResult(settlement.winning);
      setHistory((prev) => [...prev, winningNumber]);
      setSpinning(false);

      setTimeout(() => {
        setBets([]);
        setResult(null);
        setPayout(0);
        setBallActive(false);
      }, spinDurationMs);
    }, spinDurationMs);
  }

  function handleDevTopUp() {
    const wallet = topUpWallet();
    setBalance(wallet.balance);
  }

  return (
    <main className="roulette-page" style={{ gap: 6 }}>

      {/* ── Top bar ─────────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
        <button className="secondary-button" style={{ fontSize: 13, padding: '6px 14px' }} onClick={onReturnToMenu}>Vissza</button>
        <div style={{ textAlign: 'center' }}>
          <div className="roulette-eyebrow">Európai Rulett</div>
          <h3 className="roulette-title" style={{ margin: 0, fontSize: '1.3rem' }}>Rulett</h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ color: '#e2e8f0', fontWeight: 700, fontSize: 13 }}>
            {balance.toLocaleString('hu-HU')} Ft
          </span>
          <button type="button" className="dev-topup-button dev-topup-button--inline" onClick={handleDevTopUp}>
            +10 000 Ft
          </button>
          <button
            className="roulette-button roulette-button--outline"
            style={{ padding: '4px 10px', fontSize: 11 }}
            onClick={() => setMuted((m) => !m)}
          >
            {muted ? '🔇' : '🔊'}
          </button>
        </div>
      </div>

      {/* ── Main: two-column layout ─────────────────────── */}
      <div style={{ display: 'flex', flex: 1, gap: 12, overflow: 'hidden', minHeight: 0, paddingTop: 8 }}>

        {/* Left — wheel + history */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, flexShrink: 0 }}>
          <ResultHistory history={history} />
          <RouletteWheel
            rotationDeg={wheelRotation}
            durationMs={wheelDuration}
            spinning={spinning}
            ballActive={ballActive}
          />
        </div>

        {/* Right — toggle + board */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 6, overflow: 'auto', minWidth: 0 }}>

          {/* Toggle */}
          <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
            {(['standard', 'racetrack'] as const).map((v) => (
              <button
                key={v}
                onClick={() => setBoardView(v)}
                style={{
                  padding: '4px 14px',
                  borderRadius: 999,
                  border: '1px solid rgba(148,163,184,0.25)',
                  background: boardView === v
                    ? (v === 'standard' ? 'rgba(249,115,22,0.2)' : 'rgba(56,189,248,0.2)')
                    : 'transparent',
                  color: boardView === v
                    ? (v === 'standard' ? '#f97316' : '#38bdf8')
                    : '#64748b',
                  fontWeight: 700,
                  fontSize: 11,
                  cursor: 'pointer',
                }}
              >
                {v === 'standard' ? 'Standard' : 'Versenypalya'}
              </button>
            ))}
          </div>

          {/* Board */}
          <div style={{ flex: 1, overflow: 'auto' }}>
            {boardView === 'standard' ? (
              <BettingBoard
                bets={bets.map((e) => e.bet)}
                onAddBet={handleAddBet}
                onClearBets={() => setBets([])}
                onSpin={handleSpin}
                onReBet={lastBets.length > 0 ? handleReBet : undefined}
                disabled={spinning}
                totalStake={totalStake()}
              />
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <RacetrackBoard onAddBets={handleAddBets} disabled={spinning} />
                <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                  <span style={{ color: '#64748b', fontSize: 12 }}>
                    Tét: <strong style={{ color: '#f97316' }}>{totalStake().toLocaleString('hu-HU')} Ft</strong>
                  </span>
                  <button className="rl-btn rl-btn--spin" onClick={handleSpin} disabled={spinning || totalStake() <= 0}>
                    {spinning ? 'Forog…' : 'Pörgetés'}
                  </button>
                  {lastBets.length > 0 && (
                    <button className="rl-btn rl-btn--rebet" onClick={handleReBet} disabled={spinning}>
                      Újra tét
                    </button>
                  )}
                  <button className="rl-btn rl-btn--clear" onClick={() => setBets([])} disabled={spinning || totalStake() <= 0}>
                    Törlés
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {result !== null && !spinning && (
        <div className="roulette-result-toast">
          <span className="roulette-result-toast__ball">{result}</span>
          <span className="roulette-result-toast__text">
            {payout > 0 ? `+${payout.toLocaleString('hu-HU')} Ft` : 'Nem nyert'}
          </span>
        </div>
      )}
    </main>
  );
}
