---
layout: default
codename: LabProjectDebug
title:  Labormérés projektjeinek debuggolása MI segítségével
tags: snippets mieset
authors: Kiss Ágoston
---

# Labormérés projektjeinek debuggolása MI segítségével

## A feladat leírása

Az egyik labortárgyunk keretein belül két, az USB kommunikációt bemutató laborméréshez készült projektet örököltem. Az egyik egy STM32 mikrokontrolleren futó program, a másik a hozzá tartozó, PC-n futó host alkalmazás. Bár mindkettő működőképes volt, akadtak azért bőven bug-ok és hiányosságok bennük. Ezeket szerettem volna kijavítani vagy pótolni.

Az eszköz egy USB-s zenelejátszó: a PC-s alkalmazás WAV fájlokból küldi a hangadatokat, az előadó nevét és a szám címét a mikrokontrollernek. A hardveren egy érintőkijelző mutatja a lejátszás állapotát, a szám adatait és az eltelt időt. A lejátszást a PC-s alkalmazásból billentyűparancsokkal és a hardver kijelzőjéről gombokkal is lehet vezérelni. A hangerőt az érintőkijelzőn egy csúszkával lehet állítani.

A kezdeti állapotban fennálló bug-ok és hiányosságok az alábbiak voltak:

- A zene lejátszása időnként ugrott egy kicsit
- A lejátszás közben volt egy folyamatos pattogó, ciripelő zaj
- A hangerő mindig 0-ról indult, és hiába állítottam feljebb, a következő lejátszáskor újra visszaugrott 0-ra, holott a csúszkán ez nem látszott.
- Az első lejátszás parancsot mindig a PC-n kellett kiadni, az eszköz nem tudta kezdeményezni a lejátszást, csak ha már a PC egyszer elküldte az adatokat.
- A PC-s alkalmazásban a lejátszás/szünet billentyűparancsot mindig kétszer kellett megnyomni, hogy érvényre jusson.
- Ha az érintőkijelzőn nyomtam stop gombot, az megállította a zenét, de a PC-s app olyan állapotba került, hogy nem lehetett mégegyszer elindítani a lejátszást.
- A lejátszás parancsra nem mindig indult el a zene, annak ellenére, hogy a lejátszás állapotjelző és megfelelő zeneszámhoz tartozó szöveges metaadatok helyesen megjelentek a kijelzőn.
- Bár a kijelzőn volt gomb a több zeneszám közötti léptetésre, a funkció nem volt implementálva sem a firmware-ben, sem a PC-s host applikációban.
- Ha az applikációban nyomogattam a billentyűparancsokat, azokat logolta a terminál ablakban, viszont a hardver kijelzőjén történt gombnyomások nem jelentek meg a logban, csak az állapot váltották.

Az USB kommunikáció, főleg beágyazott környezetben, kód szempontjából eléggé összetett. A hang továbbításához az USB adatfogadásnak, a pufferek kezelésének és a hangkimenetet kiszolgáló DMA-nak is együtt kell működnie. Ehhez még hozzájön a PC-s program és a kijelző felől érkező parancsok összehangolása. Mivel nem én hoztam létre ezeket a projekteket, egyedül feltérképezni és kijavítani minden hibát nagyon hosszadalmas lett volna, és nem is biztos, hogy sikerül. Ezért kértem az MI segítségét.

A munkát az OpenAI **Codex** asztali alkalmazásával, **GPT-6 Astra** modellt használva végeztem, amely hozzáfért a helyi projektfájlokhoz. A kód átnézésében és módosításában az MI segített, az aktuális állapotot én kipróbáltam mindig az eszközökön, és a tapasztalatok visszejelzésével haladtunk lépésről lépésre. Szándékosan nem egy prompt-ban akartam leírni az összes hibát, hogy minden javítási lépés után ki tudjam próbálni, és ha esetleg rossz irányba menne a módosítás, időben tudjak korrigálni. Emellett az is lényeges szempont volt, hogy ne gondolja újra az egész projektstruktúrát, csak a meglévő fájlokat, függvényeket, paramétereket módosítsa, hiszen a laborgyakrolaton a mérési feladatok az eredeti projekthez lettek kitalálva. Ezeken nem szerettem volna módosítani.

## Tanulságok

