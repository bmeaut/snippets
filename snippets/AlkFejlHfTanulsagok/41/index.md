---
layout: default
codename: AlkFejlHf41
title: 404!GroupNameDoesNotExist csapat tanácsai & tanulságok
authors: Pádár Gergely, Knyihár Gábor, Amairi Olivér Fádi
tags: alkfejl afhf skipfromindex
---

# Néhány problémás szituáció, amire mi az alábbi megoldásokat találtuk

## QList<QString> vs. QStringList
`QList<QString>` nem ugyanaz mint `QStringList` és baromira nem fog működni `ListView`-val
`Delegateben` ha a `QStringList` tartalmát akarod kiíratni, akkor nem `model`-re kell hivatkozni, hanem `modelData`-ra

## QML felületről beolvasott szöveget átvinni cpp oldalra
A QML signalnak kell tartalmaznia és a cpp slot kapja meg mint paraméter, de a QML továbbhivatkozásnál tovább kell küldeni.

## QML property változtatása kódból
Amennyiben QML object propertyjét akarjuk futásidőben változtatni, először az adott objecthez adjunk egy olyan propertyt, hogy `objectName`, mert csak ez alapján lesz kereshető c++-ből. Ezek után (az STV-t alapul véve) az `EventHandler` osztályba adjuk meg slotokat, amiket triggerelve akarjuk végezni a property módosításokat, adjunk hozzá egy `QList<QObject*>rootObjects` változót és a hozzá tartozó set függvényt. Innentől a korábban definiált slot függvényekben megírhatjuk a propertymódosításokat a következő módon:
Először a ```QQuickItem *item2 = rootObjects.at(0)->findChild<QQuickItem*>("objectnamehere");``` sorral megszerezzük a keresett objektumot. Ezután egy if-el ellenőrizzük valid objektumot kaptunk-e vagy null-t és állítsuk be a propertyt `item2->setProperty("color", color);`
Mindenképpen állítsuk be a rootObjects-et a publikus set függvényét hívva az application osztályban a rootObjects-et átadva

## QML felületről szöveg (vagy más szövegesen megadható adat pl. double) beolvasása:
Dokumentációban nagyon sokféle szövegbeviteli mezőt lehet találni, tapasztalat alapján a legjobb ezek közül a TextField. Kiemelten hasznos, hogy adható hozzá validator, azaz csak megadott feltételek teljesülése esetén fog elsülni az `onAccepted`, rossz bevitt adat esetén nem. Fontos a validatornál a `locale:"en"` vagy `"hu"` beállítása az ominózus . vagy , kérdés miatt. onAccepted-hez adjunk meg egy függvényt átadva neki a textfield.text-et. Legyen ennek a függvénynek a neve: acceptedTextField. A main.qml-ben adjunk hozzá egy új signalt `acceptedTextFieldCpp(string msg)` formában, majd az eseménykezelő továbbhívásoknál az alábbiakat: ```onAcceptedTextField:{acceptedTextFieldCpp(msg);}```
C++ oldalon (praktikusan az event handler osztályban) definiáljunk egy `void doThings(QString);` slot-ot, amihez az application osztályban hozzákötjük az `acceptedTextFieldCpp`-t, mindkettőnél kiírva a (QString) paramétert. Már csak implementálni kell a doThings-t és használhatjuk is a string-ként megkapott adatot.