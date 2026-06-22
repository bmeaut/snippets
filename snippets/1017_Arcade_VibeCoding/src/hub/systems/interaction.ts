import type { ArcadeMachineState } from '../entities/machine';
import type { PlayerAvatarState } from '../entities/player';

export type SceneId = 'hub' | 'snake' | 'casino';

export interface InteractionPromptState {
  visible: boolean;
  text: string;
  machineId: string | null;
  screenX: number;
  screenY: number;
}

export interface SceneTransitionState {
  currentScene: SceneId;
  targetScene: SceneId | null;
  requestedByMachineId: string | null;
  pending: boolean;
}

export interface ProximityResult {
  machineId: string | null;
  inRange: boolean;
  distance: number;
}

export const createHiddenPrompt = (): InteractionPromptState => ({
  visible: false,
  text: '',
  machineId: null,
  screenX: 0,
  screenY: 0,
});

export const createSceneTransitionState = (): SceneTransitionState => ({
  currentScene: 'hub',
  targetScene: null,
  requestedByMachineId: null,
  pending: false,
});

export const getProximityResult = (
  player: PlayerAvatarState,
  machines: ArcadeMachineState[],
): ProximityResult => {
  const playerCenterX = player.x + player.width / 2;
  const playerCenterY = player.y + player.height / 2;

  for (const machine of machines) {
    const machineCenterX = machine.x + machine.width / 2;
    const machineCenterY = machine.y + machine.height / 2;
    const distance = Math.hypot(machineCenterX - playerCenterX, machineCenterY - playerCenterY);

    if (distance <= machine.interactionRadius) {
      return {
        machineId: machine.id,
        inRange: true,
        distance,
      };
    }
  }

  return {
    machineId: null,
    inRange: false,
    distance: Infinity,
  };
};

const promptText = (machine: ArcadeMachineState): string => {
  if (machine.kind === 'snake') return '[E] Snake indítása';
  if (machine.kind === 'amoba') return '[E] Amőba indítása';
  if (machine.id === 'casino-roulette-terminal') return '[E] Rulett indítása';
  if (machine.id === 'casino-blackjack-terminal') return '[E] Blackjack indítása';
  return '[E] Megnyitás';
};

export const createInteractionPrompt = (
  player: PlayerAvatarState,
  machines: ArcadeMachineState[],
  scale: number,
  canvasOffsetX = 0,
  canvasOffsetY = 0,
): InteractionPromptState => {
  const proximity = getProximityResult(player, machines);

  if (!proximity.inRange) {
    return createHiddenPrompt();
  }

  const machine = machines.find((m) => m.id === proximity.machineId);
  if (!machine) {
    return createHiddenPrompt();
  }

  return {
    visible: true,
    text: promptText(machine),
    machineId: machine.id,
    screenX: (machine.x + machine.width / 2) * scale + canvasOffsetX,
    screenY: (machine.y - 16) * scale + canvasOffsetY,
  };
};