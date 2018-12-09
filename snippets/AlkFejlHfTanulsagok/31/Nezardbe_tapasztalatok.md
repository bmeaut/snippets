# Nezárdbe! csapat tapasztalatai

Föbb probléma körök, azaz mire figyeljünk: 
# **Telepítés**

A Qt telepítésekor érdemes figyelni a telepítendő összetevők kiválasztásánál. Reflexből az ember a „Next-Next-Select all” algoritmusra van ráállva, ám ez legalább 800 gigabájtnyi adat letöltéséhez vezet. Érdemes ezért körültekintőnek lenni, és figyelmesen megválasztani miket töltünk le az installerrel. Legújabb Qt Creator IDE ajánlott, azon belül:

 - MSVC 2017 compiler 
 - MinGW compiler
 -  Sources 
 - Qt Charts 
 - Qt Data visualization 
 - Qt Purchasing 
 - Qt WebEngine 
 - Qt WebGL streaming Plugin 
 - Qt Script

Ez utóbbiak jól jöhetnek GUI szerkesztéséhez.

## **Ráfordított idő**

Nem érdemes az utolsó pillanatokra hagyna, mert több munkával is járhat egy önálló labor témánál, főleg ha az ember BSc 2. féléve óta nem igazán foglalkozott objektumorientált programozással. Ha valaki hardvert épít, akkor az idő nagy részét ne az vegye el, mert különben nem marad idő a GUI fejlesztésre, ami meglepően trükkös tud lenni, és sok utána olvasást igényelhet egy-egy probléma.

## **Feladatok szétosztása**

A feladatok szétosztása sem tűnt egyszerű feladatnak. Habár az elején egyértelmű volt, hogy az Arduino és a GUI fejlesztés két külön dolog, a GUI fejlesztés megosztása már nem volt triviális. Itt néha sajnos beleestünk abba a hibába, hogy egymás commitjára vártunk, egyébként pedig igyekeztünk kihasználni a Git nyújtotta lehetőségeket.

##  **.qml fájl módosítása**

A .qml fájlban történő módosítás, amely során valami új dolgot szeretnék használni, és include-olni kell hozzá dolgokat meglepően tapasztaltuk, hogy hibát kapunk, még példaprogramok esetében is. Erre egy egyszerű megoldás a „Run qmake” parancs, amely után már hiba nélkül le fog fordulni és el fog indulni a projektunk.

## **.pro file átírása**

Annak érdekében hogy használni tudjuk az alábbi utasítást, azaz tudjunk unique pointert létrehozni az alábbi utasítással, át kell írnunk a .pro fájlt.

    std::make_unique<class >()

A következő sort kell átírni:

    CONFIG  +=  c++11

A következőre:

    CONFIG  +=  c++14

Ekkor az újabb 2014-es szerinti C++-t használjuk és az alábbi utasítás gond nélkül fog futni.

## **Old-Cast style**
A fordító use of old-style cast warning-ot dob, hogy ha egy változót a (vágyott osztály) prefixel kívánunk cast-tolni. (C-s módszerrel)

    Példa: (int)Status::Idle

A warning elkerülése érdekében a c++ cast alternatívákat kell használnunk.

Ezek a következők:

 - const_cast : eltávolítja const/volatile egy konstans változóról
 - dynamic_cast futás idejű validity check-et végez amikor polimorfikus adattípusok között cast-olnál
   
 - static_cast: up/down-cast-et végez az öröklési hierarhiában, futás
   idejű ellenőrzés nélkül konverziót valósít meg implicit tipusok
   között(példa: float to int)    
   
 - reinterpret_cast : cast-olást valósít    meg össze nem függő típusok 
   között

Egy jó tanács: a hallgatók által írt snippeteket érdemes átfutni, vagy problémamegoldás közben ott keresni a már tapasztalt korábbi problémákat megnézni, mert tényleg időt lehet vele spórolni.