---
layout: default
codename: DroneControl
title: DroneControl MI Esettanulmány
tags: snippets mieset
authors: Gergő Mahunka
---

# DroneControl MI esettanulmány

A DroneControl a saját, MAUI alapú diagnosztikai kliensünk, amely az Alkalmazásfejlesztés c. tárgy projektfeladataként készült el. A projektben az MI-t nem csak kódrészletek előállítására használtuk, hanem arra is, hogy a funkciók közti kapcsolatok tisztábban kirajzolódjanak, a felületi megoldások gyorsabban kiforrjanak, és a problémás részeknél legyen egy második, gyorsan reagáló tervezőpartnerem. A munka során főképp a GitHub Copilotot használtam, így egyszerre tudtam technikai és szerkesztési visszajelzést kérni.

## Tanulságok

A legfontosabb tanulságok nálam ezek voltak:

- Minél pontosabban leírtam, hogy a vezérlőképernyőn mit kell látni, annál kevesebb körből lett használható eredmény. A túl általános kérés gyorsan látványos, de bizonytalan megoldáshoz vezetett.
- A kliens több nézete miatt érdemes volt a változtatásokat kicsi, ellenőrizhető lépésekre bontani. Ha egyszerre kértem UI-t, állapotlogikát és vezérlési viselkedést, az MI könnyebben keverte össze a felelősségeket.
- A technikai kontextus sokat számított: ha megírtam, hogy MAUI-ról, MVVM-ről és külön page-ekről van szó, jobb szerkezetű javaslatot kaptam, mint akkor, amikor csak azt mondtam, hogy "javítsa a felületet".
- A vizuális és működésbeli elvárásokat külön kellett kezelnem. Egy nézet lehetett esztétikus, mégis rosszul illeszkedhetett a meglévő navigációhoz vagy adatkötéshez.
- A verziókövetés ebben a projektben is sokat segített. Amikor egy módosítás félrement, gyorsabban tudtam visszatalálni a jó állapothoz, mint ha csak a beszélgetés emlékeire támaszkodtam volna.

## Az eredmény használata

Ez az esettanulmány nem futtatható segédprogram, hanem egy dokumentált fejlesztési történet. Használni úgy érdemes, hogy a tanulságokból kiindulva saját promptolási mintát alakítasz ki: előbb megadod a kontextust, utána a konkrét kérést, végül a kötöttségeket. Ha a saját projekthez hasonló MAUI alkalmazást fejlesztesz, ez a minta segít abban, hogy az MI ne csak "valamit" generáljon, hanem a meglévő architektúrához illeszkedő javaslatot adjon.
## Munkafolyamat felépítése
Legelső ötletem az volt, hogy a megadott `README.md` fájl alapján egy custom agentet kellene készíteni, aki a projekt struktúrájának kialakításában tud segíteni. A megadott pontok közül kiválasztottuk azokat, amelyek úgy gondoltunk, hogy meg szeretnénk csinálni, majd ezeket angolul egy markdown file-ban összefoglaltuk. Itt volt az első olyan pillanat a projektnél, amikor rájöttünk mekkora különbség is van egy natív és egyénileg testreszabott agent között.

A továbbiakban kevés egyedi agent került használatra, viszont szinte minden feladathoz egy ideiglenes markdown fájl hoztunk létre. Ennek a folyamata az volt, hogy vázlatosan összefoglaltuk mit is szeretnék elérni, generáltattunk jellemzően Geminivel egy `adottTerv.md` leírást, amit referenciaként megadtunk a Copilotnak. A munkát mindig plan módban kezdtük, így tudtuk pontosítani a tisztázatlan részeket. Készült egy projektet összefoglaló fájl is, ami segítette az agenteket a fájlrendszerben való lehető leggyorsabb és legeffektívebb tájékozódásban. 

