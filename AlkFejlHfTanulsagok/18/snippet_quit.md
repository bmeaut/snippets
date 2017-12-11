---
layout: default
codename: Tanulságok
title: Quit csapat tanulságai
tags: snippets afhf
authors: Buchmüller Patrik, Kolonits Dominik, Putnoki Roland
---

# Quit csapat összefoglalója

A házi feladat kiírását mindig figyelmesen és pontosan kell elolvasni, hogy azt csináljuk, ami a feladat. Qt telepítéséhez kapcsolódóan futottunk bele, hogy nem gcc fordítóval tettük fel, amit utólag bár nem lehetetlen kihívás módosítani elég bosszantó tud lenni ennek az állítgatása.
A git használata nem csak ajánlott, de egy ilyen projekt esetében szinte kötelező. Eleinte ódzkodtunk a használatától, még nem igazán volt vele tapasztalatunk, így a szoftvermegosztás más, körülményesebb csatornán történt. Ennek hátrányaira elég gyorsan fény is derül:

* Csapatmunka folyik, az adott kódrészleten nem csak egy ember dolgozik, így ha valaki elvégzi a saját fejlesztését, a csapat másik tagja is a sajátját, akkor a két kódsort szemmel összehasonlítani és hibamentesen egymásba építeni szinte lehetetlen 

* Szintén az egyes mentett munkafázisokra vonatkozóan, ha például „zip-es verziókövetést” alkalmazunk, volt egy jól működő szoftverünk, próbáltuk szépíteni azonban valami hiba folytán teljesen megadta magát, akkor az előző jó állapottal történő összevetés szintén macerás

* Nem feltétlen a házi feladathoz kapcsolódóan: mivel felismertük, hogy a git-es verziókövetés rendkívül hatékony és hasznos módja a közös munka egyeztetésének, engedélyt kértünk a privát repository használatára a RobonAUT versenyen induló projektünkhöz, melyet az előadó beleegyezésével meg is kaptunk. Ezt azért emelnénk ki, mivel ingyenes fiókkal csak publikusan lehet dolgozni.
* 
## QML tapasztalatok

A qml környezet új volt számunkra, így némi időbe telt míg megbarátkoztuk vele, és kiismertük működését. Az egész felépítés egy fáéhoz hasonlatos, ahogy az egyes elemek származnak egymásból.

A fejlesztés során szerettünk volna a környezet nyújtotta lehetőségeket kihasználni egy szép, jól kinéző GUI megalkotására. Ennek érdekében animációkat rejettünk el az egyes részegységekre. Itt eljött az a probléma, hogy ha egy objektumot anchor-ral igazítunk és paramétereiben animáljuk, akkor nem fog megfelelően működni. Ez esetben vagy anchor animációt kell alkalmazni, vagy nem szabad vele pozícionálni, hanem csak koordinátákkal. A mi esetünkben rengeteg idő elment vele, mire rájöttünk, hogy egyszer miért jó az animácó máskor miért nem.

Szintén itt jött elő az is, hogy ha két qml között szeretnénk hivatkozni egymásra, akkor azt az property alias segítségével tehetjük meg, így láthatóvá válnak egymás számára a fájlban lévő obejktumok, és így már hivatkozni tudunk rájuk. A mi példánkban ez az animáció bekötése volt a legördülő menüsorba, ha megnyomjuk az adott fület akkor indítsa azt el. Ezt eleinte csak a window qml-jébe rakott gomb segítségével tudtuk elérni, míg rá nem jöttünk a "nem láthatóság" okára.

A GUI-nk további szépítése érdekében egy olyan visszajelző rendszert terveztünk, mely nem csak számértékkel szemléltet egy adott értéket, de ha túllép egy bizonyos köszöböt akkor azt úgymond világító LED formájában jelezze. Első megoldásunkra a LED-ek sikeresen megvalósításra kerültek, gomb segítségével a tesztelésük is működött, azonban ha rákötöttük a kívülről érkező adatokat, nem váltottak állapotot. Itt a megoldást az jelentette számunkra, hogy a LED-eknek definiált Rectangle-ket külön GroupBoxban helyeztük el, így már sikeresen vették a kívülről érkező adatok frissítését.

A robotunk gyorsulását legalábbis két dimenzióban egy forgó vektor (nyíl) segítségével szerettük volna változtatni. Erre két transzformációt felhasználva (szög és skálázás) azonban a két transzformációt egyszerre nem végezte el. Megoldásként csak a skálázást transzformáljuk, a kép rotation - tulajdonsága mindig frissül az aktuálisan érkező adattal.

Nagy kihivást okozott az, hogy szerettünk volna adatot beadni manuálisan a robotunk számára, tehát egy adott mezőt kitöltve és egy küldés gomb segítségével a robotunk valamilyen paraméterét állíthassuk, esetünkben ez a kormányzásért felelős szervó szöge, illetve a kormányzásért felelős szabályozó paraméterek állítása. Nagy kihívást jelentett, hogy hogyan tudjuk az adatokat qml oldalról visszaküldeni C++ oldal felé. Erre a kapott példakódok közül a QmlControlKupac nevűt érdemes áttanulmányozni.

## Tanácsok a házi feladathoz:
* Kezdjük el időben, a félév vége felé a sűrűsödő teendőink mellett egyre kevesebb marad a házira, mely bár elsőre nem tűnik eget rengetően nehéznek, de azért nem is triviális.
* Magához a Qt hez rengeteg forrás és segédanyag található az interneten, valamit saját weboldala és a fejlesztői környezetbe integrált súgórendszer is jól használható.
* Rengeteg modul készen elérhető, vagy egy-egy példában bemutatva fellelhető, melyek minimális változtatással beépíthetőek a saját kódunkba
* A dokumentáció elkészítése ne csak leadás előtti este jusson eszünkbe, hiszen ez szerves részét képezi a feladatnak. Az iparban rengeteg rosszul esetleg egyáltalán nem dokumentált szoftverrel találkozhatunk. Saját magunk védelme érdekben mindig készítsünk alapos és részletes dokumentációt.

Összefoglalva a házi feladat elvégzése rendkívül hasznos, rengeteget lehet tanulni belőle mind verziókövetésről, mind Qt-ről és nem utolsó sorban C++-ról.