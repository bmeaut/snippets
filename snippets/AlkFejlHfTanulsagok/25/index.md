---
layout: default
codename: AlkFelHf25
title: Csapatnev csapat tanulságai
tags: alkfejl afhf skipfromindex
authors: Katona Attila Mihály, Láncz Gergő, Sárközy Balázs
---

<body>
<h1>Csapatnev csapat tanulságai</h1>


<h2>Mikor kezdjük el a házit?</h2>
<p align="justify">Mi a félév első felében nem nagyon haladtunk a házival, mert arra vártunk, hogy a releváns anyagrészek lemenjenek előadáson. Ez azért volt nagy hiba, mert pont akkor lehetett volna könnyen megírni. Igazából, ami lényeges a házi elkezdéséhez, az a tárgy Github oldalán megtalálható rengeteg jó példa. Ha  eredetileg abból indultunk volna ki és nem az előadásokra vártunk volna sokkal előbb befejezhettük volna a feladatok nagyját. 
Egy példa, hogy a robot és Qt program közötti kommunikációra konkrétan megtalálható a megoldás a Simple Telemetry Visualizer projektben. Az előadó mondta is, hogy ezt lehet használni, amikor odaértünk.
</p>

<h2>Feladatok elosztása</h2>
<p align="justify">Hasznos volt a feladatok elkezdése előtt alaposan átgondolni, hogy a három emberre hogyan érdemes szétosztani a feladatokat. Akkor jó a elosztás, ha a külön részek valamilyen előre definiált interfészen fognak kommunikálni, amiről a két rész fejlesztője megállapodott. Ez azért nagyon fontos, hogy utána ne kelljen egymás commitolásaira várni, hogy a másik dolgozni tudjon. (Mi néha beleestünk ebbe a hibába, de azért a nagyobb feladatoknál sikerült megoldanunk). Ekkor lehet a leghatékonyabban dolgozni 3 külön branchen.
</p>

<h2>Git verziókövetés</h2>
<p align="justify">A verziókövetéssel páran a projekt keretein belül ismerkedhettünk meg tüzetesebben. Egyébként ez talán a leghasznosabb feature, amit a hallgató a tárgy során elsajátíthat, ugyanis majdnem minden céges környezetben használnak valamilyen verziókövető rendszert a fejlesztéshez. Igyekeztünk minél több branchen dolgozni párhuzamosan, és kihasználni a git által nyújtott lehetőségeket. Egyébként a GitTortoise keretprogramot használtuk, amelynek GUI felülete a munkát nagyban könnyítette.
</p>

<h2>Működik a console.log()</h2>
<p align="justify">Tekintve, hogy JavaScriptről van szól, érdeme lehet a console.log()-ot használni. Csak sok szenvedés után jöttem rá, hogy ezt tudom használni QML oldali hibakeresésre.
</p>

<h2>W3Schools</h2>
<p align="justify">Főleg a grafikon rajzolásánál ez az oldal nagyon hasznosnak bizonyult. Itt például különböző alakzatok kirajzolására lehet sok példát találni és a legjobb, hogy ki is lehet őket próbálni saját módosításokkal. Ez nem keveset segített, amikor nem értettem miért ellenkező irányba forog az általam kirajzolt objektum.
</p>

<h2>QML és timer</h2>
<p align="justify">A JavasScript-es „new Timer()” megoldás időzítő dinamikus létrehozására közvetlenül QML-ből nem működött. A külön ütemezendő feladatokhoz szükség volt manuálisan definiált timerek beillesztésére:
Timer 
{
	id: timer0 
}
Például. Ezek így már működtek rendesen.
</p>

<h2>Öntesztelés</h2>
<p align="justify">Az öntesztelés a már kész parancsok kiadása, valamilyen sorrendben bizonyos késleltetések beiktatásával. Itt számunkra a az bizonyult járható útnak, hogy ez QML oldalról valósítottuk meg, és időzített callback függvényeket írtunk a parancsok küldésére.
</p>

<h2>QML GUI készítés</h2>
<p align="justify">A grafikus felület elkészítése során sok problémát okozott a lehelyezett elemek átskálázhatósága. Sok esetben az utasítások kiadásának hatására nem történt semmi (vagy teljesen más, mint ami várható lett volna), így sok időt vett el ennek a feladatnak a megoldása (pontosan hová kell betenni az anchor. és a Layout. változókat).<br />
A megjelenés megtervezésekor először nem gondoltunk arra, hogy a bal felső sarokba helyezett elem a legkevésbé skálázható (a kód implementációjából kifolyólag), így a GUI-t újra kellett tervezni megvalósítás közben.<br /><br />
Az eredeti terveink szerint a drón előző pozícióit egy fokozatosan halványodó vonallal ki szerettük volna jelezni, azonban a végeredmény esztétikailag megkérdőjelezhető volt, így fölöslegesnek találtuk a meglétét.
</p>

