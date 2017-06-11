---
layout: default
codename: QtQmlFocus
title: QtQml Focus
tags: snippets qt qml focus
authors: Nemkin Viktória
---

# Qt Qml Focus

## Kezdetek

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

### Debuggolás

A fókuszproblémák debuggolása nehéz feladat, mivel a felületi elemek nagy részénél nem látszik, hogy fókuszban vannak-e éppen vagy sem. (Ez alól például a TextField kivétel, hiszen ott a villogó kurzor jelzi.)

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

* Az objectName propertyt manuálisan beállíthatjuk a komponenseinken, így könnyebb megkülönböztetni a felületi elemeket.
* Az object.toString() az objektumról ad információkat, számunkra az objektum típusa érdekes, hiszen így nem kell a teljes alkalmazásunkat telerakni objectName-kkel, enélkül is nagyjából be tudjuk azonosítani ki kicsoda.
* Az activeFocus és a focus propertyk segítségével tudjuk meghatározni melyik elem került/kerüljön fókuszba, ezekről lesz a továbbiakban részletesebben szó.

### Jó tanács

Ha ilyen nehézkesen látható problémákat szeretnénk javítani saját alkalmazásunk fejlesztésekor érdemes minden változtatás után manuálisan teljesen kitörölni a build könyvtárat. A qmake ugyanis még nem tökéletes, néha előfordul, hogy bizonyos változtatásokat nem érzékel a qml fájlokban és nagyon sokáig lehet keresni a hibát 'Miért nem működik?' amikor a mi kódunk jó lenne csak éppen még egy régebbi verziót látunk futtatáskor.

## Egyszerű alkalmazások

A fókusz kezeléséhez QML-ben két fontos propertyt tudunk használni.

**Focus property:** Alapvetően minden komponensre false a default értéke, a programozó kézzel állíthatja be igazra. Ha az értéke igazra van állítva az azt jelenti hogy ez a komponens *szeretne* fókuszba kerülni.

**ActiveFocus property:** Ez egy csak olvasható property amely akkor válik igazzá, hogyha a komponens elnyerte a fókuszt.

### Egyszerű példa

Szúrjuk be az alábbi két TextFieldet az ApplicationWindow törzsébe!

```javascript
    TextField  {
        id: elso
        objectName: "elso"
        text: "Első: " + (focus ? "Fókuszt kér, " : "Fókuszt nem kér, ") + (activeFocus ? "fókuszt kap." : "fókuszt nem kap.")
        width: 300
        height: 30
        anchors.horizontalCenter: parent.horizontalCenter
    }

    TextField {
        id: masodik
        objectName: "masodik"
        text: "Második: " + (focus ? "Fókuszt kér, " : "Fókuszt nem kér, ") + (activeFocus ? "fókuszt kap." : "fókuszt nem kap.")
        width: 300
        height: 30
        anchors.top: elso.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: parent.horizontalCenter
    }
```

Elindítottam az alkalmazást, ráklikkeltem az első majd a második TextField-re, majd bezártam az alkalmazást. A debug konzolon az alábbiak jelentek meg:

```console
Debugging starts
QML debugging is enabled. Only use this in a safe environment.
QML Debugger: Waiting for connection on port 8624...
qml: Actvie focus changed! -----------------------
qml:  QQuickItem(0x2b687a853b0) AF: true F: true
qml:  QQuickRootItem(0x2b687904cd0) AF: true F: true
qml: Actvie focus changed! -----------------------
qml: elso QQuickTextField(0x2b70c22e390, "elso") AF: true F: true
qml:  QQuickItem(0x2b687a853b0) AF: true F: true
qml:  QQuickRootItem(0x2b687904cd0) AF: true F: true
qml: Actvie focus changed! -----------------------
qml: masodik QQuickTextField(0x2b687a78880, "masodik") AF: true F: true
qml:  QQuickItem(0x2b687a853b0) AF: true F: true
qml:  QQuickRootItem(0x2b687904cd0) AF: true F: true
qml: Actvie focus changed! -----------------------
Debugging has finished
```

Látható, hogy induláskor csak a gyökérelem fókuszálódik. Ez nem ApplicationWindow típusú, mivel az ApplicationWindowba tett komponensek az ApplicationWindow contentItem nevű, QQuickRootItem típusú propertyjét kapják meg szülőnek. Ezért látunk ezt az elemet a listában először.

Ha beleklikkelünk az első TextFieldbe a következő képet fogjuk látni:

![Fókuszt kér, fókuszt kap.](image/01_fokuszt_ker_fokuszt_kap.png "Fókuszt kér, fókuszt kap.")

A második TextFieldbe klikkelés hasonlóan néz ki.

Ha másik ablakra klikkelünk (jelen esetben én a QtCreator ablakára klikkeltem a leállításhoz) azáltal a teljes alkalmazás fókusza elveszik. Ilyenkor a focus propertyje a TextFieldnek igaz marad, tehát amint visszaváltunk erre az ablakra ismét ez a TextField fog fókuszba kerülni.