- Egy örökölt, több összefüggő projektből álló rendszer megértésében sokat segíthet az MI. Nem kellett előre tudnom, melyik fájlban van a hiba.
- A visszajelzett tapasztalatok minél részletesebbek, annál kevesebb iterációban, kevesebb visszakérdezéssel tudja megoldani az MI a hibajavítást.
- Volt, hogy egy funkcióról először azt feltételezte, hogy működnie kellene, majd a forráskód alaposabb átnézésekor kiderült, hogy valójában nincs megvalósítva.
- Bár lefordítani le tudja az MI a kódokat, beágyazott környezetben a tesztelés hardveren problémás lehet. Ezt az MI jelen esetben nem tudta megtenni, nekem kellett letölteni és futtatni az eszközön a programot.
- Ha a lokálisan elérhető kódbázisból dolgozik, igyekszik az MI nem felülírni a meglévő fájlokat. (Ehhez alapból írási jogosultság megadására lenne szüksége.) Vagy készít belőlük egy backup másolatot előtte, vagy az új módosításokat teszi külön mappába. (Ez utóbbi a jellemzőbb.) Természetesen, ha utasítjuk és megadjuk az engedélyt, az aktív projektmappában is beilleszti a módosításokat, hogy ne kelljen nekünk kézzel bemásolni.

## A munkafolyamat tanulságos részletei

A prompt-okban nem adtam részletes megvalósítási utasításokat, hiszen abban sem voltam biztos, hogy az adott hibát melyik projektben kell keresni. Csak leírtam, hogyan működik az eszköz, mit tapasztalok, és miben szeretnék segítséget. Ezután mindig kipróbáltam a módosított változatot, és visszajeleztem, mi javult meg, illetve milyen probléma maradt.

### Kezdő prompt

```prompt
Meg van nyitva a cubeIDE-ben egy projekt, egy USB-s zenelejátszó eszköz kódja. Az eszköz egy USB host PC-től kapja meg a hangadatokat és minden egyebet. Az vele a probléma, hogy a zene lejátszásakor vannak benne kis pillanatnyi ugrások, megszakadások, nézd át a projektet, látsz-e megoldást erre a problémára, vagy a PC-n futó host applikációban kell keresni.
```

MI:

```MI
[...]
Igen, a firmware-ben több konkrét problémát is látok, ezért elsőként az eszköz oldalán kezdeném a javítást.
[...]
1. Nincs védelem a hangpuffer kiürülése vagy felülírása ellen.
[...]
A puffer 80 ms hangot tárol, a lejátszás 40 ms előtöltés után indul. Ez átmeneti ingadozás ellen segít, de tartós sebességkülönbség ellen nem. Ha az olvasó utoléri az írót, régi hangadatot játszhat vissza; fordított esetben még le nem játszott minták íródhatnak felül. Ez jól illik a hallott ugrásokhoz.
[...]
2. A hangórajel beállítása különösen gyanús.
[...]
3. A DMA és a processzor gyorsítótára között hiányzik az adatkoherencia kezelése.
[...]
Az átnézett hangútvonalon nincs cache-clean művelet a CPU által beírt hangadatok DMA-s kiolvasása előtt.
Ez azt okozhatja, hogy a DMA nem a legfrissebb mintákat látja. Első javítási lépésként dedikált, nem gyorsítótárazott, DMA által elérhető hangpuffert választanék. Alternatíva a helyesen igazított pufferek és explicit cache-kezelés. Ezt az ST is előírja a CPU–DMA adatmegosztásnál. ST AN4839
[...]
4. A fogadás minden csomagot teljes méretűnek vesz.
[...]
Az AudioDataOut() mindig 192 bájttal lépteti az írási mutatót, nem ellenőrzi a tényleges fogadott hosszt. Az IsoOutIncomplete() pedig üres.
[...]
```

Az MI rögtön a mikrokontroller kódjában kezdte vizsgálni a hangadatok útját. A javítási javaslatok az USB-n érkező adatok pufferelését, a ténylegesen fogadott adatmennyiség kezelését, a DMA által olvasott memória frissítését és a hangkimenet időzítését is érintették. A válaszból is látszik, hogy az MI nem csak a kódbázist nézte át, hanem a hardverhez tartozó dokumentumokat, ajánlásokat is.

Mivel az első prompt-ban csak azt kértem, nézze át, szerinte mi lehet a hiba, ezután külön utasítanom kellett, hogy csinálja meg ezeket a módosításokat a kódban.

### A megakadások megszűntek, a pattogás maradt

Az első változtatások után a zene már nem akadt meg, viszont folyamatos pattogó, ciripelő hangot hallottam. Ez az első lejátszásnál mindig jelen volt, azonban egy stop és új play parancsot követően megszűnt.

