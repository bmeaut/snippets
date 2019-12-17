---
layout: default
codename: AlkFejlHf41
title: 404!GroupNameDoesNotExist csapat tanulságai
authors: Pádár Gergely, Knyihár Gábor, Amairi Olivér Fádi
tags: alkfejl afhf skipfromindex
---

# Néhány problémás szituáció, amire mi az alábbi megoldásokat találtuk

## QList<QString> vs. QStringList
`QList<QString>` nem ugyanaz mint `QStringList` és baromira nem fog működni `ListView`-val QML-ben.
Részletesen: ha valaki nem csak állapot objektumból akar listát, hanem simán stringek listáját kiíratni QML oldalon, akkor a logikussal ellentétben nem `QList` adattípusát kell megváltoztatni `QString`-re, hanem az egészet `QListString`-re cserélni, mert minden hiba nélkül fog úgy is fordulni, csak nem csinál semmit.
Delegateben ha a `QStringList` tartalmát akarod kiíratni, akkor nem `model`-re kell hivatkozni, hanem `modelData`-ra.

## QML Property változtatása kódból
Amennyiben QML object propertyjét akarjuk futásidőben változtatni, először az adott objecthez adjunk egy olyan propertyt, hogy `objectName`, mert csak ez alapján lesz kereshető c++-ből. Ezek után (az STV-t alapul véve) az `EventHandler` osztályba adjuk meg slotokat, amiket triggerelve akarjuk végezni a property módosításokat, adjunk hozzá egy `QList<QObject*>rootObjects` változót és a hozzá tartozó set függvényt. Innentől a korábban definiált slot függvényekben megírhatjuk a propertymódosításokat a következő módon:
Először a következő sorral megszerezzük a keresett objektumot:
```cpp 
QQuickItem *item2 = rootObjects.at(0)->findChild<QQuickItem*>("objectnamehere");
```
Ezután egy if-el ellenőrizzük valid objektumot kaptunk-e vagy null-t és állítsuk be a propertyt: 
 ```cpp
 item2->setProperty("color", color);
 ```
Mindenképpen állítsuk be a `rootObjects`-et a publikus set függvényét hívva az application osztályban a `rootObjects`-et átadva

## QML felületről szöveg (vagy más szövegesen megadható adat pl double) beolvasása:
Dokumentációban nagyon sokféle szövegbeviteli mezőt lehet találni, tapasztalat alapján a legjobb ezek közül a TextField. Kiemelten hasznos, hogy adható hozzá validator, azaz csak megadott feltételek teljesülése esetén fog elsülni az `onAccepted`, rossz bevitt adat esetén nem. Fontos a validatornál a `locale:"en"` vagy `"hu"` beállítása az ominózus . vagy , kérdés miatt. `onAccepted`-hez adjunk meg egy függvényt átadva neki a `textfield.text`-et. Legyen ennek a függvénynek a neve: acceptedTextField. A main.qml-ben adjunk hozzá egy új signalt `acceptedTextFieldCpp(string msg)` formában, majd az eseménykezelő továbbhívásoknál az alábbiakat: 
```cpp
onAcceptedTextField:{acceptedTextFieldCpp(msg);}
```
C++ oldalon (praktikusan az event handler osztályban) definiáljunk egy `void doThings(QString);` slot-ot, amihez az application osztályban hozzákötjük az `acceptedTextFieldCpp`-t, mindkettőnél kiírva a `(QString)` paramétert. Már csak implementálni kell a doThings-t és használhatjuk is a string-ként megkapott adatot.

## QML szebb design készítése
A QML tartalmaz előre definiált design-okat, melyeket szabadon használhatunk. Ennek következtében az alkalmazás felülete sokkal inkább modernnek tűnik, és nem az alapértelmezett Windows-os elemeket használja. Ezek a stílusok közül, mi az Imagine nevezetűt használtuk. Erről részletesebben itt lehet olvasni: 
[Imagine Style](https://doc.qt.io/qt-5/qtquickcontrols2-imagine.html)
A téma alkalmazásához nem kell mást tennünk, mint a main.cpp fájl-ba a `main` függvénybe alábbi sorokat beszúrni:
```cpp
#include <QQuickStyle>

QGuiApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
QQuickStyle::setStyle("Imagine");
```
Fontos, ennek még az `Application` példányosítása előtt meg kell történnie.

Előfordulhat, hogy a QTCreator a fenti include-ot nem fogja tudni értelmezni. Ilyenkor annyit kell tenni, hogy beszúrjuk a következő sort a project (.pro) fájlba:
```
QT += quickcontrols2
```
Ezután egy Rebuild All, és nem fog többet hibát jelezni.

A részletes leírást a stílusokról és a többi stíluslapokról [itt](https://doc.qt.io/qt-5/qtquickcontrols2-styles.html#using-styles-in-qt-quick-controls) lehet elolvasni.

