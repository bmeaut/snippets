import { AmoebaGame } from './AmoebaGame';
import type { GameModuleContract, GameInitConfig } from '../../../specs/001-arcade-hub-snake/contracts/game-module.contract';

export { AmoebaGame };

export const amobaGameModule: Partial<GameModuleContract> = {
  id: 'amoba',
  name: 'Amőba',
  description: '8x8 Amőba (Gomoku) játék gép ellen, 3 nehézséggel',
  iconPath: 'src/games/ameoba/icon.svg',
  version: '0.1.0',
  component: (props: any) => <AmoebaGame {...props} />,
  initialize: async (config: GameInitConfig) => {
    // no-op for now; real initialization can pre-load assets
    return Promise.resolve();
  },
  destroy: async () => Promise.resolve(),
  getStats: () => ({ currentScore: 0, status: 'active' as const, duration: 0 }),
};
