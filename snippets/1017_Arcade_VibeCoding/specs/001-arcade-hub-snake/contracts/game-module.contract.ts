/**
 * Game Module Contract
 * 
 * Every game module (e.g., Snake, Amőba, Blackjack) MUST export
 * its public interface via this contract. This ensures modularity,
 * isolation, and Hub compatibility.
 * 
 * File location: src/games/{gameName}/index.ts
 * Export: `const gameModule: GameModuleContract = { ... }`
 */

/**
 * Game initialization configuration.
 * Passed by Hub to game on load.
 */
export interface GameInitConfig {
  containerId: string;           // ID of DOM container (e.g., "game-container")
  containerWidth: number;        // Width in pixels (may be responsive)
  containerHeight: number;       // Height in pixels (may be responsive)
  onGameOver: (score: number) => void;  // Callback when game ends
  onBackToMenu: () => void;      // Callback when user requests menu return
}

/**
 * Game module public interface.
 * Hub loads and uses ONLY this contract; game internals are opaque.
 */
export interface GameModuleContract {
  /**
   * Unique game identifier.
   * Must be lowercase alphanumeric, no spaces (e.g., "snake", "amoba").
   */
  readonly id: string;

  /**
   * Display name of the game (e.g., "Snake", "Tic-Tac-Toe").
   */
  readonly name: string;

  /**
   * Human-readable game description (max 100 characters).
   */
  readonly description: string;

  /**
   * Relative path to game icon/thumbnail image.
   * Example: "src/games/snake/assets/icon.svg"
   */
  readonly iconPath: string;

  /**
   * Semantic version of the game (e.g., "1.0.0").
   */
  readonly version: string;

  /**
   * React component that renders the game.
   * Hub passes GameInitConfig as props.
   * 
   * Example usage:
   *   <GameComponent 
   *     config={gameInitConfig}
   *     onGameOver={(score) => hub.onGameOver(score)}
   *   />
   */
  readonly component: React.ComponentType<{ config: GameInitConfig }>;

  /**
   * Initialize game (called when component mounts).
   * Sets up event listeners, loads resources, initializes state.
   * 
   * @param config Game initialization configuration
   * @throws GameInitError if initialization fails
   * @returns Promise that resolves when game is ready to play
   */
  initialize(config: GameInitConfig): Promise<void>;

  /**
   * Clean up resources (called when component unmounts or game exits).
   * Removes event listeners, cancels animation frames, clears timers.
   * 
   * @throws GameCleanupError if cleanup fails
   */
  destroy(): Promise<void>;

  /**
   * Get current game statistics.
   * Called to display score, session info, etc.
   * 
   * @returns Object with current score and metadata
   */
  getStats(): {
    currentScore: number;
    status: "active" | "gameOver";
    duration: number; // milliseconds
  };

  /**
   * Optional: Resume game (if implementing pause feature in future).
   * Not required for MVP; reserved for extensibility.
   */
  resume?(): void;

  /**
   * Optional: Pause game (if implementing pause feature in future).
   * Not required for MVP; reserved for extensibility.
   */
  pause?(): void;
}

/**
 * Error types for game module failures.
 * Thrown during initialize() or destroy() failures.
 */
export class GameInitError extends Error {
  constructor(gameId: string, message: string) {
    super(`Game initialization failed (${gameId}): ${message}`);
    this.name = "GameInitError";
  }
}

export class GameCleanupError extends Error {
  constructor(gameId: string, message: string) {
    super(`Game cleanup failed (${gameId}): ${message}`);
    this.name = "GameCleanupError";
  }
}

/**
 * Contract validation function (helper for Hub).
 * Ensures a module implements the full contract.
 */
export const validateGameModuleContract = (module: any): module is GameModuleContract => {
  return (
    module &&
    typeof module.id === "string" &&
    typeof module.name === "string" &&
    typeof module.description === "string" &&
    typeof module.iconPath === "string" &&
    typeof module.version === "string" &&
    typeof module.component === "function" &&
    typeof module.initialize === "function" &&
    typeof module.destroy === "function" &&
    typeof module.getStats === "function"
  );
};
