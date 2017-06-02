---
layout: default
codename: AlkFejlHf12
title: SZPP csapat tanulságai
tags: alkfejl afhf skipfromindex
authors: SZPP csapat
---

## 1. Adatok megjelenítése grafikusan

A vonalszenzor adatainak megjelenítése során egy új qml objektumot hoztunk létre, amelynek egyik paramétere egy tömb, ami a szenzorok értékeit tartalmazza. A megjelenítést aszerint szerettük volna ütemezni, hogy a grafikus felület akkor frissüljön, amikor az adatokat tartalmazó tömb is frissült. Azt tapasztaltuk, hogy a "dataChanged" metódus csak akkor hívódik meg, ha a teljes tömb felülíródik. Amennyiben csak egy elemét változtatjuk, a metódus nem hajtódik végre.
Az egyes grafikus megjelenítőket úgy készítettük el, hogy ezek paraméterként kapják meg a megjelenítendő adatot. Ennek a    tesztelésére remek lehetőséget nyújt a PropertyAnimation qml típus, amellyel bármilyen paramétert meg tudunk változtatni periodikusan.

## 2.  Qt fejlesztői környezet

Ahogy egyre több qml fájlt kezdett tartalmazni a projekt, úgy mindig újra kellett buildelni a teljes projektet, mielőtt tapasztaltuk volna a változtatásokat. Ha csak a “Run” gombra kattintottunk, akkor a véghezvitt változtatásokat nem láttuk.

A signal-slot mechanizmus használata során ügyelni kell az egyes signalok emittálására, ugyanis könnyedén okozhatunk végtelen rekurziót. Pl. ha egy slotban ugyan azt a signalt emittáljuk, mint ami meghívta a slotot, akkor elszáll a programunk, vagy ha egy mutexet lefoglalunk, majd emittálunk egy signalt, és az így meghívódó slot is ugyan azt a mutexet szeretné lefoglalni, akkor lefagy a program.

Mivel a mikrokontrolleren nem használunk double típusú változót, ezért Qt oldalon a QDataStream-ben be kell állítani a floatingprecision-t, különben csak double típusú változót fog olvasni és írni.

Ha egy qml objektum property-jének kezdőértékét a component.onload eseménykezelőben állítjuk be, akkor törlődik a property binding. Később hiába változtatjuk a hozzá kapcsolt változó értékét, a qml objektumban nem fog frissülni.

## 3.  Qt applikáció Android platformon

Az alkalmazást Android operációs rendszert futtató mobil eszközre terveztük, viszont a Qt adottságait kihasználva (pár kattintással bármelyik támogatott platformra lefordítható) PC-n is lehetett tesztelni, így rengeteg időt tudtunk spórolni, tekintve, hogy Androidra sokkal tovább tart lefordítani és telepíteni a szoftvert.

A kommunikáció során használtuk a QBluetooth osztályt, viszont ez az osztály különböző módon van implementálva minden platformon. PC-n valójában egy egyszerű soros portként működik, amelyben gyakran tapasztaltunk nem várt hibákat, fagyásokat, leállásokat. Pl. ha bontunk egy kapcsolatot, akkor egy bizonyos ideig várakoznunk kell újracsatlakozás előtt, különben elszáll a program.

Az Android NDK-ban még egy régebbi C++ fordító van, így az nem támogatta a C++14-es újdonságokat. Erre a következő megoldást
alkalmaztuk:
```cpp
static
#ifndef Q_OS_ANDROID
constexpr
#else
inline
#endif
```
DataType toggleArrayType(DataType t){...}

Erre azért volt szükség, mert használtunk olyan kódrészletet, amely a robotban és az alkalmazásban is ugyan az volt.

Az egyes grafikus elemek máshogy néznek ki a különböző platformokon. Észrevettünk layout szétcsúszásokat, pl. a slider csúszkája más helyen volt.

## 4.  Stíluselemek használata

Készítettünk egy singleton osztályt qml-ben, amiben az alkalmazás stíluselemeit tárultuk, így könnyedén módosítható az alkalmazásunk színvilága, stílusa.
