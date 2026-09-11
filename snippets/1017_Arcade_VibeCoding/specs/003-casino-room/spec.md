# Feature Specification: Casino Room

**Feature Branch**: `003-casino-room`  
**Created**: 2026-05-23  
**Status**: Draft  
**Input**: User description: "Egy új, kaszinó szobát (Casino Room) szeretnék hozzáadni a meglévő Arcade Hubhoz.\n\nKérlek, hozz létre egy új specifikációs könyvtárat (valószínűleg 003-casino-room) és frissítsd a `spec.md`, `plan.md` és `data-model.md` dokumentumokat az alábbi követelmények alapján, majd generálj egy új `tasks.md` fájlt az implementációhoz!\n\nÚj követelmények (FR - Functional Requirements):\n1. Többszobás navigáció (Multi-room): Az eredeti Arcade Hub jobb oldalán legyen egy kijárat/ajtó (pl. egy sárga téglalap \"Casino\" felirattal). Ha a játékos odasétál és megnyomja az 'E' gombot, a játéktér váltson át a Casino szobába. A Casino szobában is legyen egy ajtó a bal oldalon, amivel vissza lehet menni az Arcade Hubba.\n2. Közös Pénztárca (Wallet) Napi Bónusszal: Az egyenleget és az utolsó belépés dátumát (timestamp) a böngésző `localStorage` memóriájában kell tárolni. Ha a játékos először nyitja meg a játékot az adott napon, automatikusan kapjon egy 10.000 Ft-os \"Napi Bónuszt\" (ez hozzáadódik a meglévő egyenlegéhez). Ha életében először játszik, a kezdőtőkéje szintén 10.000 Ft legyen. Ezt az egyenleget a Casino szobában a képernyő sarkában folyamatosan mutassa a UI.\n3. Blackjack Gép (Standard szabályok): \n   - A Casino szobában egy zöld asztal/gép reprezentálja. 'E' betűvel indítható.\n   - Tétek megrakása után osztás. Kártyaértékek: Számok névértéken, Figurák 10, Ász 1 vagy 11.\n   - Játékos akciók: Hit (Húz), Stand (Megáll), Double Down (Duplázás). (A Split egyelőre kihagyható az MVP-ből).\n   - Osztó logikája: 16-ig kötelező húznia, 17-nél (vagy a felett) meg kell állnia.\n   - Nyeremény: Sima nyerés 1:1, Blackjack (21 két lapból) 3:2. A tétek és nyeremények a közös Pénztárcát módosítják.\n4. Rulett Gép (Európai rulett):\n   - A Casino szobában egy piros gép reprezentálja. 'E' betűvel indítható.\n   - A játékos zsetonokat rakhat le (Tét megadása).\n   - Fogadási típusok: Színek (Piros/Fekete 1:1), Páros/Páratlan (1:1), Harmadok (Dozens 2:1), és konkrét számok (Straight up 35:1). A keréken 0-36-ig vannak számok. A tétek és nyeremények a közös Pénztárcát módosítják.\n5. Architektúra: A Casino játékoknak (Blackjack, Rulett) ugyanúgy a `GameModuleContract` interfészt kell követniük, és rendelkezniük kell \"Vissza a Casino Szobába\" gombbal."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Szobák közti átjárás (Priority: P1)
A játékos az Arcade Hub jobb oldalán lévő Casino ajtóhoz sétál, megnyomja az `E` gombot, majd átlép a Casino Room nézetbe. A Casino szobából a bal oldali ajtóval ugyanígy vissza tud menni a Hubba.

**Why this priority**: A casino tartalom csak akkor érhető el, ha a két szoba közti váltás megbízhatóan működik.

**Independent Test**: A Hub és a Casino Room külön-külön megnyitható és visszalépéssel lezárható, anélkül hogy bármelyik játékmodult el kellene indítani.

**Acceptance Scenarios**:

1. **Given** a játékos a Hub jobb oldali ajtója mellett áll, **When** megnyomja az `E` gombot, **Then** a Casino Room jelenik meg.
2. **Given** a játékos a Casino Room bal oldali ajtója mellett áll, **When** megnyomja az `E` gombot, **Then** visszatér az Arcade Hubba.

---

### User Story 2 - Közös pénztárca és napi bónusz (Priority: P1)
A játékos egy közös egyenleget használ a Casino Room valamennyi játékához. Az egyenleg megmarad a böngészőben, és minden új nap elején automatikusan jóváíródik a napi bónusz.

**Why this priority**: A pénzkezelés a casino fő motivációja; a játékok tétjei csak ezzel együtt értelmezhetők.

**Independent Test**: A böngésző újranyitása után a korábbi egyenleg visszatöltődik, és aznap legfeljebb egyszer kap a játékos napi bónuszt.

**Acceptance Scenarios**:

1. **Given** első induláskor nincs mentett egyenleg, **When** a játék betölt, **Then** a játékos 10.000 Ft kezdőtőkét kap.
2. **Given** a játékos korábban már belépett aznap, **When** újra megnyitja a játékot, **Then** a napi bónusz nem íródik jóvá ismét.
3. **Given** a Casino Room aktív, **When** a játékos nézi a képernyőt, **Then** az aktuális egyenleg folyamatosan látható.

---

### User Story 3 - Blackjack játék (Priority: P2)
A játékos a Casino Room zöld Blackjack asztalához megy, téttel indul, majd a standard blackjack szabályok szerint játszik az osztó ellen.

**Why this priority**: Ez az első teljes casino-játék, amely közvetlenül használja a közös pénztárcát.

