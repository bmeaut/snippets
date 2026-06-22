# Feature Specification: Rulett Overhaul

**Feature Branch**: `008-roulette-overhaul`
**Created**: 2026-06-02
**Status**: Ready

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Forgó kerék golyóval (Priority: P1)

A játékos egy animált rulett kereket lát, amelyben egy fehér golyó az óramutató járásával ellentétesen kering a kerék peremén, majd lelassulva begördül a nyerő zsebbe. Vizuálisan hiteles, mint egy igazi rulett asztalnál.

**Why this priority**: Ez a legfontosabb vizuális fejlesztés — a golyó nélküli kerék nem adja vissza a rulett élményt.

**Independent Test**: Pörgetéskor látható egy fehér kör a kerék peremén, amely gyorsan kering, majd lelassul és a nyerő zseb felett áll meg.

**Acceptance Scenarios**:

1. **Given** a játékos megnyomja a "Pörgetés" gombot, **When** az animáció elindul, **Then** egy fehér golyó jelenik meg a kerék külső gyűrűjén és gyorsan kering (ellentétes irányban mint a kerék).
2. **Given** az animáció lefut (3 másodperc), **When** a kerék megáll, **Then** a golyó a nyerő számnak megfelelő zsebben látható.
3. **Given** a kerék megállt, **When** a játékos az eredményt nézi, **Then** a golyó mozdulatlanul ül a zsebben amíg az eredmény megjelenik.

---

### User Story 2 — Utolsó 10 szám kijelzése (Priority: P1)

A kerék mellett vagy felett megjelenik az utolsó 10 pörgetés eredménye — szép, kaszinós stílusban: kis színes körök (piros/fekete/zöld) a számmal, a legfrissebb bal/felső oldalon.

**Why this priority**: Minden online kaszinóban alapfunkció — a játékos meglátja a "hot/cold" számokat és dönti el a következő tét stratégiáját.

**Independent Test**: 3 pörgetés után 3 szám jelenik meg a kijelzőn, helyes sorrendben és helyes piros/fekete/zöld színnel.

**Acceptance Scenarios**:

1. **Given** az első pörgetés eredménye 17 (piros), **When** az eredmény megjelenik, **Then** a history panelben egy piros "17" badge látható.
2. **Given** 10 pörgetés után egy 11. is lefut, **When** az eredmény megjelenik, **Then** a legrégebbi szám kiesik — mindig max. 10 szám látható.
3. **Given** a kerék pörög, **When** a játékos nézi a history-t, **Then** az előző eredmények láthatók (az éppen futó pörgetés eredménye még nem jelenik meg).

---

### User Story 3 — Versenypalya (Racetrack) nézet (Priority: P1)

A standard számtábla mellé egy második nézet kapcsolható: a Racetrack (versenypalya / announce tábla). Ez ovális elrendezésben mutatja a 0–36 számokat kerék-sorrendben. Innen elérhető:
- **Szomszédok** (Voisins): kattintásra egy számra, megadható 1–4 szomszéd — a szám + N szomszéd mindkét oldalon (kerék-sorrend szerint) straight tétként kerül fel
- **Kis széria** (Tiers du Cylindre): 12 szám a kerék 5/8-a körül (27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33) — 6 split tét
- **Nagy széria** (Voisins du Zéro): 17 szám a nulla körül — hagyományos chip-elosztással (trio, splitek, corner)
- **Árva számok** (Orphelins): 8 szám amit a Tiers és Voisins nem fed (1, 6, 9, 14, 17, 20, 31, 34) — straight és split tétek
- **Zéró játék** (Jeu Zéro): 7 szám a 0 közelében (12, 35, 3, 26, 0, 32, 15) — 3 split + 1 straight

**Why this priority**: Ez a feature különbözteti meg a profil roulette-től — a haladó játékos ezt keresi.

**Independent Test**: A "Kis széria" gomb megnyomása után a tétek között megjelenik 6 split tét a 12 Tiers-számra; a szomszéd szelektor egy szám kiválasztásakor pontosan 2N+1 straight tét keletkezik.

**Acceptance Scenarios**:

1. **Given** Racetrack nézetben a játékos rákattint a "Kis széria" gombra, **When** a tét hozzáadódik, **Then** 6 split tét keletkezik (27-13, 36-11, 30-8, 23-10, 5-24, 16-33) a kiválasztott chipértékkel.
2. **Given** Racetrack nézetben a szomszéd szelektor 2-re van állítva és a játékos a 17-re kattint, **When** a tét felvesz, **Then** 5 straight tét keletkezik: 17 + 2 szomszéd mindkét oldalon (9, 22, 17, 34, 6 — kerék sorrendben).
3. **Given** a Racetrack nézet aktív, **When** a játékos visszavált a Standard nézetre, **Then** a már felvett Racetrack tétek megmaradnak.
4. **Given** Nagy széria gomb megnyomva, **When** a tétek keletkeznek, **Then** a standard tábla bet listájában megjelennek a Voisins du Zéro hagyományos tétjei.

