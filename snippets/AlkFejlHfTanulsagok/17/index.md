
---
layout: default
codename: AlkFejlHf17
title: AlkFejlHf17 (2017 ősz - mikrobi)
authors: mikrobi csapat (AlkFejl 2017 ősz)
tags: snippets alkfejl házi qml qrc
---

# QML Image típus és .QRC fájl #

## Bevezetés ##
Alapvetően, ahogy a névből kitalálható, ez a típus kép fájlok megjelenítésére szolgál. De azt is érdemes tudni, hogy az Item QML típsuból származik, így rendelkezik annak property-ivel.
A kép forrása egy URL címmel adható meg a *source* property-vel. Ezen URL-t a program úgy értelmezi, mint a .qrc fájl gyökérkönyvtárától vett abszuolút elérési útja a képnek.
Minden olyan formátumú kép, melyet a Qt támogat, használható (a teljesség igénye nélkül: JPG, PNG, BMP, SVG). Valamint lehetőséget biztosít animált képek megjelenítésére is.

## QML Image típus ##
### Egyszerű példa ###
Egy szimpla kép betöltésére láthatunk példát az alábbi kódban:
```qml
import QtQuick 2.0

Image {
	source: "abra/kep.png"
}
```
![A betölött kép](https://github.com/ajohntom/snippets/blob/gh-pages/snippets/AlkFejlHfTanulsagok/17/abra/qtlogo-simple.png "A betöltött kép")

Mint látható, a képek betöltéséhez szükség van *QtQuick 2.0* importálására, ami lényegében az alapvető típusokat biztosítja a QML alapú kezelőfelületek kialakításához.
Alapesetben ha betöltünk egy képet, és nem adunk meg semmilyen property-t, kizárólag a *source*-ot definiáltuk, akkor a kép eredeti méreteiben kerül beillesztésre.
### Property-k ###
Ám van lehetőségünk a *height* és *width* paramétert is állítani, amivel a magasságot és szélességet szabályozva kedvünkre skálázhatjuk a képet. Ez persze érdekes eredményekhez vezet... Nézzük is a kódot és az eredményét:

```qml
import QtQuick 2.0

Image {
	width: 130; height: 100
	source: "abra/kep.png"
}
```

![Megynyújtott kép](https://github.com/ajohntom/snippets/blob/gh-pages/snippets/AlkFejlHfTanulsagok/17/abra/qtlogo-stretch.png "Megnyújtott kép")

Ahogyan látható, a képünk, ha gondolkodás nélkül skálázzuk, nem örzi meg arányait és az eredetileg 87x100 pixeles képünk, 130x100-asra módosult.. 
Ezt elkerülendő hozzáadhatunk egy extra property-t, a *fillMode*-ot.
Ennek állításával megszabhatjuk, hogy milyen módon reagáljon a képünk, ha *width* vagy *height* property-ét állítjuk.

A következő kódban, ezt a paramétert *Image.PreserveAspectFit*-re állítjuk:
```qml
import QtQuick 2.0

Image {
	width: 130
	height: 100
	source: "abra/kep.png"
	fillMode: Image.PreserveAspectFit
}
```
Az eredmény, hogy a képünk 130x100 pixeles lett:

![Megynyújtott kép, megőrzött arányokkal](https://github.com/ajohntom/snippets/blob/gh-pages/snippets/AlkFejlHfTanulsagok/17/abra/qtlogo-preserveaspectfit.png "Megnyújtott kép, megőrzött arányokkal")


Ezzel, mint az elnevezéséből is látszik, a kép megőrzi az arányokat, és ennek megfelelően reagál majd a direkt dimenzió állításokra. 
Ezt a beállítást mindenképpen hasznos alkalmazni,
mivel a képek torzítása sosem célunk. Ha pedig skálázni szeretnénk a képet, akkor ott a *scale* property, amivel arányosan lehet nyújtani az objektumokat, és könnyebb is mint az arányokat számítgatni.
Arról, hogy a *fillMode* property-t egyébként milyen értékekre állíthatjuk be [itt](https://doc-snapshots.qt.io/qt5-dev/qml-qtquick-image.html#fillMode-prop) olvashatunk többet.

A másik relatív hasznos property-e az Image típusnak a *smooth*, amely - boolean típusú - ha igazra van állítva, feljavítja a kép megjelenítését, ha transzformáljuk valamilyen módon azt.
Ennek eredménye egyes kép skálázások/transzformációk után igen szembetűnő. Ez a property egyébként alapból engedélyezve van. Engedélyezett esetben szimpla lineáris interpolációt használ a program, míg a másik esetben a legközelebbi szomszéd metódust.
Jótékony hatása látható a következő képen, ahol a felső sorban ezen property *false* értékkel lett deiniálva, alul pedig nyilván, *true* értékkel.

![A smooth property hatása](https://github.com/ajohntom/snippets/blob/gh-pages/snippets/AlkFejlHfTanulsagok/17/abra/rectangle-smooth.png "A smooth property hatása")

### További property-k ###

Mint említtetem, az Image örökli az Item QML típus property-it. Ezek közül sok olyan van, amit egy általános kép kezelésénél használhatunk, s melyek a következő listában szerepelnek:
* *rotation*: Kép forgatása, egy fokban megadott értékkel (real típusú), az óramutató járásával megegyező irányba.
* *scale*:  Kép skálázása adott (real típusú) értékkel. 1-nél kisebb érték esetén értelemszerűen összenyom, negatív értékben tükrözést vált ki.
* *transformOrigin*: Azt állítja, honnan menjen végbe például a skálázás vagy forgatás művelete, melynek lehetséges értékeit [itt](https://doc-snapshots.qt.io/qt5-dev/qml-qtquick-item.html#transformOrigin-prop) találhatjuk.
* *opacity*: Az átlátszóságát állítja az objektumnak, szintén real típusú számot vár, ám értékét csak 0 és 1 között lehet változtatni.
* *visible*: A láthatóságát állítja be a képnek, boolean típusú értéket vár. Ha vannak leszármazott objektumai az adott elemnek, akkor azokra is kihat a változó állítása.
* *x,y,z*: Lehetséges velük az adott szülő objektumon belüli direkt pozíció megadása. A z tengely az alkalmazás ablakából kifelé mutat, ahogyan az a jobbsodrású rendszerből adódik. 
Ennek állításával tehát lehetséges az objektumok fedésének modosítása. Érdemes még tudni azt is erről a property-ről, hogy a szülő objektumot a leszármazott objetum mindig fedi, s ennek korrigálására például nagyon hasznos tud lenni.
Alapértéke egyébként 0.

Ezen property-k állításával elvégezhetőek a képeket érintő alapvető manipulációk, melyek szükségesek lehetnek, például egy jól megtervezett logó/dizájnelem elhelyezéshez.

## Képek betöltése - .QRC fájl ##

Jogosan felmerülhet a kérdés, hogy hogyan lehet képeket betölteni, hogy elérhetőek legyenek a QML környezetben. Erre a legegyszerűbb mód, ha a QtCreator felületen a projektben a gyökérkönyvtáron(/) egy jobbklikk után az
*Add existing direcotry* opciót választjuk.
 
![Fájlok hozzáadása](https://github.com/ajohntom/snippets/blob/gh-pages/snippets/AlkFejlHfTanulsagok/17/abra/qtcreator-rcc2.JPG "Menü 1")

Ezek után van lehetőségünk választani a projektmappában előkészített kép fájlokból (itt éppen a pic/car.png állományt kívántam hozzáadni).Ügyelni kell arra, hogy a .qrc fájlunk mellett (vagy almappában) legyenek a megadott fájlok.
 
![Megfelelő fájlok kiválasztása](https://github.com/ajohntom/snippets/blob/gh-pages/snippets/AlkFejlHfTanulsagok/17/abra/qtcreator-rcc3.JPG "Menü 2")

Persze van mód, direkt a projektunk .qrc fájlját szerkeszteni. Ez a kicsit bonyolultabb módszer, lényegében a QtCreator is ezt hajtja számunkra végre. Ennek felépítésének tanulmányozásához nézzük a következő példákat:

```xml
<!DOCTYPE RCC><RCC version="1.0">
<qresource>
    <file>abra/kep.png</file>
</qresource>
</RCC>
```
Itt lényegében egyetlen fájl van a .qrc fájlunkban, melyet direkt az */abra/kep.png* hivatkozással érhetünk el.
Ám van lehetőség felüldefiniálásra:

```xml
<!DOCTYPE RCC><RCC version="1.0">
<file alias="kep.png">abra/kep.png</file>
</qresource>
</RCC>
```

Ezzel, ezentúl elérhetjük a képet a */kep.png* hivatkozással.
Ám lehetséges megadni nem csak egy fájl alias-t, hanem egy elérési útvonal prefix-et is.

```xml
<!DOCTYPE RCC><RCC version="1.0">
<qresource prefix="/sajatAbra">
    <file alias="kep.png">abra/kep.png</file>
</qresource>
</RCC>
```
Ezek után a képet lehetséges elérni a */sajatAbra/kep.png* hivatkozással.

Most azt is nézzük meg, hogy saját példában, hogyan módosult a .qrc fájl, ha a QtCreator-al adtuk hozzá:

![A .qrc fájl tartlama](https://github.com/ajohntom/snippets/blob/gh-pages/snippets/AlkFejlHfTanulsagok/17/abra/qtcreator-rcc4.JPG "A .qrc fájl tartlama")

Látható, hogy itt is van egy prefix, ami a gyökérkönyvtár(/) elérési utat definiálja, de utána azt is lehet látni, hogy minden fájlt az eredeti nevén, és elérésvel tudunk megadni.

Tehát alapból, a QtCreator-ban történt betöltés után olyan néven van lehetőségünk elérni a fájlokat, ahogyan azokat eredetileg elneveztük, s ha egy almappában volt megtalálható az, akkor az is felvételre kerül a .qrc fájlba az elérési útvonalhoz.
De mint láttuk van lehetőségünk felüldefiniálni ezen elérési módokat a .qrc fájl szerkesztésével. Ez esetleg akkor lehet hasznos, ha például az egy modulhoz tartozó képek fizikailag nem egy almappában vannak (mondjuk
az eltérő kategorizálás miatt) de a velük való munka során hasznosabb, ha elérésükhöz egy prefix-et állítunk be.

A Qt RCC rendszer egyébként azért nagyon jó, mert egy platformfüggetlen módot biztosít különféle bináris fájlok tárolására az alkalmazás végrehajtható fájljában. Ez nagyon hasznos tud lenni, ha az alkalmazásnak mindig szüksége van
bizonyos fájlokra (például ikonokra, képekre) a helyes megjelenítéshez, és nem akarunk koczkáztatni, hogy ezeket külső forrásban tároljuk el. Ezen nélkülözhetetlen fájlok vehetőek fel a fentebb taglalt módon a .qrc (Resource Collection) fájlban. Ahhoz, hogy valóban belekerüljenek ezek a fájlok a végső, végrehajtható fájlba, a kövekező sort kell hozzáadnunk a .pro fájlhoz (nyilván a *filename* részt személyre szabva):

```
RESOURCES     += filename.qrc
```

Ha betöltöttük a képeket, utána a kezdetben tárgyalt módon van lehetőség definiálni a kép forrását.

Különféle képek beszúrására sok helyen szükség lehet, legyen szó design vagy funkciónális (például a GUI-n eseményeket kiváltó felület) egységekről. Fontos tisztában lenni azzal, hogyan lehetséges ezek betöltése és alapvető 
manipulálása.


