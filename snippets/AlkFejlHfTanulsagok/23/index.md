---
layout: default
codename: AlkFejlHf23
title: Githunters csapat snippet
tags: alkfejl afhf skipfromindex
authors: Ölvedi Balázs, Szabó Zsolt, Szakály Balázs
---

# Tanulságok

## Triviális?

Talán triviálisnak tűnik, de feltétlen figyeljünk oda, hogy a "Sources" fájlok kiterjesztése ".cpp" legyen. Ha az adott fájl ".c" kiterjesztésű, akkor a (feladat megoldása miatt szükséges) C++ nyelvi különbségek hibát fognak eredményezni.

## Projekt fájl kiegészítések

A ".pro" kiterjesztésű projekt fájl feltétlen tartalmazza a következő kiegészítéseket:

    CONFIG += c++14

    QMAKE_CXXFLAGS_CXX11    = -std=c++1y

Ezzel a C++14 nyelvi kiegészítések (pl.: unique_ptr) is használhatóvá válnak.

## Ikon beillesztés

Ikon beillesztése a programba egyszerű (http://doc.qt.io/qt-4.8/appicon.html), de mivel belefordul a programkódba, így utólagos megváltoztatása problémás. (fun: https://www.youtube.com/watch?v=yv-ft9ZvCBc)

## Design nézet

A megjelenítésért felelős qml fájlokat nem csak programkódból lehet előállítani, hanem a "Design" nézetben is, ez azonban eléggé körülményes. Ha a programkódba olyat írunk, amit a fordító nem tud értelmezni, arra a fordító lefut (csupán piros aláhúzás lesz a kódban), de akkor a "Design" nézet már nem lesz elérhető.

## Verziók

Előbbi probléma könnyen előfordul, ha módosítjuk a beimportált fájl verziószámát. Előfordult nálunk, hogy az adott verziójú Control objektum (Dial) esetén a minimum, maximum értékek beállítása a minimumValue/maximumValue property-vel volt állítható. Más kipróbált verzió esetén a from/to property-ket kellett beállítani. Ha az internetes dokumentációt olvassuk, feltétlen ellenőrizzük, hogy a megfelelő verzióhoz tartozó dokumentációt olvassuk.

## Forgatás

Ha forgatunk egy objektumot, akkor egyes property-jei is vele fordulnak. (width/height; x/y). Pl: widht --> height (widht forgatás nélkül az x tengellyel párhuzamos méretet jelentette, 270°-os forgatás után ez már az y tengellyel párhuzamos méretet jelenti).

https://imgur.com/a/HJqHf
 
## ObjectName vs id

Fontos kiemelni, hogy cpp oldalról elérjük a qml-es objektumainkat, akkor a findChild() metódus működéséhez elengedhetetlen, hogy a qml-es oldalon az objektumok "objectName" property-jét kitöltsük, ugyanis ez alapján tudjuk megkeresni őket (és nem az "id" alapján!).

## Elérési út

Figyeljünk oda, hogy ne használjunk ékezeteket az elérési útban, fordító erre hajlamos hibát dobni (nekünk ez a probléma a beadás előtti éjszakán jött elő, amikor elkezdtünk subdirectorykat használni).

## Mappaszerkezet módosítása

Olyan anomáliával is találkoztunk, hogy subdirectoryk használata után a programunk egyik funkciója hibát dobott (bár a hibaüzenet mögött a háttérben szépen futott :) ).

## Clean - build!

A mágikus clean - build fix random hibákra egyetlen egyszer működött a program fejlesztése során.

