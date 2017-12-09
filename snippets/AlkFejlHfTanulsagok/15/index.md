---
layout: default
codename: AlkFejlHf15
title: AlkFejlHf15 (2017 ősz - Destroyerzz)
authors: Destroyerzz csapat (AlkFejl 2017 ősz)
tags: alkfejl afhf skipfromindex
---

# Alkalmazásfejlesztés Házi Feladat Snippet Oldal (Destroyerzz) #
## Tanulságok a fejlesztés során ##

## 1. Megfelelo Qt verzió és fordító kiválasztása ##

A háromfős csapatból kettőnknek is sikerült belefutni abba a hibába, hogy a telepítésnél nagy örömmel kiválasztottuk 
a Qt Creator legújabb verzióját, azonban arra nem gondoltunk, hogy ebből mely komponensek kellenek igazán, így kb. 30GB-nyi 
programot telepítettünk, ami ráadásul sokáig is tart amellett, hogy sok helyet foglal.

Tanulság: csak a szükséges komponenseket telepíteni és gyanakodni, ha túl nagy a telepítendő program becsült mérete. 

## 2. QML fájlok nem fordulnak ##

A projekthez hozzáadtunk egy új QML fájlt, azonban feltűnt, hogy akármit is módosítunk benne, az Build után nem kerül bele 
a programba. A kezdeti amatőr megoldás az volt, hogy az egyik eredeti QML fájlt módosítottuk, ha látni akartuk az új QML fájlban
történt változtatásokat. 

Végül egy fórumon (https://bugreports.qt.io/browse/QTCREATORBUG-1627) egy Tim nevű felhasználó által 
találtunk rá az igazi megoldásra, ami annyi, hogy új QML fájl hozzáadása után a Qt Creatorban a Build menüponton belül 
a Run Qmake parancsot kell futtatni, ez megoldja a problémát, innentől minden változás az új fájlban érvényre kerül.

## 3. Adattípusok ##

A programban szerettük volna vizuálisan megjeleníteni a vonalszenzor állapotát és erre a quint8 adattípus tűnt kézenfekvőnek.
Több órán keresztül kerestük a hiba forrását, hogy miért mindig undefined az érték, gyanakodtunk a sorosításra, a helytelen 
összekapcsolására a C++ és QML oldalnak, míg végül kipróbáltuk int adattípussal és gond nélkül működött. 

A tanulságunk tehát, hogy elsőre kerüljük az egzotikusabb adattípusokat, az int általában jól működik, és ha azzal ellenőrzötten
jól működik, akkor meg lehet próbálni átírni a kézenfekvőbb, optimálisabb típusra.

## 4. Pull =/= refresh ##

A Git Extensions Start menüpontja alatt helyezkedik el egy zöld refresh gomb. Erre mi az első néhány alkalommal azt gondoltuk,
hogy a githubos repository alapján megjeleníti nekünk, ha valaki új kódot pusholt és akkor majd pullal frissítjük a gépünkön 
is ha van. Hát ez tévedés, az új pushokat a pullal tudjuk megjeleníttetni a Git Extensions fájában, a refresh a lokális 
változások frissítésére szolgál.

## 5. Elfelejtett pull ##
Jópárszor előfordult a fejlesztés elején, hogy egyből munkához láttunk és csak utána vettük észre, hogy utolsó alkotásunk 
óta valamelyik másik csapattagunk is fejlesztett az alkalmazáson, ezáltal tök fölösleges leágazást hoztunk létre, illetve 
volt olyanra is példa, hogy ketten is kijavítottuk ugyanazt a problémás részt. 

Készítette: Destroyerzz (Mendlik András, Ürge László, Varga Ádám)
