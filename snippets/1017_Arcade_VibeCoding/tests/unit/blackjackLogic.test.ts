import { describe, it, expect, beforeEach } from 'vitest';
import {
  newDeck,
  cardValue,
  handValues,
  startRound,
  placeBet,
  split,
  playerHit,
  playerStand,
  dealerPlay,
  evaluateBets,
  bestHandValue,
  isBlackjack,
  isBust,
  type Card,
  type BlackjackState,
} from '../../src/games/blackjack/gameLogic';
import { WALLET_STORAGE_KEY } from '../../src/casino/state/wallet';
import { loadWallet, debit, credit } from '../../src/casino/services/walletStorage';

const card = (rank: Card['rank'], suit: Card['suit'] = '♠'): Card => ({ rank, suit });
const revealedCard = (rank: Card['rank'], suit: Card['suit'] = '♠'): Card => ({ rank, suit, isRevealed: true });
const roundWithDeck = (deck: Card[]) => startRound(() => deck);
const stateWithHands = (playerHands: Card[][], dealer: Card[], handFlags: Array<{ splitAces: boolean }> = playerHands.map(() => ({ splitAces: false }))): BlackjackState => ({
  deck: [],
  playerHands,
  activeHandIndex: 0,
  handFlags,
  player: playerHands[0],
  dealer,
  bet: 100,
  status: 'settled',
});

