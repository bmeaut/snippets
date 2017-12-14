---
layout: default
codename: Tanulságok
title: Faketelen Taxi csapat tanulságai
tags: snippets alkhf alkfjl
authors: KAtona Attila Mihály
---

# Faketelen Taxi csapat tapasztalai

Ez a snippet csapatunk által összegyűjtött tapasztalatokat hivatott bemutatni, melyek másoknak a későbbiekben segítséget jelenthetnek.

## 1) Vonalszenzor értékek megjelenítése

Sokszor abba a hibába estünk, hogy a GUI-nk nem frissült, miközben, mi módosítottunk rajta. Ennek oka az, hogy a QT Creator valamiért rebuild-et igényleg a grafikus felület frissítéséhez.

## 2) QML

Amikor nekiláttunk a feladatnak rengeteg időt töltöttünk azzal, hogy a GIT-re vártunk míg a többiek gépén is láthatóva váltak a módosítások. Egészen addig nem töltődnek fel a változtatások, míg a jobb felső sarokban nem kattintunk a SYNC gombra.

## 3) Build/clean

QML-ben az egyes kasztolási funkciók nem vagy csak nagyon nehézkesen működnek. (Nem olyan rugalmas ebből a szempontból, mint a C.) Érdemes tehát jó előre átgondolni a típusainkat, hogy ne ütközzünk ilyen problémába.

## 4) Qmake

Amennyiben a GUI-ban képeket szeretnénk használni be kell jegyezzük őket a qml.qrc fájlba. Ezt a fájlt a Resources mappában találjuk. Jobb klikk/Open With/Plain Text Editor kombinációval nyitható meg. a fájl. 

## 5) Timerek

Amennyiben a GUI-ban képeket szeretnénk használni be kell jegyezzük őket a qml.qrc fájlba. Ezt a fájlt a Resources mappában találjuk. Jobb klikk/Open With/Plain Text Editor kombinációval nyitható meg. a fájl. 

## 6) Dokumentáció

Amennyiben a GUI-ban képeket szeretnénk használni be kell jegyezzük őket a qml.qrc fájlba. Ezt a fájlt a Resources mappában találjuk. Jobb klikk/Open With/Plain Text Editor kombinációval nyitható meg. a fájl. 

## 7) Rendszerterv készítése, feladatok felosztása

Amennyiben a GUI-ban képeket szeretnénk használni be kell jegyezzük őket a qml.qrc fájlba. Ezt a fájlt a Resources mappában találjuk. Jobb klikk/Open With/Plain Text Editor kombinációval nyitható meg. a fájl. 


Itt egy példa a bejegyzésekre:

```html
<RCC>
    <qresource prefix="/">
		<file>images/breakpedal.png</file>
        <file>images/breakpedal_active.png</file>
        <file>images/key.png</file>
        <file>images/key_active.png</file>
    </qresource>
</RCC>
```
