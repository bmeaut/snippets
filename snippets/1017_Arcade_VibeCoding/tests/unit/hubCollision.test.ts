import { describe, expect, it } from 'vitest';
import { createPlayer } from '../../src/hub/entities/player';
import { createSnakeMachine } from '../../src/hub/entities/machine';
import { getProximityResult } from '../../src/hub/systems/interaction';

describe('hub proximity', () => {
  it('detects when the player is in range of the Snake machine', () => {
    const player = createPlayer();
    const machine = createSnakeMachine();
    const inRangePlayer = {
      ...player,
      x: machine.x - 72,
      y: machine.y + 30,
    };

    const result = getProximityResult(inRangePlayer, machine);

    expect(result.inRange).toBe(true);
    expect(result.machineId).toBe(machine.id);
  });

  it('detects when the player is too far away', () => {
    const player = createPlayer();
    const machine = createSnakeMachine();

    const result = getProximityResult(player, machine);

    expect(result.inRange).toBe(false);
  });
});