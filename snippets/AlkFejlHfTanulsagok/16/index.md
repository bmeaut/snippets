---
layout: default
codename: Tanulságok
title: alkfejlhf-team csapat tanulságai
tags: alkfejl afhf skipfromindex
authors: Branauer Ágoston, Détári Balázs, Csuka Róbert
---


# Alkfejlhf-team csapat tapasztalatai a Robot Diagnostics alkalmazás fejlesztése során

A Snippet a fejlesztés alatt felvetődött tanulságokat nehézségeket mutaja be. Reméljük a jövőben ezt mások elolvassák és tanulnak belőle.

## 1) QT letöltése

Amikor a honlapról letöltjük a QT-t, akkor figyeljünk oda amikor az telepítőt futtatjuk. Alapból nekem nem volt kiválasztva, hogy felrakja valamelyik QT verziót, sem fordítót hozzá, csak egyes kiegészítőket. Érdemes ezért bepipálni akívánt verziót, ezzel elkerülve az esetleges újratelepítést.

## 2) Konstruktor nem abban a sorrendben fut le

Többször előfordult, hogy lefordult a program, de hibaüzenet nélkül leállt. Debugálás után rájöttünk, hogy az egyik elem elviekben nincs létrehozva, miközben a konstruktorban mi az létrehozzuk. Hosszas gondolkodás után rájöttünk, hogy a QT nem a Konstruktorban leírtaknak megfelelő sorrendben futattja az inicializálásokat, hanem ahogy az osztályban deklarálva van.

## 3) Fordítási hibaüzenet

Voltak esetek, amikor pulloltuk az alkalmazást, és másik gépen működött a program de a másik gépen nem akartak lefordulni. A hibaüzenet a következő volt: 

```cpp
Qt Linker Error: “undefined reference to vtable”
```
Ekkor, ha a projekten újrafutattuk a  `` qmake ``-t, akkor a hiba megszünt. Ezt a projekten a jobb egérkattintással, run qmake paranccsal lehet megtenni. Igazából ilyenkor érdemes egy az egyben törölni az összes, Qt által generált fájlt (makefile-okat, binárisokat), és újrafordítani az egész projektet. Ez ugyan időben egy kis pluszt jelent, de legalább biztosan nem ütközünk problémába.

## 4) A C++ alkalmazás adatainak átadása QML felületelemeknek

A QML számára az alkalmazás QObject-ből származó osztályok, illetve azok adattagja is elérhetővé tehetőek. Ha csak az adadattagokat akarjuk exportálni, akkor a ezt Qt a ```Q_PROPERTY``` makróval tehetjük meg, ahogy a ```SimpleTelemetryVisualizer``` példaprojektben is látható. A fejlesztés során abba a problémába ütköztünk, hogy az animáció számára ```float ``` értékeket akartunk exportálni ```QList<float>``` típusú listával, azonban ezt a QML-ben definiált JavaScript metódusok nem tudták értelmezni. A dokumentációban természetesen le van írva, hogy lebegőpontos számokat tartalmazó listát ```QList<qreal>``` formában kell elérhetővé tenni, sajnos mi erre csak a teljes alkalmazás hosszas debug-olása után jöttünk rá. Érdemes tehát nem a logikusnak gondolt megoldást választani, hanem először utánanézni a dokumentációban a helyes módszernek.

## 5) Előre definiált QML elemek

A QML számos, előre definiált, egyszerűen használható felületi elemmel rendelkezik, ezért a GUI megtervezése előtt érdmes szétnézni a Qt példaprojektjei között. A ```CircularGauge``` elem például ehhez az alkalmazáshoz esztétikus megjelenítést tesz lehetővé, és a pédaprogram alapján könnyen használható is. A ```Timer``` QML típussal pedig egyszerűen lehet animációkat megvalósítani ahelyett, hogy ezt JavaScript kódból oldanánk meg.

## 6) Projektstruktúra

Ha teszteket is akarunk implementálni, akkor a tesztalkalmazást külön projektben kell létrehoznunk. Annak érdekében, hogy a projektünk struktúrájában is megjelenjen, hogy a fő alkalmazáshoz milyen tesztek tartoznak, érdemes lehet a C#-hoz hasonló, Solution projekt kialakítása. Ezt úgy tehetjük meg, hogy az alkalmazást egy közös Solution mappába helyezzük át, és melletük definiálunk egy .pro fájlt a Solution számára, amiben felsoroljuk, milyen komponensekből áll:

```cpp TEMPLATE = subdirs
SUBDIRS += /* alkalmazáskomponensek felsorolása */
```
## 7) Alkalmazás elérhetővé tétele a tesztek számára

A nehézséget az jelentette, hogy az alkalmazás forrásfájljai, másik projektben helyezkednek el. A legelegánsabb megoldás az lenne, hogy létrehozunk egy statikus library-t, ami külön projektként jelenik meg a solution alatt, és ezt használja mind az alkalmazás, mind pedig a teszt metódusok. Sajnos mi nem ezt az utat választottuk (idő hiányában), hanem a tesztalkalmazás .pro fájljában elérhetővé tettük a forrásfájlokat a fő alkalmazásból:

```cpp
INCLUDEPATH += /* a fő projektünk helye a fájlrendszerben */
SOURCES += /* forrásfájlok felsorolva */
HEADERS += /* header fájlok felsorolva */
```

Ennek a megoldásnak a hátránya, hogy a build-elés ideje nagyon megnő.

## 8) Whitespace az alkalmazás elérési útjában

Ennek elég evidensnek kellene lennie, mi azonban nem figyeltünk erre, ami rengeteg furcsa hibát eredményezett, mert a qmake néha nem tudta ezt kezelni. A legegyszerűbb az ilyesmit mindig elkerülni értelmes elérési út választásával.


Szerzők: Branauer Ágoston, Détári Balázs, Csuka Róbert