Ezen felül, bár nem kértem, a lejátszás indításakor ő automatikus max hangerőt állított be, ami már túl hangosnak bizonyult.

Prompt:

```prompt
Most az első lejátszáskor még hallom a pattogó, ciripelő hangot, viszont ha a host app-ban lestoppolom, majd újra elindítom Play-el, akkor már jó. Viszont az nem tetszik, hogy automatikusan nagyon hangosan indul, inkább a kezdeti hangerő 20% körül legyen.
```

MI:

```MI
[...]
Beírtam a javításokat a projekt hat fájljába.
- Megszüntettem az első indításkor történő órajel- és DMA-beállítás felülírását, ami magyarázhatja a ciripelést.
- A kezdő hangerő és a képernyő csúszkája 20%.
- Stop–Play után megmarad az általad később beállított hangerő.
A módosított források fordítói ellenőrzése sikerült; teljes build és hardveres teszt még szükséges. Fordítsd újra, töltsd fel, majd teljes kikapcsolás–bekapcsolás után az első lejátszást próbáld ki.
[...]
```

Az, hogy az első indítás és a Stop utáni újraindítás eltérően viselkedett, az inicializálás felé terelte a vizsgálatot. A kódban az MI ütközést talált a panelhez tartozó hangkezelő kód és a CubeMX által generált periféria-inicializálás között. Az első indításkor olyan beállítások is felülíródhattak, amelyek a következő indításkor már nem változtak meg ugyanígy.

A javítás után a lejátszás minősége megfelelő lett.

### A PC-s vezérlés hibái

Miután a hang lejátszása javult, megkértem az MI-t, hogy a host alkalmazást is nézze át.

Prompt:

```prompt
Így már jó a lejátszás. Ebben a mappában van a PC host app kódja is, az usblab_full mappában, megnéznéd, abban is találsz-e valami hibát? Amit eddig tapasztaltam: Nem mindig indul el megnyitás után a p betű lenyomásakor a zene. a p betűt kétszer kell megnyomni a pause és play funkciókhoz is. Ha a mikrokontroller kijelzőjén nyomok stoppot, utána nem lehet újraindítani a zenét
```

MI:

```MI
[...]
Igen, a host kódban több konkrét hibát találtam. A kétszeri p és a kijelzőről történő vezérlés problémája közvetlenül magyarázható ezekkel.
[...]
1. A host olyan Pause parancsot küld, amelyet a firmware nem ismer.
A PlaybackController::playPause() lejátszás közben AudioState::Pause, azaz 7 értéket küld. A firmware-ben viszont a 2-es parancs vált Play és Pause között, a 7-est figyelmen kívül hagyja. A host mégis sikeres állapotváltásnak tekinti a küldést. Így a PC és az eszköz eltérő állapotba kerül, a következő p pedig már rossz kiinduló állapot alapján működik. Ez megmagyarázza a kétszeri gombnyomást.
[...]
2. A kijelzőről érkező Play/Pause parancsot kész állapotként kezeli.
[...]
Stop utáni, kijelzőről indított Play esetén pedig kimarad a fájl újranyitása és a kezdő pufferek feltöltése: csak a régi átvitel folytatását próbálja meg.
[...]
3. Stop után túl korán újrahasználhatja az USB-átviteleket.
[...]
4. Több parancsküldés ugyanazt a változó puffert használja.
[...]
5. A szám végét is túl korán állíthatja le.
[...]
Beírtam a javításokat az AI_debug/usblab_full projektbe.
- A Play/Pause a firmware által támogatott parancsot használja.
- A kijelző Stop–Play művelete újranyitja a fájlt, visszaküldött dupla parancs nélkül.
- A gyors gombnyomások sorba kerülnek; újraindítás előtt lezárulnak a régi USB-átvitelek.
- A szám vége előtt megvárja a hangpufferek kiürülését.
Tíz regressziós tesztet is hozzáadtam. Fordítani és futtatni itt nem tudtam a hiányzó fejlécek és PC-s fordító miatt; a letöltést tanúsítványhiba akadályozta.
Újrafordítás után próbáld ki az egyszeri p-t, majd a kijelzőn Stop → Play műveletet.
[...]
```

Itt már a két program együttműködését kellett vizsgálni. A host külön Pause parancsot kezelt, miközben a firmware ugyanazt a Play parancsot használta a lejátszás és a szünet kezelésére is. A kijelző felől érkező parancsokat is össze kellett hangolni a PC által nyilvántartott állapottal.

