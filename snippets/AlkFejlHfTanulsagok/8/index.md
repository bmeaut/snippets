---
layout: default
codename: AlkFejlHf8
title: Team B tapasztalatok (2016 ősz)
authors: Team B csapat (AlkFejl 2016 ősz)
tags: alkfejl afhf skipfromindex
---

### 1. QML build probléma

Sokszor belefutottunk abba a problémába, hogy a QML oldali módosításokat a build után nem érzékelte a Qt Creator.
Az egyik lehetséges megoldás – amit mi alkalmaztunk -  az, hogy a QML oldali módosítások után mindig clean-eljük és újrafordítjuk az egész projectet.
A probléma egyébként nem mindenkinél jött elő mindig.

### 2. A Qt adattípusok sorosításáról

Hogyan lehet soros vonalon kiküldeni különböző objektumokat? Pontosan milyen bájtokat küldünk ki,
amikor például egy Qt adattípust sorosítunk? A kérdésre a "serialize" kulcsszó adja meg a választ.
Mielőtt bármit is elküldenénk a vezérelendő eszköz felé - különösképp ha fizikai eszközről van szó és nem szimulátorról - érdemes utánajárni,
hogy a kiküldendő objektumok hogy sorosítják ki magukat és erre felkészíteni a beágyazott rendszerünk firmware-ét.\n
A következő linken megtalálható, hogy az alapvető Qt adattípusok hogyan sorosítják ki magukat,
azaz hogyan implementálták Qt-ben az adott osztályhoz tortozó „<<” operátort:
[http://doc.qt.io/qt-4.8/datastreamformat.html](http://doc.qt.io/qt-4.8/datastreamformat.html) \n
Mi először QString-ként próbáltunk adatokat kiküldeni a hardver egységünk felé és nem értettük,
hogy miért érkeznek „fura” bájtsorozatok a hardverhez. Sejtettük,
hogy a sorosításnál lehet valami amit figyelmen kívül hagytunk, ezért megnéztük az iménti linken található,
a Qt dokumentációjának ide vonatkozó részét , ahol rövid keresés után meg is található a dolog nyitja.
Nevezetesen arról van szó, hogy a QString adattípus sorosítása a „megszokott” 8 bites ASCII helyett,
UTF-16 kódolással történik, amire nem volt felkészítve a hardverünk.
Természetesen a problémát többféleképpen is áthidalhatjuk, mi például rövidrezárva a kérdést QString típusról áttértünk az egyszerű QbyteArray típus használatára.
Érdemes még megjegyezni azt is, hogy sorosításkor az említett típusok először mindig az adatvektor hosszát küldik ki 32 biten.
Ez egy hasznos kényelmi funkció, hiszen így a vevő oldalon mindig tudjuk, hogy pontosan hány adatbájtot kell fogadnunk egy egy adatcsomag esetében.

### 3. A dokumentáció készítését megkönnyítő szoftverek

Egy jó szoftver nagyon meg tudja könnyíteni a különböző diagramok szerkesztését, rajzolását.
Mivel nekünk még nem sok tapasztalatunk volt UML diagramokkal kiegészített dokumentációk készítésében, ezért először a feladathoz megfelelő programo(ka)t kellett megkeresnünk.
Bár elsőre nem tűnnek bonyolultnak ezek az ábrák, azt gondolhatnánk, hogy bőven elég egy „paint” is hozzájuk, azonban az ilyen "ekecs" megoldásokkal a munka nagyon lassú és szenvedős tud lenni,
főleg ha nem csak egy-két diagramot kell elkészítenünk. A program, amivel végül mi készítettük a dokumentáció ábráit , a Microsof Visio, melyet az egyetem hallgatói ingyenesen letölthetnek az MSDNAA szerverről.
Ez egy általános diagram készítő program, ami különböző „modulokból” épül fel, a különböző diagram típusok szerint.Ezeket igen sokrétűen tudjuk felhasználni összetett információk megjelenítésére, vizualizálására.
Amire nekünk elsősorban szükségünk volt az az osztálydiagram és a szekvenciadiagram rajzoló modul. Osztálydiagram szerkesztő alapesetben is része a Visio 2016-nak, de a szekvencia diagramok rajzolásához mi egy addonként letölthető template-et használtunk, ami a következő linken elérhető:   
[http://www.softwarestencils.com/uml/](http://www.softwarestencils.com/uml/)

A template telepítésének menete az alábbi:

    1.    Tömörítsük ki a letöltött fájlokat egy tetszőleges könyvtárunkba (mindegy, hogy hová).
    2.    Indítsuk el a Microsoft Visio-t, majd navigáljunk a File/Options/Save menüpont alá.
    3.    Itt illesszük be a fájljainkhoz tartozó elérési utat a „Default personal templates and location” mezőbe, majd klikkeljünk az OK-ra.
    4.    Ezek után, ha új munkalapot nyitunk meg a Visioban (File/New),  a telepített template meg fog jelenni a PERSONAL tab alatt.
    5.    Válasszuk ki a template-et és máris használhatjuk az UML diagram rajzoló szolgáltatásait.

### 4. QObject, mint ősosztály

Valószínűleg a többség számára nyilvánvaló, hogy miért kell a saját osztályainkat a QObject-ből származtatni,
mi azonban mégis belefutottunk abba, hogy ezt elfelejtettük, így nem tudtuk használni a Qt Signals & Slots mechanizmusát.
A származtatást két okból is célszerű elvégezni: egyik a már említett Signals & Slots, másik pedig a memóriakezelés.
A szülő megszűnésekor a destruktorában automatikusan felszabadulnak a gyerekei is.
("When you create a QObject with another object as parent, the object will automatically add itself to the parent's children() list. The parent takes ownership of the object; i.e., it will automatically delete its children in its destructor.")
És természetesen ne felejtsük el a Q_OBJECT makrót sem!
