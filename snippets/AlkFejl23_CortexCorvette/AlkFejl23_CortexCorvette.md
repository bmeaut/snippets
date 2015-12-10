---
layout: default
---

# Cortex Corvette összefoglaló

![Cortex Corvette Logó](image/cc_logo.png "Cortex Corvette logó")

Ez a Snippet a Cortex Corvette RobonAUT csapat összefoglalója az autóhoz írt QT-s alkalmazásfejlesztésről.

[Facebook oldalunk](http://www.facebook.com/cortexcorvette/)

## Általános

vmi rizsát ide.

## QCustomPlot

A fejlesztést nagyban megkönnyítette, hogy nem kellett mindent nulláról megírnunk. Az egyik külső forrásból származó (third-party) felhasznált osztály a *QCustomPlot* volt. Segítségével, gyakorlatilag pár sorban tudunk létrehozni gyönyörű, végtelenül paraméterezhető és reszponzív diagrammokat.

![Cortex Corvette Vonaldetektálás](image/cc_linesensor.png "Cortex Corvette Vonaldetektálás")

Nem csak látványnak volt jó a megjelenítés, hanem segítségével a többfajta vonaldetektálási algoritmust is ki tudtunk próbálni, valamint láthattuk azt is közel valósidőben (egy 32 elemű tömb elemeinek nézegetése helyett), hogy melyik szenzorunk "rosszalkodik", illetve hol van még hardveres problémánk.

[QCustomPlot hivatalos weboldal](http://www.qcustomplot.com/)


## QTest használata

A QT-s Unit tesztek okoztak fejtörést az alkalmazásfejlesztés közben. A gondot az okozta, hogy nehezen találtunk jó leírást a használatukról és egy meglévő projektbe történő integrálásáról. Az egyszerű QT Unit Test új, független projektként való létrehozása nem tetszett nekünk, mivel akkor lett volna két független projektünk, amik pedig egymáshoz tartoznak szorosan. Sok kutakodás után rátaláltunk egy jó megoldásra: Ahogy a Microsoft Visual Studio is támogatja a Hierachikus projekteket, ez itt QT-ban sincs másként.

### Hierarchikus project létrehozása

A cél olyan projekt létrehozása, melyben több al-projekt is szerepel. Jelen esetben most 2: a szoftver maga, és egy unit tesztkörnyezet. Ehhez a következőt kellett tennünk:

0. Adott a létező szoftveres projektünk (*RobonAUT_CSW*)
1. Létrehozunk egy QTest projektet, tetszőleges osztály névvel (*RobonAUT_CSW_QTest*)
2. Létrehozunk egy könyvtárat, ami tartalmazni fogja mind a két projektet (*RobonAUT_CSWSolution*)
3. A két projektet közös mappába másoljuk, majd létrehozunk egy .pro kiterjesztésű fájlt, melyben definiáljuk, hogy ez a projekt bizony egy hierarchikus projekt lesz.

A *RobonAUT_CSWSolution.pro* tartalma:

    TEMPLATE = subdirs  
    SUBDIRS += RobonAUT_CSW \
               RobonAUT_CSW_QTest

Ebből a QT tudni fogja, hogy amennyiben megnyitjuk a *RobonAUT_CSWSolution* projektet, vizsgálja meg a két almappát is, mert abban alprojektek lesznek. Ekkor a QT Creatorban így néz ki a hierarchia:

![Hierarchikus projekt](image/hierarchy.png "Hierarchikus projekt")

### QTest használata

Ezek után, már nincs más dolgunk, mint:

1. a QTest alkalmazásban hivatkozni a fő projekt fájlraira úgy, hogy egyszerűen beszúrjuk őket a projektbe (a QT relatív útvonalon kezeli majd a fájlokat, de mivel mostmár egy "Solution"-ünk van, ez nem probléma).
2. Megírunk egy teszt osztályt adott funkció kipróbálásához
3. Majd a ``QTEST_APPLESS_MAIN(..)`` makróval létrehozunk egy main()-t és lefordítjuk a QTest alkalmazásunkat.

### Unit tesztek tanulsága

A Projekt részeként létrehoztunk két tesztelő osztályt, mely egy Polinomális regresziót számító osztályt, valamint egy egyszerű mátrix osztály implementációt tesztelnek. A tesztek során derült ki, hogy a mátrix osztály transzponáló függvénye csupán N*N-es mátrixokra működik. Ami bár a jelenlegi beállításokkal nem okozott hibát, de a későbbiekben, amennyiben más regressziós formát választunk, bajba kerültünk volna.

## Tárgy hasznosságga

Bár mindannyian használtunk már verziókövetést a tárgy előtt is, nem értjük, hogy ez miért nem került előbb tananyagba, hiszen sokaknak teljesen újdonság volt ez a téma. Javasolnánk a tárgy (legalább részeinek) bevitelét az alapképzés részébe.

*True story: bejöttem előadásra, volt pár olyan rész a GIT-ben, amiről még nem hallottam, mivel nem kellett használnom (stash, cherry-pick). Majd két nap múlva elmentem állásinterjúra, ahol megkérdezték pont ezeket. :)*

<small>Szerzők: Major Péter, Nagy Balázs, Imre Dávid</small>