A lejátszást vezérlő parancsok ezután már jól működtek.

### A zene néha nem indul el

A vezérlés javítása után még maradt egy nehezebben reprodukálható hiba. A Play parancsra időnként nem indult el a zenelejátszás (sem az időszámláló), habár a dal szöveges metaadataimegjelentek, és a kijelző lejátszást jelzett.

Prompt:

```prompt
Most is előfordul többször, hogy nem indul el a zene, csak a szövegek átmennek, az állapot változik, de se a lejátszási idő számláló, se a zene nem indul el. Ez az első play parancsnál is, vagy többedik stop-play kombinációnál is előfordul. Van amikor pedig gond nélkül működik
```

A további vizsgálat során az MI megtalálta, hogy az USB core egyik függvénye nem továbbította a hiányos izokron OUT átvitel eseményét az osztálykezelőnek. Az izokron átvitel szolgált a folyamatos hangadatok továbbítására. A helyreállítást végző kód már megvolt az osztálykezelőben, de az esemény nem jutott el hozzá, így bizonyos esetekben a hangot fogadó végpont nem lett újra fogadásra kész állapotba helyezve.

MI:

```MI
[...]
Találtam és javítottam egy konkrét hibát a firmware-ben.
Kimaradt USB-hangátvitelnél a HAL letilthatja a hangfogadó végpontot. Az USB core eddig nem továbbította ezt az eseményt a már meglévő újraélesítő függvénynek, így a hangfogadás leállhatott, miközben a szöveg és a vezérlés tovább működött.
A javítás az USB_myclass/Core/Src/usbd_core.c fájlba került. Hét célzott ellenőrzés és az ARM-fordítói ellenőrzés sikerült.
[...]
```

Ezután a hardveren végzett próbák során megszűntek ezek a lejátszási hibák. Ezt vissza is jeleztem az MI-nek
em ellenőrzött funkció is hiányzott.

### A számok közötti váltás hiányzott

A host forrásában három zeneszám is szerepelt. Amikor a hozzájuk tartozó WAV fájlokat az alkalmazás mellé tettem, azt vártam, hogy váltani is lehet közöttük, mégis csak az első szám indult el.

Az MI először azt magyarázta el, hogy a program nem gyűjti össze automatikusan a mappában lévő összes WAV fájlt. Ezen nem akartam változtatni, nem egy általános zenelejátszó eszköz a cél, elég, ha az előre megadott zenéket problémamentesen le tudja játszni.
De a megadott zeneszámokkal sem működött. Itt derült ki, hogy eddig a számváltást ő tévesen működő funkciónak tekintette, nem vette észre, hogy nincs implementálva. Igaz, korábban én sem említettem.

Prompt:

```prompt
csak a billyjean játszódik le, nem lehet váltani
```
MI:

```MI
[...]
Megtaláltam az okot: a számváltás nem volt megvalósítva sem a hostban, sem a kijelző nyílgombjainál. Ezt korábban tévesen működő funkciónak feltételeztem.

Elkészítettem a javítócsomagot:
- PC: n = következő, b = előző szám.
- Kijelző: előző/következő nyilak bekötve.
- A három szám között körbe lehet lépkedni; váltáskor elindul a kiválasztott szám.
[...]
```

Ezután már működött a számváltás: a PC-n az `n` és `b` billentyűkkel, a hardveren a nyílgombokkal lehetett lépkedni a három szám között.

### Megjelenítési finomítások

Utolsó lépésként azt kértem, hogy az új léptetési funkciók visszajelzése és a kijelzőn való gombnyomások is jelenjenek meg a PC-s alkalmazás logjában, ezáltal jobban követhetőbbé téve a használat közbeni állapotváltásokat.

Prompt:

```prompt
Szeretném még, ha a PC alkalmazás ugyanúgy kiírná az 'n' és 'b' billentyűparancsoknál, hogy "next track" és "previous track". Ezen kívül a hardver kijelzőjén történő gombnyomások is ugyanúgy jelenjenek meg a PC app termináljában
```

### Kipróbálás és eredmény

A végső ellenőrzést is a tényleges hardveren végeztem: meghallgattam a zenéket, többször próbáltam a Play, Pause és Stop műveleteket, valamint a számváltást a PC-ről és a kijelzőről is. A kipróbált változatban a korábban tapasztalt megakadások és indítási hibák megszűntek, és a három tesztszám között is működött a léptetés.
