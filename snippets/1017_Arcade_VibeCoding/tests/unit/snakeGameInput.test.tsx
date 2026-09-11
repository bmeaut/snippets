import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react-dom/test-utils';
import { createRoot, type Root } from 'react-dom/client';
import { SnakeGame } from '../../src/games/snake/SnakeGame';

describe('snake game input', () => {
  let container: HTMLDivElement;
  let root: Root;
  let setTimeoutSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
    setTimeoutSpy = vi.spyOn(window, 'setTimeout');
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    setTimeoutSpy.mockRestore();
    container.remove();
  });

  it('only updates direction when pressing a key', () => {
    act(() => {
      root.render(<SnakeGame onReturnToMenu={() => undefined} />);
    });

    const initialTimeoutCalls = setTimeoutSpy.mock.calls.length;

    act(() => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true }));
    });

    expect(setTimeoutSpy.mock.calls.length).toBe(initialTimeoutCalls);
  });
});