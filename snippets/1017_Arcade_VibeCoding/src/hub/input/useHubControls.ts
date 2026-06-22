import { useEffect, useRef, type MutableRefObject } from 'react';

const MOVE_KEYS = new Set([
  'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
  'w', 'W', 'a', 'A', 's', 'S', 'd', 'D',
]);

/** Returns a ref containing the set of currently held keys. */
export function useHeldKeys(): MutableRefObject<Set<string>> {
  const keysRef = useRef<Set<string>>(new Set());
  useEffect(() => {
    const onDown = (e: KeyboardEvent) => {
      if (MOVE_KEYS.has(e.key)) e.preventDefault();
      keysRef.current.add(e.key);
    };
    const onUp = (e: KeyboardEvent) => keysRef.current.delete(e.key);
    window.addEventListener('keydown', onDown);
    window.addEventListener('keyup', onUp);
    return () => {
      window.removeEventListener('keydown', onDown);
      window.removeEventListener('keyup', onUp);
    };
  }, []);
  return keysRef;
}

interface UseInteractOptions {
  onInteract: () => void;
  interactionEnabledRef: MutableRefObject<boolean>;
}

/** Listens for E key and calls onInteract when enabled. */
export function useInteractKey({ onInteract, interactionEnabledRef }: UseInteractOptions): void {
  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if ((e.key === 'e' || e.key === 'E') && !e.repeat && interactionEnabledRef.current) {
        e.preventDefault();
        onInteract();
      }
    };
    window.addEventListener('keydown', handle);
    return () => window.removeEventListener('keydown', handle);
  }, [interactionEnabledRef, onInteract]);
}

// Legacy hook kept for any surviving import
interface UseHubControlsOptions {
  onMove: (direction: import('../entities/player').HubDirection) => void;
  onInteract: () => void;
  interactionEnabledRef: MutableRefObject<boolean>;
}

export const useHubControls = ({ onInteract, interactionEnabledRef }: UseHubControlsOptions): void => {
  useInteractKey({ onInteract, interactionEnabledRef });
};
