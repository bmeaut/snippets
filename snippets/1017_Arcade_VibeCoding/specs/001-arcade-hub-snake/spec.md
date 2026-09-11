# Feature Specification: Arcade Hub Canvas RPG + Snake

**Feature Branch**: `001-arcade-hub-snake`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "A Hub legyen felülnézetes, 2D-s játékterem Canvas alapon, ahol egy karakter sétál a termében, gépekkel interakcióba lép, és E-vel elindítja a Snake játékot."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Játékterem bejárása és Snake indítása (Priority: P1)

A felhasználó egy top-down, 2D-s játékterembe érkezik, ahol egy egyszerű, színes téglalapokból álló karaktert irányít. A karakter odasétál a Snake játékgéphez, megjelenik az [E] interakciós jelzés, majd az E billentyű megnyomására a Snake játék betöltődik.

**Why this priority**: Ez az új Hub magja. Ha a játékterem mozgása és az interakció nem működik, nincs belépési pont a Snake-hez.

**Independent Test**: Az alkalmazás megnyitása, karakter mozgatása, gép megközelítése, [E] prompt megjelenése, Snake indítása.

**Acceptance Scenarios**:

1. **Given** a játékterem aktív, **When** a felhasználó WASD-vel vagy nyílbillentyűkkel mozgatja a karaktert, **Then** a karakter a Canvas térben mozog
2. **Given** a karakter egy gép közelében van, **When** belép az interakciós zónába, **Then** megjelenik az [E] jelzés a gép felett vagy mellett
3. **Given** az [E] jelzés látható, **When** a felhasználó megnyomja az E billentyűt, **Then** a Hub Canvas átvált és elindul a Snake játék
4. **Given** a Snake játék véget ér vagy a felhasználó visszatér a menübe, **When** a Hub újra megjelenik, **Then** a játékterem ismét használható

---

### User Story 2 - Snake játék játszása (Priority: P1)

A felhasználó a már meglévő Snake játékkal játszik: a kígyó almákat eszik, növekszik és gyorsul. Falnak vagy önmagának ütközve a játék véget ér.

**Why this priority**: A Snake marad a fő játéktartalom, és a Hub csak belépési pont hozzá.

**Independent Test**: Játék indítása a Hubból, Snake végigjátszása, pontok gyűjtése, játékvég és újraindítás.

**Acceptance Scenarios**:

1. **Given** a Snake játék aktív, **When** a játékos nyílbillentyűket nyom, **Then** a kígyó az adott irányba mozog
2. **Given** a kígyó almát eszik, **When** az alma eltűnik, **Then** az aktuális pontszám nő és új alma jelenik meg
3. **Given** a kígyó falnak vagy önmagának ütközik, **When** a collision bekövetkezik, **Then** a játék véget ér
4. **Given** a játék véget ért, **When** a felhasználó újraindítja, **Then** egy új Snake kör indul

---

### User Story 3 - Pontszámok és High Score követése (Priority: P2)

A felhasználó a játék során látja az aktuális pontszámot. A legjobb eredmény böngészőben megmarad, és a következő körökben is megjelenik.

**Why this priority**: A scoring továbbra is fontos, de a Hub pivot nem érinti a storage működését.

**Independent Test**: Snake indítása, pontszerzés, játékvég, high score ellenőrzése, új játék indítása.

**Acceptance Scenarios**:

1. **Given** a Snake játék aktív, **When** az első almát megeszi, **Then** az aktuális pontszám 1-re nő
2. **Given** a játék véget ért, **When** a következő kör indul, **Then** a korábbi high score továbbra is látható
3. **Given** az új körben jobb eredmény születik, **When** a játék véget ér, **Then** az új high score megőrzésre kerül

---

### Edge Cases

- **Interakciós zóna**: mekkora távolságról jelenjen meg az [E] prompt?
- **Hub állapot visszatéréskor**: a karakter hol jelenjen meg újra a Hubban?
- **Gépek száma**: az MVP-ben csak a Snake gép legyen aktív, a helyek későbbi bővítésre előkészítve.
- **Placeholder grafika**: a karakter és gépek egyszerű színes téglalapok maradjanak, külső asset nélkül.

## Requirements *(mandatory)*

### Functional Requirements

**FR1: Top-down Canvas Hub**
- A Hub egy felülnézetes, 2D-s játékterem Canvas alapon.
- A felhasználó egy egyszerű karaktert irányít, aki a teremben mozog.
- A karakter és a gépek placeholder grafikával jelennek meg: egyszerű színes téglalapokkal.
- Az UI legyen reszponzív és billentyűzettel irányítható.

