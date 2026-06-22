# Feature Specification: Amőba Vizuális Csiszolás

**Feature Branch**: `005-amoba-visual-polish`
**Created**: 2026-06-02
**Status**: Draft
**Input**: User description: "Szeretném az amőba játékot kicsit feldíszíteni, javítani, jobbá tenni a speckit workflow segítségével."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stílusos tábla és jelölők (Priority: P1)

A játékos egy vizuálisan vonzó 8x8-as táblán játszik, ahol az X és O jelölők színes, formázott megjelenéssel rendelkeznek, nem pusztán karakter-szövegként jelennek meg.

**Why this priority**: Az alapélmény – a tábla és a jelölők megjelenése az első dolog amit a játékos lát. Ez adja az alap „feel"-t a játéknak.

**Independent Test**: A tábla megjelenítésekor az X jelölők piros/narancs színnel, az O jelölők kék/cián színnel jelennek meg. A cellák hover állapotban enyhe kiemelést mutatnak.

**Acceptance Scenarios**:

1. **Given** futó játék, **When** a játékos megnézi a táblát, **Then** az X és O jelölők különböző színekkel jelennek meg, nem fehér alapon fekete karakterként.
2. **Given** üres cella, **When** a játékos fölé viszi az egeret, **Then** a cella enyhe fénnyel/kiemeléssel jelzi hogy kattintható.
3. **Given** az AI lép, **When** az AI tesz le egy jelet, **Then** az AI jele ugyanolyan stílusosan jelenik meg mint a játékos jele.

---

### User Story 2 - Nyerési sor kiemelés (Priority: P1)

Amikor a játék véget ér győzelemmel, a nyerő 4 jel vizuálisan kiemelésre kerül (villogás, kiemelő szín, vagy vonal rajzolása), hogy a játékos azonnal lássa melyik sorban győzött.

**Why this priority**: Egyértelmű vizuális visszajelzés a győzelemről – ez az egyik leghiányoltabb feature a jelenlegi verzióból, és sokat dob az élményen.

**Independent Test**: Győzelmi helyzetben a 4 nyerő cella vizuálisan megkülönböztethető a többitől (pl. zöld háttér, ragyogó keret, animált kiemelés).

**Acceptance Scenarios**:

1. **Given** játékos nyer, **When** a győzelem detektálódik, **Then** a nyerő 4 cella kiemelésre kerül (pl. zöld/arany háttér vagy pulzáló animáció).
2. **Given** AI nyer, **When** az AI győzelmét detektálja a rendszer, **Then** az AI nyerő celláit is kiemeli.
3. **Given** döntetlen, **When** a tábla megtelik, **Then** nincs kiemelés, csak a döntetlen felirat jelenik meg.

---

### User Story 3 - Aktuális játékos jelzője és lépés-visszajelzés (Priority: P2)

A játékos mindig látja kinek a köre van, és az utolsó lerakott jel vizuálisan megkülönböztethető a többitől (pl. kis pont / kiemelő keret), így nem kell emlékezni melyik volt az AI utolsó lépése.

**Why this priority**: Segíti a játékos tájékozódását – főleg a Hard AI ellen, ahol az AI gyorsan lép.

**Independent Test**: A felső sávban vagy a tábla közelében egy "Játékos köre" / "AI gondolkodik..." felirat jelenik meg. Az utolsó lerakott jel cellája enyhe kerettel van jelölve.

**Acceptance Scenarios**:

1. **Given** játékos köre, **When** a játék fut, **Then** a UI mutatja hogy "A te köröd (X)".
2. **Given** AI köre, **When** az AI gondolkodik, **Then** a UI mutatja "AI gondolkodik..." állapotot, és a tábla nem kattintható.
3. **Given** bármelyik lépés után, **When** a jel lekerül a táblára, **Then** az utolsó jel cellája enyhe vizuális kiemelést kap.

---

### User Story 4 - Meccs-statisztika a session alatt (Priority: P3)

A játékos egy session során nyomon követheti a nyert/vesztett/döntetlen meccsek számát az adott nehézség ellen.

**Why this priority**: Kisebb, de a visszatérő játékosoknak motiváló feature – addig maradnak ameddig legalább egyszer nyernek.

