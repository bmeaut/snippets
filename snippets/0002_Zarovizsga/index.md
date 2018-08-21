---
layout: default
codename: Zarovizsga
title: Alkalmazásfejlesztés záróvizsga tudnivalók
tags: alkfejl zv
authors: Csorba Kristóf
---

# Alkalmazásfejlesztés záróvizsga

FIGYELEM! Ez a snippet az Alkalmazásfejlesztés tantárgyra vonatkozik (VIAUMA09)! Ne keverjétek össze például az Alkalmazásfejlesztési környezetekkel (VIAUAC04)!

A záróvizsgán a tananyag az Alkalmazásfejlesztés tárgy anyagát fedi le, a konkrét kérdések azonban a záróvizsga koncepciójának megfelelően sokkal inkább koncepciókra és témakörökre fókuszálnak és nem alacsony szintű részletekre. A záróvizsgán a kiinduló kérdések az alábbiak lehetnek:

  * Verziókövetés témakör
    * Elosztott és centralizált verziókövetés különbségei (előnyök, hátrányok), a repositoryk szinkronizálása (push, pull, fetch) Git alatt.
    * Csapatmunka git alatt: merge és rebase, git flow (master, development, feature branchek, release branchek, hotfixek stb.)
  * C++14, Qt és QML
    * C++ smart pointerek (unique, shared és weak pointerek)
    * C++ lambda kifejezések, auto kulcsszó és range for
    * Teljes fordítási folyamat Qt alatt (compiler, linker, MOC, QRC mechanizmus, statikus és dinamikus library (DLL) jelentése)
    * A QML és QmlEngine működése
      * QML scriptnyelv, JavaScript, események kezelése, kapcsolat a C++ oldallal
      * QML controlok: listák (model és delegate jelentése), rajzolás (onPaint működése, Context)
    * A signals and slots mechanizmus célja, működése, mi mire fordul le (emit, signal, slot kulcsszavak, a működés alapgondolata és a MOC szerepe)
  * Tervezés
    * SOLID elvek és jelentésük
    * Létrehozási tervezési minták
    * Struktúrális tervezési minták
    * Viselkedési tervezési minták

Minden témakörben, de különösen a tervezéssel kapcsolatos kérdések esetében előfordulhat olyan kérdés, hogy a diplomatervben szerepel-e valamilyen tervezési minta vagy hogyan érvényesülnek a SOLID elvek. Ha nem szerepelnek benne, akkor hogyan lehetne őket felhasználni, alkalmazni.

Néhány konkrétabb példa kérdés:

  * Git alatt visszaállas korábbi állapotra: reset, checkout, detached head, hard reset jelentése
  * Egy pályatervező algoritmus strategy patternként kerül bele egy programba. Hogyan lehet átadni a pályatervezést használó objektumoknak a pályatervezőt (stratégiát) úgy, hogy az a tesztelést is jól támogassa? (dependency injection)
  * Qt alatt hogyan lehet egy PNG fájlt (pl. splash screen) eltárolni az exe fájlban? (QRC, ilyenkor mit generál le a MOC?)
  * Git branching, merge és rebase, push utáni rebase által okozott gond mibenléte és javítása.
  * Valójában mi a branch és mi a HEAD. Mit jelentenek? A .git könyvtárban ezek hogyan jelennek meg?
  * C++11 óta hová tűnt a new operátor? (smart pointerek, működésük)
  * Qt alatt van signals and slots. Mik ezek és hogyan lehet, hogy szabvány C++ fordító (pl. gcc, msvc) le tudja fordítani az ilyen forráskódot?
  * Singleton: hogyan lehet implementálni, többszálú programok esetén mire kell figyelni, milyen nehézséget okozhat egy singleton teszteléskor? (Teszteléskor nehéz lecserélni, nem lehet csak úgy egy másik objektumot átadni a tesztelendő kódnak, ha a függőség egy singleton.)
  * Stringeket összefűzni költséges (miért?), ezen hogy segít a builder minta? (Minden műveletnál új string objektum jön létre, a builder tudja a tartalmát módosítani az összeállítás alatt, nem úgy, mint a QString.)
  * Miért rossz a force push? Mire kényszeríti a többieket és hogyan lehet "visszacsinálni"?
  * Qt C++ alatt mire fordul le az emit kulcsszó? A signal és slot közül melyik sima metódus? Ki írja meg őket?
  * Mi az interaktiv rebase (squashing)? Mire jó?
