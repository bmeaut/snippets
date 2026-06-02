import { beforeEach, describe, expect, it } from 'vitest';
import { loadHighScore, saveHighScore } from '../../src/storage';

describe('storage', () => {
  beforeEach(() => {
    globalThis.localStorage.clear();
  });

  it('returns zero when there is no stored score', () => {
    expect(loadHighScore()).toBe(0);
  });

  it('persists the best score only', () => {
    saveHighScore(3);
    saveHighScore(1);
    saveHighScore(7);

    expect(loadHighScore()).toBe(7);
  });
});
