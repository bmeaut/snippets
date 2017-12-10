# Tragacs csapat - tapasztalatok

***
* A QML fájlok nem fordulnak autómatikusan, csak akkor, ha a root / legfelső forrás változik, ezzel sokat lehet szívni. Ilyenkor célszerű a main.qml-ben egy Enter beírásával majd kitörlésével frissíteni a fájlt.
***
* A QtCreator teljes képernyős módban bugos: Ha kiteszem full screen-re, akkor nem lehet onnan kilépni belőle. Emellett a főmenüsorhoz tartozó legördülő menük sem jelennek meg, azaz nem lehet semmiféle beállítást eszközölni. Ebben az állapotban még az F11 sem segít, nem lehet kilépni, csak a program újraindításával, vagy egyéb trükközésekkel.
***
* A qml szerkesztésekor nem érdemes kizárólag a grafikus felületre, vagy a szövegszerkesztőre hagyatkozni. Számunkra az volt az optimális megoldás, hogy a grafikus szerkesztőben összeklikkelgettük a kinézetet: az elemeket és az elrendezést. Ezt követően lehet a paramétereket illetve a rétegeket a szöveges szerkesztőben kialakítani.
***
* A Qt - qml adattípusok tulajdonságaikban és kezelhetőségükben kicsit eltérnek a C, C++ - ben megszokottól. Erre érdemes odafigyelni amikor a különböző adatokat kapjuk a robottól/szimulátortól, amikor feldolgozzuk, illetve átadjuk a QML oldalnak.
***
* A mi protokollunk karakteres volt, ami bár először jó ötletnek tűnt, végül kiderült, hogy az adatok sorosítása illetve páruzamosítása karakteres esetben jóval bonyolultabb, illetve ez a kommunikációs vonalban is nem kis overhead-et eredményez (bár ez alapesetben nem okozott problémát, elképzelhető olyan eset, amikor nem elég az uart sávszélessége).
***
* Q_OBJECT hozzáadásakor osztályhoz szükséges virtuális függvény (vagy ha nincs, akkor destruktor) deklarálása, illetve a qmake-et újra futtatni kell.
***
* Kritikus helyzetekben praktikus fejből tudni a git parancsokat, mert ilyenkor a grafikus kliensekben biztos nem találjuk meg a megfelelő menüpontot.
***
* Érdemes lett volna először a SimpleTelemetryVisualizer által használt protokoll alapján tájékozódni, hogy hogyan érdemes a kliensprogram és a robot közötti kommunikációt megvalósítani, mielőtt kidolgoztunk volna egy karakter alapú protokollt.