# A jeti123 csapat tanulságai az Alkalmazásfejlesztés házi feladattal kapcsolatban.

## .c .h fileok

Mindenképpen javasolt szépen struktúrált .cpp és .h fileokat készíteni, melyeknek beszédes neveik vannak. Ez jelentősen megkönnyíti a projekt átláthatóságát, valamint debuggolásnál is egyértelmű lesz miért és hova ugrálunk.

## Osztályok, öröklés

Az előbb leírtak itt is érvényesek, beszédes osztályneveket ajánlott kitalálni. Ne féljünk, ha esetleg hosszúra sikerül, inkább legyen átlátható, a code completion úgy is megkönnyíti a gépelést. Kiemelném, hogy az öröklési mechanizmus egy rendkívül hasznos funkciója a c++ -nak. Ne sajnáljuk az időt attól, hogy egy korrekt ősosztályt alkossunk meg, melyből örökölt példányok könnyebben átláthatóak. 

Esetünkben a `` WindowEventHandling `` osztályból származnak a szimulátor és a monitor ablakkezelői, rendre `` MonitorWindowEventHandling `` és `` SimulatorWindowEventHandling `` . Az ősosztály tartalmazza a QML oldali elemek keresésére szolgáló `` FindItemByName `` függvényeket, protected öröklési mechanizmussal. A konstruktora átveszi a `` QQmlContext `` objektumot, mely tovább öröklődik. Szintén itt kerül deklarálásra az ablakkezelők signal-slot mechanizmusához szükséges virtual öröklődésű `` ConnectQmlSignals `` függvénye, mely az alosztályokban az override kulcsszóval felülírható mint pl.: `` void ConnectQmlSignals(QObject *rootObject) override; `` Ennek segítségével az örököltetett osztályok saját módon írhatják felül az adott függvényt.

## c++ és QML környezet közötti változó átadás

Ez talán a grafikus felület egyik alapvető működési feltétele. Ha nem vagyunk képesek átadni a cpp oldali változóinkat a grafikus felületet alkotó QML-nek, szinte semmi értelme GUI-t készíteni. Ez persze visszafelés is igaz, hiszen olykor pl. egy csúszkával beállított értéket kell a cpp oldalon megvalósított funkciónknak átadni.

A probléma megoldása a következő:

#### cpp -> QML: "QString"
* Az átadni kívánt változó létrehozása:
```cpp
QString testResult = (testOK == true) ? "OK" : "NOK";
```
* Átadás a QML környezetnek "testResultText" néven:
```cpp
qmlContext.setContextProperty(QStringLiteral("testResultText"), QVariant::fromValue(testResult));
```
* Ezzel létrejött egy `` testResultText `` nevű változó a QML oldalon, melyet tetszőleges módon használhatunk a QML környezetben.

#### cpp -> QML: "QVector"
* Az átadni kívánt vektor:
```cpp
QVector<int> activeAlarmZones;
```
* Az átadáshoz deklarálni kell egy `` QVarianList `` nevű változót, melyet fel kell tölteni az átadni kívánt tömb elemeivel:
```cpp
QVarianList alarmZonesQML;
```
* A feltöltés:
```cpp
QVariantList alarmzone = QVariantList{}; //Átmeneti változó
for(int i = 0; i < activeAlarmZones.length(); i++)
{
    int zone = activeAlarmZones[i];
    alarmzone.append(QVariant::fromValue(zone));
}
alarmZonesQML = alarmzone;
```
* Átadás a QML környezetnek `` alarmZones `` néven:
```cpp
qmlContext.setContextProperty(QStringLiteral("alarmZones"), QVariant::fromValue(alarmZonesQML));
```

#### cpp -> QML: "2D vektor"
* A probléma a következő:
A szimulátorunk egy házat modellez, melyben több szoba van. A szobák hőmérséklete különbözik, melyet szeretnénk átadni a QML környezetnek. Az ábrázolhatóság érdekében azonban szeretnénk az utolsó N értéket megjeleníteni ezzel minden szobához N hőmérséklet tartozik. Az így keletkezett 2D tömb pl. a következőképpen nézhet ki:
Szoba1: | T1,1 | T1,2 | T1,3 | ... | T1,N |
Szoba2: | T2,1 | T2,2 | T2,3 | ... | T2,N |
Szoba3: | T3,1 | T3,2 | T3,3 | ... | T3,N |
Szoba4: | T4,1 | T4,2 | T4,3 | ... | T4,N |
* Az átadáshoz deklarált változó:
```cpp
QVariantList roomTemperaturesQML;
```
* Az adatok másolása és a 2D tömb létrehozása:
A "container" eltárolja a szobák állapotát minden új állapot érkezésekor, azaz ebben megtalálható az utolsó N állapot.
```cpp
for (int i = 0; i < container[0].get()->rooms.length(); i++)//Ciklus végig a szobákon
{
    auto index = container.size() - N; //Megjelenítendő utolsó N adat első elemének helye
    
    QVariantList ll = QVariantList{};//Átmeneti QVariantList típusú változó
    for(; index != container.size(); index++) //Ciklus végig az utolsó N bejegyzésen
    {
        float temp = container[index].get()->rooms[i].temperature; //Egy érték kinyerése
        ll.append(QVariant::fromValue(temp)); //ll lista feltöltése  1. dimenzió
    }
    l << QVariant::fromValue(QVariantList(ll)); //Az ll lista hozzáfűzése az l listához: 2. dimenzió
}
roomTemperaturesQML = l; // a 2D lista másolása az átadni kívánt változóba
```
* Átadás a QML környezetnek `` roomTemperatures `` néven:
```cpp
qmlContext.setContextProperty(QStringLiteral("roomTemperatures"), QVariant::fromValue(roomTemperaturesQML));
```
* A QML oldalon az ismert módon érjük el a tömb elemeit:
```cpp
var T = graphTemperatures[i][j];
```