---

### Edge Cases

- Szomszéd bet ahol a szám a kerék végén van (pl. N=4 szomszéd, wrap-around kerék sorrendben).
- Ha a játékosnak nincs elég egyenlege a teljes Voisins/Tiers bet fedezetéhez → a tét nem kerül fel, hibaüzenet.
- Golyó animáció: ha az előző pörgetés még fut, az új pörgetés nem indítható (disabled gomb).
- Racetrack nézetben kattintott tét + Standard nézetből is felvett tét egyszerre is szerepelhet a listában.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A kerék animáció során egy fehér golyó kering a külső gyűrűn (Canvas vagy SVG `requestAnimationFrame`), ellentétes irányban a kerékkel, majd a nyerő zsebben áll meg.
- **FR-002**: Az utolsó 10 pörgetés eredménye piros/fekete/zöld színes badge-ként jelenik meg, a legfrissebb bal oldalon. Session-only (nem kell localStorage).
- **FR-003**: A standard táblán egy "Versenypalya" / "Standard" toggle gomb vált a két nézet között.
- **FR-004**: A Racetrack ovális elrendezésben mutatja a számokat kerék-sorrendben (WHEEL_SEQUENCE alapján).
- **FR-005**: Szomszéd szelektor: 1–4 értékre állítható (alapértelmezett: 1). Szám kattintásra `2*N+1` straight tét keletkezik.
- **FR-006**: Predefined gombok — mind a kiválasztott chipértékkel kerülnek fel:
  - Kis széria: 6 split
  - Nagy széria: Voisins du Zéro hagyományos elosztás (9 chip: trio×2, corner×2, split×5)
  - Árva számok: Orphelins (5 chip: straight×1, split×4)
  - Zéró játék: Jeu Zéro (4 chip: straight×1, split×3)
- **FR-007**: Magyar UI: "Vissza", "Pörgetés", "Törlés", "Versenypalya", "Szomszédok", "Kis széria", "Nagy széria", "Árva számok", "Zéró játék".
- **FR-008**: A golyó animáció kezdeti szögsebessége a kerék forgásától független (golyó gyorsabb, ellentétes irányú), és `requestAnimationFrame` alapú.

### Key Entities

- **RouletteHistory**: `number[]` — az utolsó max. 10 pörgetés eredménye (session-only state)
- **RactrackBet** nem új típus — a Racetrack mindig a meglévő `Bet` típusokra (`straight`, `split` stb.) bontja le a téteket
- **NeighborCount**: `1 | 2 | 3 | 4` — a szomszéd szelektor értéke

### Golyó animáció technikai terv

A golyó pozícióját `requestAnimationFrame`-ben számolom:
- `ballAngle` indul 0°-ból, gyorsan nő negatív irányban (ellentétes kering)
- `ballRadius` a pörgetés végén csökken a külső gyűrűből a zseb közepéig
- A kerék CSS transform-ja (cubic-bezier) és a golyó rAF-animációja szinkronban dekelerál
- A nyerő szög = kerék célszöge ellentétese (golyó statikus nézőpontból a zsebhez kerül)

## Success Criteria

- **SC-001**: A golyó minden pörgetésnél láthatóan a nyerő szám zsebénél áll meg (±1 zseb tolerancia a vizuális precizitásban).
- **SC-002**: Az utolsó 10 szám history mindig helyes sorrendben és színnel jelenik meg.
- **SC-003**: Kis széria pontosan 6 split tét, Nagy széria pontosan 9 chip, Árva 5, Jeu Zéro 4.
- **SC-004**: Szomszéd bet 0 esetén: 3 straight (0 + bal + jobb), 4 esetén: 9 straight.
- **SC-005**: Racetrack nézetváltás nem törli a már felvett téteket.

## Assumptions

- European single-zero wheel marad (37 szám).
- A golyó Canvas-alapú lesz (a meglévő SVG kerék mellé Canvas overlay, vagy teljes Canvas újraírás — az implementáció dönti el).
- A predefined Racetrack bétek chipértéke a jelenleg kiválasztott chip értékével egyenlő (nem fix 1 chip).
- Hang effekteket NEM adunk hozzá ebben a PR-ban.
- A meglévő BettingBoard (standard nézet) érintetlen marad — a Racetrack mellé kerül, nem helyette.
