import { RouletteGame } from './RouletteGame';
import type { GameModuleContract, GameInitConfig } from '../../../specs/001-arcade-hub-snake/contracts/game-module.contract';

export { RouletteGame };

export const rouletteGameModule: Partial<GameModuleContract> = {
  id: 'roulette',
  name: 'Roulette',
  description: 'European roulette (MVP)',
  iconPath: 'src/games/roulette/icon.svg',
  version: '0.1.0',
  component: (props: any) => <RouletteGame {...props} />,
  initialize: async (config: GameInitConfig) => Promise.resolve(),
  destroy: async () => Promise.resolve(),
  getStats: () => ({ currentScore: 0, status: 'active' as const, duration: 0 }),
};
