import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import CasinoScene from '../../src/casino/scene/CasinoScene';

describe('casino navigation', () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
  });

  it('launches roulette from the shared casino room without crashing', () => {
    const onLaunchRoulette = vi.fn();

    act(() => {
      root.render(
        <CasinoScene
          onReturnToHub={() => undefined}
          onLaunchRoulette={onLaunchRoulette}
          onLaunchBlackjack={() => undefined}
          spawnSide="left"
        />,
      );
    });

    expect(container.querySelector('canvas')).not.toBeNull();

    act(() => {
      for (let index = 0; index < 25; index += 1) {
        globalThis.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
      }

      globalThis.dispatchEvent(new KeyboardEvent('keydown', { key: 'e', bubbles: true }));
    });

    expect(onLaunchRoulette).toHaveBeenCalledTimes(1);
  });
});