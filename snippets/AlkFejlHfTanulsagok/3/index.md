---
layout: default
codename: AlkFejlHf3
title: AlkFejlHf3
authors: Zelei Kristóf, Vógel Ákos, Laczkó Tibor
tags: alkfejl afhf skipfromindex
---

A fejlesztés során felmerülő nehézségeket a fejlesztés során tapasztal sorrendben tálaljuk.

### Felvetődő problémák konfigurálás közben
A fejlesztés megkezdése során az egyik legnagyobb kihívást a keretrendszer megismerése
  - Megfelelő C++ verzió választása  
  - GCC beállítása
  
 Mivel szerettünk volna smart pointereket használni, így szükségünk volt a C++14-re. Ezt a .pro fájlban a következő makrót kellett elhelyeznünk:
```sh
QMAKE_CXXFLAGS_CXX11 += -std=c++14
```
  Egyes gépeken a GCC 4.2-es verziója volt telepítve, ezért szükség volt ennek a frissítésére. Ez a terminalon keresztül egyszerűen megoldható volt. A Homebrew nevű program telepítése után csak az alábbi parancsot kellett beírni a terminálba:
 ```sh
 brew install gcc
```

### UI problémák
>Create your own visual styleâ€¦ let it be unique for yourself and yet identifiable for others.
Orson Welles

A UI fejlesztése során a legnagyobb problémát az adatok beállításához és az eredményeket, folyamatokat legjobban bemutató desing elemek kiválasztása, megalkotása volt a legnehezebb. Mivel QML-JavaScript párossal dolgoztunk olykor a debuggolás is nehézkes volt. Tapasztalataink szerint minél dinamikusabbra szeretnénk egy oldalt készíteni, annál inkább érdemes az elemek megrajzolását JavaScript-tel, kódból megtenni, mint QML oldalon. 

### Unit test bug
A Unit Teszt viszonylag egyszerű kis modul, a fejlesztés során viszont egy érdekes bug jelentkezett. Az akadály oszály Unit teszjéhez ugyanis szükség volt QpolygonF objektumokra, ehhez a projekt .pro fájljában importáltam a következőt 

     QT += qml quick widgets
Ezzel már le is fordult a Unit teszt, cserébe a debugger elszállt a következővel:

    Unknown option: '-qmljsdebugger=port:2348,block'
Ezután kivettem a .pro fájlból a qml quick widget-et, de a probléma továbbra is megmaradt és csak egy hard reset segített rajta. (Megjegyzés: release módban lefutott a Unit Test, csak a debug mód volt a rossz.)
A hibát azzal küszöböltem ki, hogy a QT -= gui sort QT += gui-ra.

### Akadály megjelenítési problémák
Az eredeti elképzelésem az volt, hogy egy QList<QPoligonF> listát használva fogom kirajzolni a GUI-ra az akadályokat, de ennek a QML oldali beregisztrálása (számomra) nehéznek bizonyult és nem is sikerült megoldanom. A Google találatok többsége az ilyen általános Qlist-ek regisztrálásánál a [QQmlListProperty](http://doc.qt.io/qt-5/qqmllistproperty.html) használatát javasolja azonban nekem ezzel se sikerült (egyéni ügyetlenség). Az áthidaló megoldás az lett, hogy egy QList<QVariant> listát hozok létre, ugyanis ezt látja a qml oldal is. A Qvariant kvázi egy "magic" objektum, ami sok változót fog össze, köztük a QrectF-et is, így az a megoldás született, hogy a poligonokat körülhatároló négyszögeket jelenítjük meg a felhasználói felületen. Ez jelenleg nem korlátozás, ugyanis négyszögeket akaruk megjeleníteni, de az akadály osztály általánosabb, ott tetszőleges Polygon definiálható.

<small>Szerzők, verziók: Zelei Kristóf, Vógel Ákos, Laczkó Tibor</small>