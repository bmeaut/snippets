import { describe, expect, it } from 'vitest';
import { createPlayer, movePlayer } from '../../src/hub/entities/player';
import { HUB_ROOM_WIDTH } from '../../src/hub/rendering/drawHub';

describe('hub movement', () => {
  it('keeps the player inside the room bounds', () => {
    const player = createPlayer();

    let nextPlayer = player;
    for (let index = 0; index < 100; index += 1) {
      nextPlayer = movePlayer(nextPlayer, 'right');
    }

    expect(nextPlayer.x + nextPlayer.width).toBeLessThanOrEqual(HUB_ROOM_WIDTH - 24);
  });

  it('updates facing and position when moving', () => {
    const player = createPlayer();
    const nextPlayer = movePlayer(player, 'up');

    expect(nextPlayer.facing).toBe('up');
    expect(nextPlayer.y).toBeLessThan(player.y);
  });
});