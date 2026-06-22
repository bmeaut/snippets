# Feature Specification: Amőba (Gomoku)

**Feature Branch**: `002-ameoba-hub-integration`
**Created**: 2026-05-19
**Status**: Draft
**Input**: User description: "Egy új játékot szeretnék hozzáadni az Arcade Hubhoz: egy 8x8-as Amőba (Gomoku) játékot, ahol a gép ellen kell játszani.\n\nKövetelmények: Hub integráció, nehézségi menü (Könnyű/Közepes/Nehéz), 8x8-as tábla, 4 jel a győzelemhez, játékos (X) kezd, AI különböző logikákkal, GameModuleContract követése, ErrorBoundary és "Vissza a Hubba" gomb." 

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Indítás a Hubból (Priority: P1)
A játékos a Hub 2D Canvas nézetében egy kék játékegységhez sétál, lenyomja az `E` gombot és elindul az Amőba modul.

**Why this priority**: Ez a belépési pont — enélkül a játék nem érhető el.

**Independent Test**: A Hubban jelenjen meg kék placeholder; közelítve az `E` lenyomása megnyitja a nehézségi menüt.

**Acceptance Scenarios**:
1. **Given** a Hub nézet, **When** a játékos megközelíti a kék gépet és lenyomja `E`, **Then** megjelenik a nehézségi választó képernyő.
2. **Given** választás után, **When** a nehézségi szintet kiválasztja, **Then** elindul az 8x8-as játék és a játékos (X) kezd.

---

### User Story 2 - Játék és visszatérés (Priority: P1)
A játékos játszik az AI ellen; a `Vissza a Hubba` gomb bármikor visszaviszi a Hubba, mentés nélkül lezárva a játékot.

**Why this priority**: Alapvető navigáció és hibamentes felhasználói élmény.

**Independent Test**: A játékablakban látható a `Vissza a Hubba` gomb; lenyomva bezárja a modult és visszatér a Hub nézetre.

**Acceptance Scenarios**:
1. **Given** a futó játék, **When** a játékos megnyomja a `Vissza a Hubba` gombot, **Then** a modul bezárul és a Hub jelenik meg.

---

### User Story 3 - AI nehézségek viselkedése (Priority: P2)
A játékos különböző nehézségeket választhat, az AI viselkedése a követelmények szerint változik.

**Independent Test**: Egyszerű vizsgálatokkal ellenőrizhető az AI viselkedése (véletlenszerű lépés, blokkoló lépések, Minimax-szerű döntések korlátozott mélységgel).

**Acceptance Scenarios**:
1. **Given** Easy módban, **When** az AI lép, **Then** egy véletlenszerű üres mezőre tesz jel.
2. **Given** Medium módban, **When** a játékosnak 2 vagy 3 egymás melletti jele van, **Then** az AI megpróbálja blokkolni; egyébként véletlenszerű lépést ad.
3. **Given** Hard módban, **When** az AI döntést hoz, **Then** a Minimax (alfa-béta vágással) korlátozott mélységgel választ jó lépést és nem blokkolja a böngészőt.

---

### Edge Cases
- Döntetlen: a tábla megtelik, nincs 4 egy sorban → döntetlen állapot kezelése.
- Érvénytelen lépés: mező foglalt → lépés elutasítása.
- AI időtúllépés: Ha a Hard AI túl sokáig számol, időlimit-et alkalmazunk és visszaesik Medium/Easy viselkedésre.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001 (Hub Integráció)**: A Hub 2D Canvas nézetében jelenjen meg az Amőba játékegység (más színű placeholder, pl. kék). Ha a játékos odamegy és lenyomja az `E` gombot, az Amőba modul megnyílik.
- **FR-002 (Nehézségi választó)**: Indításkor megjelenik egy választóképernyő 3 gombbal: `Könnyű`, `Közepes`, `Nehéz`.
- **FR-003 (Tábla és szabályok)**: A játék 8x8-as rácson zajlik; a győzelemhez 4 jelet kell összegyűjteni egy folyamatos vonalban (horizontálisan, vertikálisan vagy átlósan). A játékos (`X`) kezd.
- **FR-004 (AI Nehézségek)**:
  - **Easy**: véletlenszerű üres mező.
  - **Medium**: egyszerű blokkoló logika — prioritása a játékos 2 vagy 3 egy sorban lévő jeleinek blokkolása; ha nincs ilyen fenyegetés, véletlenszerű lép.
  - **Hard**: Minimax algoritmus alfa-béta vágással, korlátozott mélységgel a teljesítmény megőrzéséért.
- **FR-005 (Architektúra / Contract)**: Az Amőba modul teljesítenie kell a `GameModuleContract` interfészt: be kell építeni `ErrorBoundary`-t, és támogatni kell a `Vissza a Hubba` gombot.
- **FR-006 (Teljesítmény és biztonság)**: A Hard AI számítása korlátozott mélységű legyen, és a fő szálat ne blokkolja (nem fagyhat le a böngésző). Szükség esetén alkalmazz időlimitet vagy worker-t a számításhoz.

### Key Entities
- **GameState**: `board: string[][]` (8x8), `currentPlayer: 'X'|'O'`, `difficulty: 'easy'|'medium'|'hard'`, `winner: 'X'|'O'|'draw'|null`, `moveHistory: Move[]`, `startedAt`, `endedAt`, `isOver: boolean`.
- **Move**: `{row: number, col: number, player: 'X'|'O', time: string}`
- **AIEngine**: Konfigurálható `difficulty` és `maxDepth` (Hard esetén).

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: A Hub-ból indítás `E` lenyomás után sikeres: 100% esetben megjelenik a nehézségi menü.
- **SC-002**: A választott nehézségi szint után legfeljebb 1 másodperc alatt elindul a játék UI (kivéve, ha a Hard AI számítása aktívan fut — ebben az esetben látható progress vagy fallback viselkedés).
- **SC-003**: Hard módban az AI nem blokkolja 2 másodpercnél tovább a fő szálat egy teljes döntés során (ha szükséges, használjunk időlimitet vagy web worker-t).
- **SC-004**: Minden FR megfelelhetősége automata és manuális acceptance tesztekkel igazolható (unit + integrációs tesztek a `tests/unit` alatt).

## Assumptions
- A projekt meglévő `GameModuleContract` interfésze és Hub integrációs pontjai rendelkezésre állnak.
- A játék fut a böngészőben, és nem cél natív alkalmazás támogatása v1-ben.
- Ha a `Hard` AI túl lassú, elfogadható a mélység korlátozása (pl. max 4-6 lépés), vagy a számítás worker-be helyezése.
- Mentés / persistálás nem szükséges az első verzióhoz (játék állapota nem marad meg újraindítás után).
