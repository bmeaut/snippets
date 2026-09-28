---
layout: default
codename: TanulasTamogatas
title: Önálló tanulás támogatása
tags: snippets mieset
authors: Técsi Zsuzsanna Vilma
---

# Önálló tanulás támogatása

A tanuláskutatás eredményei szerint a leghatékonyabb technikák közé tartozik az aktív felidézés ([*active recall*](https://en.wikipedia.org/wiki/Testing_effect)) és az elosztott ismétlés ([*spaced repetition*](https://en.wikipedia.org/wiki/Spaced_repetition)) [[1]].

Aktív felidézésnél a tanuló nem újraolvassa az anyagot, hanem emlékezetből hívja elő, például kérdésekre válaszol, fejből leírja vagy elmagyarázza a tananyagot. Már a felidézéssel járó erőfeszítés is erősíti az emléknyomot, közben pedig kiderül, mi az, ami még nem megy. Az elosztott ismétlés inkább ütemezési stratégia. Az anyagot egyre hosszabb időközönként vesszük elő újra, jellemzően akkor, amikor már kezdenénk elfelejteni. Így kevesebb összes tanulási idővel tartósabb tudás alakul ki, mint egyetlen hosszú, tömbösített tanulással. A két módszer jól kiegészíti egymást. Az elosztott ismétlés azt határozza meg, mikor vegyük elő az anyagot, az aktív felidézés pedig azt, hogyan.

A gyakorlatban mégis gyakran már az is nagy feladatnak tűnik, hogy beosszuk az anyagot és nekikezdjünk. Ha a tananyag átláthatatlan, könnyen jön a kudarcélmény, és vele együtt a visszatérés a passzív újraolvasáshoz.

Ezen tud sokat segíteni az MI (mesterséges intelligencia). Felkészülési stratégiát és ütemtervet állít össze, a tanulás során pedig kérdezőként és ellenőrzőként működik. Így az aktív felidézés akkor is kivitelezhető, ha nincs mellettünk senki, aki kikérdezne.

Az esettanulmány első fele módszereket és minta promptokat gyűjt össze, amelyek más tárgyakhoz és helyzetekhez is átvehetők. A második fele egy vizsgafelkészülés és a diplomamunkám példáján mutatja be a saját tapasztalataimat, amelyekből a módszerek többsége kialakult.

## Tanulságok, tippek

A legfőbb tapasztalatom az, hogy az MI akkor segít a tanulásban, ha én dolgozom, ő pedig kérdez, ellenőriz és rendszerez. Ha helyettem gondolkodik, a haladás gyorsnak tűnik, de kevés marad meg belőle.

- Nagyobb témához használjunk projektet, és írjunk hozzá projekt-utasítást. Az egyszer megadott tananyag, cél és munkastílus minden beszélgetésben érvényes, így nem kell újra és újra elmagyarázni a helyzetünket.
- Mondjuk ki, hogy kérdezzen, ne magyarázzon. Alapértelmezésben az MI magyaráz, és menet közben is hajlamos visszacsúszni a felsorolásba. Ilyenkor azonnal szólni kell.
- Ne hagyjuk, hogy helyettünk priorizáljon. Kérjük, hogy mondja ki, ha valamit kihagy vagy csak röviden érint.
- Témánként mondjuk meg, mit tudunk és mit nem. A „van alapom” túl általános, és az MI rosszul fogja belőni a szintünket.
- Kérjünk szigorú javítást. A visszajelzés alapból biztató, vizsgán viszont a „majdnem jó” pontvesztés.
- Előbb mi dolgozzunk (jegyzet, válasz, kód), és csak utána kérjünk visszajelzést. Elakadásnál 15–20 perc önálló próbálkozás után kérjünk irányt, ne kész megoldást.
- Az MI ugyanolyan magabiztosan téved, mint amikor igaza van. Ellentmondásnál mindig a hivatalos anyag dönt.
- Az egyes hibák javítása helyett keressük a visszatérő hibamintát, mert az a még nem látott kérdéseknél is hibát okoz.
- Olvasás vagy kódolás közben érdemes összegyűjteni a kérdéseket, és egyben feltenni őket, így nem szakad meg a munka minden apróságnál.
- Gyanús válasznál kérdezzünk rá a forrásra („Honnan tudod ezt? Adj forrást.”), túl általános válasznál pedig mondjuk meg, miért nem illik a helyzetünkre.
- Egy magyarázat után kérjük, hogy kérdezzen ki belőle egyesével, nehezedő kérdésekkel. A hét végén pedig érdemes vele együtt átgondolni, mi működött és mi nem.

## Módszerek és minta promptok

Az alábbi promptok sablonok, amelyek javarészt a saját beszélgetéseim alapján készültek.

### Az alap: projekt és projekt-utasítás (benne a saját szokások)

Az MI-alapú tanulást leginkább az segíti, ha a projekt funkciót használjuk. Ide feltölthetjük a kapcsolódó forrásanyagokat (előadásdiák, jegyzetek, régi feladatok, forráskód stb.), és egy projekt-utasításban egyszer leírhatjuk, mit szeretnénk. Enélkül minden új beszélgetés elején el kell magyarázni a vizsgát, a szintünket és a kéréseinket, és ez sok felesleges kört jelent.

Érdemes az utasításba a saját tanulási szokásainkat is beleírni. Nálam ilyen volt, hogy hosszú, megszakítás nélküli blokkokban szeretek dolgozni, passzív olvasásnál nehezen tartom a figyelmemet, és gyakran közbekérdezek. Ha ezeket az MI előre tudja, a tempót és a feladatok formáját is ehhez igazítja.

```
Szerepköröd: vizsgafelkészítő mentor vagy. A vizsgám [dátum]-án lesz, [formátum].
Az anyag [A része] ismert, de megkopott, [B része] teljesen új.
Célom a megértés, nem a magolás: a váratlan kérdéseket is meg akarom oldani.

Rólam:
- Hosszú, megszakítás nélküli blokkokban dolgozom.
- Passzív olvasásnál nehezen tartom a figyelmem, ezért kérdező módot kérek.
- Gyakran közbekérdezek. Ilyenkor válaszolj röviden, majd folytasd ott, ahol abbahagytuk.
- Kézzel, tömör kulcsszavas jegyzetet írok.

Módszer:
1. Ismert anyagnál kérdezz, ne magyarázz. Csak ott segíts, ahol elakadok.
2. Új anyagnál előbb a nagy kép és egy hétköznapi analógia, utána lépésenkénti levezetés, és csak ezután a szakkifejezések.
3. Kifejtős válaszomat szigorúan javítsd, emeld ki a kötelező kulcsszavakat. Ne puhíts.
4. Ne hagyj ki semmit, ami az előadásanyagban szerepel. Ha szerinted valami kevésbé fontos,
   mondd ki, és érintsük röviden.
5. Kizárólag a feltöltött dokumentumokból dolgozz, és hivatkozz a fájlnévre. Ha valami nincs benne, jelezd.

A válaszaidban ismételd meg a kérdést, amire felelsz.
Minden témablokk végén kérek tömör jegyzetjavaslatot és hibalistát.
```

Az utasítás nem kész a legelején. Ha menet közben valamit többször kell korrigálni, azt érdemes beleírni. Nálam a 4. pont is így került bele.

Bizonyos esetekben frusztráló tud lenni, hogy az MI sokszor hosszú, szétfolyó válaszokat ad, ami megnehezíti a lényeg kiragadását. Ilyen esetekben jól használható a projekt-utasítás kiegészítésére az [i-have-adhd](https://github.com/ayghri/i-have-adhd) nevű nyílt forrású repó, melynek segítségével a válaszok rövidebbek és fókuszáltabbak lesznek. Eredetileg kódolóasszisztensekhez készült plugin, de nem szükséges telepíteni, a szabályai egyszerűen bemásolhatók az utasításba a [SKILL.md](https://github.com/ayghri/i-have-adhd/blob/main/skills/i-have-adhd/SKILL.md) fájlból.

### Tervezés és beosztás

Ez a lépés oldja meg a bevezetőben említett elindulási problémát, és ide tartozik az elosztott ismétlés is. A jó terv nemcsak a sorrendet adja meg, hanem azt is, mikor térjünk vissza egy témára.

#### Felkészülési terv

A felkészülés elején érdemes egy napi bontású tervet kérni, amelyet aztán minden nap végén a tényleges haladáshoz igazítunk.

```
[N] napom van a(z) [tárgy] vizsgáig. A vizsga formátuma: [feladattípusok, pontozás].
Ezt ismerem: [témák].
Ezt nem ismerem: [témák].
Készíts napi bontású tervet az új anyaggal kezdve, és tervezz be ismétlő köröket a korábban átvett témákra. A témalistán jelöld, melyik témát kell mechanizmus szintjén érteni, és melyiknél elég egy-két mondat.
```

A becsült tempó általában túl optimista, ezért a napi zárás része legyen a „Frissítsd a tervet a mai haladás alapján.” kérés.

Amennyiben nincs vizsga, csak egy új témát kezdünk, a terv helyett egy tanulási térkép is elég.

```
Most kezdem tanulni a(z) [téma] témát. 
Ezt már tudom: [előismeretek]. 
A célom: [cél, határidő].
Adj egy tanulási térképet: a 8–10 legfontosabb fogalmat, a javasolt sorrendet, és hogy melyikhez mi az előfeltétel. Még ne magyarázz el semmit részletesen.
```

#### Tanulási útvonal önálló projekthez

Szakdolgozatnál, önálló laboratóriumnál, ahol nincs kész tananyag, a saját projektre szabott útvonal többet ér egy általános tananyagnál.

```
A projektem: [leírás, eszközök, jelenlegi állapot]. 
Nem kész megoldást kérek, hanem tanulási útvonalat.
Bontsd több fázisra, és mindegyiknél írd le, milyen fogalmat kell hozzá megértenem, és miből látom, hogy kész vagyok vele.
```

#### Olvasási terv szakcikkekhez

Keshav háromlépéses olvasási módszere [[2]] szerint nem kell minden cikket elejétől végéig ugyanolyan mélységben elolvasni. Először 5–10 perc átfutás jön (cím, absztrakt, ábrák, konklúzió), utána alapos olvasás, mély olvasás pedig csak a kulcscikkeknél, fejezeteknél. Ha sok cikket kell feldolgozni, az MI abban segít, hogy milyen sorrendben olvassuk őket, és melyik mennyi figyelmet érdemel.

```
A témám: [1-2 mondat]. A projektbe feltöltöttem a cikkeket, amelyeket fel kell dolgoznom.
1. Javasolj olvasási sorrendet úgy, hogy az alapozó cikkek kerüljenek előre, és mindegyiknél írd le egy mondatban, mire épít az előzőekből.
2. Jelöld mindegyiknél, mennyire kapcsolódik a témámhoz: SZOROSAN / RÉSZBEN / HÁTTÉRKÉNT.
3. A szorosan kapcsolódó cikkeknél jelöld fejezetenként: MÉLYEN / FIGYELMESEN / ÁTFUTNI.
Ne foglald össze a cikkeket, azt én akarom megtenni.
```

#### Gyakorlási terv egy készség fejlesztéséhez

Hobbinál vagy egy régen abbahagyott tudás újrakezdésénél nincs tananyag és vizsgadátum, ezért először azt érdemes felmérni, hol tartunk, és a meglévő forrásokból a saját helyzetünkhöz illő tervet összerakni.

```
Régen tanultam a(z) [téma] témát, de sokat felejtettem. Tegyél fel 5 diagnosztikus kérdést, és a válaszaim alapján mondd meg, honnan érdemes újrakezdenem.
```

```
A jelenlegi szintem: [leírás]. A célom: [cél]. Heti [N] alkalommal, [idő] gyakorlásra van időm.
Ezekből a forrásokból állíts össze gyakorlási tervet: [linkek]. Jelöld, mi melyik forrásból származik, és ha a források ellentmondanak, azt is.
```

Ha a javasolt gyakorlat nálunk nem kivitelezhető (hely, eszköz, idő miatt), mondjuk ki és kérjünk saját helyzetünkhöz illő alternatívát.

### Aktív felidézés

Ebbe a lépésbe nemcsak a kikérdezés tartozik. Amikor saját szavainkkal leírjuk, amit egy cikkről vagy egy kódbázisról megértettünk, és ezt ellenőriztetjük, szintén emlékezetből hívjuk elő a tudást, és azonnal visszajelzést kapunk.

#### Kikérdezés forráshoz kötve

A már tanult anyag felfrissítésére és az új anyag másnapi ellenőrzésére a kikérdezés a leghatékonyabb. Fontos, hogy a gyakorlás formátuma a számonkérését kövesse, ezen felül a kötelező indoklás kiszűri a szerencsés tippeket és rávilágít a valós tudás mélységére.

```
Kérdezz ki a(z) [téma] témából, kizárólag a feltöltött [fájlnév] alapján.
[Kérdésformátum, pl. igaz/hamis] kérdések legyenek, és minden válaszomhoz kérj indoklást.
Egyszerre 5 kérdés legyen. A javításban ismételd meg a kérdést, hogy ne kelljen visszagörgetnem.
Tegyél bele szándékos szóhasználati csapdákat is (pl. „képes rá” és „csak arra képes”).
```

Sok, egymáshoz hasonló elemnél (parancsok, függvények, kapcsolók) a párosítós forma jobb azzal a kéréssel kiegészítve, hogy hiba esetén azt is magyarázza el, miért kevertük össze a két elemet. Kötetlenebb számonkéréshez az egyesével feltett, fokozatosan nehezedő kérdések illenek jobban.

#### Szókratészi feldolgozás és analógia új anyagnál

Teljesen új, logikailag összefüggő anyagnál a részletek előtt érdemes a szerkezetet megérteni.

```
A(z) [téma] nekem új. Ne magyarázd el egyben! Tegyél fel egy logikai kérdést, amire előismeret nélkül, józan ésszel is tudok felelni, várd meg a válaszomat, javíts, és csak utána add meg a hivatalos definíciót forrásmegjelöléssel.
Ne lépj tovább, amíg nem jeleztem, hogy értem.
```

Absztrakt architektúráknál, ahol a részek viszonya a lényeg, analógia is kérhető.

```
Nincs tiszta mentális modellem arról, hogyan kapcsolódik [A], [B] és [C].
Építs egy hétköznapi analógiát, amelyben minden elemnek megvan a párja.
Utána én kérdezek bele.
```

Az analógia nem bizonyíték. Érdemes rákérdezni, hol hibás és mi az, ami már nem illeszthető össze, mivel így kapunk pontosabb képet.

#### Szigorú javítás és feladatgyakorlás

Kifejtős kérdéseknél és gyakorlófeladatoknál nem elég nagyjából tudni a választ. Szigorú visszajelzés kell, mert az MI alapból biztató, és a „majdnem jó” választ is elfogadja.

Kifejtős válasznál először mi írjuk meg a választ, és csak utána kérjük a javítást.

```
Íme a válaszom erre a kérdésre: [kérdés] [válasz]
Javítsd úgy, mint egy szigorú vizsgáztató. Emeld ki a kulcsszavakat, amelyek nélkül nem teljes a válasz, jelöld, mi hiányzik, és írj egy rövid, vizsgán leírható mintaválaszt.
Ne kímélj.
```

A mintaválaszt nem érdemes lemásolni. Többet ér, ha emlékezetből újraírjuk, és újra javíttatjuk.

Feladatgyakorlásnál a megoldáson túl a mögöttes szabályt is érdemes megérteni, mert az más megfogalmazású feladatoknál is használható.

```
Itt egy feladat: [feladat]. Előbb megoldom, te javítod.
Utána mondd meg, milyen általános szabály van mögötte, és adj két variánst, amelyekben ugyanezt másképp kérdezik. Azokat is én oldom meg.
```

#### „Íme az értelmezésem, ellenőrizd”

A diplomamunka során ez volt a legfontosabb módszer. Előbb saját szavainkkal leírjuk, amit megértettünk (cikkről, kódról, fogalomról), és csak utána kérünk visszajelzést, a forráshoz kötve.

```
Feldolgoztam a(z) [cikk / fájl / fogalom] anyagát. Ez az én jegyzetem: [jegyzet]
Nézd át a forrással összevetve. Jelöld, mi pontos, mi pontatlan, mi hiányzik.
Minden javításnál mutasd meg, hol van a forrásban (oldalszám / fejezet / kódsor).
Ne írd át a jegyzetemet, csak mondd meg, mit javítsak, és én javítom.
```

Szakcikkekhez érdemes egyszer jegyzetsablont készíttetni, és minden cikknél ugyanazokat a mezőket kitölteni (probléma, módszer, eredmények, korlátok, viszony a saját munkámhoz). Az üresen maradó mező megmutatja, hol hiányos a megértés. Kézzel rajzolt gondolattérképnél ugyanez működik, azzal a kiegészítéssel, hogy jelölje a kapcsolat nélkül lógó elemeket, és tartsa meg a mi ágszerkezetünket.

### Ellenőrzés és reflexió

#### Összevetés a hivatalos anyaggal és másodlagos forrással

Az MI által készített táblázatok és összefoglalók gyorsan elkészülnek, de nem hibátlanok. Érdemes őket a hivatalos anyaggal és egy másik forrással, például egy évfolyamtárs jegyzetével is összevetni.

```
Feltöltöttem egy más által készített jegyzetet. Vesd össze azzal, amit eddig átvettünk.
1. Milyen téma szerepel benne, amit kihagytunk?
2. Hol mond ellent a hivatalos anyagnak?
Ellentmondásnál a hivatalos anyag a mérvadó.
```

#### Hibanapló

Egy munkamenet vagy témablokk végén érdemes összegyűjteni a hibáinkat, mert egyenként javítva nem látszik, ha ugyanaz a gondolkodási hiba ismétlődik.

```
A mai munkamenet végén gyűjtsd össze az összes hibámat egy táblázatba:
mit gondoltam, mi a helyes, és melyik hibatípusba tartozik.
Mondd meg, van-e visszatérő mintázat, és adj rá 5 célzott kérdést holnapra.
```

A másnapra ütemezett célzott kérdések egyben az elosztott ismétlés legegyszerűbb formája.

## Saját tapasztalatok

### Vizsgafelkészülés

A felkészülés bő egy hétre esett. A tárgy első felét egy zárthelyiből ismertem, de sok minden megkopott. A második felén kevesebbet vettem részt, így az szinte teljesen új anyag volt. A zárthelyi alapján a vizsgán is igaz/hamis kérdésekre számítottam negatív pontozással, párosításra, rövid kifejtésre és két nagy feladatra.

Egy Claude-projektbe töltöttem fel az előadásdiákat, a két tárgyjegyzetet, a tematikát és a gyakorlatok C-forrásfájljait, egy évfolyamtárs jegyzetét pedig ellenőrzésre használtam. A munka 14 beszélgetésen át tartott. Mellette kézzel írtam jegyzetet, gondolattérképeket rajzoltam, és az összefoglaló kártyákat Notionben gyűjtöttem.

#### Amikor az MI helyettem priorizált

Az idő szűkössége miatt az MI javasolta, hogy a 80/20-as szabály kerüljön be az utasítások közé, és a fontos részekre koncentráljunk. Ennek következtében szó nélkül kihagyott részeket, és emiatt sokat vitatkoztam vele, ami időt vett el.

Prompt:
```
[...] Ezen felül meg szeretném kivenni az utasításaid közül a 80/20-as szabályt, mivel nagyon sok mindent emiatt hagytál ki. Emiatt sokszor "vitatkoztam" és beleszóltam a dolgokba, ami szerintem plusz időt vett el a készülésből. És nem mellesleg így, most hiányzik a proc rész, [...]
```

MI:
```
[...]
80/20 szabály — kiveszem az explicit alkalmazásából. Igazad van, több anyagrészt kihagytam miatta indokolatlanul, pl. éppen a /proc-ot. Inkább te jelzed ha valami túl részletesnek tűnik.
[...]
```

Ezután átírtam a projekt-utasítást. Az MI ezt követően semmit nem hagyott ki, a kevésbé hangsúlyos részeket rövidebben vette.

Hasonló korrekcióra többször is szükség volt. Egy témablokk például azért maradt ki a tervből, mert azt mondtam, hogy van alapom hozzá, pedig csak egy kis részét ismertem, és ez csak napokkal később derült ki. Máskor a magyarázat passzív felsorolásba csúszott, vagy a kvíz kilépett a kért keretből.

#### Amikor az MI tévedett

Az MI hibáit mindig a hivatalos anyaggal való összevetés hozta elő. A legtanulságosabb eset egy állapotgráf volt, amelyet az MI hibásan írt le.
 
Prompt:
```
A taszk állapotok kapcsán csak azt nem értem, hogy a ucos2 esetén miért lenne a megszakítva az a várakoziknak az alesete. A taszk állapotok képe alapján nekem nem úgy tűnik, hogy ez így lenne.
```
 
MI:
```
Igazad van, és köszönöm, hogy megmutattad a diagramot — ez egyértelműen cáfolja, amit korábban mondtam.
[...]
Öt, egymással egyenrangú állapot van, nem négy + egy aleset
[...]
```
Ennél az esetnél tanultam a legtöbbet, mert pontosan meg kellett fogalmaznom, mit mutat a diagram, és így a két állapot közötti különbség is rögzült.
 
#### A nagy kép összeállása

A vizsga előtti estén egy kódértelmezési szimuláció megmutatta, hogy a részletek megvannak, de az egész kép hiányzik. Két fogalmi hibát vétettem, ezért megálltam, és arra kértem az MI-t, hogy egy analógián keresztül magyarázza el, hogyan kapcsolódnak egymáshoz a részek.
 
Prompt:
```
[...] nem annyira tudom elképzelni a kernel modulok és eszköz kezelők világát. Nem látom át, hogy akkor mi mit csinál. [saját elképzelés] [...]
```
 
MI:
```
[...]
Képzeld el a számítógépet egy nagy, őrzött irodaházként. Az irodaházban van egy páncélterem, tele közös, értékes erőforrásokkal [...]
Szóval kell egy házvezetőség, akiknek egyedül van kulcsuk mindenhez [...] Ez a kernel.
[...]
Van egy szolgálati ablak az ajtón: a rendszerhívás (syscall).
[...]
```
Az analógiát kérdésekkel próbáltam ki, és a tárgy korábbi részéből ismert fogalmakat is elhelyeztem benne. A nagy kép így csak a vizsga előtti estén, hat nap részletei után állt össze. Utólag ezzel kezdeném egy új anyag feldolgozását.

### Diplomamunka

A diplomamunkámhoz számos szakcikket gyűjtöttem össze. Az MI-től azt kértem, hogy segítsen hatékonyan feldolgozni őket, mert nem akartam, hogy passzív olvasás legyen belőle, és végül semmi ne maradjon meg. Először olvasási sorrendet állított össze, és megjelölte, melyik cikk kapcsolódik szorosan a témámhoz, és melyik kevésbé. Ezután jegyzetsablont javasolt, és tanácsokat adott ahhoz, hogyan töltsem ki eredményesen. A kitöltött jegyzeteimet elküldtem neki, és a cikkel összevetve javíttattam. A sablon „viszony a saját rendszeremhez” mezője rendre üresen maradt, és ez megmutatta, hogy a saját rendszerem működését még nem látom át elejétől a végéig. Ez lett a következő tanulási célom.

A fejlesztéshez meg kellett értenem a rendszert és a kódbázist, ami több, mások által írt repóból álló rendszernél nem egyszerű feladat. Ahelyett, hogy rögtön magyarázatot kértem volna, először magam próbáltam megérteni a működést. Amikor elakadtam, iránymutatást és forrásokat kértem. Amikor már volt rálátásom a rendszerre, leírtam neki a saját értelmezésemet, és megkértem, hogy ellenőrizze, helytálló-e.

A hibakeresésről és a konténeres fejlesztőkörnyezetről külön esettanulmányt írtam ([1007_KontenerizacioROS](../1007_KontenerizacioROS/index.md)).

## Források
- [[1]] J. Dunlosky et al.: Improving Students' Learning With Effective Learning Techniques. Psychological Science in the Public Interest, 2013 
- [[2]] S. Keshav: How to Read a Paper. ACM SIGCOMM Computer Communication Review, 2007

[1]: https://www.whz.de/fileadmin/lehre/hochschuldidaktik/docs/dunloskiimprovingstudentlearning.pdf  "J. Dunlosky et al.: Improving Students' Learning With Effective Learning Techniques. Psychological Science in the Public Interest, 2013"
[2]: https://dl.acm.org/doi/abs/10.1145/1273445.1273458 "S. Keshav: How to Read a Paper. ACM SIGCOMM Computer Communication Review, 2007"
