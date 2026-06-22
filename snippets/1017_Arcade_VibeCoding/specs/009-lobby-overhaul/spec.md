# Feature Specification: Lobby & Casino Room Overhaul

**Feature Branch**: `009-lobby-overhaul`
**Created**: 2026-06-02
**Status**: Draft

---

## Összefoglaló

A jelenlegi lobby és kaszinó szoba vizuálisan felfrissül: a téglalapból álló "robot" karaktert egy felülnézetes sétáló ember váltja, a szobák márványpadlós, arany díszítésű kaszinótermekké alakulnak, az egyszerű barna négyzetek helyett részletes játékgépek jelennek meg, a kaszinó bejárata pedig egy átjárható portálkapuvá változik — belé kell sétálni, nem kell E-t nyomni.

---

## User Scenarios & Testing

### User Story 1 — Sétáló ember karakter (Priority: P1)

A játékos egy felülnézetes emberi figurát irányít a szobában. A figura fejjel, testtel rendelkezik, és mozgás közben láthatóan sétál (lábak váltakoznak). Megállásnál természetesen áll, az utoljára tartott irányba nézve.

**Acceptance Scenarios**:

1. **Given** a játék elindul, **When** a lobby betölt, **Then** egy ember-alakú figura látható (ovális fej, vállak, test), nem egy téglatest.
2. **Given** a játékos nyomja az irányvezérlőt, **When** a karakter mozog, **Then** a test enyhén „lépegető" animációt mutat (inga-mozgás, nem teleport-ugrás).
3. **Given** a játékos megáll, **When** 0,3 másodperc eltelt, **Then** a karakter álló pózba kerül, az utoljára mozgott irányba nézve.
4. **Given** a karakter mozog, **When** az irány megváltozik, **Then** a figura azonnali és sima irányváltást végez (nincs grid-snap delay).

---

### User Story 2 — Portálkapu walk-through (Priority: P1)

A kaszinó bejárata egy nyitott, díszes ívkapu. Belé kell sétálni — nem kell E-t nyomni, nincs felirat. Ha a karakter belép a küszöbzónába, automatikusan indul a szobába lépés.

**Acceptance Scenarios**:

1. **Given** a karakter a kaputól 200px-re van, **When** nem lép be, **Then** semmi nem történik, nincs UI prompt.
2. **Given** a karakter befelé sétál a kapun, **When** a testének közepe átlépi a küszöbvonalat, **Then** a kaszinó szoba automatikusan betölt.
3. **Given** a karakter a kapu közelében van, **When** hátrafelé mozog, **Then** nem vált szobát.
4. **Given** a kaszinóban a kijárati portálnál, **When** a karakter átsétál rajta, **Then** visszakerül a lobbyba.

---

### User Story 3 — Igényes szoba dizájn: Lobby (Priority: P1)

A lobby egy elegáns, felülnézetes kaszinó-előcsarnokot ábrázol: márványpadló, díszes falak, csillár fénycsóva, sarokban növények, bejárat közelében vörös bársonyszalag-kerítés.

**Acceptance Scenarios**:

1. **Given** a lobby betölt, **When** a játékos látja a szobát, **Then** a padló sakktábla-mintás (krém/antracit márvány, ~48px csempe).
2. **Given** a falak láthatóak, **When** a játékos a szoba szélére megy, **Then** a falak vastagabbak (24px), sötét alapon arany díszcsíkkal a belső szélükön.
3. **Given** a szoba közepén csillár van, **When** a játékos látja a padlót, **Then** a csillár pozíciója alatt kör alakú, meleg sárga fényfolt látható (alpha gradient).
4. **Given** a sarokokban növények vannak, **When** a játékos közel megy, **Then** a növény ütközési területe van (nem lehet átmenni rajta).
5. **Given** a portálkapu közelében bársonyszalag áll, **When** a játékos megnézi, **Then** 2 arany tartóoszlop + piros vonal látható (dekoratív, nem ütközik).

---

### User Story 4 — Igényes szoba dizájn: Kaszinó szoba (Priority: P2)

A kaszinó szoba belső terme: zöld posztó asztalfelületek, arany sáv a falakon, kristálycsillár, plüss szőnyeg a középső részen.

**Acceptance Scenarios**:

1. **Given** a kaszinó szoba betölt, **When** a játékos körülnéz, **Then** a padló közepén ovális sötétvörös szőnyeg látható arany szegéllyel.
2. **Given** a kaszinóban terminálok vannak, **When** a játékos nézi őket, **Then** minden gép saját asztalon/posztón áll, nem a csupasz padlón.
3. **Given** a kijárati kapu a szobában van, **When** a játékos arrafelé sétál, **Then** az ugyanolyan portálkapu, mint a lobby bejárata.

