---
layout: default
codename: QtQmlFocus
title: QtQml Focus
tags: snippets qt qml focus
authors: Nemkin Viktória
---

# Qt Qml Focus

## Kiinduló alkalmazás

A bemutatót egy nagyon egyszerű Hello World alkalmazással kezdjük.

```javascript
import QtQuick 2.7
import QtQuick.Controls 2.0

ApplicationWindow {

    visible: true
    width: 640
    height: 480
    title: qsTr("Hello World")

}
```

## Debuggolás

A fókuszproblémák debuggolása nehéz feladat, mivel a felületi elemek nagy részénél nem látszik hogy fókuszban vannak-e éppen vagy sem. (Ez alól például a TextField kivétel, hiszen ott a villogó kurzor jelzi.)

Első lépésként ezért szúrjuk be a következő kódot az ApplicationWindow törzsébe.

```javascript
onActiveFocusItemChanged: {
    console.log("Actvie focus changed! -----------------------")
    var object = activeFocusItem
    while(object) {
        console.log(object.objectName + " " + object.toString() + " AF: " + object.activeFocus + " F: " + object.focus)
        object = object.parent
    }
}
```

A fenti kódrészlet minden esetben meghívódik amikor az ApplicationWindow érzékeli hogy másik (nem feltétlenül közvetlen) gyereke került fókuszba. Az éppen fókuszban lévő gyermekét az activeFocusItem nevű propertyjén keresztül érhetjük el.

Ebből az objektumból kiindulva felmászunk az objektumfán egészen a root elemig és minden megtalált szülő elemről kiírjuk az alábbiakat:

* Az objectName propertyt manuálisan beállíthatjuk a komponenseinken, így könnyebb beazonosítani a felületi elemeket.
* Az object.toString() az objektum típusát és memóriacímét írja ki, számunkra főleg az előbbi érdekes, hiszen így nem kell a teljes alkalmazásunkat telerakni objectName-kkel ha egyébként azokat nem használnánk.
* Az activeFocus és a focus propertyk segítségével tudjuk meghatározni melyik elem kerüljön fókuszba, ezekről lesz a továbbiakban részletesebben szó.

### Jó tanács

Ha ilyen nehézkesen látható problémákat szeretnénk javítani saját alkalmazásunk fejlesztésekor érdemes minden változtatás után manuálisan teljesen kitörölni a build könyvtárat. A qmake ugyanis még nem tökéletes, néha előfordul, hogy bizonyos változtatásokat nem érzékel a qml fájlokban és nagyon sokáig lehet keresni a hibát 'Miért nem működik?' amikor a mi kódunk működne csak éppen nem azt a verziót látjuk futni.

## Működése

* Ha az activeFocus propertyje az Itemnek true akkor jelenleg ez az Item van fókuszban. Ez egy csak olvasható property.

* Az egész applikációban egyetlen egy Itemnek lehet az activeFocus propertyje true, hiszen egyszerre egyetlen objektum lehet csak fókuszban. (Speciális objektumok a FocusScopeok, erről később.)

* Ha egy item focus propertyje true-ra van állítva, akkor ez azt jelenti hogy ez az Item szeretne activeFocust kapni. Ezt nem feltétlenül fogja megkapni.

* Ha a jelenleg betöltött qml komponensek között több mint egy Itemen található focus: true property, az hogy közülük ki fogja megkaptni az activeFocust nincs specifikálva a Qt dokumentációja szerint. A háttérben valójában a komponensek betöltési sorrendje dönti el, amit pedig a forráskódbeli elhelyezésük, azonban egy jó programozó nem használ ki nem specifikált viselkedést.

### Alkomponensek esetén

* Az ember azt hinné, hogy ha egy Item A-nak gyereke Item B akkor Item A-n egy focus:false property megakadályozza hogy Item B fókuszba kerüljön.  Ha pedig Item A-n focus:true property van beállítva akkor Item B-nek van esélye fókuszba kerülni. (Példáula visible property így működik.) Pontosan ellentétesen működik a focus property.

* Ha az Item A-n a focus propertyt igazra állítjuk akkor ez azt jelenti, hogy a gyerekei közül egyik sem kerülhet fókuszba. Az objektumfában a fókusz terjedése megáll, megakad amint elér egy olyan Itemet, amelynek a focus propertyje igazra van állítva, vagyis a gyerekei nem kerülhetnek automatikusan aktív fókuszba. Természetesen a felhasználó klikkeléssel vagy tabulátorral fókuszba tudja hozni az adott Itemet, kizárólag induláskor az automatikusan kisztott fókuszt akadályozza ez meg.

* Ha egy Itemen a focus propertyt hamisra állítjuk, az nem fogja megakadályozni hogy a gyerekei fókuszba kerülhessenek.

* Egy jó módszer arra, hogy szabályozni tudjuk melyik Item kaphat aktív fókuszt az alkalmazásunkban az, hogy mindig kizárólag egyetlen Item focus propertyjét állítjuk igazra. Ezt könnyen el lehet érni, hiszen a QML property bindingja segítségével egyszerű feltételrendszert köthetünk a focus propertykhez. Kisebb alkalmazásokban ez elegendő.

* Nagyobb, bonyolultabb alkalmazásokban ennek a módszernek a használata exponenciálisan nehézzé válhat a rengeteg komponens miatt. Itt jön képbe a FocusScope, ami a következőképpen működik: Ha egy FocusScope focus propertyje igazra van állítva és megkapja az aktív fókuszt akkor ezt tovább terjeszti a gyermekei felé (a FocusScopeon belül ugyanazok a szabályok érvényesek mint egy egyszerű alkalmazásban, egyszerre csak egy Item kaphat fókuszt).

* Ez pont az ellenkezője annak ahogyan az Item működik: a focus property hamisra állításával a FocusScope nem fogja engedni, hogy a gyerekei fókuszba kerülhessenek. Ha igazra állítjuk akkor pedig ez nem fogja megakadályozni azt.

* Egymásba ágyazott FocusScopek is működnek: ha mindnek igazra van állítva a focus propertyje akkor az aktív fókusz le tud jutni mindhez és elterjedni a szülő-gyerek láncban a legalsó szintekre.

* Létezik egy függvény, a forceActiveFocus(), amely az Item minden közvetlen felmenőjén, ami FocusScope beállítja a focus propertyt truera. Ez jól jön ha sok egymásba ágyazott FocusScope-on belül van az Item.