A projekt 2026 tavaszán készült, amikor a Copilot még nem vezette be a token alapú számlázást, viszont a session és weekly/monthly limitek jelen voltak. A hallgatóknak elérhető ingyenes Copilot Pro előfizetést még a befagyasztás előtt aktiváltam, ezért elérhető volt valamennyi premium modell is. Itt már a legfrissebb Claude modellek csak az eggyel drágább előfizetésben voltak elérhetőek. Jellemzően Auto módban hagytuk a választást, így a kontextus alaőján választotta ki a megfelelő modellt. Ennek a működését nem éreztem determinisztikusank, sokszor olyan érzésem volt, mintha egy random generátoron múlna mit kapok. Az a probléma is felmerült, ha egy chat elején volt egy bonyolultabb kérdés, amire egy nagyobb szorzójú modell adott választ, akkor az után lévő kérdésekre konktextustól függetlenül is ugyanez válaszolt, ha ezt specififkusan nem írtam felül.

A fejlesztés korai szakaszaiban az engedélyeket, amik egy adott sessionre vonatkoznak legtöbbször "Default"-on hagytam, majd az első alkalommal megadtam, hogy minden utasítást engedélyezek. Úgy éreztem, hogy az MI által kiadott utasítások ebben a kódbázisban nem tudnak olyan kockázatot jelenteni, ami miatt nagyobb kontroll alá kéne helyezni a munkáját. Később az alapbeállítás a "Bypass Approvals" lett, hogy ez a probléma megszűnjön. 

Talán az egyik legfontosabb szabály MI-vel történő fejlesztés során, hogy a verziókövetést komolyan kell venni. Egy chat ablakon belül egy kérésre, ha módosít x fájl az AI és utána még 4-5 kérést intézünk felé, viszont egyszer sem fogadjuk vagy utasítjuk el a változtatásait, akkor ezek összeolvadnak. A probléma, hogy itt, amint elromlik valami és vissza akarunk menni, akkor a "Restore Checkpoint" opcióval tudunk ugrálni, viszont nem kapunk róla pontos képet, hogy mikor mit változtatott meg. 


## A munkafolyamat tanulságos részletei

Itt azokat a promptokat és válaszokat gyűjtöttem össze, amelyek a legjobban megmutatták, hogyan változott a kommunikációm az MI-vel a projekt során. A cél nem a beszélgetések teljes visszaadása, hanem annak bemutatása, hogy melyik típusú kérés milyen minőségű választ hozott.

### Projektirány kiválasztása

```
What would be a good structure for a MAUI-based diagnostic client that controls a drone simulator and shows telemetry clearly?
```

MI:
```
...
I would split it into a control page, a planning page, a configuration page, and a telemetry page.
Keep the domain logic separate from the UI, and let the view models own state transitions.
...
```

Ez a válasz azért volt hasznos, mert nem egyetlen képernyőben gondolkodott, hanem rögtön a rendszer egészét próbálta felrajzolni. A későbbi megoldásban ez jól visszaköszönt: a navigáció és az állapotkezelés külön nézetekre tagolódott.

### Specifikáció pontosítása

Először csak annyit kértem, hogy segítsen átgondolni a projektet egy meglévő specifikáció alapján.

```
Could you review the specification and ask clarification questions before implementation?
```

MI: több témára bontott kérdéseket tett fel, például a működési határokra, a képernyők szerepére és arra, hogy milyen adatfolyamot kell támogatni.

Ez azért volt hasznos, mert kiderült, hogy az első elképzelésem még túl tömör volt. A pontosító kérdések után világosabb lett, hogy melyik funkció milyen view modelhez tartozzon, és hol érdemes a logikát elválasztani a megjelenítéstől.

```
The specification is clearer now. Please start the implementation of the requested screens and interactions.
```

Ebben a fázisban az MI már nem új ötleteket dobott be, hanem inkább a részletek kidolgozására koncentrált. A hasznos része az volt, hogy a kérésből szét tudta választani a vezérlőképernyőt, az útvonaltervezést és a telemetriai visszajelzést.

