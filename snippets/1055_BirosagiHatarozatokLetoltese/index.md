---
layout: default
codename: BirosagiHatarozatokLetoltese
title: Bírósági határozatok letöltése iteratívan fejlesztett MI generálta programmal
tags: snippets mieset
authors: Kövesdán Gábor
---

# Bírósági határozatok letöltése iteratívan fejlesztett MI generálta programmal

Az e-akta felületéről anonimizált bírósági határozatokat szerettem volna PDF-formátumban letölteni későbbi feldolgozáshoz. A feladathoz Claude segítségével készíttettem Python-programot, saját használati beállításom szerint a Sonnet 5 modell medium szintjén. A folyamat több körből állt: az első változat után a tényleges oldalszerkezettel pontosítottam a kódgenerálást, majd a futtatás közben tapasztalt hibák és korlátok alapján újabb követelményeket adtam meg.

A kezdetben egyszerű letöltőnek szánt program így fokozatosan folytatható, a helyi fájlokat ellenőrző és jogterületenként kereső alkalmazássá alakult. Az esettanulmány írásakor a legújabb változat még futott, de már több mint 21 000 dokumentumot letöltött. Ez meghaladta a szűrés nélküli bejárással elért 10 000 fájlt; a teljes gyűjtemény letöltését ekkor még nem lehetett befejezettnek tekinteni.

**Használt eszközök:** Claude, Python, Selenium, Chrome, `requests`, valamint a böngésző fejlesztői eszközei a renderelt DOM kinyeréséhez.

## Tanulságok

- **A valós bemenet többet segíthet, mint a feladat újrafogalmazása.** A böngészőből kimásolt DOM alapján a Claude már konkrét HTML-elemekhez tudta igazítani a programot, és egy felesleges kattintási lépést is elhagyott.
- **Az angol prompt itt is jól használható volt.** A korábbi tapasztalataim alapján angolul fogalmaztam meg a szoftveres követelményeket, a magyar felületi feliratokat pedig pontosan idéztem. Ez a saját munkamódszerem volt, nem összehasonlító nyelvi teszt.
- **A látható böngésző hasznos visszajelzést adott.** A headless, vagyis látható böngészőablak nélküli futás nálam nem működött. Ennek kikapcsolásával használható lett a program, és követni tudtam, hol tart.
- **A folytathatóság önálló követelmény.** Egy hosszú letöltésnél nem elég a hibamentes működésre számítani: meg kell őrizni, hol tartott a munka, és újraindítás után vissza kell állítani a megfelelő keresést is.
- **A folytatás és a hiánypótlás külön feladat.** Az állapotfájl segít visszatérni a megszakítás helyére, de a korábban kimaradt dokumentumok pótlásához a helyi fájlok meglétét is ellenőrizni kellett.
- **A találati lista vége nem feltétlenül az adatbázis vége.** A kerek 100 oldal és a kizárólag kúriai dokumentumok együtt arra utaltak, hogy a keresőből szűrés nélkül elérhető találatok köre korlátozott lehet.
- **Az új követelmények mellett a bevált működést is rögzíteni kell.** A jogterületi bontás kérésénél külön előírtam a folytatás megtartását, a hash nélküli fájlneveket és a látható böngészőt, hogy ezeket ne kelljen újra kézzel javítanom.

## Az eredmény használata

A program a megadott célkönyvtárba mentette a PDF-eket, a fájlneveket pedig a bíróság nevéből és az ügyszámból képezte. Ez számomra jól felismerhető állományokat eredményezett. A működéshez a Claude az alábbi függőségeket és telepített Chrome böngészőt írta elő:

```bash
pip install selenium requests
```

A végsőként bemutatott változat látható böngészővel indult, jogterületenként keresett, az adott kategórián belül lapozott, és a már helyben megtalálható dokumentumokat kihagyta. Az aktuális könyvtárban elhelyezett állapotfájl a megszakadt munka folytatását szolgálta. Újraindításkor ezért ugyanazt az állapotfájlt és letöltési könyvtárat kellett használni.

Az esettanulmány a promptokat tartalmazza, a teljes programot és az átadott HTML-fájlok tartalmát nem. Az esettanulmány ezért a fejlesztési folyamatot dokumentálja; nem önállóan futtatható programcsomag.

## A munkafolyamat tanulságos részletei

### A kezdeti feladatleírás a felületen látható műveleteket követte