![Fókuszt kér, fókuszt nem kap.](image/02_fokuszt_ker_fokuszt_nem_kap.png "Fókuszt kér, fókuszt nem kap.")

Nézzük meg mi történik ha hozzáadunk egy

```javascript
focus: true
```
sort például a második TextField törzsébe és úgy indítjuk el az alkalmazást!

Azt fogjuk tapasztalni, hogy induláskor azonnal a második TextField fókuszálódik. Nem kellett beleklikkelnünk!

![Fókusz automatikusan.](image/03_fokusz_automatikusan.png "Fókusz automatikusan.")

Ez jól jön olyan oldalak fejlesztésekor ahol a felhasználótól azonnal inputot fogunk kérni (például felhasználónév - jelszó párost). Ilyenkor megspóroljuk a usernek azt a kellemetlenséget hogy neki kelljen ráklikkelnie a megfelelő mezőre, hogy az adatait megadhassa.

### Property bindinggal

Nézzünk egy kicsit bonyolultabb példát!

Tegyük fel, hogy olyan alkalmazást írunk ahol opcionálisan megadható a felhasználó email címe. Először be kell jelölnünk hogy igen, meg szeretnénk adni az email címünket és utána írhatjuk be a megfelelő mezőbe.

Illesszük be a következő, ezt megvalósító kódot az ApplicationWindow törzsébe:

```javascript
   RadioButton {
        id: radio
        objectName: "radio"
    }

    Text {
        id: question
        objectName: "question1"
        text: "Would you like to give me your email address?"
        anchors.left: radio.right
        anchors.verticalCenter: radio.verticalCenter
    }

    TextField  {
        id: email
        objectName: "email"
        width: 300
        height: 30
        anchors.top: radio.bottom
        focus: radio.checked
        enabled: radio.checked
    }
```

Indítsuk be az alkalmazást!

![Email nincs fókuszban.](image/04_email_nincs_fokuszban.png "Email nincs fókuszban.")

Kapcsoljuk be a RadioButtont!

![Email fókuszban.](image/05_email_fokuszban.png "Email fókuszban.")

A property binding segítségével a focus property igazzá válik amint a RadioButtont bekapcsoljuk és a TextField fókuszba kerül. Így a usernek nem kellett külön beleklikkelnie a mezőbe, hanem rögtön kezdheti írni az email címét.

A konzolon eközben az alábbi kimenet látható:

```console
Debugging starts
QML debugging is enabled. Only use this in a safe environment.
QML Debugger: Waiting for connection on port 10680...
qml: Actvie focus changed! -----------------------
qml:  QQuickItem(0x197f2bc91a0) AF: true F: true
qml:  QQuickRootItem(0x197f2a65880) AF: true F: true
qml: Actvie focus changed! -----------------------
qml: radio QQuickRadioButton(0x197f2a98900, "radio") AF: true F: true
qml:  QQuickItem(0x197f2bc91a0) AF: true F: true
qml:  QQuickRootItem(0x197f2a65880) AF: true F: true
qml: Actvie focus changed! -----------------------
qml: email QQuickTextField(0x19837153fe0, "email") AF: true F: true
qml:  QQuickItem(0x197f2bc91a0) AF: true F: true
qml:  QQuickRootItem(0x197f2a65880) AF: true F: true
qml: Actvie focus changed! -----------------------
Debugging has finished
```

Az alkalmazás bekapcsolása után rákattintottunk a RadioButtonre, ami emiatt fókuszba került. A klikkelésünk eredménye az lett, hogy a RadioButton checked propertyjének értéke igaz lett. Emiatt aktiválódott a hozzá tartozó property binding és a TextField focus propertyjének értékébe belemásolódott a checked új értéke. Ennek hatására a TextField elkérte és meg is kapta az aktív fókuszt.

A szépség kedvéért az enabled propertyt is ugyanezen mechanizmus mentén kezeltem, így nem is lehet írni a mezőbe ha nem engedélyezett az email megadása.

### Konkurens fókuszkérések

Próbáljuk ki mi történik ha egynél több komponensre tesszük rá a focus propertyt!

```javascript
    TextField  {
        id: elso
        objectName: "elso"
        text: "Első: " + (focus ? "Fókuszt kér, " : "Fókuszt nem kér, ") + (activeFocus ? "fókuszt kap." : "fókuszt nem kap.")
        width: 300
        height: 30
        focus: true
        anchors.horizontalCenter: parent.horizontalCenter
    }

    TextField {
        id: masodik
        objectName: "masodik"
        text: "Második: " + (focus ? "Fókuszt kér, " : "Fókuszt nem kér, ") + (activeFocus ? "fókuszt kap." : "fókuszt nem kap.")
        width: 300
        height: 30
        anchors.top: elso.bottom
        anchors.topMargin: 10
        focus: true
        anchors.horizontalCenter: parent.horizontalCenter
    }
```

![Konkurens fókusz.](image/06_konkurens_fokusz.png "Konkurens fókusz.")