### Vezérlőfelület és állapotjelzés

```
The control screen should make it obvious where the drone currently is, what the target point means, and when the battery state becomes critical.
```

MI:
```
...
Use a dedicated visual grid, show the drone position separately from the target point, and keep status feedback close to the main controls.
...
```

Ez a javaslat segített abban, hogy a főképernyő ne csak egy általános dashboard legyen. A vizuális rács, az animált pozíció és a státuszjelzés együtt sokkal könnyebben értelmezhető felületet adott, mint egy túlzsúfolt vezérlőpanel.

### Hibás kör visszajelzése

```
The telemetry view feels too static, especially when values update frequently. Can you make the live data easier to scan?
```

MI:
```
...
Consider grouping changing values, highlighting the active row, and using clearer separation between live readings and historical data.
...
```

Itt az volt a lényeg, hogy az MI nem csak a kinézetet próbálta szebbé tenni, hanem a leolvashatóságot is. Ez fontos különbség volt, mert egy diagnosztikai kliensnél nem az a cél, hogy látványos legyen, hanem hogy gyorsan értelmezhető maradjon.

### Navigáció és külön nézetek

```
Could you suggest a simple navigation structure for control, path planning, configuration, and telemetry?
```

MI:
```
...
Use a shell-based layout with one page per responsibility.
Keep configuration separate from live control so the user can change settings without losing context.
...
```

Ez a válasz jól illeszkedett a végső architektúrához. A külön oldalak nem csak technikailag tisztábbak lettek, hanem a használhatóságot is javították, mert egy adott feladat mindig ugyanazon a nézeten maradt.

### Összegzés a promptolási mintáról

```
Could you summarize the best way to ask for changes in this project so the answers stay precise?
```

MI:
```
...
Use: context + request + constraints.
State what part of the app is affected, describe the exact change, and name the things that must not change.
...
```

Ez a legjobban használható tanács volt az egész folyamatból. A saját projektben tényleg akkor lett a legjobb a válasz, amikor előre megadtam, hogy melyik oldalról van szó, mit akarok rajta látni, és mihez nem szabad hozzányúlni.

### Statikus kódanalizátor által jelzett hibák javítása

Az ilyen hibák nagy részénél a Visual Studio-ban volt lehetőség "Quick fix" lehetőségre, amivel az adott warning típust fájl vagy akár solution szinten is javította. Azonban, amikor kiadtam az utasítást a Copilotnak:

```
Resolve all IDE0055 warnings in files xyz...
```

Itt nem a "Quick fix" általi megoldást alkalmazta, hanem új ötletet talált ki. A probléma ezzel több esetben is az volt, hogy a javítási nem voltak minden esetben effektívek, valamint több új warning és hiba is jelentkezett utána. Mivel minden parancs futtatására kapott engedélyt az agent, így az új hibákat is javította. Az eredmény általában az lett, hogy minden hibát megoldott, amire kértem de rengeteg olyan sor is bekerült a kódbázisba, ami a "Quick fix" használatával elkerülhető. Rengeteg tokenbe is kerültek ezek a folyamatok, így pár próbálkozás után minden így készült kódrészletet töröltem és manuálisan kattingattam végig a warningokat. Utólag eszembe jutott, hogy lehettem volna pontosabb is a promptokkal, utasíthattam volna, hogy a Visual Studio által felkínált megoldásokat alkalmazza. 

## Rövid zárás

A DroneControl esettanulmány számomra főleg azt bizonyította, hogy az MI akkor működik igazán jól, ha nem helyettesíti a fejlesztői gondolkodást, hanem gyorsítja azt. A jó prompt nem attól jó, hogy hosszú, hanem attól, hogy világos a kontextus, egyértelmű a cél, és látszik benne a kötöttség is. Ebben a projektben ez a megközelítés sokkal stabilabb eredményt adott, mint az első, túl általános kérések.