---

### User Story 5 — Részletes játékgépek (Priority: P2)

Az arcade gépek és kaszinó terminálok nem egyszerű téglalapok, hanem sziluett-szintű rajzok: monitorkeret, kezelőpult, márkafelirat, izzó képernyő.

**Acceptance Scenarios**:

1. **Given** a Snake gép látható, **When** a játékos nézi, **Then** arcade kabinet-formát mutat: szélesebb alap, szűkülő marquee felső rész, képernyő belső ragyogással, joystick-dot a kezelőpulton.
2. **Given** az Amőba gép látható, **When** a játékos nézi, **Then** hasonló kabinet-forma, de eltérő képernyőszínnel és márkafelirattal.
3. **Given** a Rulett/Blackjack terminál látható, **When** a játékos nézi, **Then** álló érintőképernyős terminál: karcsú alap, nagy kijelző, kaszinó-logó.
4. **Given** bármely gép közelében van a játékos, **When** az interakciós távolságba ér, **Then** a felirat-prompt (`[E] Játék neve`) megjelenik a gép felett.

---

### User Story 6 — Folyamatos mozgás (Priority: P1)

A karakter mozgása folyamatos és sima, nem ugrálós grid-lépések. A sebesség állandó, ütközéskor megáll, de nem teleportál vissza.

**Acceptance Scenarios**:

1. **Given** a játékos nyomva tartja az irányvezérlőt, **When** a karakter mozog, **Then** pixelpontos, frame-alapú mozgás (nem 28px-es ugrások).
2. **Given** a karakter egy falnak ütközik, **When** a játékos átlósan mozog, **Then** az ütközési tengelyen megáll, de a másik tengelyen tovább csúszik (wall-slide).
3. **Given** a karakter sebessége 120px/sec, **When** a szoba átlója ~1100px, **Then** kb. 9 másodperc alatt ér át (természetes tempó).

---

## Technikai terv

### Karakter rajzolása (`drawHub.ts`)

A karakter felülnézetes emberi figura, canvas 2D API-val:

```
Részek (mozgásirány: dél, alapeset):
  Árnyék:      ellipse(cx+4, cy+6, 16, 10) — fekete, 30% alpha
  Fej:         ellipse(cx, cy-18, 12, 12) — bőrszín (#e8c49a)
  Haj:         ellipse(cx, cy-22, 10, 7)  — sötétbarna (#3d2314), csak felső félkör
  Test/kabát:  roundRect(cx-11, cy-8, 22, 26, 4) — sötétkék (#1e3a5f)
  Gallér/ing:  rect(cx-4, cy-8, 8, 6) — fehér
  Bal láb:     ellipse(cx-5, cy+20+legSwing, 5, 7) — sötétszürke (#2d2d2d)
  Jobb láb:    ellipse(cx+5, cy+20-legSwing, 5, 7) — sötétszürke
```

`legSwing = sin(animTick * 8) * 5` — mozgáskor; 0 megállásnál.

Irányonként a test és fej eltolódik (N: fej előre; S: fej hátul; W/E: profilszerű torzítás).

### Portálkapu

**Geometria**: 88px széles × 160px magas ívkapu.

```
Rajz rétegek (alulról felfelé):
  1. Küszöbzóna:  rect(x, y+130, 88, 30) — halvány arany glow (alpha 0.15–0.3, pulzáló)
  2. Bal pillér:  rect(x, y+20, 18, 140) — sötétbarna (#4a2c0a) + arany szél
  3. Jobb pillér: rect(x+70, y+20, 18, 140)
  4. Ívkorona:    arc(x+44, y+40, 44, π, 0) — tömör ív, arany szegéllyel
  5. Felirat:     "KASZINÓ" — arany, serif-stílusú betű, az ív belsejébe
  6. Csillogás:   3 kis fehér pont az ív belső szélén (statikus highlight)
```

**Trigger**: ha `playerCenter.x` ∈ [gateX, gateX+88] **és** `playerCenter.y` >= `gateY+130`, átlép.

### Padló

```
Márványcsempe: 48×48px sakktábla
  Világos mező: #e8e0d0 (krémfehér)
  Sötét mező:   #2a2a2a (antracit)
  Csempe él:    0.5px #00000033 vonal

Csillár fényfolt:
  radialGradient(cx, cy, 0, cx, cy, 120)
  belső: rgba(255, 220, 100, 0.18)
  külső: transparent
  Pozíció: szoba közepe
```

