---
layout: default
codename: AlkFejlHF
title: AFHF csapat tanulságok
tags: alkfejl afhf skipfromindex
authors: Kerekes Ákos, Gaják Tibor
---

# AFHF csapat tanulságai

 ## 1. Általános

Ahogy a legtöbb csapat is írta már korábban, a legelső tanácsunk nekünk is az, hogy tényleg érdemes elolvasni az összes korábbi csapat tanulságait, tanácsait. Érdemes akár fejlesztés közben is, ha bármilyen elakadás előfordul, az online keresés helyett a korábbi tanulságok között keresni. Nagy valószínűséggel már más is belefutott ugyan abba a problémába és a tapasztalatok között megosztotta a megoldást is. Ezzel jelentős időt lehet megspórolni.

A félév során az előadásokon előkerültek különböző programozói módszertanok, hogyan érdemes egy projektet elkészíteni, hogyan érdemes egy csapatban dolgozni.

Az első ötlet az idő és munka optimalizálása szempontjából általában, hogy érdemes felosztani a munkaköröket a csapattagok között úgy, hogy mindenki a saját részét fejleszti, felügyeli. Ennek a megoldásnak is van előnye, azonban gyakran előfordul, hogy amíg egy adott funkció nem kerül elkészítésre, addig a ráépülő másik funkciót sem lehet fejleszteni. Így előállhat az a helyzet, hogy az egyik csapattag a másikra vár és értékes fejlesztési idő veszik el.

Erre az egyik megoldás, hogy egy adott feladaton ketten dolgoznak egyszerre. Ha  ketten dolgoznak egy feladaton úgy, hogy az egyikük kódol és a másik azt „ellenőrzi” – figyeli azt, akkor ha az illető észrevesz egy elírást, hibát és rögtön jelzi azt, akkor talán jobban kikerülhetőek az elírásból fakadó hosszas debugolás során felfedezhető hibák. Továbbá ha szükséges, akkor közben utána tud nézni a kérdéses részeknek. Így gyakorlatilag nem dupla idő a fejlesztés, ugyanis mind a ketten nyomon követik a kódot és később ha bármi történik, akkor bármelyikük tudja folytatni a feladatot, nincsen az, hogy ez a „te” részed „én nem értek hozzá”. 

 ## 2. Management
 
Az időbeosztásra érdemes már a legelején odafigyelni és a csapattagok között felosztani a feladatokat. Erre már rengeteg applikáció is segítséget nyújthat, így akár online is nyomon lehet követni egymás munkáját, továbbá a kitűzött határidők tartásában is nagy segítségre lehet. pl: Trello, Teamweek

 ## 3. Telepítés

Érdemes odafigyelni a QT telepítése során, hogy csak a szükséges csomagokat válasszuk ki, mivel egyébként bőven 30Gb fölé tud nőni a telepítő mérete. 

 ## 3. Verziókezelő
 
Akik még korábban nem használták a Git verziókezelőt, nekik azt tudjuk javasolni, hogy először egy saját próba repository készítsenek és azon próbálják ki a lehetőségeket.

Azonban oda kell figyelni arra, hogy a félév során a teljes munkát nem érdemes egy saját repositoryba pusholni  és a végén visszaállítva az egyes korábbi állapotokat, onnan újra feltölteni a végleges tantárgy repositoryba, mivel utólag sokkal nehezebb, időigényesebb így  a folyamat. A különböző funkciók kipróbálása után érdemes csak a hivatalos repositoryba dolgozni.
 
 ## 4. Fejlesztés
  
A grafikus felület fejlesztése során az első dolog amivel szembetalálkoztunk, hogy érdemes a Qt verziókat frissíteni és azok alapján tovább fejleszteni a felületet.
  
Második legfontosabb észrevételünk, hogy mindig kell clean build futtatás előtt, mivel gyakran sok bosszúságot okoz, ha beépítünk egy új funkciót és a megszokásból futtatásra kattintva nem történik változás.
  
A QT rengeteg mintakódot felkínál számunkra, amiket felhasználva könnyebben esztétikusabbá és felhasználóbarátabbá lehet varázsolni az alkalmazást.  
  
A grafikus felület fejlesztésénél előkerült egy olyan probléma, hogy ami az egyik csapattagnál futott a másik csapattagnál elszállt egy értelmezhetetlen hibakóddal. Konkrétan a QtCharts modulnál. Ennek megoldása, hogy a fordítót át kellett állítani minGW64 bit verzióra. (Érdekesség, hogy release módban fordult a program ennél a csapattagnál is.)
