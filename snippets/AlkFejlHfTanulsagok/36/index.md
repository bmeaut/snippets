---
layout: default
codename: AlkFejlHf36
title: AlkFejlHf1 - Glitter összefoglaló
authors: Havasi Dávid, Papp Lilla, Nagy Tibor
tags: alkfejl afhf skipfromindex
---

---
# A Glitter csapat tapasztalatai

Ez a kis snippet az alkalmazásfejlesztés házi feladat készítése során összegyűjtött tapasztalatainkat gyűjti össze.

## Qt környezet és a program fejlesztés kezdeti lépései
Az oldalon található snippetek, és pullolható példakódok rendkívül hasznosnak bizonyultak a teljesen ismeretlen fejlesztőkörnyezet, és programnyelv megismerése során. Különböző snippetek és példakódok segítségével meglehetősen hamar sikerült működőképessé tenni a környezetet, és lefordítani az első működő programrészletet. A környezet telepítéséről szóló snippet kicsit hiányos abból a szempontból, hogy nem írja le az egyik telepítési lépésnél pontosan mely csomagokra lesz szükség, így mindent bepipáltam a biztonság kedvéért azonban gyorsan kiderült, hogy az ötlet nem volt a legjobb, mivel a telepítés így 40GB helyet vett igénybe és órákig tartott. A legfrisebb Qt verziót lenyitva, csupán a MinGW bepipálására van szükség, így a telepítés kevesebb mint 1GB.

## A Qt fejlesztőkörnyezet
Jómagam jártas vagyok C# fejlesztésben, Visual Studio környezet alatt, amihez képest a Qt környezet lényegesen kiforratlanabbnak tűnt, lassítva ezzel a fejlesztés menetét. Ha a QML részben volt hiba, azt a 'Applicaton Output' fülön futás közben lehetett látni, amint nem nyílt meg az ablak a vártnak megfelelően. Ha a C++ részben volt a hiba, akkor a program szerkesztés közben nem mindig jelezte azt, csak fordítás során, ami viszont lényegesen hosszabb időt vesz igénybe (~1-2perc) mint Visual Studio esetében. Találkoztam olyan problémákkal is, hogy ha csak szimplán a futtatás gombra kattintottam, akkor általában újrafordítja ha a C++ oldalon talált módosítást, de sajnos nem mindig így történt ami egy-két alkalommal okozott fejfájást. Ezt manuálisan elindított Rebuildeléssel oldottam meg. Többször belefutottam olyan hibába is, hogy a rebuildelés sem oldotta meg a problémám. Ekkor töröltem az egész build mappát és úgy rebuideltem, ami valamilyen okból megoldotta a gondom. Összességében véve úgy gondolom, hogy a Qt környezet kevesebb funkcióval, kevesebb fejlesztés segítő lehetőséggel, és általánosan kiforratlanabb a Visual Studio-nál, amik egy hozzám hasonló viszonylag ritkán programozó egyénnek hatalmas segítséget jelentenek.

## UART kommunikáció a Qt és más hardvereszköz között

A házifeladatunk során saját RobonAUT-os versenyautóm diagnosztikai szoftverét készítettük el. Az én feladatom volt többek között az autó szoftverének megírása, mely valós idoben képes adatok küldésére és fogadására egy külso, jelen esetben Qt szoftvertol, továbbá az ezzel kompatibilis Qt-ben lévo adatfogadó modul implementálása.

A feladat során Bluetooth kommunikációt használtunk, amely a számítógép oldalán soros portként jelenik meg, a hardvereszközben legtöbbször fizikai UART porton valósul meg a kommunikáció. A diagnosztika és fejlesztés idejére a Bluetooth modul adott esetben egy FTDI átalakító segítségével pótolható. Ennek a megoldásnak az elonye, hogy még az UART-> Bluetooth átalakítók konfigurációja az eszköz egy külön módjában lehetséges egy parancssoros felületen keresztül, az FTDI chipp paraméterei gyakorlatilag a Windows felületén keresztül szabadon beállathatóak. 