A céloldal az [anonimizált határozatok keresője](https://eakta.birosag.hu/anonimizalt-hatarozatok) volt. Az első promptban konkrétan megadtam, hogyan lehet egy dokumentumot a felületről megnyitni:

> Write me a simple Python program that opens https://eakta.birosag.hu/anonimizalt-hatarozatok and downloads each court decision as a PDF in the specified folder. Each entry has a button with an etcButton class that opens a menu, in which there is a "Megnyitás új ablakban" link that retrieves the document as a PDF file. Use this to download the documents. There is pagination on the webpage so you must go over all the pages and download all the documents.

A prompt a Python nyelvet, a kiinduló címet, a célformátumot, a célkönyvtár igényét, egy CSS-osztályt, a menüpont pontos feliratát és a lapozást is rögzítette. A leírás így jóval konkrétabb volt annál, mintha csak az összes dokumentum letöltését kértem volna.

A Claude JavaScript által felépített felületként írta le az oldalt, és Selenium által vezérelt böngészőt javasolt. A válasz szerint a PDF-ek tényleges mentését a `requests` végezte volna a böngésző sütijeinek átvételével. A modell egyúttal jelezte, hogy a renderelt DOM-ot nem látja, ezért a lapozás és egyes elemek kiválasztásának módja feltételezéseken alapul.

### A renderelt DOM átadásával pontosítottam az első változatot

A böngésző fejlesztői eszközeiből kimásoltam a renderelt DOM-ot, vagyis az oldalnak azt az elemszerkezetét, amely a JavaScript futása után ténylegesen létrejött. Ezt adtam át Claude-nak a következő kéréssel:

> Here is the code of the rendered website with the first page selected. Use this code to make the generated code and selectors more accurate.

A selector itt azt a kijelölési szabályt jelenti, amellyel a program megtalál egy elemet az oldalon. A valós DOM alapján a modell már konkrét azonosítókat és osztályokat tudott használni:

| Feladat | A válaszban azonosított HTML-részlet |
| --- | --- |
| A találati táblázat sorainak keresése | `tbody#anonimHatarozatGridContent`, azon belül `tr.add-border-top` |
| Az ügyszám kiolvasása | `td[aria-label="Határozat sorszáma"]` |
| A bíróság kiolvasása | `td[aria-label="Bíróság"]` |
| Továbblapozás | `button.grid-pager-next` |
| Az oldalméret beállítása | `select#page-size` |

A legfontosabb felismerés az volt, hogy a „Megnyitás új ablakban” hivatkozás a rejtett menüben is benne volt a DOM-ban, és már tartalmazta a dokumentum címét. Nem kellett minden sorban megnyitni a menüt: a program közvetlenül kiolvashatta a hivatkozás `href` értékét.

Ez a kör tehát nemcsak pontosabbá, hanem egyszerűbbé is tette a megoldást. Én a felület használatát írtam le, a tényleges elemszerkezet ismeretében viszont a Claude ugyanazt a célt kevesebb felületi művelettel tudta elérni. A kódban 100 találatos oldalméretet is lehetett választani.

### A headless mód kikapcsolása után elindult a letöltés

Az így kapott program nálam nem működött headless módban. Kikapcsoltam ezt a beállítást, így a program látható Chrome-ablakot indított. A Claude már az első teszthez is ezt javasolta, hogy meg lehessen figyelni a linkek kezelését és a lapozást.

A látható böngésző nem zavart, sőt segített követni a folyamatot. A headless hiba pontos okát nem tártam fel; a működő beállítás elegendő volt a feladat folytatásához.

A letöltés később megállt. Lehetséges okként az internetkapcsolat megszakadása merült fel, de ez nem volt bizonyított. A gyakorlati probléma az volt, hogy a program még nem tudta folytatni a félbehagyott munkát.

### Állapotfájlt kértem a folytatáshoz

A következő módosításban azt kértem a Claude-tól, hogy a program az aktuális könyvtárban vezessen egy állapotot tároló fájlt, és újraindításkor abból folytassa a letöltést. Ez a funkció működött, de az új változat egy számomra nem kívánt módosítást is tartalmazott: hash értéket fűzött a fájlnevekhez.

A bíróság neve és az ügyszám számomra megfelelő azonosíthatóságot adott, a további karaktersorozatot feleslegesnek találtam. Ezt először kézzel távolítottam el a kódból. A későbbi promptban már kifejezett követelményként szerepelt, hogy a fájlnevek ne tartalmazzanak hash értéket.

Ez jól mutatta, hogy egy új funkció kérése mellett a meglévő, fontos viselkedéseket is érdemes megnevezni. A folytathatóságra koncentrálva kezdetben nem rögzítettem külön a fájlnévképzés változatlanságát.

### A helyi fájlok ellenőrzésével pótoltam a kimaradásokat

A folytatható változat futtatása után is kevesebb fájlom volt a vártnál. A felületen 100-as oldalmérettel 100 oldal látszott, ezért körülbelül 10 000 dokumentumra számítottam. Az állapotfájlból történő folytatás önmagában nem pótolta az összes hiányt.

Ezért azt kértem, hogy újrapróbáláskor minden elérhető dokumentumnál ellenőrizze a program, megtalálható-e már a megfelelő fájl a helyi könyvtárban. A hiányzókat töltse le, a meglévőket hagyja ki. Ezzel végül elértem a 10 000 letöltött fájlt.

A két megoldás eltérő kérdésre adott választ. Az állapotfájl azt mondta meg, hol tartott a bejárás; a helyi ellenőrzés azt, mely dokumentumok voltak ténylegesen jelen. Az esetben mindkettőre szükség volt. A fájl létezésének ellenőrzése ugyanakkor önmagában még nem bizonyítja a PDF sértetlenségét; ilyen tartalmi ellenőrzést nem végeztem.

### A kerek találatszám új problémára utalt

A 10 000 fájl elsőre sikernek tűnt, de két körülmény gyanút keltett bennem. Pontosan 100 oldal volt elérhető, és minden letöltött dokumentum a Kúriától származott. Tudtam, hogy a rendszerben törvényszéki és ítélőtáblai határozatok is vannak.

Ebből arra következtettem, hogy a szűrés nélküli listában megjelenített találatok köre korlátozott lehet. Ez eltért az előző problémától: már nem pusztán a bejárt oldalakról kimaradt fájlokat kellett pótolni, hanem további dokumentumokat kellett elérhetővé tenni a keresőben.

A Claude a DOM elemzésekor maga is észlelte a „10000+” találati jelzést, de ezt kezdetben egy hosszú letöltés jelének tekintette, és felvetette, hogy ez lehet a teljes adatbázis. A futási eredmény és a dokumentumok összetétele alapján ezt a feltételezést újra kellett gondolnom. A formailag szabályos lapozás még nem igazolta a gyűjtés teljességét.

### Jogterületenkénti keresést kértem a következő iterációban

A következő promptban új külső ciklust kértem: a program válasszon ki egy jogterületet, indítsa el a keresést, majd azon belül végezze el a korábban kialakított lapozást és letöltést. Ehhez ismét renderelt DOM-ot adtam át, ezúttal a megnyitott keresőűrlapról.

A kérés konkrétan megnevezte a „Több szűrő” gombot, a `Jogterulet` azonosítójú legördülő listát és a „Keresés” gombot. Emellett a korábbi tapasztalatokat is követelménnyé alakítottam:

> Do not change any earlier behavior. Also, do not add hashes to filenames, just the court name and case number is enough, it uniquely identifies the documents. Also, set headless to false by default. Take special care on maintaining the resume function working.

A folytatásnál már a keresési környezet visszaállítását is előírtam: megszakítás után először azt a jogterületet válassza ki a program, amelyen korábban dolgozott, és azon belül folytassa a bejárást.

A Claude válasza szerint az új változat a legördülő lista tényleges elemeiből olvasta ki a kategóriákat, az „Összes” lehetőséget kihagyta, és minden jogterületre külön keresést indított. Az állapotfájl a kategóriák listájával, az aktuális kategória indexével és a teljes munka befejezettségének jelzésével bővült. Újraindításkor a program visszaállította a megfelelő jogterületet, majd az azon belül elért oldalra lépett.

A válasz szerint a teljesen befejezett futás utáni új indítás ismét végigellenőrizte a kategóriákat. A hash értékek kikerültek a fájlnevekből, és a `HEADLESS = False` lett az alapbeállítás. A fájlnév szerinti ellenőrzés egyúttal arra is szolgált, hogy a több kategóriában szereplő, azonos névre képzett dokumentumokat ne töltse le ismét.

### Az eredmény és a még nyitott kérdés

Az esettanulmány írásakor a jogterületenként kereső változat már több mint 21 000 dokumentumot letöltött, és még nem fejezte be a munkát. A szűrés nélküli bejárásnál megfigyelt 10 000-es határt így sikerült meghaladni. Ez alátámasztotta, hogy a keresés részekre bontásával több dokumentum vált elérhetővé, de a webalkalmazás pontos korlátozási szabályát és a teljes adatbázis méretét ebből még nem lehetett megállapítani.

További módosítást ekkor még nem kértem. Ha valamelyik jogterület önmagában is elérné a feltételezett találati korlátot, a következő lépés a keresés további felosztása lenne: jogterületen belül például a határozatot hozó bíróságokon is végigiterálnék, és csak ezen belül lapoznék. Ez tervezett továbbfejlesztési irány, nem már megvalósított funkció.

Az esetben az MI a program létrehozását és ismételt átalakítását végezte, én pedig a valós oldalszerkezetet, a futási tapasztalatokat és az eredmények értelmezését adtam hozzá. A fejlesztés lépéseit az határozta meg, hogy a tényleges használat során mi hiányzott még a működésből. A döntő előrelépést több alkalommal egy új megfigyelés pontos követelménnyé alakítása hozta.
