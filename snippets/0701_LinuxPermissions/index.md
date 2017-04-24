---
layout: default
codename: LinuxPermissions
title: Linux jogosultság-kezelés
tags: linux
authors: Németh Gergely Dániel, Szántó Tamás
---

# Linux jogosultság-kezelés

Ez a snippet a linux jogosulság-kezeléséről szól. Megismerkedünk a jogokkal és csoportokkal.

## Állomány jogosultságainak kiírása

Egy állomány jogosultságainak lekérdezésére a legegyszerűbb megoldás az ``ls -l <filename>`` használata. Pl. ``ls -l level.txt``

A parancsot kiadva az válasz első oszlopában ehhez hasonlót kell látnunk: ``-rwxr-xr-x`` De mit is jelent ez?

A fenti sor négy oszlopba bontható: ``-``|``rwx``|``r-x``|``r-x`` Az első csoport jól láthatóan különbözik a többitől. Valóban, ennek más a jelentése, míg a többi megegyező tartalmú.

### Állomány típusa

Az első oszlopban az állomány típusát olvashatjuk. Az itt előforduló rövidítések jelentése a következő:

 -  d (directory)
 -  c (character device)
 -  l (symlink)
 -  p (named pipe)
 -  s (socket)
 -  b (block device)
 -  D (door)
 -  \- (regular file)

### Tulajdonos, csoport, mindenki más (owner, group, other)

A következő három oszlop a tulajdonos, a csoport és mindenki más számára a fájlon végezhető műveletek olvashatóak.
 
 - owner(u): a fájl létrehozója
 - group(g): a fájlhoz hozzárendelt csoportokba tartozó felhasználók
 - other(o): mindenki más
 - all user(a): minden felhasználó

### Írás, olvasás, végrehajtás (Read, Write, eXecute)

Az ``rwx`` hármas az írási, olvasási és futtatási jogot jelenti. Ha ``-`` szerepel az egyik helyén, azt jelenti, hogy az a felhasználókör nem rendelkezik az adott jogosultsággal.

A fent látható ``rwxr-xr-x`` jogkör tehát azt jelenti, hogy a tulajdonosnak lehetősége van a fájlt írni, olvasni és futtatni, a csoportnak és mindenki másnak pedig olvasni és futtatni.

Az oktális írásmód: az ``rwxr-xr-x`` jogkör előfordul az alábbi írásmódban is: ``755``. Hogy keletkezett ez a szám? A már megismert oszlopokra bontva: ``rwx``|``r-x``|``r-x``. Most a jogosulságok helyére ``1``-et, a tiltások helyére ``0``-t írva: ``111``|``101``|``101``, ami kettes számrendszerben éppen a ``7``|``5``|``5``-nek felel meg.

## Jogosultság váltás (chmod)

Egy fájl jogosultságainak állítására szolgál a chmod parancs.

 - ``chmod 755 <filename>`` a fájlnak a fent megbeszélt 755 jogkört adja.
 - ``chmod u+rwx <filename>`` a ``+`` jellel a tulajdonosnak(``u``) írási, olvasási és futtatási jogot adunk (``rwx``)
 - ``chmod g+x <filename>`` a csoport(``g``) számára futtathatóvá teszük az állományt
 - ``chmod a-rwx <filename>`` mindenkitől(``a``) minden jogot megvonunk(``-``)

## Tulajdonosváltás (chown, chgrp)
A ``chown`` paranccsal állítható a tulajdonosi és csoporti jogkör.

 - ``chown <user> <filename>`` a fájl tulajdonosának a felhasználót nevezi ki
 - ``chown <user>:<group> <filename>`` a fájlnak a felhasználó lesz a tulajdonosa és hozzárendeli a csoporthoz
 - ``chown -R <user> <directory>`` a könyvtárt és tartalmát rekurzívan a felhasználó tulajdonába teszi

A ``chgrp`` paranccsal a fájl csoportja állítható. A ``chown :<group> <filename>`` és a ``chgrp <group> <filename>`` parancs ugyanazt hajtja végre.

## Sudo

A ``sudo`` paranccsal fájlokat hajthatunk végre más felhasználóként. A szó a *su* és a *do* részekből tevődik össze, az előbbi egy különálló parancs, az adott felhasználóként indít egy terminált. Az utóbbi az angol csinálni szót jelenti.

Ha nincsen felhasználó megadva (ez a leggyakrabban használt eset) *superuser*ként futtatja az állományt, amennyiben a felhasználónak van jogköre ehhez és megadja a jelszavát.
