---
layout: default
codename: AlkFejlHf27
title: Pickle-Rick csapat tanulságai
tags: alkfejl afhf skipfromindex
authors: Quit csapat
---

## Pickle-Rick csapat tapasztalatai és tanácsai az Alkalmazásfejlesztés feladat megoldásával kapcsolatban.

#1. Rejtélyes hiba és annak oka/megoldása
A fejlesztés során GIT verziókövetőt használtunk, így párhuzamosan tudtunk dolgozni az egyes feladatrészeken. Az első mergel-ig nem is volt ezzel probléma. A mergelést követően a csapat két tagjánál nem működött a program. Az alkalmazás Runtime error-al elszállt náluk és a legérdekesebb a hibaüzenet és az összeomlás ideje.  A 3 tick környékén szállt el mindig pure virtual method called-al, netes keresgélések és debuggolás nem hozott sok sikert és nem értettük, hogy mehet valakinél hiba nélkül és valakinél pedig összeomlik. Kellett pár óra mire észrevettük, hogy a fent lévő fordítók verziója különbözik MinGW 5.9.2-ön fut (legújabb), de MinGW 5.9.0-n elszáll. Ezt követő újra telepítéseknek hála megoldódott a problémánk, bár azt még most sem tudjuk, hogy mi lehet az a nagy különbség két alverzió között, hogy ilyen hiba keletkezett belőle.

![kep](kep1.png)


![kep2](kep2.png)

#2. A QML oldal szerkesztése
A grafikonok apró szépítgetésénél futottunk bele abba, hogy  a Canvas elem módosítása nem minden esetben fog megtörténni újra buildelés során. Például a betűméret, kitöltő szín nem változott meg módosítás és újra buildelést követően. Ez okozott némi fejfájást és utána keresgélést, hogy mi lehet a baj, hogyan is kéne akkor ezeket a paramétereket megváltoztatni. A megoldás, hogy az egész build mappát törölni kellett és azt követően az új buildelt verzióban már látszódni fognak a változtatások.

#3. Kép beillesztése
A kép beillesztésénél fontos, hogy nem elég a képet a project mappában elhelyezni, hozzá kell adni a qml.qrc fájlhoz. Helyes hozzáadás után qt-ban a project mappái között látni lehet a hozzáadott képfájlokat. 


![kep3](kep3.png)

#4. Mapviewer
Feladatunkban használtunk térképet, ehhez volt egy alap példa amit módosítottunk. Az első pontban leírt fordító verzió eltérés itt is egy kis zűrt tudott okozni, valamiért a régebbi verzióban debug módban is futni tudott a példa mapviewer, de az újabban csak release-ben fordítva és futtatva, különben runtime error-al elszállt.

#5. Tanácsok
Jó tanács a későbbi tárgy hallgatóinak, hogy a legjobb, ha közösen telepítitek fel a Qt-t, ezzel sok rejtélyes problémát meg tudtok spórolni, amibe mi belefutottunk. Másik tanács, hogy a hallgatók által írt snippeteket tényleg érdemes átfutni, mivel elég sok probléma leírása és megoldása olvasható ezekben, így rengeteg időt meg lehet spórolni.
