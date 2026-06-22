export type MachineKind = 'snake' | 'amoba' | 'casino' | 'portal' | 'plant';

export interface ArcadeMachineState {
  id: string;
  kind: MachineKind;
  x: number;
  y: number;
  width: number;
  height: number;
  interactionRadius: number;
  isInteractive: boolean;
  isSolid: boolean;
  screenColor?: string;
  label?: string;
}

const INTERACTION_RADIUS = 110;

export const createSnakeMachine = (): ArcadeMachineState => ({
  id: 'snake-machine',
  kind: 'snake',
  x: 200, y: 90,
  width: 72, height: 96,
  interactionRadius: INTERACTION_RADIUS,
  isInteractive: true,
  isSolid: true,
  screenColor: '#22d3ee',
});

export const createAmeobaMachine = (): ArcadeMachineState => ({
  id: 'amoba-machine',
  kind: 'amoba',
  x: 390, y: 90,
  width: 72, height: 96,
  interactionRadius: INTERACTION_RADIUS,
  isInteractive: true,
  isSolid: true,
  screenColor: '#818cf8',
});

export const createHubPortal = (): ArcadeMachineState => ({
  id: 'hub-portal',
  kind: 'portal',
  x: 824, y: 216,
  width: 88, height: 160,
  interactionRadius: 0,
  isInteractive: false,
  isSolid: false,
  label: 'KASZINÓ',
});

export const createCasinoExitPortal = (): ArcadeMachineState => ({
  id: 'casino-exit-portal',
  kind: 'portal',
  x: 48, y: 216,
  width: 88, height: 160,
  interactionRadius: 0,
  isInteractive: false,
  isSolid: false,
  label: 'KIJÁRAT',
});

export const createCasinoRouletteTerminal = (): ArcadeMachineState => ({
  id: 'casino-roulette-terminal',
  kind: 'casino',
  x: 530, y: 140,
  width: 56, height: 80,
  interactionRadius: INTERACTION_RADIUS,
  isInteractive: true,
  isSolid: true,
  screenColor: '#ef4444',
  label: 'RULETT',
});

export const createCasinoBlackjackTerminal = (): ArcadeMachineState => ({
  id: 'casino-blackjack-terminal',
  kind: 'casino',
  x: 680, y: 310,
  width: 56, height: 80,
  interactionRadius: INTERACTION_RADIUS,
  isInteractive: true,
  isSolid: true,
  screenColor: '#22c55e',
  label: 'BLACKJACK',
});

const createPlant = (x: number, y: number, id: string): ArcadeMachineState => ({
  id,
  kind: 'plant',
  x, y,
  width: 30, height: 30,
  interactionRadius: 0,
  isInteractive: false,
  isSolid: true,
});

export const createLobbyPlants = (): ArcadeMachineState[] => [
  createPlant(28, 28, 'plant-tl'),
  createPlant(902, 28, 'plant-tr'),
  createPlant(28, 582, 'plant-bl'),
  createPlant(902, 582, 'plant-br'),
];

export const createCasinoPlants = (): ArcadeMachineState[] => [
  createPlant(28, 28, 'plant-tl'),
  createPlant(902, 28, 'plant-tr'),
  createPlant(28, 582, 'plant-bl'),
  createPlant(902, 582, 'plant-br'),
];

