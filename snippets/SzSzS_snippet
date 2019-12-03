---
layout: default
codename: AlkFejlHf
title: SzSzS csapat tanácsai & tanulságok
tags: snippets alkfejl afhf
authors: Stummer Tamás, Szenczi Máté, Szakály Balázs
---

# Tapasztalataink az alkalmazásfejlesztés házi elkészítése közben

## Mielőtt nekiállnál
* Első tanácsként azt ajánlanám, hogy a fejlesztés megkezdése előtt nagyon hasznos a korábbi évek és csapatok tapasztalatainak átnézése. Gyakorlatilag ez egy olyan aranybánya amit nem éri meg nem kihasználni, elvégre melyik másik tárgyból kapunk ekkora hallgatói visszajelzést és tapasztalatokat?? (talán EMTA kivételével :) )
Vannak a tárgyhoz snippetek, segédanyagok, magyarázós videók (ráadásul nem hindi-angol!) hát használjátok őket! (ha mégsem, ott a google)
* A fejlesztés megkezdése előtt érdemes lehet egyeztetni, és lefektetni hogy pontosan ki milyen feladatokat csinál, és mikorra, hogy a lehető legkevesebb legyen a merge-ek száma. Nyilván mindenki más tudás szinttel indul neki a feladatnak, ezért érdemes ezek alapján megosztani a feladatokat, az idő minimalizálás érdekében. 
* Határpzzatok meg részfeladatokat, és azoknak határidőt (& igyekezzetek be is tartani...)
## A dolog esszenciája :)
### Signal slot
Ne felejtsétek el a header fájlokban is felvezetni a signal és slot-okat, máskülönben nem működik
A Signal - Solt mechanizmus zseniális, érdemes használni. A projektünk jelentős része azon az elven működik, hogy események hatására függvények futnak le, amit újabb eseményeket lőnek el…
```
connect(mSerial, SIGNAL(gotCommand(QString)), this,
SLOT(processSerialData(QString)));
```
### Qmake
Qmake a barátunk. Fejlesztés során sokszor tapasztaltuk, hogy egy teljesen egyértelmű dologra (pl. Egy változó meglétére) dobott hibát a Qt, ilyenkor érdemes nyomni egy Build -> Rrun Qmake -et, és az esetek nagy részében megoldódik a probléma.
### Wrapper osztályok használata
A kényelmes használat érdekében érdemes Wrapper osztályokat kialakítani a Qt-s beépített osztályok felé

Pl.: más olvasni azt hogy:  
```
timer2->startTimer(1000)
```
És más azt hogy:  
```
plotTimer->startTimer(time_interval_plot_ms);
```
### Érték vagy referencia?
Érdemes arra is figyelni fejlesztéskor, hogy érték vagy referencia szerint adunk át egy objektumot egy függvénynek. Egy korai fázisban előfordult hogy a soros kommunikáció kialakítása után az ezért felelős osztályt átadtam egy mellék függvénynek használtara, majd sorozatosan azt a hibát kaptam hogy a kommunikációs csatorna nincs nyitva. Miután smart pointereket használtunk, kíváncsiságból kiírattam a jellemzőit, és utána vettem észre hogy 2db volt az adott objektumból.

### QT beépített osztályok használatakor
Ha furcsa hibákat kapunk build-kor, és használni szeretnénk a QT beépített osztályait, ne felejtsük el a Q_OBJECT parancsot beírni az osztályunkba, és ebből származtatni a classunkat, pl:
```
class Alarm: public QObject
{
	Q_OBJECT
public:
...
}
```
### GIT
GIT - verziókezelésnél érdemes figyelni arra, hogy a commitok “ésszerű” módon kerüljenek be. Ezalatt azt értem hogy ha a csapat ügyesen szervezi a fejlesztés menetét, akkor gyakorlatilag 0-ra csökkenthetők a megoldandó merge conflict-ok. Az alábbi módszer megszívlelendő:
![git_example](image/git_example.png "GIT example")

### Ha úgy érzed mégsem te vagy a hibás
Ha sokadszorra sem klappol valami, és úgy érzed működnie kéne, egy próbát mindenképp megér a jóöreg ***clean - bulid***. Relative sokáig tart, de ha nme oldotta meg, akkor mégis neked kell.
## Végszó
Ez nem a házihoz kapcsolódik, viszont tagja voltam kb annak a 2-3 embernek aki rendszeresen bejárt órára. Szerintem olyan dolgokat, szemléletmódot tanulhattok, amik sokat hozzátok tesznek, érdemes bejárni.
