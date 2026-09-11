import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { useRef } from 'react';
import { act } from 'react-dom/test-utils';
import { createRoot, type Root } from 'react-dom/client';
import { useHubResize } from '../../src/hub/hooks/useHubResize';

describe('hub resize', () => {
  let container: HTMLDivElement;
  let root: Root;

  function Probe() {
    const stageRef = useRef<HTMLDivElement | null>(null);
    const size = useHubResize(stageRef);

    return (
      <div>
        <div ref={stageRef} data-testid="stage" />
        <span data-testid="size">{`${size.width}x${size.height}`}</span>
      </div>
    );
  }

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

  it('updates the viewport size from the stage width', () => {
    act(() => {
      root.render(<Probe />);
    });

    const stage = container.querySelector('[data-testid="stage"]') as HTMLDivElement;
    Object.defineProperty(stage, 'clientWidth', { configurable: true, value: 720 });

    act(() => {
      window.dispatchEvent(new Event('resize'));
    });

    expect(container.querySelector('[data-testid="size"]')?.textContent).toContain('720');
  });
});