---
layout: default
codename: AlkFejlHf29
title: Anyajegy tanulságok
tags: alkfejl afhf skipfromindex
authors: Veszelovszki Soma, Nagy Bálint
---

# Anyajegy csapat
## Tanulságok az Alkalmazásfejlesztés (VIAUMA09) című tantárgy házi feladatának megoldása közben

### Feladat
A mi feladatunk – a RobonAUT versenyhez kapcsolódva – egy olyan alkalmazás fejlesztése volt, ami a versenyautónk diagnosztizálását segíti: üzeneteket fogad az autótól Bluetooth-on keresztül, megjeleníti az autó pályáját, illetve a vonalérzékelés eredményét és hibáját vizualizálja.
### Általános tapasztalatok
A félév elején semmilyen koncepcióval nem készültünk arra vonatkozóan, hogy miként kellene felosztani egymás között a feladatokat. Ez hiba volt. Az applikációt eleinte hektikusan éppen kinek van ideje rá fejlesztettük, amiből az adódott, hogy (lévén 2 fős a csapatunk) egyikünk elkezdte relatíve korán és másikunk csak nagyon későn, a program logikai magjának majdnem teljes elkészültekor csatlakozott. Így egy jókora mennyiségű kódot kellett megérteni, mielőtt a funkciók implementálását elkezdhette a másik. Ezzel kapcsolatosan egy tanács: Ha a fenti jelenséget nem tudjátok elkerülni, javaslom, hogy a későn érkező dokumentálja le az eddig megírt kódot, mert ez egyszer motiváló is, hogy ne késs (dokumentálni nem szeretünk), illetve biztosan tudni fogod, hogy mi történik a háttérben.
Dokumentáláshoz még egy tanács: Amikor már úgy érzitek, hogy egy adott funkció már nagyjából kész van, akkor dokumentáljátok le, mert ha akkor kezditek a kommentek írását, mikor már a teljes program kész, az nagyon sok lesz.
### Grid layout
Az alkalmazás GUI tervezése során a beépített Grid layout-ot használtuk előszeretettel, mikor egy Widget/Tab táblázatosítását akartuk megoldani. Ez azért jó, mert később az ablakméret változtatásnál nem fog szétesni a GUI, arányosan fognak változni a grid mezőibe illesztett elemek. Fontos megjegyezni, hogy a Grid layout Widget-hez való importálás sikerességét mindenképp ellenőrizzétek! Mikor a GUI szétesést próbáltuk megoldani, akkor csak sok idő múlva derült ki, hogy egy érvénytelen grid hozzáadás miatt nem működött úgy a GUI, ahogy mi azt vártuk. Ha rossz volt a grid hozzárendelés, akkor egy    ikont fogtok látni a Widgetetek mellett. Érdemes a Widget létrehozás -> elemhozzáadás a Widgethez -> Widget-re jobb gomb -> Lay out -> Lay Out in a Grid sorrendet tartani, és akkor jó lesz.
### Bluetooth és Serial kommunikáció
A soros porton történő kommunikáció megvalósítása a vártnál lényegesen gyorsabban ment, a QSerial API hivatalos (Qt honlapon lévő) dokumentációja és példakódja sokat tud segíteni. Ne felejtsétek el az <applikációnév>.pro fájlban (kacsacsőrök nélkül ) hozzáadni a függőséget a 
```sh
QT += serialport
```
segítségével! 
A mi feladatunkban a kommunikáció Bluetooth-on keresztül történik. A Qt-nak van beépített Bluetooth API-ja – ne ezt használjátok! Az egyik ok, hogy Windows 10-en nem működik, de ráadásul a projekthez kapott Bluetooth modul (és valószínűleg a piacon kapható összes Bluetooth modul) kezelhető virtuális soros porton keresztül. Gyakorlatilag annyit kell csinálni, hogy ha rácsatlakoztatok a Bluetooth modulra a számítógépről, az Eszközkezelőben megjelenik a COM portok alatt két virtuális soros port – ezek közül az egyik működni fog (pl. nálunk a ’COM6’). Ezek után egy mezei soros portként lehet kommunikálni a modullal, ugyanúgy, mint eddig, a QSerial API-n keresztül.
### Lista megjelenítése
Valószínűleg mindenkinek kell listát megjelenítenie az alkalmazásában. Mi például a Bluetooth-on (virtuális soros porton) keresztül érkező üzeneteket tettük bele egy listába. Az elején a beépített listamegjelenítéssel próbálkoztunk (QStringList, QListView). Egész egyszerűen lehet kezelni, viszont egy bizonyos mennyiségű üzenetet utánelkezdett nagyon belassulni a megjelenítés. Próbálkoztunk a lista mögötti modell optimalizálásával, de végül a működő megoldás az lett, hogy egy QTextBrowser-t tettünk a QListView helyére. Ez egy egyszerű szövegdoboz, amihez hozzá lehet fűzni string-eket. A bejövő üzeneteket így egyszerűen hozzá lehet fűzni a szövegdoboz tartalmához, és ez nem lassul be.
### Megjelenítő modulok tesztelése
A megírt megjelenítő modulok tesztelését célszerű az alkalmazáson belül leimplementálni. Mi például készítettünk egy olyan segédosztályt, ami a soros kommunikációt helyettesítve generált üzeneteket küld az üzenetkezelőnknek. Ezzel nagyban meg lehet könnyíteni a fejlesztést, mert ha a roboton futó kód éppen nem működik, vagy egyszerűen csak még nincs elkészítve a tesztelendő modul, a Qt alkalmazást akkor is ki lehet próbálni. 
### QTest
A QTest írása során többnyire a tesztelendő projekt függvényeinek láthatóságával kapcsolatban voltak problémák. Ahhoz, hogy a QTest projektben hivatkozhass az applikációban használt függvényekre, egyrészről a QTest .pro fájljában adjátok hozzá a header-öket tartalmazó mappa elérési útvonalát az 
```sh
INCLUDEPATH += <útvonal> 
```
hozzáadásával illetve ez még nem lesz elég, szükség van a függvénytörzseket leíró .cpp fájlok elérési útvonalára, itt a 
```sh
SOURCE += <útvonal/fájlnév.cpp> 
````
sorokkal tudtok dolgozni. Ne felejtsétek el, hogy ne abszolút útvonalat adjatok meg, hanem relatívat, hogy ne csak a saját gépeteken működjön a QTest. Másik tanács: Érdemes a QTest Snippet-ben leírtakhoz hasonlóan direkt rossz példát adni vizsgáló feltételnek, hogy megbizonyosodjatok a helyes működésről.
### Q_OBJECT
Amennyiben „Qt undefined reference to vtable …” hibaüzenetet kaptok, az vagy azért van, mert a Q_OBJECT makró hiányzik a class-otoknál, vagy éppen nem kell oda (furcsa, de ilyen is volt), illetve egy qmake lefuttatása is tud segíteni a dolgon.
