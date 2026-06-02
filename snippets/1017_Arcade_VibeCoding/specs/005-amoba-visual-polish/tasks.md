# Tasks: Amőba Vizuális Csiszolás

## Phase 1 — gameLogic.ts bővítés

- [ ] `findWinCells(board, player)` helper implementálása: visszaad `{row,col}[]` tömböt a nyerő 4 cellával (vagy üres tömböt)
- [ ] `checkWin` refaktorálása: belülről hívja `findWinCells`-t (logika ne duplikálódjon)
- [ ] Unit teszt: `findWinCells` visszaad 4 cellát vízszintes/függőleges/átlós győzelem esetén; üres tömböt ha nincs győzelem

Acceptance: `checkWin` visszafelé kompatibilis; `findWinCells` tesztekkel igazolt.

---

## Phase 2 — CSS stílusfájl (`AmoebaGame.css`)

- [ ] `AmoebaGame.css` létrehozása `src/games/ameoba/` alatt
- [ ] `.ameoba-cell` alap stílus: méret (48px), háttér, border, transition
- [ ] `.ameoba-cell--x` és `.ameoba-cell--o`: eltérő szín (X = narancs, O = kék), nagyobb betűméret (28px+), bold
- [ ] `.ameoba-cell:hover` (üres, játékos köre): enyhe kiemelő háttér, `cursor: pointer`
- [ ] `.ameoba-cell--last`: enyhe keret vagy pont az utolsó lépésnél
- [ ] `.ameoba-cell--win`: zöld/arany háttér, opcionálisan pulzáló CSS animáció (`@keyframes`)
- [ ] Import hozzáadása `AmoebaGame.tsx`-be

Acceptance: Vizuálisan látható különbség X/O között; hover, last, win osztályok hatása megfigyelhető.

---

## Phase 3 — AmoebaGame.tsx refaktor + winCells + lastMove

- [ ] Inline stílusok eltávolítása a táblacellákról, CSS osztályok alkalmazása
- [ ] State hozzáadása: `winCells: {row:number, col:number}[]`, `lastMove: {row:number, col:number} | null`
- [ ] Játékos lépésnél `lastMove` frissítése
- [ ] AI lépésnél `lastMove` frissítése
- [ ] Győzelem esetén `findWinCells` meghívása és `winCells` beállítása
- [ ] Cella renderelésénél dinamikus CSS osztályok: `--x`/`--o`, `--last`, `--win`
- [ ] `startNew` híváskor `winCells = []`, `lastMove = null` visszaállítása

Acceptance: A tábla vizuálisan kész; nyerő cellák kiemelve; utolsó lépés jelölve.

---

## Phase 4 — Állapotjelző sáv

- [ ] Állapotjelző szöveg meghatározó logika: `statusText` számítása `winner`, `currentPlayer`, `difficulty` alapján
  - Nincs difficulty: `"Válassz nehézséget"`
  - Játékos köre: `"A te köröd (X)"`
  - AI köre: `"AI gondolkodik..."`
  - X nyert: `"Nyertél! 🎉"` (vagy emoji nélkül)
  - O nyert: `"AI nyert."`
  - Döntetlen: `"Döntetlen!"`
- [ ] Állapotjelző panel elhelyezése a tábla felett
- [ ] AI gondolkodás alatt a táblára `pointer-events: none` alkalmazása (CSS osztály alapján)

Acceptance: Az állapotjelző mindig helyes szöveget mutat; AI köre alatt a tábla nem kattintható.

---

## Phase 5 — Session statisztika

- [ ] `SessionStats` típus definiálása: `{ wins: number, losses: number, draws: number }`
- [ ] `stats` state hozzáadása `AmoebaGame`-ben (alapértelmezett: `{wins:0, losses:0, draws:0}`)
- [ ] Meccs végekor statisztika frissítése: X nyert → `wins++`, O nyert → `losses++`, döntetlen → `draws++`
- [ ] Nehézségváltáskor (`startNew` más nehézséggel) statisztika visszaáll nullára
- [ ] Statisztika megjelenítése a topbárban: `Gy: X | V: Y | D: Z`

Acceptance: 20 meccs után is helyes számok; nehézségváltáskor visszaáll.

---

## Notes

- Hang effekteket NEM adunk hozzá ebben a PR-ban.
- A `BOARD_SIZE` és `WIN_LENGTH` konstansok nem változnak.
- A `checkWin` szignatúrája nem változik — visszafelé kompatibilitás kötelező.
- CSS prefix: `ameoba-` (a többi játék stílusával való ütközés elkerüléséért).
