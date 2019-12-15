---
layout: default
codename: AlkFejlHf41
title: Riders of the ST ARM csapat tanulságai
authors: Balogh Bence, Kiss Ágoston, Reucsán Bence
tags: alkfejl afhf skipfromindex

---

# Riders of the ST ARM csapat tanulságai Alkalmazásfejlesztés házifeladathoz
A csapat tagjai közül ketten a RobonAut versenyben is részt vesznek, így a kliensalkalmazást nem szimulátorral, hanem a valóságos versenyautóval használjuk. A feladat egy olyan alkalmazás fejlesztése volt, ami a versenyautónk diagnosztizálását segíti: üzeneteket fogad az autótól TCP kapcsolaton keresztül, megjeleníti a szenzorok adatait és az autó állapotát, továbbá lehetőség van az autó bizonyos paramétereinek állítására is. Az alábbiakban néhány, a fejlesztés során felmerült probléma megoldása, valamint hasznos tanácsok találhatók.

### 1. Csapatmunka
Érdemes a feladatokat elkülöníteni és felosztani, így az egy emberre jutó munka harmadolódik. Fontos megjegyezni, hogy nem elég a kliens-oldalt megcsinálni, a roboton is sok munka lesz, így azzal is számolni kell. Mivel lehet, hogy a robotnak nem lesz meg minden funkciója időben, ezért mindenképpen érdemes összedobni a szimulátort is, hogy addig is lehessen haladni, majd ha elkészült a program, akkor már csak a kommunikációs osztályokat kell összelőni, hogy működjön a való életben is. Az projekt managmenthez mi felhasználtuk a [trello](https://trello.com/) webalkalmazást. Itt különböző táblákba lehet rendezni a feladatokat és sok egyéb funkció könnyíti meg a házi állapotának követését. 

### 2. Clean build
A Qt Creator-ban történő fejlesztés során néhányszor előfordult, hogy a Build gombra történő kattintás után nem érzékelte a változtatásokat. (Ez főleg a QML fájlokat érintő változásoknál fordult elő.) Ilyenkor hasznos lehet az egész projektet clean-elni, majd ezután újrafordítani.  

### 3. Szóköz és ékezet az elérési útban
Érdemes arra figyelni, hogy a projekt elérési útvonala ne tartalmazzon ékezeteket és/vagy szóközt, mivel rejtélyes hibák fordulhatnak így elő.

### 4. Debug üzenetek
Sok esetben hasznos lehet a debug konzolra való üzenet kiírás. C-ben általában a printf függvényt használjuk erre a célra, de Qt környezetben a `qDebug() <<  "Hello world!";` parancs használható debug üzenetek kiírására. A QML oldalon is lehetőség van ilyen üzenetek megjelenítésére, ehhez az adott javascript függvényben a `console.log()` függvényt kell meghívni egy sztring paraméterrel.

### 5. Online dokumentáció
A Qt QML nagyon jól van dokumentálva és sok példa található hozzá. Érdemes lehet az egyes dolgokra rákeresni, mielőtt túlbonyolítanánk valamit, mert valószínűleg van hozzá megfelelő QML type, aminek részletesen le van írva a használata. Ezek mellett érdemes átnézni az alkalmazás fejlesztéshez tartozó korábbi házi snippeteket.

### 6. QML import
Bár sok QML Type található online dokumentációkban, arra is figyelni kell, hogy az azokat tartalmazó könyvtár importálva van-e a QML kódunkba, illetve, hogy tudjuk-e egyáltalán importálni, azaz telepítve van-e a számítógépünkre. A fordító nem minden esetben dob erre hibát, csak egyszerűen nem jelenik meg a QML felület a program indításakor.

### 7. Qt debug kitek
Debug módban előfordult, hogy egy-egy breakpoint-nál nem állt meg a program futása ott, ahol biztosan meg kellett volna, viszont egy másik Kit-et használva igen. Ezért érdemes debugolás esetén ezt is figyelembe venni, akár még a kódban történő hibakeresés előtt.

### 8. QML Repeater
Ha több, hasonló működésű komponenst akarunk kezelni a QML oldalon, akkor érdemes egy Repeater QML típust használni. Ezt igazából utána lehet egy tömbként használni. Elkészíteni nagyon egyszerű, miután megadtuk, hogy hogy legyenek elrendezve a komponensek, csak meg kell adni a darabszámot és magát a komponenst:
```javascript
    Row {

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            Repeater {
                id: lineSensorDispArray
                model: 32
                StatusIndicator { color: "green"; width: lineSensorElement.width / 32; active: true}
            }
        }
```
Ezután az itemAt(index) metódussal lehet kezelni az egyes elemeket. 
Bővebb információ a [hivatalos honlapon](https://doc.qt.io/qt-5/qml-qtquick-repeater.html)

### 9. Grafikonok létrehozása
Grafikonokat létrehozni nem csak az Simple Telemetry Visualizer-ben szereplő Canvas osztállyal lehet, erre a célra használható a ChartView is. Az alkalmazásunkban a ChartView segítségével jelenítettük meg a gyorsulásmérő és a szabályozóhoz tartozó jeleket. 
A ChartView-n belül a ValueAxis típussal lehet tengelyeket hozzáadni a grafikonhoz, továbbá a tengelyekhez kapcsolódó tulajdonságokat is lehet beállítani:
```javascript
ValueAxis {
	id: axisXTop // a tengely azonosítója
	titleText: "X axis [g]" // a tengely elnevezése
	min: -4 // minimum érték
	max: 4 // maximum érték
}
```
Adatsorokat például a ScatterSeries segítségével adhatunk a grafikonhoz:
```javascript
ScatterSeries {
    id: accelerationSeries // adatsor azonosítója
    axisXTop:  axisXTop // x tengely
    axisYRight: axisYRight // y tengely
    markerSize: 15 // az adatpontot jelképező "pötty" mérete
}
```
Egy új adatpont beszúrása az adatsorba az `accelerationSeries.append( xCoord, yCoord);` függvényhívással lehetséges.
## Összefoglalás
A házi feladatnak ajánlatos időben nekilátni, mivel nem teljesen triviális a megoldás. Ha RobonAUT-hoz kapcsolódik a téma, akkor érdemes úgy választani a kijelzett értékeket, hogy azokat valóban hasznosítani lehessen fejlesztés során. A félév során rendkívül sokat tanultunk a Qt és QML használatáról, valamint a verziókövetésről és a megfelelő dokumentáció készítésről.