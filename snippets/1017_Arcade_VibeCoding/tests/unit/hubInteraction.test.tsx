import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react-dom/test-utils';
import { createRoot, type Root } from 'react-dom/client';
import { HubScene } from '../../src/hub/scene/HubScene';

describe('hub interaction', () => {
  let container: HTMLDivElement;
  let root: Root;
  const onLaunchSnake = vi.fn();

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
    onLaunchSnake.mockReset();
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
  });

  it('shows the interaction prompt and launches Snake from the hub', () => {
    act(() => {
      root.render(<HubScene onLaunchSnake={onLaunchSnake} />);
    });

    act(() => {
      for (let index = 0; index < 20; index += 1) {
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
      }
    });

    expect(container.textContent).toContain('[E] Játék indítása');

    act(() => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'e', bubbles: true }));
    });

    expect(onLaunchSnake).toHaveBeenCalledTimes(1);
  });
});