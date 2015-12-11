

# Alkalmazásfejlesztés házifeladat tapasztalatok
## Tapasztalatok
### A csapatban fejlesztésről

Mivel a feladatot három fős csapatban kellett elvégeznünk a félév során, így ahhoz, hogy hatékonyan tudjunk haladni, igyekeztünk jól elkülöníthető részfeladatokat találni. A MVC tervezési elv alapján szerettük volna megírni az alkalmazásunkat, így végül e szerintpróbáltuk  kialakítani a feladatainkat.
Így mindenki a fejlesztés nagy részében saját branchen, egymástól nagyjából függetlenül tudott dolgozni, kihasználva a verziókezelés előnyeit.

Féléves elfoglaltságaink miatt csak meglehetősen későn kezdtük el az éredemi munkát, viszont a tanult fejlesztési módszereket alkalmazva,
gyorsan, könnyen együttműködve haladtunk, így a rövid idő alatt megírt nagyobb mennyiségű kód is letisztult, szép tudott maradni.


### A tervezési mintákról

A feladat első, az alkalmazás tervezésével töltött részében úgy álltunk hozzá a tervezési mintákhoz, hogy megpróbáltuk az egész feladatunkat, az alkalmazás visekledését úgy kialakítani, hogy minél több tervezési minta felhasználására nyíljon lehetőségünk. Ez viszont sokszor fölösleges, erőltetett megoldásokat eredményezett volna.
A tervezési mintákkal, illetve a feladatunkkal kicsit jobban megismerkedve, feltérképezve a lehetőségeket, sikerült az aktuális feladatban olyan területeket találni, amikre adta magát egy tervezési minta használata.


### A GUI tervezésről

Az egyik legérdekesebb részfeladatnak a felhasználói felület megfelelő kialakítását tartottuk, tapasztalatlan QML és Cpp fejlesztőként - korábbi Androidos xml tapasztalatokal -
kezdetben meglehetősen nehézkes volt megfelelően összeilleszteni a két oldalt, illetve a fellépő hibákat megkeresni. A Qt kifejezetten jó online dokumentációját átböngészve azonban a hibákat több-kevesebb idő alatt, de mindig sikerült megoldani.

![UI](images/ui.JPG "Felhasználói felület")

## Problémák
### QML által támogatott adattípusok
Grafikonok rajzolása során futottunk bele abba a hibába, miszerint float típusú listát szerettünk volna QML oldalról elérni, de ez sokadik próbálkozásra sem
tűnt úgy, hogy működőképes lesz. Alapértelmezetten át kellett volna alakítania a float típusunkat QML számára is értelmezhető real típussá, végül a problémát
float helyett qreal típusú lista használatával sikerült megoldani.

### QByteArray-float konverzió

A robot státuszát frissítő üzenet feldolgozása során találkoztunk a következő hibajelenséggel. A státuszüzenet tartalmaz float típus adatokat is, melyek fogadása bájtonként történt. Az adatok fogadása, illetve a konverzió a következőképpen történt.
```
QByteArray bytes;
for(int j = 0; j < 4; j++) {
    inStream >> byteIn;
    bytes.append(byteIn);
}

float value = bytes.toFloat();

```
Ennek az eredménye azonban folyamatosan 0-kat adott, pedig QByteArray  `qDebug() << "Hex values: " << bytes.toHex();` hívással kiíratott értékeket megfigyelve az üzenet helyesen megérkezett.

Az érdekes hibajelenség alternatívájaként a következő magától értetődő, "C stílusú" megoldás született,
```
float value;
quint8* bytePtr = (quint8*) &value;

for(int j = 0; j < 4; j++) {
    inStream >> byteIn;
    bytePtr[j] = byteIn;
}
```
amely hibátlanul visszaadta a beérkezett float típusú üzenetdarabot.


A hiba okára azóta sem sikerült rájönnünk (nem nagy hiba, nagyon sokat nem is kerestük az okát, hiszen könnyű alternatív megoldásokat adni), mindenesetre érdekes jelenség, és a Qt dokumentációjában sem találtuk nyomát.


![Alt Text](images/logo.png "git•egylet")

<small>Szerzők: Divald Viktor, Nagy Bálint Máté, Szabó Oszkár</small>