**Independent Test**: A tábla felett vagy a topbárban megjelenik egy "Győzelmek: X | Vereségek: Y | Döntetlen: Z" számláló, ami minden meccs végén frissül.

**Acceptance Scenarios**:

1. **Given** egy meccs véget ér győzelemmel, **When** a játékos újraindul, **Then** a győzelmek számlálója eggyel nő.
2. **Given** nehézséget vált a játékos (új meccs más nehézséggel), **When** új játék indul, **Then** a statisztika visszaáll.
3. **Given** böngésző frissítése, **When** az oldal újratöltődik, **Then** a statisztika visszaáll (session-only, nem kell persistálni).

---

### Edge Cases

- Mi történik ha a nyerési sor kiemelő animáció közben a játékos rákattint az "Újra" gombra? → Az animáció azonnal leáll, a tábla visszaáll.
- Az AI gondolkodás közben a tábla nem reagál kattintásra — ezt az akadálymentesség szempontjából jelezni kell (pl. cursor: not-allowed).
- Ha nincs nyerő cella (pl. a checkWin hibás adatot ad vissza), a kiemelés gracefully skip-elhető hibaüzenet nélkül.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A cellák X jelölői narancs/piros (#ef4444 vagy hasonló), az O jelölők kék/cián (#3b82f6 vagy hasonló) színnel és nagyobb betűmérettel (28px+) jelennek meg.
- **FR-002**: A cellák hover állapotban kiemelést mutatnak (háttérszín változás), ha a cella üres és a játékos köre van.
- **FR-003**: Győzelem esetén a `checkWin` által megtalált 4 nyerő cella koordinátái visszaadásra kerülnek és a UI kiemel minden nyerő cellát (zöld/arany háttér vagy CSS animáció).
- **FR-004**: A játék állapot-sáv (aktuális játékos / AI gondolkodás / győztes / döntetlen) a tábla felett vagy alatt jelenik meg, jól olvasható méretben.
- **FR-005**: Az utolsó lerakott jel cellája (mind játékos, mind AI) kisebb vizuális jelzőt kap (pl. pont a sarokban, enyhe keret).
- **FR-006**: A session statisztika (győzelmek/vereségek/döntetlen) React state-ben tárolódik és a felső sávban megjelenik. Nehézség váltásakor visszaáll.
- **FR-007**: A `checkWin` függvény kiegészítendő/körbevehető egy olyan helperrel, ami visszaadja a nyerő cellák koordinátáit (nem csak boolean-t).

### Key Entities

- **WinResult**: `{ winner: 'X' | 'O' | null, cells: Array<{row: number, col: number}> }` — a győzelemvizsgálat eredménye cellák listájával.
- **SessionStats**: `{ wins: number, losses: number, draws: number }` — session-szintű statisztika.
- **LastMove**: `{ row: number, col: number } | null` — az utolsó lerakott jel pozíciója.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A tábla 30 FPS+ felett fut vizuális animációkkal is (CSS transition alapú animációk, nem canvas-heavy megoldás).
- **SC-002**: A nyerő cellák kiemelése győzelem után azonnal (1 frame-en belül) megjelenik.
- **SC-003**: A "AI gondolkodik" állapot jelzése 100ms-on belül megjelenik az AI lépésének indítása után.
- **SC-004**: A session statisztika helyes: 20 meccsen keresztül nem csúszik el a számláló.
- **SC-005**: A változtatások nem törik az existing gameLogic unit teszteket; a `checkWin` visszafelé kompatibilis marad.

## Assumptions

- A megoldás CSS/React alapú (nem canvas) — a jelenlegi grid-alapú megközelítést megtartjuk, kiegészítjük stílussal.
- Hangeffekteket NEM adunk hozzá ebben a feature-ben (külön task lehet).
- A `checkWin` bővítése visszafelé kompatibilis módon történik (pl. egy új `findWinCells` helper hozzáadásával a `gameLogic.ts`-be).
- Nincs szükség persistálásra (localStorage) a session statisztikához.
- A jelenlegi `BOARD_SIZE=8` és `WIN_LENGTH=4` értékek nem változnak.