### Falak

```
Alaplap:   14 → 24px vastagság, #1a0f00 (nagyon sötét barna)
Arany sáv: 3px vonal a belső szélen, #b8860b
Sarkok:    8×8px négyzetes arany sarokdísz
```

### Arcade gép rajza

```
Méret: 72px széles × 96px magas

Alulról:
  Talplemez:   rect(x+4, y+84, 64, 12) — #1a1a1a, lekerekített
  Kabinet törzs: rect(x+8, y+30, 56, 56) — #2d1a0e (sötétbarna)
  Képernyő:    rect(x+14, y+36, 44, 36) — sötét + belső glow
  Screen glow: radialGradient a képernyő közepéről, játék-specifikus szín
  Kezelőpult:  rect(x+8, y+68, 56, 16) — #1f1007, enyhén dőlt (perspective hint)
  Joystick:    circle(x+22, y+74, 4) + circle(x+22, y+71, 3) — szürke
  Gombok:      3× circle(x+42..58, y+73, 4) — piros/sárga/zöld
  Marquee:     rect(x+8, y+14, 56, 16) — kabinet teteje, játéknév felirattal
  Marquee háló: 4 függőleges vonal a marquee-n (dekoratív rács)
```

### Kaszinó terminál (Rulett, Blackjack)

```
Méret: 56px széles × 80px magas (karcsúbb, modernebb)

Talplemez:   rect(x+8, y+72, 40, 8) — #111, kerek sarok
Szár/állvány: rect(x+24, y+50, 8, 24) — #222
Monitor:     rect(x, y, 56, 52) — lekerekített sarok (r=6), fekete keret
Kijelző:     rect(x+4, y+4, 48, 44) — belső glow, tematikus szín
Logo sáv:    rect(x+4, y+46, 48, 6) — arany csík a kijelző alján
Felirat:     "RULETT" / "BLACKJACK" — kis fehér betű a monitor alján
```

### Mozgás átírása

- Jelenlegi: `position += direction * 28` per `keydown` event
- Új: `velocity = direction * 120` (px/sec), rAF loop-ban `position += velocity * dt`
- Wall-slide: X és Y ütközés külön vizsgálva, csak az ütköző tengely nullázódik
- Karakter animáció: `animTick` akkumulátor nő mozgáskor (`+= dt * speed / 60`), megállásnál visszafut 0-ra (lerp)

### Növény dekoráció

```
Cserép:  rect(cx-8, cy+6, 16, 12) — #8b4513, trapéz forma
Föld:    ellipse(cx, cy+6, 8, 3) — #3d2314
Levelek: 3× ellipse különböző szögön, cx±10, cy-5..cy+5, 10×16px — #2d7a2d
```

---

## Vizuális paletta (összefoglaló)

| Elem              | Szín              |
|-------------------|-------------------|
| Padló – világos   | `#e8e0d0`         |
| Padló – sötét     | `#2a2a2a`         |
| Fal alap          | `#1a0f00`         |
| Arany díszítés    | `#b8860b`         |
| Portál glow       | `#ffd700` (pulse) |
| Karakter – bőr    | `#e8c49a`         |
| Karakter – kabát  | `#1e3a5f`         |
| Gép kabinet       | `#2d1a0e`         |
| Terminál keret    | `#111111`         |
| Csillár fény      | `rgba(255,220,100,0.18)` |

---

## Érintett fájlok

| Fájl | Változás |
|------|----------|
| `src/hub/rendering/drawHub.ts` | Teljes újraírás: padló, falak, gépek, portál, karakter |
| `src/hub/entities/player.ts` | Velocity-alapú mozgás, animTick állapot |
| `src/hub/scene/HubScene.tsx` | rAF loop, walk-through trigger portálhoz |
| `src/casino/scene/CasinoScene.tsx` | Ugyanaz a portál + szoba dizájn |
| `src/hub/systems/collision.ts` | Wall-slide support |
| `src/hub/input/useHubControls.ts` | Velocity-input (held keys) keydown/keyup helyett |
| `src/hub/entities/machine.ts` | Gép méret/pozíció frissítés az új rajzhoz |

---

## Nem változik ebben a spekben

- Interakciós rendszer (E gomb, proximity check) — gépekre megmarad
- Wallet HUD, casino belső játékok (blackjack, rulett, snake, amőba)
- Scene-váltás logikája (csak a trigger módja változik portálnál)
