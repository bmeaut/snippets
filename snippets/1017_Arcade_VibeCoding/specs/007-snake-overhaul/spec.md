# Feature Specification: Snake Overhaul

**Feature Branch**: `007-snake-overhaul`
**Created**: 2026-06-02
**Status**: Ready

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Sima mozgás, jobb vizuál (Priority: P1)

A játékos egy vizuálisan vonzó, akadásmentes Snake játékot lát. A kígyó folyamatosan mozog (nem ugrik képkockáról képkockára), a cellák lekerekítettek, a fej és a test különböző árnyalatú, az alma sugárzik.

**Why this priority**: Ezek az alapélmény javítások — nélkülük a többi feature is kevésbé élvezhető.

**Independent Test**: A játék elindítása után a kígyó mozgása vizuálisan folyamatos; az alma kerek és "glowol"; a test zöld gradienssel sötétedik a fej felé haladva.

**Acceptance Scenarios**:

1. **Given** futó játék, **When** a kígyó mozog, **Then** a mozgás nem ugrik — `requestAnimationFrame` alapú renderelés, nincsenek `setTimeout`-ból fakadó frame-kihagyások.
2. **Given** a canvas renderelve van, **When** a játékos megnézi, **Then** a cellák lekerekítettek (`roundRect`), a fej világosabb mint a farok, az alma kerek (kis körív) és narancs glowot mutat.
3. **Given** a játék elindul, **When** a UI látható, **Then** a szövegek magyarok ("Vissza a Hubba", "Újraindítás", "Játék vége"), score/rekord HTML overlay-ként jelenik meg (nem canvas-szövegként).

---

### User Story 2 — Portál falak (Priority: P1)

A kígyó nem hal meg ha eléri a falat — átmegy az egyik oldalon és kijön a szemköztin. Teljesen megváltoztatja a stratégiát.

**Why this priority**: Ez az egyetlen szabályváltozás ami a legtöbb döntéshozatali helyzetet megváltoztatja — a sarokba szorulás megszűnik végzetesnek lenni.

**Independent Test**: A kígyó a jobb szélről kilépve azonnal a bal szélen jelenik meg; ugyanígy fel/le irányban.

**Acceptance Scenarios**:

1. **Given** a kígyó eléri a jobb falat, **When** a következő tick-en továbblép, **Then** a bal szélen jelenik meg (x=0), teljes hosszában.
2. **Given** a kígyó eléri a felső falat, **When** továbblép, **Then** az alsó szélén jelenik meg.
3. **Given** a kígyó saját testébe hajtana portálon keresztül, **When** az ütközés detektálódik, **Then** a játék véget ér (önmagába hajtás továbbra is halált jelent).

---

### User Story 3 — Arany alma (Priority: P2)

Minden 7. rendes alma elfogyasztása után megjelenik egy arany alma 6 másodpercre. 3 pontot ér. Ha a játékos nem eszi meg idejében, eltűnik.

**Why this priority**: Izgalmat ad anélkül hogy kötelező lenne — opcionális risk/reward döntés.

**Independent Test**: Az arany alma megjelenésekor egy látható visszaszámláló (pl. körös progress bar vagy számjegy a cella sarkában) jelzi a hátralévő időt; eltűnéskor nem keletkezik pont.

**Acceptance Scenarios**:

1. **Given** a játékos 7 almát evett, **When** a 7. alma megevése után, **Then** megjelenik egy arany alma (sárga/arany szín) a táblán a normál almával együtt.
2. **Given** az arany alma látható, **When** a játékos ráhajtja a kígyót, **Then** 3 pont íródik jóvá és az arany alma eltűnik (7 alma múlva újra megjelenik a ciklus).
3. **Given** az arany alma látható, **When** 6 másodperc eltelik evés nélkül, **Then** az arany alma eltűnik, a ciklus újraindul.
4. **Given** az arany alma aktív, **When** a játékos megnézi a cellát, **Then** látható visszaszámláló jelzi a hátralévő időt.

---

### User Story 4 — Kő akadályok (Priority: P2)

Score 8 elérése után minden 4. pont egy új kő cella jelenik meg véletlenszerű pozícióban. A kőbe hajtva a kígyó meghal. Maximum 12 kő lehet egyszerre a pályán.

**Why this priority**: A nehézség nem csak a sebességtől függ — a tér fokozatosan szűkül, hosszú játékok is kihívóak maradnak.

**Independent Test**: Score 8-nál megjelenik az 1. kő (szürke cella); score 12-nél a 2.; stb. A kőbe hajtás azonnal game over-t vált ki.

**Acceptance Scenarios**:

