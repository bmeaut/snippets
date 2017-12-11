---
layout: default
codename: AlkFejlHf20
title: Unity csapat tanulságai
tags: alkfejl afhf skipfromindex
authors: Bóka Jenő, Kovács Péter Szabolcs, Medgyesi Zsolt
---

# Alkalmazásfejlesztés házifeladat tanulságok

0. **Fejlesztőkörnyezet beüzemelése**
 * Érdemes a félév során minél hamarabb beüzemelni és összeegyeztetni a csapattársakkal a fejlesztőkörnyezetet. Ha szerencsés az ember, ez egy pár perces feladat, ha nem, akkor előfordulhat, hogy az effektív fejlesztéssel összemérhető ideig tart. Bárhogy is legyen, nem árt minnél hamarabb túlesni rajta. A továbbiakban egy lista, a teljesség igénye nélkül, a nálunk felmerült beüzemelési problémákról.

1. **Vírusírtó**
 * Telepítés és futtatás közben többször is belefutottam a vírusírtómba (Bitdefender 2018). Érdemes figyelni, hogy milyen webhelyeket/alkalmazásokat blokkol,
milyen file-okat karanténoz. Célszerû olyan helyre csinálni a projektet, amit nem akar nagyon megvédeni és érdemes ezt a helyet is hozzáadni a kivételekhez.
2. **Qt Telepítés** 
 * Ne felejtsd el a megfelelõ compiler-t is telepíteni.
Ha MinGW-t használsz, akkor telepítésnél a `Tools` alatt (verzióra figyelni).

3. **Compiler-t a PATH-hoz**
 * Ne felejtsd el hozzáadni a compilert a PATH-hoz
ha Qt-val együtt telepítetted akkor a `Qt/Tools/mingw-verzó/bin`
 * Hasznos cucc: [PathEditor.exe](https://patheditor2.codeplex.com/)

4. **DLL-ek importálása**
 * Ha build-eltél, a `project/build/debug` mappábá rakd be a használt dll-eket.
 * windeployqt a Qt dll-ekhez(`Qt/verzió/mingw-verzió/bin`)
 * Többi hiányzó dll-hez: [DependencyWalker](http://www.dependencywalker.com/) (figyelni a hamisan talált hibákra)

5. **Qt Módosítás**
 * Ha valami ok folytán változtatni akartok valamit a Qt telepítésen, a teljes reinstall elõtt érdemes megpróbálni a *Qt Maintenance Tool*-t.

6. **Ha sehogy se akar összejönni...**
 * Ha véletlenül olyan helyzetbe kerülnél, hogy minden próbálkozásod ellenére sem akar működni a fejlesztőkörnyezet Windows alatt, akkor érdemes kipróbálni egy Linux virtuális gépen. A projekt során általunk használt fejlesztőeszköz ott is elérhető (*Git*, *QT Creator*, *Doxygen*, ...) és tapasztalataim szerint a különböző dependenciák feloldása is egyszerűbb.

7. **Git GUI**
 * Néha segít ha a fejlesztés során az ember grafikus formában is át tudja tekinteni a branch-eit/commit-jait, átláthatóbban látja a manuális merge-eket, vagy egyszerűen irtózik a command line gondolatától. Mi erre a *GitKraken* nevű programot használtuk, mert viszonylag jól használható, multiplatform és ingyenes.
 * Fontos megjegyezni, hogy egy trükkösebb Git-műveletet érdemesebb lehet command line-ban megcsinálni, mert úgy biztosabb az eredmény.

8. **QML frontend és C++ backend készítés**
 * A [mintától](https://github.com/csorbakristof/alkalmazasfejlesztes/tree/master/QmlControlKupac) eltérő módon is lehet a QML és C++ oldal között kapcsolatot létrehozni. Méghozzá úgy, hogy nem kell végigkeresni a QML osztályokat, az ős osztálytól kezdve név szerint.
  ![findItemByName metódus forráskódja](.\diagrams\findItemByName.png)
  * Ehelyett a QT egy kényelmes megoldást biztosít. Lehetőség nyílik arra, hogy a QML dokumentum belöltése előtt (amit a QQmlApplicationEngine végez), a QML fájlba bele tudjuk injektálni a C++ oszályunkat.
 Ehhez nem kell mást tenni, csupán létrehozni egy példányt a backend osztályunkból, majd a rootContext-be injektálni. Fontos, hogy csak ezután töltsük be a QML dokumentumot.
  ![QmlInjection forráskódja](.\diagrams\QmlInjection.png)
  * A backend oldalon nem kell mást tenni elkészíteni a setter (WRITE) és getter (READ) függvényeket, valamint a szignált amit emmitálunk megváltozáskor. Eztán a  Q_PROPERTY macro segtsévével regisztrálni ezeket a függvényeket.
  ![singnalsAndSlots regisztráció forráskódja](.\diagrams\singnalsAndSlots.png)
  * Fontos, hogy ne felejtsük el a setter metódusban kibocsájtani az sziglált!
  ![seter getter implementacio](.\diagrams\implementacio.png)
  * Eztán már a QML oldalon létre is jön a megfelelő nevű backend oszály. Nem szükséges példányosítani, és a szignálok bekötése is mertörtént. Egyszerűen csak használjuk.
  ![qml oldali implementacio](.\diagrams\qmlSide.png)
  * Ha bármelyik oldalon módosul egy property akkor az onChanged metódusok meghívódnak. Így automatikusan megvalósul a C++ és QML közötti szinkronizáció.
  
Készítette: Bóka Jenő, Kovács Péter Szabolcs, Medgyesi Zsolt
 
