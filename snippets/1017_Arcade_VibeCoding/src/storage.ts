const HIGH_SCORE_KEY = 'arcade-hub-snake-high-score';

export const loadHighScore = (): number => {
  try {
    const raw = globalThis.localStorage.getItem(HIGH_SCORE_KEY);
    if (!raw) {
      return 0;
    }

    const parsed = Number(raw);
    return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
  } catch {
    return 0;
  }
};

export const saveHighScore = (score: number): void => {
  try {
    const current = loadHighScore();
    if (score > current) {
      globalThis.localStorage.setItem(HIGH_SCORE_KEY, String(score));
    }
  } catch {
    return;
  }
};
