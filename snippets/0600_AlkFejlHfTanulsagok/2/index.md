---
layout: default
codename: AlkFejlHf2
title: AlkFejlHf2 (2015 ősz - RobonAut 12. csapat)
authors: 12. csapat (AlkFejl 2015 ősz)
tags: alkfejlhf
---

# Az Alkalmazásfejlesztés házi feladat tanulságai a 12. csapat szerint

Ez a snippet azokat a dolgokat tartalmazza, amit jó lett volna, ha a 12. csapat már a fejlesztés megkezdése előtt tud.

## 1.) Több alprojektből álló projektstruktúra létrehozása a QT Creator fejlesztői környezetben

Legegyszerűbb a File -> New File or Project... -> Other project -> Subdirs project paranccsal létrehozni egy közös főprojektet, közös .pro fájllal az alkalmazásnak
Ekkor a főprojekt nevére jobb gombbal kattintva New Subproject... segítségével adhatunk hozzá új projektfájlokat. 
Ezeknek saját almappa is generálódik, ezt nem érdemes előre létrehozni.
A létrehozott projektstruktúra a mi esetünkben egy unit testeket tartalmazó projektből, egy static library-ből és a főprogramból állt, ezek típusát (Application, Library, Unit Test Project) a létrehozáskor be lehet állítani.
A statikus library hozzáadása kicsivel bonyolultabb, mert a főprogramnak és a unit testeknek is hivatkozniuk kell a generálódó .lib fájlokra.
Ezekre azonban mindig szükségünk van, ha unit testeket használunk a főprogram mellett.
A library projektbe azokat a .cpp és .h fájlokat érdemes tenni, amelyeket az application és a unit testek is használnak (illetve azokat az osztályokat, amelyekre ezek hivatkoznak).

A témáról bővebben: 
	* [Subprojektek létrehozása](http://doc.qt.io/qtcreator/creator-project-creating.html#adding-subprojects-to-projects)
	* [Statikus könyvtár létrehozása](https://wiki.qt.io/How_to_create_a_library_with_Qt_and_use_it_in_an_application)

## 2.) Clean a Build előtt

Ha qml-ben fejlesztünk, észrevehetjük, hogy a qml-fájlokat nem fordítja újra a program egy egyszerű build-re.
Tehát, ha előre tudjuk, hogy a teljes projektet (qml fájlokkal együtt) sokszor kell majd újrafordítanunk, beiktathatunk egy clean lépést a sima build elé is a QT-ben.

Módszer: 
* Projects fül -> Build Steps -> Add Build Step -> Make
* Make arguments: clean
* Az újonnan létrehozott clean-t beállítjuk a build első lépésének.

[A témáról bővebben](http://doc.qt.io/qtcreator/creator-build-settings.html)

## 3.) A shadow buildet érdemes kikapcsolni

A shadow build funkció lényege, hogy a fordítás eredményét a QT Creator egy általunk kijelölt mappába teszi, nem az alapértelmezett Projekt/Debug, illetve Projekt/Release mappákba. 
Erre általában nincs szükség, és nagyon megnehezítheti a fejlesztés folyamatát, például ha nem találjuk a kimeneti fájlokat. 
A QT Creator az újonan létrehozott projektekben automatikusan bekapcsolja a shadow build funkciót, ezt azonban érdemes kikapcsolni az első fordítás előtt a bal oldalon lévő Projects fül Build ablakában.

## 4.) QString elérése a qml oldalról

Amikor qml és cpp fájlok dolgoznak együtt, nehézkes a debuggolás. Bizonyos változóértékek, amik a cpp oldalon még jelen vannak és szimpla debuggolással könnyen ellenőrizhetők, a qml oldalon titokzatos módon eltűnnek, sokszor anélkül, hogy a rendszer hibát dobna.
Ennek tipikus esete a cpp oldalról átküldött QString típusú változó. Ha a qml oldalon a stringet egy Text objektum segítségével akarjuk megjeleníteni, minden gond nélkül működik, azonban ha előtte értékül adjuk egy változónak, majd ezt a változót akarjuk kiírni a felületre, ez nem sikerül.

Egy példa:
A cpp oldalon a következő kódrészlettel adjuk át a változót: 
		
		qmlContext.setContextProperty(QStringLiteral("stateName"), QVariant::fromValue(QString("default")));

Ekkor a következő kódrészlet működni fog:
		
		Text { text: "State: " +  ( stateName!=null ? stateName : "?")  }
		
Azonban ez a kód már nem:
	
		property var statusz_qml : stateName;

		Text { text: "State: " +  ( statusz_qml!=null ? statusz_qml : "?")  }
		
Szerencsére a cpp oldali változók a qml oldalon mindenhonnan közvetlenül elérhetők.

<small>Szerzők: 12. csapat </small>
