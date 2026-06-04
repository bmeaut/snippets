import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createSnakeMachine, createAmeobaMachine, createHubPortal, createLobbyPlants } from '../entities/machine';
import { createRoomSpawnPlayer, PLAYER_SPEED, type PlayerAvatarState, type RoomSpawnSide } from '../entities/player';
import { createLobbyNpcs, updateNpc, type NpcState } from '../entities/npc';
import { movePlayerWithSlide } from '../systems/collision';
import {
  createInteractionPrompt,
  createHiddenPrompt,
  getProximityResult,
  type InteractionPromptState,
} from '../systems/interaction';
import { drawHub, HUB_ROOM_HEIGHT, HUB_ROOM_WIDTH } from '../rendering/drawHub';
import { useHubResize } from '../hooks/useHubResize';
import { InteractionPrompt } from '../ui/InteractionPrompt';
import type { ArcadeMachineState } from '../entities/machine';

interface HubSceneProps {
  onLaunchSnake: () => void;
  onLaunchAmeoba: () => void;
  onLaunchCasino: () => void;
  spawnSide?: RoomSpawnSide;
}

const BOUNDS = { width: HUB_ROOM_WIDTH, height: HUB_ROOM_HEIGHT };

function playerInPortal(player: PlayerAvatarState, portal: ArcadeMachineState): boolean {
  const cx = player.x + player.width / 2;
  const cy = player.y + player.height / 2;
  return (
    cx >= portal.x + 10 && cx <= portal.x + portal.width - 10 &&
    cy >= portal.y && cy <= portal.y + portal.height
  );
}

