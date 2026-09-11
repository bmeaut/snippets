import { useEffect, useState, type RefObject } from 'react';
import { HUB_ROOM_HEIGHT, HUB_ROOM_WIDTH } from '../rendering/drawHub';

export interface HubViewportSize {
  width: number;
  height: number;
  scale: number;
}

export const useHubResize = (stageRef: RefObject<HTMLElement>): HubViewportSize => {
  const [size, setSize] = useState<HubViewportSize>({
    width: HUB_ROOM_WIDTH,
    height: HUB_ROOM_HEIGHT,
    scale: 1,
  });

  useEffect(() => {
    const updateSize = () => {
      const stageWidth = stageRef.current?.clientWidth ?? HUB_ROOM_WIDTH;
      const width = Math.max(320, Math.min(HUB_ROOM_WIDTH, stageWidth));
      const scale = width / HUB_ROOM_WIDTH;

      setSize({
        width,
        height: Math.round(HUB_ROOM_HEIGHT * scale),
        scale,
      });
    };

    updateSize();

    let resizeObserver: ResizeObserver | null = null;

    if (stageRef.current && typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(updateSize);
      resizeObserver.observe(stageRef.current);
    }

    window.addEventListener('resize', updateSize);

    return () => {
      window.removeEventListener('resize', updateSize);
      resizeObserver?.disconnect();
    };
  }, [stageRef]);

  return size;
};