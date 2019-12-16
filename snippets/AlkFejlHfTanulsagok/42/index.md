
---
layout: default     
codename: AlkFejlHf42   
title: RuntimeTerrors csapat tanulságai     
authors: Csókási Marcell, Fekete Marcell, Majer Imre    
tags: alkfejl afhf skipfromindex
---


# RuntimeTerrors csapat által levont tanulságok

Csapattagok:
* Csókási Marcell
* Fekete Marcell
* Majer Imre

## Git megfelelő használata 

A git használatát, aki még nem ismeri, érdemes a legelején elsajátítani és használni a szoftverfejlesztés mindennapjaiban használt koncepciókat.  

Amit egyáltalán ne csináljunk, hogy mindenki ugyanazon a branch-en fejleszt. Sok fejfájástól menthet meg minket, hiszen a folyamatos pull és push-olás ugyanarra a branch-re több mint valószínű, hogy conflictokat fog okozni és ezt itt sokkal nehezebb kijavítani, mint egy másik branch-en. Így célszerű minden csapattagnak létrehoznia egy-egy saját branchet, ahol fejleszti a saját dolgait, majd **PullRequest** formájában merge-elni a **master branch**-re. 

Ezen felül érdemes még az elején letölteni egy olyan **alkalmazást**, ahol egyszerű **verziókezelni** (és merge-elni!). (GitHub Desktop, és VSCode nem annyira alkalmas a merge-re, de az alapműveletekre igen, merge-re én például IntelliJ-t használtam, mivel abban vagyok járatos a mindennapokban) 

## QVector 

Ez egy kis apróság..  Amikor TCP socket-en küldtük át, úgy próbáltuk, hogy először elküldtük a vector méretét és utána a vectort, socketből kiolvasva pedig ugyanez. Ekkor mindenféle memóriaszemetet találtunk.. Mint kiderült a QVector alapból úgy megy át a socketen, hogy elküldi előre a méretét, így nekünk ezt már nem kellett pluszban megtenni. 

## TeamViewer használata

Az együttműködést és a konzultációkat számunkra jelentősen megkönnyítette a TeamViewer nevű alkalmazás. Ezen keresztül meg tudjuk osztani a képernyőnket több emberrel is, akik még távoli vezérlési jogot is kapnak, így tulajdonképpen online Pair Programmingra is lehet használni (mint ahogy mi használtuk is). Közösen könnyebben lehet hibát keresni, illetve megtervezni egy-egy új feature megvalósítását. Érdemes kombinálva használni valamilyen online beszélgetőplatformmal. 

## Clean Code 

Amikor közösen dolgoztok együtt egy projekten, akkor tűnik ki igazán, hogy mennyire fontos a clean code elvek betartása. Ha esetleg egy csapattársnak bele kell nyúlnia a másik társa kódjába, mert éppen olyasmit fejleszt (ilyen biztos lesz), akkor hálás lesz, ha nem spagetti kódba kell belefejlesztenie, hanem egy jól struktúrált, jó megnevezésekkel teli kódba.  

A legfontosabb dolgok, amiket mindenképp tartsunk szem előtt: 

* Beszédes neveket alkalmazzunk. Ha egy jó nevet találunk ki egy-egy függvénynek vagy változónak, akkor kommentelni sem kell a kódot (sőt zavaró is lesz) 

* Egy függvénynek egyetlen feladata legyen. Ha több dolgot csinál egy függvény, akkor inkább bontsuk fel azt, több, kisebb, de egyetlen feladatot ellátó függvényre (na de túlzásokba sem kell esni). Ezzel elkerüljük, hogy egy-egy függvény 100 sorosra hízzon és átláthatatlan legyen. 

* A közös dolgokat szervezzük ki. Esetünkben például a hibakezelésre egy külön osztályt hoztunk létre a hibakódoknak, amelyet több osztály is használhatott. 

## Változók inicializálása 

Ezt főleg akkor hajlamos elfelejteni az ember, ha valamilyen modernebb programozási nyelvvel dolgozik a mindennapokban. Vissza kell térnünk a C-s világba és mindent inicializálni. Mi egy állapotgép implementálása közben futottunk bele ebbe, elfelejtettünk kezdőállapotot inicializálni és mindenféle furcsaság történt :) 