## Kommunikáció a QML oldalról a CPP oldalnak
* Ezt könnyen megtehetjük a "signal & slot" mechanizmussal. A cpp oldalon definiáljuk a QML oldalról meghívandó slotot pl.:
```cpp
public slots:
	void setHeatingSetPoint(int value);
```
* A QML oldalon létrehozunk egy signalt:
```cpp
signal setHeatingSetPointCpp(int value);
```
* A QML ojektumunk, melyet majd meg kell keressünk a CPP oldalról `` <objectName> `` néven:
```cpp
Item
{
	objectName: "controlPanel"
	...
	//Ezen objektumon belül található majd az a slider pl. mely az adott értéket változtatni akarja.
}
```
* Összekötés a cpp slottal:
```cpp
QQuickItem *controlPanel = FindItemByName(rootObject,QString("controlPanel")); //Megkeressük a QML "controlPanel" objektumát
if (controlPanel) //Ha megtaláltuk összekapcsoljuk a QML signalt a cpp slottal:
	QObject::connect(controlPanel, SIGNAL(setHeatingSetPointCpp(int)), this, SLOT(setHeatingSetPoint(int)));
else //Ha nem, sírunk...
	qDebug() << "HIBA: Nem találom a controlPanel objektumot a QML környezetben.";
```
* A "slider" elem blokkján belül létrehozunk egy JS függvényt, mely az érték megváltozásakor meghívja a cpp oldalon regisztrált signalt:
```cpp
Slider
{
	function setHeating() {setHeatingSetPointCpp(heatingSlider.value)} //JS függvény
	id:heatingSlider
	onValueChanged: setHeating() //JS függvény meghívása, mely a CPP signalt aktiválja
}
```
* Az így meghívódott cpp oldali `` setHeatingSetPoint `` függvényünk tetszőlegesen használhatja az átadott értéket.

## Grafikonok rajzolása qml oldalon
Ha nagyon nincs ötlete az embernek, hogyan lehet qml-ből grafikont rajzolni, akkor érdemes szétnézni a példák között. A Qt Creator Welcome felületéről is elérhetőek gyorsan, az Examples gomb alatt. Ezek közül mi a Qml Weather és Qml F1 Legends példa alapján készítettük el a saját grafikonunkat. Ebben a snippet-ben a ChartView általunk felfedezett lehetőségeit szeretnénk bemutatni.

#### ChartView
Egyszerűen lehet grafikont rajzoltatni vele, mi a hőmérséklet kijelzésére használtuk. Az idő előre haladtával a grafikon is változott, mindig az utolsó pár értéket jelenítette meg.
```cpp
ChartView
{
    id: chartView
    animationOptions: ChartView.SeriesAnimations
    antialiasing: true

    ValueAxis{
        id: valueAxisY
        min: 10
        max: 40
        titleText: "Temperature [&deg;C]"
    }

    LineSeries {
        id: tempNappali
        axisX: valueAxisX
        axisY: valueAxisY
        name: "Nappali"
    }
// ...
```
* `` ValueAxis `` segítségével megadhatjuk, hogy mi legyen a tengelyek neve, a tengelyen mi legyen a minimális és maximálisan kijelzett érték. A minimum és a maximum menet közben dinamikusan változtatható. Példáil: `` chartView.axisY().max = 30 ``
* `` LineSeries `` segítségével fogjuk kezelni a kirajzolandó adatokat. Az `` id `` azonosítja a vonalat, a `` name `` pedig legendnél jelenik meg.
* `` tempNappali.append(currentIndex,i1); `` sorral tudunk értéket hozzáfűzni a grafikonunkhoz. A `` currentIndex `` mondja meg, hogy az x tengely melyik értékéhez tartozzon az `` i1 `` változóban megadott érték.
* A grafikon mozgatását úgy oldottuk meg, hogy az x tengelyhez tartozó minimum és maximum értékeket változtattuk, így mindig csak az utolsó 45 érték volt megjelenítve.
```cpp
if (currentIndex > 43) {
        chartView.axisX().max = currentIndex + 1;
        chartView.axisX().min = chartView.axisX().max - 45;
    } else {
        chartView.axisX().max = 45;
        chartView.axisX().min = 0;
    }
```

## Befejezésül
A házi feladattal rendkívül sokat tanultunk, nem csak QML és CPP programozás terén, de abban is jelentős tapasztalatra
tettünk szert, hogyan kell megfelelően struktúrált kódot készíteni és hogyan kell azt átláthatóan ledokumentálni. Reméljük a leírtakkal segíteni tudtunk mindazoknak, akik még az első lépéseket teszik a házi feladat megoldása során.