export function HubScene({ onLaunchSnake, onLaunchAmeoba, onLaunchCasino, spawnSide }: Readonly<HubSceneProps>) {
  const stageRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const playerRef = useRef<PlayerAvatarState>(createRoomSpawnPlayer('left'));
  const keysRef = useRef<Set<string>>(new Set());
  const interactionEnabledRef = useRef(false);
  const portalTriggeredRef = useRef(false);
  const lastTimeRef = useRef<number>(0);
  const rafRef = useRef<number>(0);
  const pulseTickRef = useRef<number>(0);
  const lastPromptKeyRef = useRef('');
  const npcsRef = useRef<NpcState[]>(createLobbyNpcs());

  const machines = useMemo(() => [...createLobbyPlants(), createSnakeMachine(), createAmeobaMachine()], []);
  const portal = useMemo(() => createHubPortal(), []);
  const interactiveMachines = useMemo(() => machines.filter((m) => m.isInteractive), [machines]);

  const [prompt, setPrompt] = useState<InteractionPromptState>(() => createHiddenPrompt());
  const viewport = useHubResize(stageRef);
  const viewportRef = useRef(viewport);
  viewportRef.current = viewport;

  // Stable callbacks via refs
  const onLaunchSnakeRef = useRef(onLaunchSnake);
  const onLaunchAmeobaRef = useRef(onLaunchAmeoba);
  const onLaunchCasinoRef = useRef(onLaunchCasino);
  onLaunchSnakeRef.current = onLaunchSnake;
  onLaunchAmeobaRef.current = onLaunchAmeoba;
  onLaunchCasinoRef.current = onLaunchCasino;

  // Spawn on side change
  useEffect(() => {
    playerRef.current = createRoomSpawnPlayer(spawnSide ?? 'left');
    portalTriggeredRef.current = false;
  }, [spawnSide]);

  const handleInteract = useCallback(() => {
    const prox = getProximityResult(playerRef.current, interactiveMachines);
    if (prox.machineId === 'snake-machine') onLaunchSnakeRef.current();
    else if (prox.machineId === 'amoba-machine') onLaunchAmeobaRef.current();
  }, [interactiveMachines]);

  // Key listeners
  useEffect(() => {
    const MOVE_KEYS = new Set(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'w', 'W', 'a', 'A', 's', 'S', 'd', 'D']);
    const onDown = (e: KeyboardEvent) => {
      if (MOVE_KEYS.has(e.key)) e.preventDefault();
      keysRef.current.add(e.key);
      if ((e.key === 'e' || e.key === 'E') && !e.repeat && interactionEnabledRef.current) {
        handleInteract();
      }
    };
    const onUp = (e: KeyboardEvent) => keysRef.current.delete(e.key);
    window.addEventListener('keydown', onDown);
    window.addEventListener('keyup', onUp);
    return () => {
      window.removeEventListener('keydown', onDown);
      window.removeEventListener('keyup', onUp);
    };
  }, [handleInteract]);

  // rAF loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const loop = (timestamp: number) => {
      const dt = lastTimeRef.current === 0 ? 0 : Math.min((timestamp - lastTimeRef.current) / 1000, 0.05);
      lastTimeRef.current = timestamp;
      pulseTickRef.current += dt;

      const keys = keysRef.current;
      let dx = 0, dy = 0;
      if (keys.has('ArrowLeft')  || keys.has('a') || keys.has('A')) dx -= 1;
      if (keys.has('ArrowRight') || keys.has('d') || keys.has('D')) dx += 1;
      if (keys.has('ArrowUp')    || keys.has('w') || keys.has('W')) dy -= 1;
      if (keys.has('ArrowDown')  || keys.has('s') || keys.has('S')) dy += 1;

      const isMoving = dx !== 0 || dy !== 0;

      // Diagonal normalise
      if (dx !== 0 && dy !== 0) { dx *= 0.7071; dy *= 0.7071; }

      let { facing, animTick } = playerRef.current;
      if (dx < 0) facing = 'left';
      else if (dx > 0) facing = 'right';
      else if (dy < 0) facing = 'up';
      else if (dy > 0) facing = 'down';

      animTick = isMoving
        ? animTick + dt * 3
        : animTick * 0.82; // decay to 0

      const moved = movePlayerWithSlide(
        { ...playerRef.current, facing, isMoving, animTick },
        dx * PLAYER_SPEED * dt,
        dy * PLAYER_SPEED * dt,
        BOUNDS,
        machines,
      );
      playerRef.current = { ...moved, animTick };

      // Portal trigger
      if (!portalTriggeredRef.current && playerInPortal(playerRef.current, portal)) {
        portalTriggeredRef.current = true;
        onLaunchCasinoRef.current();
      }

      // Proximity → interaction prompt (only update React state when changed)
      const vp = viewportRef.current;
      const stageW = stageRef.current?.clientWidth ?? vp.width;
      const stageH = stageRef.current?.clientHeight ?? vp.height;
      const offX = Math.max(0, (stageW - vp.width) / 2);
      const offY = Math.max(0, (stageH - vp.height) / 2);
      const prox = getProximityResult(playerRef.current, interactiveMachines);
      interactionEnabledRef.current = prox.inRange;
      const nextPrompt = createInteractionPrompt(playerRef.current, interactiveMachines, vp.scale, offX, offY);
      const promptKey = `${nextPrompt.visible}-${nextPrompt.text}-${Math.round(nextPrompt.screenX)}-${Math.round(nextPrompt.screenY)}`;
      if (promptKey !== lastPromptKeyRef.current) {
        lastPromptKeyRef.current = promptKey;
        setPrompt(nextPrompt);
      }

      // Update NPCs
      npcsRef.current = npcsRef.current.map((npc) =>
        updateNpc(npc, dt, BOUNDS, machines),
      );

      // Draw
      drawHub({
        canvas,
        width: vp.width,
        height: vp.height,
        scale: vp.scale,
        player: playerRef.current,
        machines,
        portals: [portal],
        npcs: npcsRef.current,
        roomType: 'hub',
        pulseTick: pulseTickRef.current,
      });

      rafRef.current = requestAnimationFrame(loop);
    };

    lastTimeRef.current = 0;
    rafRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafRef.current);
  }, [machines, portal, interactiveMachines]);

  return (
    <main className="hub-shell">
      <section ref={stageRef} className="hub-stage" aria-label="Arcade hub room">
        <canvas ref={canvasRef} className="hub-canvas" aria-label="Top-down arcade room" />
        <InteractionPrompt prompt={prompt} />
      </section>
    </main>
  );
}