<h2>A grafikus ábrák elkészítése</h2>
<p align="justify">Ami még fejtörést okozott a GUI fejlesztése során, az a grafikus ábrák rajzolása. A 2D Canvas context-et használva a rajzolás egy igen bonyolult művelet, amely során minden pont helyét és méretét pixelenként kell megfontolni. Így akár egy drón kirajzolása is rengeteg időt vehet igénybe. 
</p>

<h2> .qml fájlban történő módosítás fordítása </h2>
<p align="justify">Amikor a GUI részét terveztük a programnak feltűnt, hogy a qml oldali fájlokat ha változtatjuk, a fordító nem veszi észre a változásokat, így a korábban lefordult állapot kerül futtatásra. Ahhoz hogy újra kelljen egy adott qml fájlt fordítani, az egész projektet Rebuildelni kellett. Gyorsan rájöttünk, hogy ez így túl időigényes, és szeretnénk a fordítási folyamatot gyorsítani. Egymástól független két síkon is sikerült megközelítenünk a problémát, így két megoldást is kaptunk. Az egyik (a gyorsabb módszer), hogy futtatjuk a qmake-et minden alkalommal, amikor változtatást eszközöltünk qml oldalon. A másik (kicsit lassabb) módszernél rájöttünk arra, hogy ha változtatjuk a .qrc fájlt, akkor a qml fájlok mindenképpen újragenerálódnak. Így egy apró script írásával (ami minden qml változás esetén egy entert helyez a .qrc megfelelő sorába) le tudtuk fordítani a projektünket secperc alatt. 
</p>

<h2>CPP oldali hibaüzenetek</h2>
<p align="justify">A szimulátor C++ kódjának elkészítésekor a Qt Creator fejlesztőkörnyezet amellett, hogy a nem igazán segítőkész a hibák és warning-ok terén, néha kifejezetten félrevezetőnek bizonyult. Erre egy jó példa a RobotStateHistory fejlesztésénél egy #include elmaradása, amelyre a fordító furcsa hibaüzenetekkel reagált (ráadásul nem is az eredeti fájlban, hanem 2 fájlon keresztül közvetetten).
</p>

<h2>Unit tesztek</h2>
<p align="justify">Unit tesztek írása a fent lévő példa alapján pofon egyszerűnek tűnt, úgy gondoltuk azt a végére hagyjuk, mert úgyis a legkönnyebb része a feladatnak. Hát ez utólag kiderült, hogy nem így van. Akkor lehet jól tesztelni egy modult, ha az jól meg is van struktúrálva. Ez nem minden esetben teljesült, így gyakorlatilag a tesztelés azért is tanulságos, mert nem csak az esetleges modulhibák kerülnek felszínre, hanem a struktúrálatlanság is. Ezeket sikerült egyébként a tesztek során szépen javítanunk.<br /><br />
Metódusok teszteléséhez szerencsésebb, ha a függvénynek van visszatérési értéke. Ez is hiányzott, általában void-dal tértünk vissza mindenhol. Így a teszt kedvéért (illetve a struktúráltság kedvéért is) például a RobotProxy közvetítő függvények visszatérési értékei egy úgynevezett RobotStateWrapper osztályra lettek átírva. Nyilván egyszerűbb lett volna RobotState típussal visszatérni, de mivel ahhoz szükséges a copy konstruktor megléte, és a RobotState a Qobject osztályból származik, így ez a kettő kizárja egymást ugyanis Qobject osztálynak nem lehet copy konstruktora. Tehát maradt a RobotStateWrapper csomagoló osztály, amely használata kényelmes a teszteknél is, mivel még az == operátorját is sikerült felüldefiniálni.<br /><br />
Még egy megjegyzés a unit teszt projekt létrehozásával kapcsolatban. Először megpróbáltuk hierarchikus projektként létrehozni a projektet, tehát egy subdir project-ben lett volna egyben a unit teszt és a simulátor is. A mappák átrendezését, és a két projekt meglétét a korábbi repoban a git nagyon nehezen kezelte, így kevés próbálkozás után maradtunk a kevésbé szofisztikált, de mindenképpen git-kompatibilis megoldásnál, miszerint két külön projektünk van. 
Egyébként a UnitTest fájljai az eredeti Simulator projekt fájljaira referálnak, így ténylegesen tudják követni a Simulatorban történt változásokat. 
</p>
<h3>Szerzők:</h2>
<p align="justify">
Béres András, Mészáros László, Molnár Gábor
</p>

</body>
