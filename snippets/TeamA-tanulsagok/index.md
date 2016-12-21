# TeamA csapat: házi feladat tanulságok


A Qt házi megírása során több izgalmas jelenséggel is találkoztunk, amelyekre érdemes máskor odafigyelni.

### 0) Mindenek előtt: milyen projektet készítsünk?
Egyszerű a válasz: ha szükségünk van grafikus kezelőfelületre (GUI), akkor QuickApplication típusú projektet hozzunk létre, semmiképp sem ConsoleApplication-t, mert az nem támogatja a *.qml fájlokból való építkezést.

### 1) Ne engedjünk a QT Designer nézet csábításának. (*.ui fájl)
Amennyiben felfedezzük, hogy van egy grafikus kezelőfelület rajzoló eszköz a QtCreatorban, amellyel drag'n'drop módon "pikk-pakk" megépítünk egy GUI-t, gyorsan feledkezzünk is el róla. Sokkal egyszerűbb az órán tanultak és a mintaprogramok alapján qml fájlokban megírni egy kezelőfelületet. Nem lesz abszolút koordinátás elhelyezés, minden elem úgy fog kapaszkodni a kis kapmóival (anchors) a megfelelő containerhez, ahogy mi akarjuk. Mi adunk azonosítókat az objektumainknak, valamint mi rendelünk hozzájuk signalokat és eseményeket, nem pedig a designer tool. Így nem fognak elkeveredni, valamint nem lesznek láthatatlan "fantom" objektumaink, melyek misztikus módon, másolások során kerültek a felületre. Az ott megrajzolt felületből is generálható qml kód, azonban annak átdolgozása több időt vett igénybe, mint megírni teljesen nulláról a GUI kódját.

### 2) QDataStream, avagy a 16 bites karakterek esete
Amennyiben olyan robothoz készítünk programot, amely 8 bites karaktereket használ és szöveges log-ot küld, valamint szöveges parancsokkal vezéreljük, érdemes QTextStream-et használni QDataStream helyett. Így a robot oldali karakteres vezérlésen nem kell módosítani.

### 3) "Késik a stream!?"
Nem kell megijedni, ha a streambe csak egy lépéssel eltolva kerülnek bele az adatok. Azért van, mert hiányzik a stream FLUSH() az elem berakása után. A streambe helyezendő adat először egy köztes tárolóba kerül, melyet csak a következő elem berakása késztet arra, hogy továbbadja az adatot a folyamnak. Amennyiben, meghívjuk az elem berakása után rögtön a stream-re a flush() függvényét, akkor kipucolja ezt a tárolót és a tartalmát kiírja a folyamba. Olyan, mintha fájlba írnánk, az esetben is van egy köztes tároló, melyet ki kell írni még a fájlba a kívánt eredmény elérése érdekében.

### 4) A qml csak a Q_PROPERTY-ket látja a C++ból
Amennyiben C++ oldali változókat szeretnénk láthatóvá tenni a qml oldal számára, a  qmlContext.setContextProperty metódussal megtehető. Igen ám, de addig nem fog működni, amíg ezekre a változókra (esetünkben általában egy osztály tagváltozói) nem állítottuk be a Q_PROPERTY-ket. Érdemes erre figyelni, mivel még a hibaüzenet sem beszédes az ezt elmulasztott esetekben, így nehéz rájönni, miért nem sikerült összekötni a két oldalt.

### 5) A qml oldali property aliasok
Amennyiben valamilyen tulajdonságát szeretnénk qml-ben állítani a GUI elemeknek, definiálni kell külön property aliasokat számukra, hogy lássák egymást az elemek, ill. a különböző függvények.

### 6) "Ne veszítsük el a fejünket"
A fejlesztés során mindig Pull-oljuk a teljes GIT repositoryt, mivel könnyen elhagyhatjuk lokálisan például a master branchet, és a munka végeztével rengeteg konfliktussal találhatjuk szembe maguknat.

### 7) Vannak dolgok, melyek nem párhuzamosíthatók
Amennyiben a feladat leadási határideje hirtelen holnap van, érdemes átgondolni a munkálatok sorrendi függőségeit. Nem lehet párhuzamosan fejleszteni, ugyanarra a részre unit tesztet írni, valamint a még változó osztályokról UML diagramot készíteni. Fontos a *tervezés* ütem*tervének* meg*tervezése*.

Szerzők: Farkas Péter, Prőhle Orsolya, Szilágyi Ábrahám
