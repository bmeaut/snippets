/**
 * Casino Room Game Module Contract
 *
 * Blackjack and Roulette reuse the same contract boundary as the existing
 * Hub-launched games. The host scene is different, but the module lifecycle
 * and validation expectations stay the same.
 */

export interface GameInitConfig {
  containerId: string;
  containerWidth: number;
  containerHeight: number;
  onGameOver: (score: number) => void;
  onBackToMenu: () => void;
}

export interface GameModuleContract {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly iconPath: string;
  readonly version: string;
  readonly component: React.ComponentType<{ config: GameInitConfig }>;
  initialize(config: GameInitConfig): Promise<void>;
  destroy(): Promise<void>;
  getStats(): {
    currentScore: number;
    status: 'active' | 'gameOver';
    duration: number;
  };
  resume?(): void;
  pause?(): void;
}

export const validateGameModuleContract = (module: any): module is GameModuleContract => {
  return (
    module &&
    typeof module.id === 'string' &&
    typeof module.name === 'string' &&
    typeof module.description === 'string' &&
    typeof module.iconPath === 'string' &&
    typeof module.version === 'string' &&
    typeof module.component === 'function' &&
    typeof module.initialize === 'function' &&
    typeof module.destroy === 'function' &&
    typeof module.getStats === 'function'
  );
};