1. **Given** score < 8, **When** a játékos játszik, **Then** nincsenek kő akadályok a pályán.
2. **Given** score eléri a 8-at, **When** az alma megevése megtörténik, **Then** egy kő jelenik meg véletlenszerű üres cellán (nem a kígyón, nem az almán).
3. **Given** kő van a pályán, **When** a kígyó feje ráhajtana, **Then** game over.
4. **Given** 12 kő már a pályán van, **When** újabb pont szerezhető, **Then** nem jelenik meg több kő (a maximum elérve).

---

### User Story 5 — Lassító alma (Priority: P3)

Minden 5. rendes alma elfogyasztása után megjelenik egy kék lassító alma. Elfogyasztva 3 másodpercig feleakkora sebesség. Ha a játékos nem eszi meg, 8 másodperc után eltűnik.

**Why this priority**: Segítség haladó játékosoknak amikor már nagyon gyors a kígyó — opcionális életmentő.

**Independent Test**: A kék alma megjelenésekor a rendes almával együtt látható; evés után a kígyó érezhetően lelassul 3 másodpercre.

**Acceptance Scenarios**:

1. **Given** a játékos 5 almát evett, **When** az 5. alma megevése után, **Then** megjelenik egy kék alma a táblán.
2. **Given** a kék alma látható, **When** a kígyó megeszi, **Then** 3 másodpercig a sebesség felére csökken (azaz a tick delay megduplázódik), 1 pont jár érte.
3. **Given** a kék alma látható, **When** 8 másodperc eltelik evés nélkül, **Then** eltűnik.
4. **Given** lassítás aktív, **When** a játékos megnézi a score panelt, **Then** látható visszaszámláló vagy ikon jelzi az aktív lassítást.

---

### Edge Cases

- Arany és kék alma egyszerre is lehet a táblán — mindkét ciklus egymástól független.
- Kő nem jelenhet meg arany alma vagy kék alma helyére.
- Portál átugráskor az ütközésdetektálás (önmaga, kő) az új pozíción fut.
- Ha az arany/kék alma lejáratakor épp az a cella szabadul fel, ahol a kígyó farka volt, a következő spawn oda kerülhet.
- Lassítás alatt arany alma is aktív lehet — a lassítás a kígyó sebességét csökkenti, a pontértéket nem.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `requestAnimationFrame` alapú render loop: a game logika tick-je változatlan (diszkrét lépések), de minden frame-ben renderelés történik.
- **FR-002**: Portál falmozgás: fal elérése helyett az ellentétes oldalon jelenik meg a fej (`x = (x + GRID_SIZE) % GRID_SIZE`).
- **FR-003**: Arany alma: 7 alma-ciklus, 6s timeout, 3 pont, arany szín, visszaszámláló.
- **FR-004**: Kő akadályok: score 8-tól, minden 4. pontnál +1 kő, max 12, kőbe hajtás = game over.
- **FR-005**: Lassító alma: 5 alma-ciklus, 8s timeout, 3s lassítás (tick delay ×2), 1 pont, kék szín.
- **FR-006**: Magyar UI: "Vissza a Hubba", "Újraindítás", "Játék vége", "Pontszám", "Rekord".
- **FR-007**: Vizuális: lekerekített cellák, gradiens test, kerek alma narancs glowval, kő szürke textúra.
- **FR-008**: Score és rekord HTML overlay-ként jelenik meg (nem canvas `fillText`).

### Key Entities (bővített SnakeState)

- **SnakeState** bővítés:
  - `stones: Coordinate[]` — kő akadályok pozíciói
  - `goldenApple: { pos: Coordinate; spawnedAt: number } | null` — arany alma
  - `blueApple: { pos: Coordinate; spawnedAt: number } | null` — kék alma
  - `slowUntil: number | null` — lassítás lejárata (timestamp)
  - `applesEaten: number` — összes alma számláló (ciklusokhoz)

## Success Criteria

- **SC-001**: Nincsenek látható frame-kihagyások `requestAnimationFrame`-re való áttérés után.
- **SC-002**: Portál falak 100%-ban megbízhatóak — falon átmenve soha nem hal meg a kígyó (csak önmagától és kőtől).
- **SC-003**: Arany alma pontosan 6s után tűnik el ha nem eszik meg.
- **SC-004**: Kő akadályok soha nem jelennek meg kígyón, almán, vagy másik kövön.
- **SC-005**: Lassítás alatt a tick delay pontosan kétszeres.
- **SC-006**: Az összes meglévő unit teszt zöld marad.

## Assumptions

- A 20×20-as grid méret és a 24px cell méret nem változik.
- High score localStorage-ból való betöltése megmarad.
- Mobilos swipe kontroll megmarad.
- Hang effekteket NEM adunk hozzá ebben a feature-ben.