describe('Blackjack logic integration (basic)', () => {
  beforeEach(() => {
    localStorage.removeItem(WALLET_STORAGE_KEY);
    // seed wallet with 1000
    credit(1000);
  });

  it('allows placing a bet and deducts from wallet', () => {
    const before = loadWallet();
    const s = roundWithDeck([card('10'), card('9'), card('8'), card('7'), card('6')]);
    expect(s.playerHands).toHaveLength(0);
    expect(s.dealer).toHaveLength(0);
    expect(s.status).toBe('betting');
    expect(s.activeHandIndex).toBe(0);
    const withBet = placeBet(s, 200);
    expect(withBet.bet).toBe(200);
    expect(withBet.playerHands).toHaveLength(1);
    expect(withBet.playerHands[0]).toHaveLength(2);
    expect(withBet.dealer).toHaveLength(2);
    expect(withBet.status).toBe('player-turn');
    const dec = debit(200);
    expect(dec.ok).toBe(true);
    const after = loadWallet();
    expect(after.balance).toBe(before.balance - 200);
  });

  it('builds a complete 52-card deck and scores face cards and aces correctly', () => {
    const deck = newDeck();
    expect(deck).toHaveLength(52);
    expect(cardValue('A')).toEqual([1, 11]);
    expect(cardValue('J')).toEqual([10]);
    expect(cardValue('Q')).toEqual([10]);
    expect(cardValue('K')).toEqual([10]);
    expect(handValues([card('A'), card('A'), card('9')])).toEqual([11, 21, 31]);
  });

  it('dealer hits on 16 and stands on 17', () => {
    const hitsOnSixteen = roundWithDeck([card('10'), card('10'), card('7'), card('6'), card('2')]);
    const hitsOnSixteenSettled = dealerPlay(playerStand(placeBet(hitsOnSixteen, 10)));
    expect(hitsOnSixteenSettled.dealer).toHaveLength(3);
    expect(bestHandValue(hitsOnSixteenSettled.dealer)).toBe(18);

    const standsOnSeventeen = roundWithDeck([card('10'), card('10'), card('7'), card('7'), card('2')]);
    const standsOnSeventeenSettled = dealerPlay(playerStand(placeBet(standsOnSeventeen, 10)));
    expect(standsOnSeventeenSettled.dealer).toHaveLength(2);
    expect(bestHandValue(standsOnSeventeenSettled.dealer)).toBe(17);
  });

  it('treats a two-card 21 as blackjack but a three-card 21 as a normal win', () => {
    const blackjackRound = roundWithDeck([card('A'), card('9'), card('10'), card('7'), card('2')]);
    const blackjackSettled = dealerPlay(playerStand(placeBet(blackjackRound, 10)));
    expect(isBlackjack(blackjackSettled.player)).toBe(true);
    expect(blackjackSettled.playerHands).toHaveLength(1);
    expect(blackjackSettled.activeHandIndex).toBe(0);
    expect(blackjackSettled.result).toBe('player-blackjack');

    const threeCardTwentyOneRound = roundWithDeck([card('7'), card('10'), card('7'), card('6'), card('7'), card('2')]);
    const afterHit = playerHit(placeBet(threeCardTwentyOneRound, 10));
    expect(bestHandValue(afterHit.player)).toBe(21);
    expect(afterHit.playerHands[0]).toHaveLength(3);
    expect(isBlackjack(afterHit.player)).toBe(false);
    const threeCardTwentyOneSettled = dealerPlay(playerStand(afterHit));
    expect(threeCardTwentyOneSettled.result).toBe('player-win');
  });

  it('settles dealer win and push outcomes deterministically', () => {
    const dealerWinRound = roundWithDeck([card('10'), card('10'), card('9'), card('10'), card('2')]);
    const dealerWinSettled = dealerPlay(playerStand(placeBet(dealerWinRound, 10)));
    expect(dealerWinSettled.result).toBe('dealer-win');

    const pushRound = roundWithDeck([card('10'), card('10'), card('9'), card('9'), card('2')]);
    const pushSettled = dealerPlay(playerStand(placeBet(pushRound, 10)));
    expect(pushSettled.result).toBe('push');
  });

  it('respects the exact bust boundary and ace scoring', () => {
    expect(isBust([card('9'), card('9'), card('4')])).toBe(true);
    expect(bestHandValue([card('9'), card('9'), card('4')])).toBe(22);

    expect(isBust([card('10'), card('6'), card('5')])).toBe(false);
    expect(bestHandValue([card('10'), card('6'), card('5')])).toBe(21);
    expect(bestHandValue([card('A'), card('A'), card('9')])).toBe(21);
  });

  it('splits the initial hand into two sequential hands and advances from hand 1 to hand 2', () => {
    const round = roundWithDeck([card('8'), card('5'), card('8'), card('6'), card('2'), card('3')]);
    const withBet = placeBet(round, 100);
    const result = split(withBet, 1000);

    expect(result.accepted).toBe(true);
    expect(result.additionalBet).toBe(100);
    expect(result.state.playerHands).toHaveLength(2);
    expect(result.state.playerHands[0]).toEqual([revealedCard('8'), revealedCard('2')]);
    expect(result.state.playerHands[1]).toEqual([revealedCard('8'), revealedCard('3')]);
    expect(result.state.activeHandIndex).toBe(0);
    expect(result.state.player).toEqual([revealedCard('8'), revealedCard('2')]);
    expect(result.state.status).toBe('player-turn');

    const afterFirstStand = playerStand(result.state);
    expect(afterFirstStand.status).toBe('player-turn');
    expect(afterFirstStand.activeHandIndex).toBe(1);
    expect(afterFirstStand.player).toEqual([revealedCard('8'), revealedCard('3')]);

    const afterSecondStand = playerStand(afterFirstStand);
    expect(afterSecondStand.status).toBe('dealer-turn');
    expect(afterSecondStand.activeHandIndex).toBe(1);
  });

  it('rejects split attempts when the wallet cannot cover the extra bet', () => {
    const round = roundWithDeck([card('8'), card('5'), card('8'), card('6'), card('2'), card('3')]);
    const withBet = placeBet(round, 100);
    const result = split(withBet, 50);

    expect(result.accepted).toBe(false);
    expect(result.reason).toBe('insufficient-funds');
    expect(result.state.playerHands).toHaveLength(1);
    expect(result.state.status).toBe('player-turn');
  });

  it('rejects split attempts when the initial two cards do not match', () => {
    const round = roundWithDeck([card('8'), card('5'), card('9'), card('6'), card('2'), card('3')]);
    const withBet = placeBet(round, 100);
    const result = split(withBet, 1000);

    expect(result.accepted).toBe(false);
    expect(result.reason).toBe('matching-value-required');
    expect(result.state.playerHands).toHaveLength(1);
  });

  it('forces split aces to finish immediately and pays split-ace twenty-one at 1:1', () => {
    const round = roundWithDeck([card('A'), card('9'), card('A'), card('7'), card('10'), card('8')]);
    const withBet = placeBet(round, 100);
    const result = split(withBet, 1000);

    expect(result.accepted).toBe(true);
    expect(result.state.status).toBe('dealer-turn');
    expect(result.state.playerHands[0]).toEqual([revealedCard('A'), revealedCard('10')]);
    expect(result.state.playerHands[1]).toEqual([revealedCard('A'), revealedCard('8')]);
    expect(result.state.handFlags.every((flag) => flag.splitAces)).toBe(true);

    const evaluation = evaluateBets(stateWithHands(
      result.state.playerHands,
      [card('9'), card('8')],
      result.state.handFlags,
    ));

    expect(evaluation.handResults[0].outcome).toBe('player-win');
    expect(evaluation.handResults[0].multiplier).toBe(2);
    expect(evaluation.handResults[0].payoutAmount).toBe(200);
    expect(evaluation.handResults[0].outcome).not.toBe('player-blackjack');
    expect(evaluation.handResults[1].outcome).toBe('player-win');
    expect(evaluation.totalPayout).toBe(400);
  });

  it('evaluates each split hand independently against the dealer final score', () => {
    const evaluation = evaluateBets(stateWithHands(
      [[card('10'), card('8')], [card('10'), card('7'), card('3')]],
      [card('10'), card('8')],
    ));

    expect(evaluation.handResults).toHaveLength(2);
    expect(evaluation.handResults[0].outcome).toBe('push');
    expect(evaluation.handResults[0].payoutAmount).toBe(100);
    expect(evaluation.handResults[1].outcome).toBe('player-win');
    expect(evaluation.handResults[1].payoutAmount).toBe(200);
    expect(evaluation.totalPayout).toBe(300);
  });
});