A robot szempontjából kizárólag akkor lehetséges egy diagnosztikai szoftver folyamatos üzemeltetése, ha az nem akadályozza meg a foprogram muködését. A versenyre készített szoftverem roudrubin felépítésu, tehát a megszakítások egy egy flaget állítanak a kocsi szoftverében amit a Maine-ben futó függvény kezel le. Amennyiben egy függvény futási ideje a Maine-ben túlságosan hosszú, az blokkolhatja (elcsúsztathatja) a fontos szabályozó algoritmusok muködését. Ennek megoldására a szoftvert a következo módon építettem fel. Az UART fogadást DMA-val oldottam meg, megy nem szakíta meg a programom muködését. Az autó oldali küldésnél a normál küldési módnál maradtam. Ennek meggyorsítását au UART sebességének növelésével valósítottam meg 480600 baud.

Az üzenetek küldéséhez egy egy framet definiáltam. A frame rendelkezett kezdokarakterekkel, elválasztó karakterekkel, egy 2 byteos (2 karakteres) azonosítóval. Az adatok az elválasztó karakterek között lettek elküldve. Két üzenet, melyek a szoftverünk kommunikál.

~~_LG_"Szöveges üzenet érkezik, melynek lezárása egy alsó vonal"_
~~_CH_0000525_025565_001255_001456_125485_145699_

A két üzenetet a programunk feldolgozó mechanizmusa az "LG" és a "CH" azonosítók alapjén különíti el. Elonye, hogy így ha új üzenettípust hozunk létre az autó oldalán, azt a fogadó szoftvern nem fogja helytelenül értelmezni, továbbá, hogy az azonosító alapján egyértelmu melyik feldolgozó függvényt kell meghívnia. 

Míg a Qt oldalán a számokat tartalmazó stringek átalakítása nem nehéz feladat, addig a robotnál erre komoly konverziós függvényeket kellett megalkotnom, melyek kizárólag elore definiált adatok stringgé alakítására alkalmasak. Ilyen volt többek között az uint32_t to string array metódusom.

Amikor az üzenetformákkal és azok kezelésével elkészültem további nehézségeim akadtak. egy nagyon fontos tanulság, hogy az UART kommunikáció paraméterezését érdemes alaposan megnézni mind a PC mind az autó oldalán. a háziban 8N1-e kommunikációt használtam. Bizonyos termináloka PC oldalán képesek automatikusan felismerni a fogadott üzenetformát. Ennek eredményeként a kommunikáció rajtuk keresztül muködik, de az autó felol kibára fut (8E1-> 8N1 közötti különbség egy bit csúszást okoz...)
 
A teszteléshez nem szükséges a fizikai autó megléte, az adatok fogadását és küldését soros terminálokon is lehet emulálni. Az autó esetén egy terminálablak magában megoldást nyújt, azonban PC esetén szükség van egy kis trükközésre. Keresni kell egy olyan szoftvert, mely képes a számítógépen található két különbözo soros port összekapcsolására. ezek után megoldható két alkalmazás pl.: Qt és putty párosítása.

A feladat során az UART kommunikációt a kiadott gitrepositoryban talált megoldás alapján igyekeztem elkészíteni. A Qt-s UART fogadás rendelkezett egy kreatív megoldással, egy csak akkor fogad adatot, ha annak az elso 4 byteja (4 karaktere) uint32_t-be castolva megadja a fogadni kívánt adatok hosszát. Ha jobban belegondolunk ez megoldás nagyon megnehezíti a fejlesztést. A soros terminál alkalmazások karakterek küldésére lettek megalkotva. Ha egy ilyen alkalmazással olyan byte formát szeretnénk elküldeni amelynek nincs ASCII karaktere azt nem tudjuk beíri a konzol ablakába. A Qt által küldött üzenet fogadásakor szintén hasonló nehézségekbe ütköztem, hiszen a terminálablak nem képes megjeleníteni azon byte formákat melyeknek nincs ASCII karaktere. A fogadás megoldását a Qt szoftverének módosításával oldottam meg. A Qt által küldött adatokkal azonban nagyobb gondom akadt, hiszen a küldési formát ez esetben nem tudtam megváltoztatni. A végso megoldást a putty logolása jelentette. A terminál ugyan nem képes minden adat megjelenítésére, azonban fogadja azokat, melyeket bináris fájlban exportálhatunk. Ennek hexeditorral való tanulmányozása során sikerült visszafejtenem a Qt szoftver által küldött adatokat, melyeket korán sem kézenfekvo formában küldött el.

Készítette: Havasi Dávid, Papp Lilla, Nagy Tibor

---
