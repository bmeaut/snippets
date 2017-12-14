---
layout: default
codename: Tanulságok
title: BAD csapat tanulságai
tags: snippets
authors: Kelemen Attila János, Pesti Bence, Szabados Dávid
---

# BAD csapat által tapasztaltak

Ez a snippet csapatunk által összegyűjtött tapasztalatokat hivatott bemutatni, melyek másoknak a későbbiekben segítséget jelenthetnek.

## 1) A GUI kinézete nem változik

Sokszor abba a hibába estünk, hogy a GUI-nk nem frissült, miközben, mi módosítottunk rajta. Ennek oka az, hogy a QT Creator valamiért rebuild-et igényleg a grafikus felület frissítéséhez.

## 2) GITHUB Desktop alkalmazás

Amikor nekiláttunk a feladatnak rengeteg időt töltöttünk azzal, hogy a GIT-re vártunk míg a többiek gépén is láthatóva váltak a módosítások. Egészen addig nem töltődnek fel a változtatások, míg a jobb felső sarokban nem kattintunk a SYNC gombra.

## 3) QML kasztolás

QML-ben az egyes kasztolási funkciók nem vagy csak nagyon nehézkesen működnek. (Nem olyan rugalmas ebből a szempontból, mint a C.) Érdemes tehát jó előre átgondolni a típusainkat, hogy ne ütközzünk ilyen problémába.

## 4) Képek használata

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
