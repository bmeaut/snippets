---
layout: default
codename: BashBev
title: Bash programozás
tags: linux
authors: Németh Gergely Dániel, Szántó Tamás
---

# Bash programozás
Ebben a snippetben bash scriptek készítését fogjuk megnézni

## Hello world!
Az alábbi kód tartalmazza a hello word programot. A ``!/bin/bash`` a szintaxis-értelmező helyét adja meg, az ``echo`` pedig a kiíró parancs(``man echo``).
```bash
#!/bin/bash
echo "Hello, World!" 
```
Mentsük el ``proba.sh`` néven! Tegyük a fájlt futtathatóvá! ``chmod +x proba.sh ``. Ezek után, ha a könyvtárban állunk ``./`` beszúrásával, egyébként simán a fájl nevével futtathatjuk: ``./proba.sh``. Ezzel kész is a Hello World! alkalmazásunk.

## Változók
A bash-ban van pár speciális, előre definiált változó, például a ``PATH`` a keresési útvonal vagy a ``HOME`` a home könyvtár elérése.

Egy változónak nem kell típust adni, értékadással lehet definiálni ``valtozo=ertek``

A változó értékét a ``$`` használatával kaphatjuk meg. Pl. ha az ``echo`` paranccsal ki szeretnénk írni a ``HOME`` könyvtár helyét, a következőképp tehetjük meg: ``echo $HOME``

Az alábbi példa egy változóban eltárolja a 42 értéket, majd kiírja azt.
```bash
szam=42
echo $szam
```
A változóként megadott számot szövegként tárolja a rendszer, azonban a ``(())`` között van lehetőségünk aritmetikai kifejezéseket is megadni:
```bash
szam=$((6*9))
echo $szam
```

## Elágazás
Hogyan döntjük el, hogy 6*9=42?
```bash
#!/bin/bash
szam=$((6*9))
if [ $szam -eq 42 ]
then
	echo ez az elet ertelme
else
	echo a matematika mast mond
fi
```
A fenti kódból három dolgot emelnék ki: 
 - az ``if``-nek van egy lezárása: a ``fi``
 - a feltételt ``[]`` közé tettük
 - a kiértékelés ``n1 -eq n2`` módon történt
### Feltételek
A ``[feltetel]`` beírásával valójában a ``test`` parancs hívódik meg (``test feltetel``). A ``man test`` meghívásával tanulmányozhatjuk az elérhető feltételek listáját. A leggyakrabban használtak a következők:
 - String
   - ``test s`` - s nem null szöveg
   - ``test -z s`` - s nulla hosszúságú
   - ``test -n s`` - s nem nulla hosszúságú
   - ``test s1 = s2`` - s1 és s2 szöveg megegyezik
   - ``test s1 != s2`` - s1 és s2 szöveg nem egyezik
 - Szám
   - ``test n1 -eq n2`` - n1 = n2
   - ``test n1 -ne n2`` - n1 != n2
   - ``test n1 -lt n2`` - n1 < n2
   - ``test n1 -le n2`` - n1 <= n2
   - ``test n1 -gt n2`` - n1 > n2
   - ``test n1 -ge n2`` - n1 >= n2
 - Fájl
   - ``test -f f`` - f létező állomány
   - ``test -r f`` - f olvasható
   - ``test -w f`` - f írható
   - ``test -d f`` - f könyvtár
   - ``test -s f`` - f létezik és nem 0 hosszúságú

Figyeljünk oda a szóközökre, mert számít!
## Ciklus
Mint az if-nél, itt is figyeljünk arra, hogy a ciklusoknak van lezárása! ``if-fi``, ``do-done``, ``case-esac``.
### For
For ciklussal egyrészt végigmehetünk felsorolva az elemeket:
```bash
for gyumolcs in alma korte szilva
do
  echo $gyumolcs
done
```
Másrészt használhatjuk a C/C++ból megszokott módon:
```bash
for ((i=1;i<=10;i++))
do
  echo $i
done
```
### While, until
Az elől- és hátultesztelős ciklus esetén a szintaxis csak a parancs nevében különbözik:
```bash
i=1
while ((i<=10))
do
  i=$((i+1))
done
```
```bash
i=1
until ((i>10))
do
  i=$((i+1))
done
```
## Gyakorlás
Most már semmi se állíthat meg minket attól, hogy kiírjuk 1-től 100-ig az 5-tel osztható számokat (segítség: a maradékszámítás itt is a ``%``)!
### Megoldás
```bash
#!/bin/bash
for ((i=1;i<=100;i++))
do
	if [ $((i%5)) -eq 0 ]
	then
		echo $i
	fi	
done
```
## Zárszó
A bash programozás ereje abban van, legalábbis szerintem, hogy használhatjuk a linuxban egyébként is használt parancsokat. Az alábbi script például az ``ls``-el kilistázza a könyvtár elemeit, a ``grep``-el szűr a ``.txt`` formátumokra, majd az ``awk``-val az előre megadott módon jeleníti meg az információkat az állományokról (a ``$N`` a tömb N. elemére hivatkozik):
```bash
#!/bin/bash

ls -l |
grep "\.txt" |
awk 'BEGIN{
	print"Könyvtár *.txt adatai:";
	print"--------------------------"}; 
{ 
	printf("%s\t%5s Byte\n",$9,$5); 
	total += $5 };
END { 
	print"--------------------------";
	printf("összesen:\t%5s Byte\n",total);
}'
```

