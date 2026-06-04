/**
 * Storage Contract
 * 
 * Defines the interface for persisting and retrieving game data
 * (High Score, preferences, etc.) from browser storage.
 */

/**
 * Storage abstraction layer.
 * Allows swapping localStorage, IndexedDB, or mock storage for testing.
 */
export interface StorageBackend {
  /**
   * Store a key-value pair.
   * @param key Storage key (e.g., "game-snake-highscore")
   * @param value JSON-serializable value
   * @throws StorageError if storage is full, unavailable, or fails
   */
  setItem(key: string, value: any): void;

  /**
   * Retrieve a value by key.
   * @param key Storage key
   * @returns Parsed value, or null if key doesn't exist
   * @throws StorageError if retrieval fails or data is corrupted
   */
  getItem(key: string): any | null;

  /**
   * Delete a key-value pair.
   * @param key Storage key
   * @throws StorageError if deletion fails
   */
  removeItem(key: string): void;

  /**
   * Clear all storage (or scoped prefix).
   * @throws StorageError if clearing fails
   */
  clear(): void;

  /**
   * Check if storage is available (e.g., localStorage accessible).
   * @returns true if storage is functional; false if unavailable (private mode, quota exceeded)
   */
  isAvailable(): boolean;
}

/**
 * High Score storage contract.
 * Specific to game score persistence.
 */
export interface HighScoreStorage {
  /**
   * Get High Score for a game.
   * @param gameId Game identifier (e.g., "snake")
   * @returns High score value, or 0 if not found or storage unavailable
   */
  getHighScore(gameId: string): number;

  /**
   * Save High Score for a game.
   * If new score > existing high score, update storage.
   * If storage unavailable, silently fail (user still sees current session score).
   * 
   * @param gameId Game identifier
   * @param score High score to save
   * @returns true if saved successfully, false if storage failed
   */
  saveHighScore(gameId: string, score: number): boolean;

  /**
   * Get full High Score record (with metadata).
   * @param gameId Game identifier
   * @returns Record with score, timestamp, session count; or null if not found
   */
  getHighScoreRecord(gameId: string): HighScoreRecord | null;

  /**
   * Clear High Score for a specific game (e.g., for debugging).
   * @param gameId Game identifier
   */
  clearHighScore(gameId: string): void;

  /**
   * Get all High Scores (for leaderboard, stats screen).
   * @returns Map of gameId → HighScoreRecord
   */
  getAllHighScores(): Map<string, HighScoreRecord>;
}

/**
 * High Score record structure (persisted in storage).
 */
export interface HighScoreRecord {
  gameId: string;           // e.g., "snake"
  highScore: number;        // Best score achieved
  lastUpdated: number;      // Timestamp of last update (ms since epoch)
  sessionCount: number;     // Number of games played (for analytics)
}

/**
 * Error class for storage failures.
 */
export class StorageError extends Error {
  constructor(operation: string, reason: string) {
    super(`Storage error (${operation}): ${reason}`);
    this.name = "StorageError";
  }
}

/**
 * LocalStorage-based implementation (default for browser).
 * Gracefully degrades if storage unavailable (private mode, quota exceeded).
 */
export class LocalStorageBackend implements StorageBackend {
  private static readonly PREFIX = "arcade-hub_";

  private isStorageAvailable(): boolean {
    try {
      const test = "__test__";
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch {
      return false;
    }
  }

  setItem(key: string, value: any): void {
    if (!this.isStorageAvailable()) {
      throw new StorageError("setItem", "localStorage not available");
    }
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(LocalStorageBackend.PREFIX + key, serialized);
    } catch (e) {
      throw new StorageError("setItem", String(e));
    }
  }

  getItem(key: string): any | null {
    if (!this.isStorageAvailable()) {
      return null; // Graceful fallback: return null instead of throwing
    }
    try {
      const serialized = localStorage.getItem(LocalStorageBackend.PREFIX + key);
      return serialized ? JSON.parse(serialized) : null;
    } catch (e) {
      throw new StorageError("getItem", `Failed to parse JSON: ${String(e)}`);
    }
  }

  removeItem(key: string): void {
    if (!this.isStorageAvailable()) {
      return; // Graceful fallback
    }
    try {
      localStorage.removeItem(LocalStorageBackend.PREFIX + key);
    } catch (e) {
      throw new StorageError("removeItem", String(e));
    }
  }

  clear(): void {
    if (!this.isStorageAvailable()) {
      return; // Graceful fallback
    }
    try {
      const keys = Object.keys(localStorage).filter((k) =>
        k.startsWith(LocalStorageBackend.PREFIX)
      );
      keys.forEach((k) => localStorage.removeItem(k));
    } catch (e) {
      throw new StorageError("clear", String(e));
    }
  }

  isAvailable(): boolean {
    return this.isStorageAvailable();
  }
}

/**
 * Mock storage for testing (doesn't persist).
 */
export class MockStorageBackend implements StorageBackend {
  private store = new Map<string, any>();

  setItem(key: string, value: any): void {
    this.store.set(key, value);
  }

  getItem(key: string): any | null {
    return this.store.get(key) ?? null;
  }

  removeItem(key: string): void {
    this.store.delete(key);
  }

  clear(): void {
    this.store.clear();
  }

  isAvailable(): boolean {
    return true;
  }
}

/**
 * Contract validation helper.
 */
export const validateStorageBackend = (backend: any): backend is StorageBackend => {
  return (
    backend &&
    typeof backend.setItem === "function" &&
    typeof backend.getItem === "function" &&
    typeof backend.removeItem === "function" &&
    typeof backend.clear === "function" &&
    typeof backend.isAvailable === "function"
  );
};