**FR2: Interakció a Snake géppel**
- A Hubban legalább egy interaktív játékgép legyen: a Snake gép.
- Ha a karakter elég közel kerül a géphez, jelenjen meg az [E] interakciós felirat.
- Az E billentyű megnyomására a Snake játék induljon el.

**FR3: Hub és Snake közötti átmenet**
- A Hub Canvas scene és a Snake játék között egyértelmű scene-váltás legyen.
- A Snake játékból a felhasználó vissza tudjon térni a Hubba.
- A Snake belső logikája és a storage réteg érintetlen maradjon.

**FR4: Snake játék és pontozás**
- A Snake szabályai változatlanok maradjanak.
- Az aktuális pontszám és a high score továbbra is látható legyen.
- A böngészőben tárolt high score megmaradjon a későbbi körökre is.

**FR5: Moduláris stabilitás**
- A Hub hibája ne döntse le a Snake modult, és fordítva.
- A Snake továbbra is külön modul maradjon, jól definiált belépési ponttal.

### Non-Functional Requirements

**NFR1: Teljesítmény**
- A Hub Canvas scene legalább 60 FPS célra legyen optimalizálva.
- A Snake továbbra is legalább 30 FPS-en fusson.

**NFR2: Reszponzivitás**
- A játékterem alkalmazkodjon a képernyőmérethez.
- A mozgás billentyűzettel történjen, későbbi érintéses bővítés lehetőségével.

**NFR3: Hozzáférhetőség és olvashatóság**
- Az [E] prompt és a gépek kontrasztosak és jól észrevehetők legyenek.
- A placeholder színek maradjanak tisztán elkülönülők.

**NFR4: Kód Minőség**
- TypeScript strict mode kötelező.
- A kód és a dokumentáció nyelve következetes maradjon.
- A Snake storage és logika ne módosuljon a Hub pivot miatt.

## Success Criteria *(mandatory)*

1. **Hubban lehet mozogni**: a felhasználó a Canvas Hubban tud sétálni a karakterrel.
2. **Snake gép felismerhető**: a gép közelében megjelenik az [E] jelzés.
3. **Snake indítható**: az E megnyomására a Snake játék elindul.
4. **Snake érintetlen marad**: a játék logikája és a storage viselkedése nem sérül.
5. **Visszatérés működik**: a Snake-ből vissza lehet térni a Hubba.

## Key Entities *(mandatory)*

### Hub Scene
- **Felelős**: a top-down játékterem, karakter és gépek megjelenítése.
- **Adatok**: scene state, player position, camera/viewport, gép-lista.
- **API**: `movePlayer(direction)`, `checkInteraction()`, `renderHub(canvas)`.

### Player Avatar
- **Felelős**: a Hubban mozgó karakter.
- **Adatok**: pozíció, méret, sebesség, irány, collision bounds.
- **API**: `updateMovement()`, `getBounds()`, `setPosition()`.

### Arcade Machine
- **Felelős**: a Snake gép vizuális és interakciós reprezentációja.
- **Adatok**: pozíció, méret, gameId, prompt állapot.
- **API**: `isInRange(player)`, `renderMachine(canvas)`, `launchGame()`.

### Interaction Prompt
- **Felelős**: az [E] felirat megjelenítése, ha a karakter közel van a géphez.
- **Adatok**: visible, label, targetMachineId.
- **API**: `show()`, `hide()`, `attachTo(machine)`.

### Snake Game Module
- **Felelős**: a már meglévő Snake játék változatlan működése.
- **Megjegyzés**: a Snake logika és storage nem része a Hub pivotnak, csak integrációs belépőpontja van.

### Storage (High Score Persistence)
- **Felelős**: a Snake high score tárolása.
- **Megjegyzés**: a Hub pivot nem módosítja a storage formátumát vagy viselkedését.

## Assumptions

- Az MVP-ben nincs szükség külső képekre vagy hangokra; minden placeholder grafikával készül.
- A Snake gép az egyetlen aktív gép az első verzióban.
- A Hub scene-ben a játékos visszaindulási pontja később finomítható.
- A Snake modul jelenlegi contractja és storage logikája változatlan marad.

## Out of Scope (Future Phases)

- Kézzel rajzolt tilemap vagy sprite-alapú art.
- Többféle gép és NPC-k a Hubban.
- Inventor, quest, combat vagy RPG progression.
- Audio, zene, külső asset pipeline.

---

**Status**: ✅ Draft Specification Ready for Review | **Next Step**: `/speckit.plan` vagy a plan.md frissítése az új Hub scene-hez