# Tasks: Snake Overhaul

## Phase 1 — SnakeState bővítés + portál falmozgás

- [ ] `src/types.ts`: SnakeState-be új mezők: `stones`, `goldenApple`, `blueApple`, `slowUntil`, `applesEaten`
- [ ] `snakeLogic.ts`: `createInitialSnakeState` — új mezők alapértékkel (`stones: []`, `goldenApple: null`, stb.)
- [ ] `snakeLogic.ts`: `moveSnake` — `hitsWall` logika törlése, helyette `(coord + GRID_SIZE) % GRID_SIZE` wrap
- [ ] `snakeLogic.ts`: `moveSnake` — kő ütközés detektálás: `stones.some(s => s.x === head.x && s.y === head.y)`
- [ ] Unit teszt frissítés: portál mozgás tesztek, fal már nem öl

Acceptance: Portál falmozgás 100%-ban megbízható; kőbe hajtás game over-t vált ki.

---

## Phase 2 — Különleges almák logikája

- [ ] `snakeLogic.ts`: `createRandomPosition(exclude: Coordinate[])` helper — max 100 próba, safe spawn
- [ ] `snakeLogic.ts`: `moveSnake` — `applesEaten` növelése rendes alma evásnál
- [ ] `snakeLogic.ts`: arany alma spawn (`applesEaten % 7 === 0`) — `goldenApple` beállítás
- [ ] `snakeLogic.ts`: kék alma spawn (`applesEaten % 5 === 0`) — `blueApple` beállítás
- [ ] `snakeLogic.ts`: arany alma evése — `+3 pont`, `goldenApple: null`, ciklus reset
- [ ] `snakeLogic.ts`: kék alma evése — `+1 pont`, `blueApple: null`, `slowUntil = Date.now() + 3000`
- [ ] `snakeLogic.ts`: `moveSnake` — timeout ellenőrzés: arany >6s, kék >8s → null
- [ ] `snakeLogic.ts`: `nextTickDelay` — ha `slowUntil > now` → `delay * 2`
- [ ] Unit tesztek: arany alma +3 pont, kék alma lassítás, timeout eltávolítás

Acceptance: Mindkét különleges alma ciklusa, pontértéke és lejárata helyes.

---

## Phase 3 — Kő akadályok logikája

- [ ] `snakeLogic.ts`: kő spawn logika — `score >= 8 && (score - 8) % 4 === 0` almaevásnál → `spawnStone`
- [ ] `snakeLogic.ts`: `spawnStone` — `createRandomPosition` hívás (kígyó + almák + meglévő kövek kizárva), max 12 kő
- [ ] `snakeLogic.ts`: `createInitialSnakeState` — `stones: []`
- [ ] Unit tesztek: score 8-nál megjelenik 1 kő, score 12-nél 2, max 12 betartása

Acceptance: Kövek helyes pozícióban, soha nem törnek invariánst.

---

## Phase 4 — requestAnimationFrame loop

- [ ] `SnakeGame.tsx`: `tickRef` átírása rAF ID-ra (`useRef<number>`)
- [ ] `SnakeGame.tsx`: `lastTickTimeRef` hozzáadása (`useRef<number>`)
- [ ] `SnakeGame.tsx`: `stateRef` pattern — `useRef<SnakeState>` a mindig friss state olvasáshoz
- [ ] `SnakeGame.tsx`: `rAF` callback: `if (now - lastTickTime >= delay) { runTick(); lastTickTime = now; } requestAnimationFrame(loop);`
- [ ] `SnakeGame.tsx`: rendering minden rAF frame-ben (nem csak state változásnál)
- [ ] `SnakeGame.tsx`: lassítás aktív state figyelése a delay számításban

Acceptance: Nincsenek látható frame-kihagyások; mozgás folyamatos.

---

## Phase 5 — Vizuális redesign

- [ ] Kígyó szegmensek: `roundRect` (radius 4px), fej #a3e635, test #4ade80 → #166534 gradiens hossz alapján
- [ ] Alma: `arc` alapú kör (félcellás radius), narancs fill (#f97316), `shadowBlur` glow
- [ ] Arany alma: sárga (#fbbf24) kör + arany glow + hátralévő másodperc kiírva a cellán belül
- [ ] Kék alma: cián (#38bdf8) kör + kék glow + hátralévő másodperc
- [ ] Kő: sötétszürke (#374151) `roundRect`, 1px belső fehér árnyék (textúra érzethez)
- [ ] Pályaháttér: sötét (#090b10) + enyhe rácsvonal (meglévő megtartva)
- [ ] Canvas méret/scaling: `devicePixelRatio` tudatos rajzolás (éles megjelenítés retina kijelzőn)

Acceptance: Minden vizuális elem megkülönböztethető és stílusos.

---

## Phase 6 — Magyar UI + HTML overlay score

- [ ] Score + rekord: canvas `fillText` eltávolítása, HTML `<div>` overlay a canvas felett
- [ ] Lassítás visszaszámláló: "🐢 Xs" megjelenítés a score panel mellett amíg aktív
- [ ] Topbar gombok: "Vissza a Hubba", "Újraindítás"
- [ ] Game over panel: "Játék vége", "Pontszám: X", "Rekord: Y" (már HTML — ellenőrzés/frissítés)

Acceptance: Minden szöveg magyar; score overlay pontosan frissül.

---

## Notes

- A `createRandomPosition` helper legyen exportált — a unit tesztek mockolhatják.
- Arany és kék alma spawnja egymástól független (külön számlálók nem kellenek — `applesEaten % 7` ill. `% 5` elegendő, de ha mindkettő trigger egyszerre, mindkét alma megjelenik).
- A `slowUntil` timestamp a `moveSnake`-be kerül, de a `nextTickDelay` is olvassa — `Date.now()` hívás mindkét helyen OK (közel azonos ms).
- Max kő: konstansként exportálva (`MAX_STONES = 12`).
