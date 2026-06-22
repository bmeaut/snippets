/**
 * Hub API Contract
 * 
 * Hub exposes these APIs to games and internal components.
 * Games interact with Hub ONLY through this contract.
 */

/**
 * Hub API provided to game modules.
 * Injected via React Context or direct props.
 */
export interface HubAPI {
  /**
   * Request to return to main menu.
   * Game calls this when user clicks "Back to Menu".
   * Hub responds by unloading game module and showing menu.
   */
  onBackToMenu(): void;

  /**
   * Notify Hub that game session ended.
   * Game calls this when game-over condition is met.
   * Hub displays end-game screen, high score update, restart option.
   * 
   * @param finalScore Final score achieved in this session
   */
  onGameOver(finalScore: number): void;

  /**
   * Get current High Score for this game (if stored).
   * Game uses this to display "Best Score" on game-over screen.
   * 
   * @param gameId Game identifier (e.g., "snake")
   * @returns High score value, or 0 if never played or localStorage unavailable
   */
  getHighScore(gameId: string): number;

  /**
   * Update High Score (Hub stores in localStorage).
   * Game calls this after game-over if current score > high score.
   * Hub handles persistence; game just reports the score.
   * 
   * @param gameId Game identifier (e.g., "snake")
   * @param score New high score value
   */
  setHighScore(gameId: string, score: number): void;

  /**
   * Get application theme preference (light/dark).
   * Game can use this to match UI colors.
   * 
   * @returns "light" or "dark"
   */
  getTheme(): "light" | "dark";

  /**
   * Subscribe to theme changes.
   * Game can listen for user theme preference changes.
   * 
   * @param callback Function called when theme changes
   * @returns Unsubscribe function
   */
  onThemeChange(callback: (theme: "light" | "dark") => void): () => void;
}

/**
 * Context provider wrapping game module.
 * Used to inject HubAPI into game components.
 * 
 * Example:
 *   <HubAPIProvider api={hubApi}>
 *     <SnakeGame config={config} />
 *   </HubAPIProvider>
 */
export interface HubAPIProviderProps {
  api: HubAPI;
  children: React.ReactNode;
}

/**
 * React Hook to access HubAPI from game components.
 * 
 * Example usage:
 *   const hub = useHubAPI();
 *   hub.onGameOver(finalScore);
 * 
 * Throws error if used outside HubAPIProvider context.
 */
export const useHubAPI = (): HubAPI => {
  // Implementation in src/components/HubAPIContext.tsx
  throw new Error("useHubAPI must be used within HubAPIProvider");
};

/**
 * Hub state exposed for external query.
 * Allows games to check if they're still active, etc.
 */
export interface HubState {
  currentGameId: string | null;  // Currently active game, or null if in menu
  isLoadingGame: boolean;
  gameError: Error | null;
}

/**
 * Contract validation helper.
 * Ensures an object implements HubAPI.
 */
export const validateHubAPI = (api: any): api is HubAPI => {
  return (
    api &&
    typeof api.onBackToMenu === "function" &&
    typeof api.onGameOver === "function" &&
    typeof api.getHighScore === "function" &&
    typeof api.setHighScore === "function" &&
    typeof api.getTheme === "function" &&
    typeof api.onThemeChange === "function"
  );
};
