---
layout: default
codename: AlkFejlHf42
title: Korso a Qtra csapat tanulságai
authors: Koi Bence, Marosi Dániel
tags: alkfejl afhf skipfromindex
---

# Alkalmazásfejlesztés házi feladat tapasztalatok

## Open Points/TODO vezetés
A házi készítése során nagyon hasznosnak bizonyult egy közös dokumentum, ahova a nyitott kérdéseket és a teendőket írhattuk. Mi egy Google Drive-os mappát hoztunk létre a csapatnak, ahol a fejlesztéshez szükséges segédleteket rakhattuk, például a rendszertervet és a TODO fájlt. A TODO egy Google Docs volt, amiben több szintre lebontva írhattuk fel a feladatokat magunknak és egymásnak is.
Alapvetően egy átfogó résszel kezdődött (System), ahova az észben tartandó követelményeket és a teljes szoftverrendszerre vonatkozó feladatokat írtuk. Ezt követte a csapattagonként elkülönített TODO rész, ahol lépésekre bonthattuk magunknak az általánosabb feladatok megoldási tervét. Ez segítette azt is, hogy a csapattagok átlássák az éppen folyó munkánkat és könnyebben segíteni tudjanak, ha elakadunk. Végül egy olyan rész következett ahova az elvégzett munkákat tettük. Emiatt letisztult maradt a tényleges TODO rész, másfelől pedig ellenőrizhettük, hogy mi az amit már elkészítettek a csapattagok.

## Commit message
Mindig jól gondoljátok végig, hogy mit írtok a commit message-hez, mert utólag már ezt nehézkes módosítani, ha rájöttök egy hét múlva, hogy nem azt kellett volna hogy “update” hanem, hogy ténylegesen mi történt abban.

## Qt Creator bug
A házi készítésekor használt Qt Creator verzióban egy igen furcsa hibát fedeztünk fel. Ha két monitoron szeretnénk fejleszteni és egy új ablakot hoztunk létre a kódoláshoz (Window->Open in New Window), akkor néha előfordul, hogy ha ebben az új ablakban szeretnénk beilleszteni egy kimásolt tartalmat, egy teljesen random helyre illeszti be. Ez akkor jelent gondod ha az ember nem veszi észre egy nagy fájlban hogy ez történt, aztán a fordításnál mi is fordulunk egyet a széken, hogy hogy került az oda.

## Clean Build
Bár ezt már sokan le írták, még így is volt, hogy nem ez volt az első dolog amire gondoltunk, ha valami nem működött, így leírom újra: Ha egy módosítás után (főleg qml fájloknál) fordítunk és futtatnuk, de a úgy tűnik, mintha a változtatásaink mégse működne, akkor egy clean szükséges, majd újra fordítás.

## Multhithreading:
Ha szálkezelést is szeretnénk használni, figyeljünk arra, hogy alapesetben a szálak közötti signal-slot összekötés “Queued Connection”, ami azt jelenti, hogy a slot akkor hívódik meg, amikor visszakerül a futás a fogadó szálhoz, tehát nem azonnal. Ez például a GUI kapcsolatnál jelenthet gondot, ugyanis mire a GUI meg kapja az emittált szignálokat, addigra a függvényünk már rég végigfutott, ezért a kijelzett adat már gyakran nem releváns.
Erre megoldás lehet a “Direct Connection” típusú kapcsolás, ami a slot futását átemeli a hívó szálba, ezért az rögtön lefut. Ez esetben viszont arra kell figyelni, hogy ne használjuk a socket írására/olvasására, ugyanis az halálfejes hiba egy ilyen hibaüzenet mellett: “socket notifiers cannot be enabled from another thread”. A socket írását és olvasását ezért érdemes minden esetben signal and slot mechanizmussal kezelni.
Erre a problémára alternatíva lehet egy állapotgép és egy QTimer használata. Az állapotgépünk állapotait minden esetben egy Timer indításával zárjuk, aminek a timeoutját visszakötjük magára az állapotgépre. Ezáltal elérhetjük a nem-blokkoló várakozást (például a kalibráció eredményének késleltetett visszaolvasásához).


<small>Készítette: Marosi Dániel, Koi Bence</small>
