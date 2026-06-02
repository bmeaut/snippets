# Feature Specification: UX Végső Simítások

**Feature Branch**: `006-ux-final-touches`
**Created**: 2026-06-02
**Status**: Ready
**Input**: Difficulty selection jobb dizájn, lobby rendbe rakás (snake túl közel az ajtóhoz, [E] prompt rossz helyen, gépfeliratok, gép-specifikus prompt szöveg)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Amőba nehézségválasztó redesign (Priority: P1)

A játékos egy letisztult, amőba-témájú választóképernyőt lát. A dizájn visszafogott és célszerű — rácsminták, X/O motívumok, de semmi extra modern (nincs glassmorphism, nincs particle effekt). Három gomb, szöveg nélkül, csak a szint neve.

**Acceptance Scenarios**:

1. **Given** az amőba elindul, **When** a nehézségválasztó megjelenik, **Then** egy amőba-témájú panel látható (pl. rács-háttér, X/O díszmotívum) a három gombbal: Könnyű / Közepes / Nehéz.
2. **Given** a választóképernyő látható, **When** a játékos fölé viszi az egeret valamelyik gombra, **Then** a gomb vizuálisan reagál (hover effekt).
3. **Given** a játékos kiválaszt egy nehézséget, **When** a játék elindul, **Then** a panel eltűnik és a tábla jelenik meg.

---

### User Story 2 — Hub lobby: Snake gép pozíció és gépfeliratok (Priority: P1)

A Snake gép arrébb kerül hogy jól látható rés legyen közte és a Casino ajtó közt. Minden gép felett megjelenik a neve a canvas-on belül rajzolva ("SNAKE", "AMŐBA", "KASZINÓ").

**Acceptance Scenarios**:

1. **Given** a hub betöltődik, **When** a játékos megnézi a szobát, **Then** a Snake gép és a Casino ajtó között legalább 60 px szabad tér látható.
2. **Given** a hub canvas renderelve van, **When** a játékos megnézi a gépeket, **Then** minden gép felett/alatt kis felirat azonosítja ("SNAKE", "AMŐBA", "KASZINÓ").

---

### User Story 3 — Hub lobby: [E] prompt pozíció és gép-specifikus szöveg (Priority: P1)

Az `[E]` interakciós felirat pontosan a hozzá tartozó gép teteje felett jelenik meg (a canvas vertikális offsetjét figyelembe véve). A szöveg gép-specifikus.

**Acceptance Scenarios**:

1. **Given** a játékos közel megy az Amőba géphez, **When** az `[E]` prompt megjelenik, **Then** a gép teteje felett látható és a szövege "[E] Amőba indítása".
2. **Given** a játékos közel megy a Snake géphez, **When** az `[E]` prompt megjelenik, **Then** a szövege "[E] Snake indítása".
3. **Given** a játékos közel megy a Casino ajtóhoz, **When** az `[E]` prompt megjelenik, **Then** a szövege "[E] Belépés a kaszinóba".
4. **Given** kisebb viewport (pl. 768px széles), **When** a prompt megjelenik, **Then** még mindig a gép felett jelenik meg, nem az oldalsávban.

---

### Edge Cases

- Ha a canvas teljesen kitölti a stage-t (1:1 skála, nincs vertikális üres tér), a prompt pozíció változatlan marad.
- Ha a játékos gyorsan mozog, a prompt azonnal frissüljön (nincs lag) — ez már most is teljesül.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A Snake gép `x` koordinátája max. 560 legyen (Casino ajtótól ≥ 80 px rés 1:1 skálán).
- **FR-002**: A `createInteractionPrompt` függvény kapja meg a stage magasságát és adja hozzá a `(stageHeight - canvasHeight) / 2` offsetet a `screenY`-hoz.
- **FR-003**: A `drawHub` függvény minden nem-door gép alá/fölé rajzolja a gép nevét (kis, visszafogott betűkkel, a machine `kind` alapján: "SNAKE", "AMŐBA").
- **FR-004**: A Casino ajtó alá/fölé "KASZINÓ" felirat kerüljön.
- **FR-005**: A `createInteractionPrompt` gépenként eltérő szöveget adjon vissza:
  - `snake-machine` → `"[E] Snake indítása"`
  - `amoba-machine` → `"[E] Amőba indítása"`
  - `casino-door` → `"[E] Belépés a kaszinóba"`
- **FR-006**: Az amőba `AmoebaGame.tsx` difficulty selection section-je amőba-témájú stílust kapjon: rácsháttér-motívum, X/O dísz, visszafogott design, nincs szöveges szintleírás.

### Key Entities

- **InteractionPromptState**: `screenY` számítása kiegészül a `canvasOffsetY` értékkel.
- **ArcadeMachineState**: `label?: string` mező adható hozzá, vagy a `kind` alapján kerül kirajzolásra a felirat a `drawHub`-ban.

## Success Criteria

- **SC-001**: Minden `[E]` prompt a gép canvas-pozíciójának teteje felett jelenik meg (±10 px).
- **SC-002**: Snake gép és Casino ajtó közt ≥ 60 px rés 1:1 skálán.
- **SC-003**: "SNAKE", "AMŐBA", "KASZINÓ" feliratok láthatók a hubban.
- **SC-004**: Az amőba difficulty képernyő vizuálisan amőba-témájú, nincs szöveges szintleírás.

## Assumptions

- A hub 960×640 belső logikai mérete nem változik.
- A Casino, Blackjack, Roulette gépek pozíciója nem változik.
- Mobilnézet / touch nem cél ebben a feature-ben.
- Az Amőba difficulty screen CSS-alapú megoldás marad (nem canvas).