**Independent Test**: A blackjack kör lejátszható önmagában, és az eredmény után a pénztárca módosul.

**Acceptance Scenarios**:

1. **Given** a játékos elegendő egyenleggel rendelkezik, **When** tétet helyez el és elindítja a Blackjack gépet, **Then** kiosztás történik és a kör elkezdődik.
2. **Given** a játékos kezében van a kör, **When** Hit, Stand vagy Double Down akciót választ, **Then** a játék a megadott szabályok szerint folytatódik.
3. **Given** az osztó 16 ponton áll vagy alatta van, **When** az osztó köréhez ér a játék, **Then** húz; **When** 17 vagy több pontja van, **Then** megáll.
4. **Given** a játékos két lapból 21-et ér el, **When** a kör lezárul, **Then** a blackjack 3:2 kifizetéssel számolódik.

---

### User Story 4 - Rulett játék (Priority: P3)
A játékos a Casino Room piros Rulett gépéhez megy, fogadást helyez el, majd európai rulett körben játszik.

**Why this priority**: A roulette a második casino-játék, amely bővíti a pénztárca-használatot és a fogadási lehetőségeket.

**Independent Test**: A rulett kör elindítható, a támogatott fogadási típusok kipróbálhatók, és a kifizetés az eredménytől függően módosítja az egyenleget.

**Acceptance Scenarios**:

1. **Given** a játékos elegendő egyenleggel rendelkezik, **When** konkrét számra, színre, páros/páratlanra vagy dozens fogadásra tesz tétet, **Then** a kör elindulhat.
2. **Given** a kerék pörgetése véget ér, **When** az eredmény ismertté válik, **Then** a megfelelő nyerő fogadások kifizetésre kerülnek a megadott arányok szerint.
3. **Given** a kerék 0-ra áll, **When** külső fogadásokat értékelünk, **Then** a 0 nem számít pirosnak, feketének, párosnak vagy páratlannak.

### Edge Cases

- Mi történik, ha a játékos nem rendelkezik elég egyenleggel a tét lefogadásához?
- Mi történik, ha a napi bónusz időpontja ugyanazon a napon többször is ellenőrzésre kerül?
- Mi történik, ha a játékos játék közben elhagyja a Casino Roomot vagy visszalép a Hubba?
- Mi történik, ha a blackjack Double Down után a játékos már nem tehet további akciót?
- Mi történik, ha a rulett fogadás több támogatott típust kever ugyanabban a körben?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow the player to move from the Arcade Hub to the Casino Room through a visible exit on the right side of the Hub and return through a visible exit on the left side of the Casino Room by pressing `E` while in range.
- **FR-002**: The system MUST maintain a shared wallet balance for the Casino Room and persist the balance together with the last bonus claim timestamp in browser `localStorage`.
- **FR-003**: The system MUST grant a 10,000 Ft daily bonus the first time the game is opened on a given calendar day, and MUST initialize first-time players with a 10,000 Ft starting balance.
- **FR-004**: The system MUST display the current wallet balance continuously in the Casino Room UI.
- **FR-005**: The Blackjack machine MUST be enterable with `E` from the Casino Room and MUST allow the player to place a bet before the first deal.
- **FR-006**: The Blackjack game MUST support Hit, Stand, and Double Down actions, with no Split support in the initial release.
- **FR-007**: The Blackjack dealer MUST draw until reaching at least 17 and MUST stand on 17 or higher.
- **FR-008**: The Blackjack game MUST resolve standard wins at 1:1 and Blackjack hands dealt in two cards at 3:2, with payouts and losses applied to the shared wallet.
- **FR-009**: The Rulett machine MUST be enterable with `E` from the Casino Room and MUST allow the player to place a bet before spinning.
- **FR-010**: The Rulett game MUST support red/black, even/odd, dozens, and straight-up number bets on an European wheel with numbers 0 through 36.
- **FR-011**: The Rulett game MUST resolve supported bets with the specified payout ratios and MUST apply results to the shared wallet.
- **FR-012**: The Blackjack and Rulett modules MUST follow the `GameModuleContract` interface and MUST include a visible `Vissza a Casino Szobába` button that returns the player to the Casino Room.

### Key Entities *(include if feature involves data)*

- **CasinoRoomState**: Represents the active room, visible exits, machines, and the current interaction target.
- **WalletState**: Represents the shared cash balance, the last daily bonus timestamp, and the first-seen timestamp for first-time initialization.
- **BlackjackRound**: Represents a single blackjack bet, the two hands, the current action phase, and the final payout.
- **RouletteRound**: Represents a single roulette bet or bet set, the chosen bet type, the spin result, and the final payout.
- **CasinoMachine**: Represents an interactive casino object, its room position, type, and launch prompt.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 95% of test users can move from the Hub to the Casino Room and back again within 5 seconds after reaching the doorway.
- **SC-002**: The wallet balance persists across page refreshes in 100% of tested sessions, and the daily bonus is applied at most once per calendar day.
- **SC-003**: A full blackjack round can be started, played to completion, and settled in under 2 minutes for a first-time player.
- **SC-004**: A full roulette round can be started, bet, spun, and settled in under 90 seconds for a first-time player.
- **SC-005**: At least 90% of test users can identify the current wallet balance and the available return action without assistance.

## Assumptions

- The browser's local calendar day is the source of truth for the daily bonus check.
- Placeholder room graphics are acceptable for the initial version; no external art assets are required.
- Blackjack Split is intentionally out of scope for the first release.
- Roulette uses standard European rules where 0 is green and does not count as red, black, even, or odd.
- The shared wallet is the only monetary state for the Casino Room and is reused by both games.
