---
layout: default
codename: AlkFejlHf5
title: AlkFejlHf5
authors: 11. csapat (AlkFejl 2015. ősz)
tags: afhf
---

# Az Alkalmazásfejlesztés házi feladat tanulságai a 11. csapat szerint


## 1.) A *.qml file-ok buildelése

Gyakran futottunk abba a hibába, hogy hiába változtatunk az alkalmazásunk felhasználói felületén, a következő futtatás mégis ugyanazt látjuk. Ennek az volt az oka, hogy a QT Creator nem tartja annyira számon a *.qml file-ok változását, mint mondjuk a c++ fájlokért, ezét ha nem mentettük el/kézzel nem indítottunk egy újabb buildet, akkor simán előszedi a régieket és azokkal fut.

## 2.) A kevesebb adat néha több

A kézhez kapott keretrendszerben a klienstől a szimulátor felé, illetve a szimulátortól a kliens felé történő kommunikáció egységes volt, minden esetben egy RobotState osztályt küldtünk át. Azonban volt olyan, hogy ezt csak arra használtuk, hogy egy 8bit információt (se) tartalmazó új állapotot átküldjünk. Az egységesség viszont még is csak szép dolog. E probléma áthidalására találtuk ki, hogy egy külön osztályt hozunk létre az üzeneteknek. Ennek egyik változójában bitenként megadhatjuk, hogy pontosan melyik tagjait akarjuk ténylegesen átküldeni a másik fél számára, illetve ebből a változóból a másik fél megfelelően tudja értelmezni a kapott csomagot. Egy kis minimális overheaddel sokat spórolhatunk az üzenetváltásokon, ráadásul a felhasználó számára ez mind átlátszó maradt.

## 3.) Réteges architektúra = connect(connect(connect())))

A kézhez kapott keretrendszerben szépen le voltak választva egymástól a különböző rétegek. Egy külön osztály felelt a QML oldalról jövő szignálok elkapásáért, a felhasználói felület is szépen egymásba ágyazott, újrafelhasználhatóra volt megtervezve. Ennek bővítése azonban néha macerás lehet. Rengeteg idő ment el azzal (azután, hogy megértettük pontosan, hogy ki miért mikor), hogy egy új QML-C++ kapcsolat létrehozásakor nem akart összeállni a rendszer. Nem is csoda, hiszen legalább 6 helyen össze kell kötni a különféle szignálokat és ehhez (közepesen fáradtan) legalább 3x át kell futni az egész kódot, hogy megtaláljuk. Célszerű lett volna erről egy szép ábrát csinálni az elején, hogy pontosan melyik file-ban mit is kell beregisztrálni, és nem minden alkalommal a néhányszáz kódsorból újra és újra kikeresni ezeket.

## 4.) Clean, Close, Open, Build és a sok kis commit a barátunk

Az egyik kódmódosítás után (persze kis commitok nélkül, mert minek) minden alkalommal elszállt a felhasználói felület egy run time hibával. A csillagok sajnos úgy álltak, hogy a hibát debug közben nem lehetett levadászni, ugyanis akkor gyönyörűen futott a kód. Így hát bepótoltam a korábban elcsalt munkát és szépen egyesével átvezettem a változtatásokat egy régebbi commit-re (persze a rossz verzióról csináltam egy backupot is, hogy biztosan kiderüljön mi volt a hiba). Ahogy arra számítottam, az áthordott kis változtatások után mindig szépen futott a kód. Amin viszont meglepődtem, hogy visszatérve a backupolt "rossz" projektre, az is szépen futott. A tippem az, hogy a .pro.user file-ban kicsit összekuszálódott a project (legalábbis a diff csak ebben mutatott különbséget), majd mikor újra megnyitottam a QT Creatorban akkor helyre rakta magát. Legközelebb célszerű ezt megpróbálni először a néhány órás bugvadászat előtt...

## 5.) Szépen kommentezett kódból szép dokumentáció generálható

Most voltunk először "rákényszerítve" arra, hogy generálni kelljen a dokumentációt. Ami egyébként nagyon hasznos, ugyanis így nem kell kétszer leírni ugyanazt, elég csak a forráskódba kommentként. Valamint nagyon jó toolok is vannak, amik nem csak a dokumentálást, hanem a forráskód megértését is segíthetik, Graphvizzel minden függvényhez lehetett hívási fát generálni, amelyből szépen látszik az adatfolyam. Az UML diagramokat Umbrello segítségével készítettem, amely fel tudta parsolni az egész projektet és gyakorlatilag csak össze kellett legózni az osztály diagramokat. Igaz szekvenciadiagramot magától nem generál, de minden segítséget megad ahhoz, hogy az is csak néhány kattintás legyen.

<small>Szerzők: 11. csapat </small>