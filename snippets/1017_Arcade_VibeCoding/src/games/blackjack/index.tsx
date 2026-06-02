import { BlackjackGame } from './BlackjackGame';
import type { GameModuleContract, GameInitConfig } from '../../../specs/001-arcade-hub-snake/contracts/game-module.contract';

export { BlackjackGame };

export const blackjackGameModule: Partial<GameModuleContract> = {
  id: 'blackjack',
  name: 'Blackjack',
  description: 'Standard blackjack table (MVP)',
  iconPath: 'src/games/blackjack/icon.svg',
  version: '0.1.0',
  component: (props: any) => <BlackjackGame {...props} />,
  initialize: async (config: GameInitConfig) => Promise.resolve(),
  destroy: async () => Promise.resolve(),
  getStats: () => ({ currentScore: 0, status: 'active' as const, duration: 0 }),
};
