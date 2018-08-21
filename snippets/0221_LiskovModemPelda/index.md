---
layout: default
codename: LiskovModemPelda
title: Modemes példa a Liskov Substitution Principlere
tags: designpatterns alkfejl
authors: Csorba Kristóf
---

# Amikor nem sikerült tartani a Liskov Substitution Principlet

Az alábbi modemes példa alapgondolata Uncle Bobtól származik, a kapcsolódó protokollokat kicsit frissítettem aktuálisabb környezetre. A történet bemutatja, hogy az első hangzásra triviálisnak tűnő Liskov Substitution Principle megtartása nem is mindig olyan triviális dolog.

A történet egy fiktív cég fiktív fejlesztőiről szól, akiknek volt egy FileMover alkalmazásuk, ami TCP/IP protokoll felett tudott fájlokat mozgatni. Volt nekik ezen kívül egy másik csapatuk, akik RS-232-höz használtak egy jól bevált, agyontesztelt függvénykönyvtárat, amit ők készítettek még vagy 15 évvel korábban.

A cégvezetés megkérte a fejlesztőket, hogy mindenféle logfájlok kezelése miatt a FileMover működjön RS-232 felett is.

## Az egységes ősosztály

Mivel a fejlesztő csapat igyekezett szépen dolgozni, kiemelték a közös interfészt és létrehoztak egy Communication ősosztályt. Mivel a TCP/IP protokoll stackben 4 metódus volt (_open_, _close_, _send_ és _receive_), az egyeséges interfészbe is ezek kerültek  bele. Bár az RS-232 esetében az első kettő hiányzott, de semmi gond, azok majd megörökölnek egy üres metódust és nem csinálnak vele semmit.

(Az RS-232 csapat már ennek sem örült, mert bele kellett nyúlni az ő kódjukba is, de végülis két üres metódus ha nem is szép, de még elfogadható.)

## Anomáliák a soros vonali küldéskor

A FileMover egy ideig szépen ment, de aztán időnként érdekes hibák jöttek elő, amikor RS-232-n kellett volna dolgoznia. Kis debuggolás után kiderült, hogy a soros vonalon néha korábban is jönnek adatok (kritikus versenyhelyzet és társai...), mint hogy a FileMover megnyitotta volna a kapcsolatot. Márcsak azért sem, mert a túloldal eleve nem ismeri azt a fogalmat, hogy "megnyitjuk az RS-232 kapcsolatot". (A CTS és RTR vezetékek már régen hiányoznak abból a kábelből és az implementációból.) A FileMover viszont ezt eléggé nehezen viselte.

## A megoldás: IsOpened

- Semmi gond, nem kell mást tenni, mint módosítani az RS-232 kommunikációt...
- Grrr...
- ...szóval egy picit ki kellene egészíteni: mentsétek el egy bool változóba, hogy meg van-e nyitva a kapcsolat (IsOpened), ezt módosítsa az _open_ és a _close_ és ha nincs megnyitva, ne fogadjatok adatokat.
- Grrr... és amiatt írjuk át a többi projektünkben is az RS-232 API hívásokat, hogy hívják meg az _open_-t? 10-15 éve nem kellett hozzányúlni azokhoz a részekhez!
- Bocs... légyszi-légyszi! Fontos az egységes kódbázis! Nagyon jó lesz utána!
- Na jó... legyen. Simán _open_?
- Öööö... az _open_-nek van egy IP cím paramétere, mert a TCP/IP-ben kell címezni is.
- Na és az egy RS-232 kapcsolat esetén mégis mi legyen??? Most komolyan mindenhol írjuk ki, hogy _open(0,0,0,0)_?
- Bocs...

Ez van... és így is lett.

## Egy újabb fejlesztés

Pár hónappal később felvetődött, hogy már nagyon ideje lenne haladni a korral és támogatni az IPv6-ot is. Ami annyiban rázós, hogy más a cím típusa, ami az _open_ paramétere. Mivel a címet nem egy sima stringként adták át neki, ami egyébként egy védhető és típus-biztosabb megközelítés, ez akkor azt is jelenti, hogy változik a közös interface! Izé, kedves soros port csapat... ki lehetne egészíteni úgy az implementációtokat, hogy az open-nek kicsit megválozott a paraméter listája?

Na ekkor pöccent be a soros porti csapat másodjára. Most a közös interface miatt egy tőlük teljesen független változás náluk is módosítást követel. 15 évig nem kellett piszkálni azt a kódot és ment minden szépen. Erre most a nagy egységesítés nevében lassan havonta kell módosítani, ami egy csomó saját kis projektjükre is hatással van...

## Mi lett volna a megoldás?

No hát így lehet beleszaladni a Liskov Substitution Principle megsértésébe, vagyis abba, hogy az ősosztály alatt nem cserélgethetőek tetszőlegesen a leszármazottak. Az "_open_ és _close_ majd nem csinál semmit" megközelítés nem jött be, az RS-232 implementáció nem volt csereszabatos a TCP/IP-vel. Ellentmondásos elvárások ütköztek az egységes interfésznél és az nem tudott egyszerre mindkettőnek megfelelni.

A megoldás lehetett volna például az Adapter tervezési mindta alkalmazása: a FileMover számára az egységes Communication létrejön, de az RS-232 kapcsolat ezt nem implementálja, mert neki nincsen _open_ és _close_. Helyette az adapter osztály a leszármazott, ami magán belül tartalmaz (beburkol) egy RS-232 hivatkozást és ő az, aki belül megoldja, hogy az örökölt _open_ meghívása előtt nem enged adatokat fogadni.

Ebben a megoldásban sem a FileMover, sem az RS-232 API nem tudna róla, hogy közöttük van egy adapter (egyfajta átjátszó). Az adaptertől senkinek a többi munkája nem függ, így az RS-232 csapatot nem érintik a későbbi interface módosítások sem, csak az adaptert kell egy kicsit kiegészíteni.

<small>Szerzők, verziók: Csorba Kristóf</small>
