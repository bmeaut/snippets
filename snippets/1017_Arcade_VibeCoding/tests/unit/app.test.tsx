import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import App from '../../src/App';
import { ErrorBoundary } from '../../src/components/ErrorBoundary';

function CrashingChild() {
  throw new Error('boom');
}

describe('app shell', () => {
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

  it('handles hub movement and interaction input without crashing', () => {
    act(() => {
      root.render(<App />);
    });

    expect(container.querySelector('canvas')).not.toBeNull();

    act(() => {
      for (let index = 0; index < 20; index += 1) {
        globalThis.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
      }
    });

    act(() => {
      globalThis.dispatchEvent(new KeyboardEvent('keydown', { key: 'e', bubbles: true }));
    });

    expect(container.querySelector('canvas')).not.toBeNull();
  });

  it('renders fallback UI when the game subtree crashes', () => {
    const originalConsoleError = console.error;
    console.error = () => undefined;

    act(() => {
      root.render(
        <ErrorBoundary onReturnToMenu={() => undefined}>
          <CrashingChild />
        </ErrorBoundary>,
      );
    });

    expect(container.textContent).toContain('Game failed to load.');
    console.error = originalConsoleError;
  });
});