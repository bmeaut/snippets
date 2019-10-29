---
layout: default
codename: AlkFejlHf39
title: Groot csapat tanuls�gai
authors: Mih�lyi Gergely, Nemes Marcell, Ny�ry L�rinc
tags: alkfejl afhf skipfromindex
---

# Alkalmaz�sfejleszt�s h�zi feladat tapasztalatok

## Fejleszt�si Tapasztalatok

### Verzi�kezel�sr�l

A verzi�kezel�s, �s a t�voli Git repository haszn�lata volt tal�n a legpozit�vabb tapasztalat a feladat megold�sa sor�n. Haszn�lat�val a k�z�s munka g�rd�l�keny tudott lenni, nem kellett k�dokat mozgatni �s �gyelni arra, hogy kin�l van �ppen a legfrissebb verzi�. A be�p�tett merge tool szint�n nagyon hasznosnak bizonyult, amikor egyszerre egy k�dr�szen t�bben dolgoztunk. A konfliktusok t�lnyom� r�sz�t aut�matikusan kezelni tudta, �s csak n�h�ny k�rd�ses esetben kellett k�zzel d�nt�st hozni. A dokument�ci� k�sz�t�se sor�n is nagy segits�g volt a v�ltoztat�sok visszak�vethet�s�ge. 
A feladat megold�sa sor�n a GitKraken-t haszn�ltuk, ami j�l �tl�that�an, �s azonnal jelzi a Qt Creator-ban megtett v�ltoztat�sokat. K�nny� �ttekint�st ada a Git-f�hoz, �s felhaszn�l�bar�t fel�letet a commit �zenetek meg�r�s�hoz.

### A tervez�si megfontol�sok

Az alkalmaz�s elk�sz�t�se sor�n �gyelt�nk arra, hogy minden oszt�ly j�l meghat�rozhat� feladatot l�sson el. P�ld�ul egy k�l�n�ll� oszt�ly felel�s a �modell� -�rt, azaz a kezelt v�ltoz�k �sszefog�s��rt. Ez az oszt�ly nem foglalkozik kommunik�ci�val, vagy megjelen�t�ssel, ezekre k�l�n kommunik�ci�s, k�zvet�t� �s a QML k�z�tt kapcsolatot tart� oszt�lyok vannak. Ez a megk�zel�t�s k�nny� �tl�that�s�got, �s b�v�t�st tesz lehet�v�, hiszen ha lecser�ln�nk p�ld�ul a kommunik�ci�t egy m�sik protokolra, akkor az �zleti logik�t ez teljesen v�ltozatlanul hagyn�, nem k�ne azzal foglalkoznunk, ez mire lehet m�g hat�ssal a k�l�nb�z� k�dokban. Ugyan�gy a megjelen�t�st att�l teljesen f�ggetlen�l tudjuk kezelni, hogy �ppen a megjelen�tett adat, hogy j�n l�tre �s hogy ker�l tov�bb�t�sra.

### Megjelen�t�s �s UI

Mindenkinek tan�csolni tudjuk a QML k�sz�t�s�n�l, hogy import�lj�k a legfrissebb QtQuick objektumokat, mert ezek drasztikusan befoly�solj�k a vez�rl� elemek alap�rtelmezett kin�zet�t, �s eszt�tikusabb, modernebb k�ls�t adnak az alkalmaz�snak. Szint�n fontos tapasztalat volt, hogy b�r nem lebecs�lve a csapat eszt�tikai �rz�k�t, az internet sz�mos el�re elk�sz�tett design-t tartalmaz, melyeket �rdemes megfontolni, �gy az �sszk�p kellemesebb lesz.

![UI](images/ui.JPG "Felhaszn�l�i fel�let")

### Qt signals and slots

A fenti mechanizmussal a h�zi feladat keretei k�z�tt tal�lkoztunk el�sz�r, �s meglep�en g�rd�l�kenyen �s k�nnyen haszn�lhat� megold�s a program r�szei k�zti asszinkron kommunik�ci�ra. Egy k�vetkez� C++ projekt k�sz�t�s�n�l, biztosan alkalmazni fogjuk az itt megtanult patterneket, hogy �tl�that�bb �s hat�konyabb k�dot tudjunk �rni.

## Tesztek �s dokument�ci�
### Felhaszn�l�i tesztek

Mint ahogy a legt�bb GUI k�sz�t�s�n�l, most is hasznosnak bizonyult a v�gs� teszteket egy �laikussal� elv�geztetni. B�r erre a csapat t�bb tagja is alkalmasnak �rezte mag�t, egy nem szak�rt� csal�dtag bevon�sa r�vil�g�tott, hogy a k�sz�t� tudja hova kell kattintatni, �gy sok hib�t nem vesz �szre. Tipikusan ilyen volt a gombok enged�lyez�s�nek szab�lyoz�sa.

### Dokument�ci� k�sz�t�s

Sz�mos f�lrevezet� inform�ci�t tal�lni interneten arr�l, hogy mi a c�lszer� m�dja a dokument�ci� elk�sz�t�s�nek. K�l�n�sen igaz ez, ha a k�l�nb�z� diagrammok k�sz�t�s�t n�zz�k. V�g�l ezekhez a Visual Paradigm programot haszn�ltuk, �s a kommentezett k�d felhaszn�l�s�val tudtunk szint�n sok energi�t sp�rolni a Doxygen miatt. Tanuls�g a j�v�re n�zve, hogy �rdemes azonnal kommentezni, ahogy egy �j sor k�d megsz�letik, �gy a le�rt inform�ci� r�szletesebb, �s ut�lag sokkal kellemetlenebb munka a k�dot visszafejteni.

## �sszefoglal�s

�sszess�g�ben az h�zi feladat elk�sz�t�se sok �j �s hasznos tud�st adott, ami az egyetemi keretekb�l kil�pve is meg�rzi �rt�k�t �s hasznoss�g�t. Ez egyr�szt igaz a felhaszn�lt technol�gi�ra, valamint azokra a fejleszt�si eszk�z�kre, melyek haszn�lat�t a projekt sor�n elsaj�t�tottuk.

<small>Szerz�k: Mih�lyi Gergely, Nemes Marcell, Ny�ry L�rinc</small>