A második elem focus propertyje hamis, pedig beleégettük a kódba hogy igaz legyen! Tehát a Qt motorja nem engedélyez egyszerre egynél több igaz fókusz propertyt. A prioritási sorrend nem dokumentált része a Qt-nek, de valójában attól függ, hogy melyik komponenst deklaráltuk előrébb. Szoftverfejlesztés során erre a tulajdonságára ne támaszkodjunk, hiszen bármikor megváltozhat egy frissítéssel.

### Összefoglaló

Egyszerű alkalmazások esetén a focus property használatával programozottan tudjuk irányítani, hogy a felhasználói felületen éppen mi kerüljön fókuszba. Ehhez annyit kell tennünk, hogy a megfelelő pillanatban a megfelelő elemen a focus propertyt igazra állítjuk.

Hogy éppen melyik komponens van fókuszban az az activeFocus read-only propertyből derül ki, az éppen fókuszált elemen és annak a szülein lesz 

Ha az activeFocus propertyje az Itemnek true akkor jelenleg ez az Item van fókuszban. Ez egy csak olvasható property.

A focus propertyk programozott beállítását property binding segítségével célszerű végezni, hiszen ezek automatikusan aktiválódnak ha megváltozik az értéke és így nagyon könnyű bizonyos feltétlekkel megszabni hogy mikor hova kerüljön a fókusz az alkalmazásban.

* 

* Az egész applikációban egyetlen egy Itemnek lehet az activeFocus propertyje true, hiszen egyszerre egyetlen objektum lehet csak fókuszban. (Speciális objektumok a FocusScopeok, erről később.)

* Ha egy item focus propertyje true-ra van állítva, akkor ez azt jelenti hogy ez az Item szeretne activeFocust kapni. Ezt nem feltétlenül fogja megkapni.

* Ha a jelenleg betöltött qml komponensek között több mint egy Itemen található focus: true property, az hogy közülük ki fogja megkaptni az activeFocust nincs specifikálva a Qt dokumentációja szerint. A háttérben valójában a komponensek betöltési sorrendje dönti el, amit pedig a forráskódbeli elhelyezésük, azonban egy jó programozó nem használ ki nem specifikált viselkedést.

## Összetett alkalmazások

### Összefoglaló

* Az ember azt hinné, hogy ha egy Item A-nak gyereke Item B akkor Item A-n egy focus:false property megakadályozza hogy Item B fókuszba kerüljön.  Ha pedig Item A-n focus:true property van beállítva akkor Item B-nek van esélye fókuszba kerülni. (Példáula visible property így működik.) Pontosan ellentétesen működik a focus property.

* Ha az Item A-n a focus propertyt igazra állítjuk akkor ez azt jelenti, hogy a gyerekei közül egyik sem kerülhet fókuszba. Az objektumfában a fókusz terjedése megáll, megakad amint elér egy olyan Itemet, amelynek a focus propertyje igazra van állítva, vagyis a gyerekei nem kerülhetnek automatikusan aktív fókuszba. Természetesen a felhasználó klikkeléssel vagy tabulátorral fókuszba tudja hozni az adott Itemet, kizárólag induláskor az automatikusan kisztott fókuszt akadályozza ez meg.

* Ha egy Itemen a focus propertyt hamisra állítjuk, az nem fogja megakadályozni hogy a gyerekei fókuszba kerülhessenek.

* Egy jó módszer arra, hogy szabályozni tudjuk melyik Item kaphat aktív fókuszt az alkalmazásunkban az, hogy mindig kizárólag egyetlen Item focus propertyjét állítjuk igazra. Ezt könnyen el lehet érni, hiszen a QML property bindingja segítségével egyszerű feltételrendszert köthetünk a focus propertykhez. Kisebb alkalmazásokban ez elegendő.

* Nagyobb, bonyolultabb alkalmazásokban ennek a módszernek a használata exponenciálisan nehézzé válhat a rengeteg komponens miatt. Itt jön képbe a FocusScope, ami a következőképpen működik: Ha egy FocusScope focus propertyje igazra van állítva és megkapja az aktív fókuszt akkor ezt tovább terjeszti a gyermekei felé (a FocusScopeon belül ugyanazok a szabályok érvényesek mint egy egyszerű alkalmazásban, egyszerre csak egy Item kaphat fókuszt).

* Ez pont az ellenkezője annak ahogyan az Item működik: a focus property hamisra állításával a FocusScope nem fogja engedni, hogy a gyerekei fókuszba kerülhessenek. Ha igazra állítjuk akkor pedig ez nem fogja megakadályozni azt.

* Egymásba ágyazott FocusScopek is működnek: ha mindnek igazra van állítva a focus propertyje akkor az aktív fókusz le tud jutni mindhez és elterjedni a szülő-gyerek láncban a legalsó szintekre.

* Létezik egy függvény, a forceActiveFocus(), amely az Item minden közvetlen felmenőjén, ami FocusScope beállítja a focus propertyt truera. Ez jól jön ha sok egymásba ágyazott FocusScope-on belül van az Item.
