---
layout: default
codename: Zarovizsga
title: Alkalmazásfejlesztés záróvizsga tudnivalók
tags: alkfejl zv
authors: Csorba Kristóf
---

# Alkalmazásfejlesztés záróvizsga

FIGYELEM! Ez a snippet az Alkalmazásfejlesztés tantárgyra vonatkozik (VIAUMA09)! Ne keverjétek össze például az Alkalmazásfejlesztési környezetekkel (VIAUAC04)!

Mivel a tematika 2020. őszén megváltozott (C++ és Qt helyett C# és .NET UWP), ezért mindenki az általa hallgatótt anyagból záróvizsgázik, a nektek megfelelő részt vegyétek figyelembe!

A záróvizsgán a tananyag az Alkalmazásfejlesztés tárgy anyagát fedi le, a konkrét kérdések azonban a záróvizsga koncepciójának megfelelően sokkal inkább koncepciókra és témakörökre fókuszálnak és nem alacsony szintű részletekre. A záróvizsgán a kiinduló kérdések például az alábbiak lehetnek:

# Tematika 2020. ősztől (C# és .NET UWP)

  * C#
    * Delegate típusok és események
    * IEnumerable és Linq
    * Sorosítás, XML és JSON
    * Kommunikáció, HttpClient
    * Entity Framework
    * Tesztelés: unit tesztek, Test Driven Development, mockolás és Moq package
  * UWP témakör
    * A xaml nyelv: szintaxis alapok, mire jó. Layout managerek, statikus erőforrások, adatkötés (x:Bind) beállításai, kapcsolat a .xaml és a .xaml.cs fájlok között.
    * Rajzolás, a Shape osztály
    * MVVM architektúra elemei, hol van adatkötés, INotifyPropertyChanged esemény jelentősége
  * Tervezés
    * Dependency injection
    * SOLID elvek és jelentésük
    * Test Driven Development
    * Létrehozási tervezési minták
      * Factory és abstract factory
      * Singleton
    * Parancsvégrehajtási minták
      * Command, CommandProcessor
      * Memento
    * További tervezési minták a tananyagból
      * Observer
      * Adapter
      * Facade
      * Composite
      * Prototype
      * Proxy
      * Builder
      * State

Minden témakörben, de különösen a tervezéssel kapcsolatos kérdések esetében előfordulhat olyan kérdés, hogy a diplomatervben szerepel-e valamilyen tervezési minta vagy hogyan érvényesülnek a SOLID elvek. Ha nem szerepelnek benne, akkor hogyan lehetne őket felhasználni, alkalmazni.

Néhány konkrétabb példa kérdés:

  * Egy pályatervező algoritmus strategy patternként kerül bele egy programba. Hogyan lehet átadni a pályatervezést használó objektumoknak a pályatervezőt (stratégiát) úgy, hogy az a tesztelést is jól támogassa? (dependency injection)
  * Singleton: hogyan lehet implementálni, többszálú programok esetén mire kell figyelni, milyen nehézséget okozhat egy singleton teszteléskor? (Teszteléskor nehéz lecserélni, nem lehet csak úgy egy másik objektumot átadni a tesztelendő kódnak, ha a függőség egy singleton.)
  * A xaml adatkötés és az INotifyPropertyChanged melyik tervezési mintának felel meg? Hogyan működik és mire kell figyelni az adatkötött propertyk setterjében?
  * Entity Framework használata esetén nem kell SQL lekérdezéseket írni a forráskódba, az adatbázist nem táblák soraiként érjük el. Hogyan működik ehelyett?
  * Mi a feladata UWP alatt egy layout managernek? Mondjon pár példát Layout Managerre.
  * Mire jó a Dependency Injection? Hogyan szokás átadni a függősegeket egy osztálynak?
  * Mi a kapcsolat a .xaml és .xaml.cs fájlok között? Melyik tartalma melyik osztályba kerül?
  * Unit tesztek készítésekor mikor van szükség egy osztály mockolására?
  * A dependency injection mit jelent? Mivel könnyíti a tesztelhetőséget? Miért nem jó, ha a függőségeket a konstruktor példányosítja? Mi a különbség, ha konstruktor paraméterként vagy propertynek adjuk át a függőséget? Mit jelent a mockolás?
  * Mire ad megoldást az Observer minta? Hogyan tudunk változást detektálni, ha nem használjuk? Milyen szereplői vannak? UWP XAML környezetben hogyan jelenik meg? Mire jó az INotifyPropertyChanged interfész és hogyan működik az x:Bind?
  * Mutassa be a Builder mintát a StringBuilder klasszikus megoldáson keresztül. Miért választjuk le ezeket a funkciókat a string osztályról? Miben tér el a Builder, a Factory és a Prototype minta?

# Tematika 2019. őszi félévvel bezárólag (C++ és Qt)

  * Verziókövetés témakör
    * Elosztott és centralizált verziókövetés különbségei (előnyök, hátrányok), a repositoryk szinkronizálása (push, pull, fetch) Git alatt.
    * Csapatmunka git alatt: merge és rebase, git flow (master, development, feature branchek, release branchek, hotfixek stb.), hibák helyre hozása (force push, elrontott merge vagy rebase, visszaállás korábbi verzióra, detached head állapot jelentése).
  * C++14, Qt és QML
    * C++ smart pointerek (unique, shared és weak pointerek)
    * C++ lambda kifejezések, auto kulcsszó és range for
    * Teljes fordítási folyamat Qt alatt (compiler, linker, MOC, QRC mechanizmus, statikus és dinamikus library (DLL) jelentése)
    * A QML és QmlEngine működése
      * QML scriptnyelv, JavaScript, események kezelése, kapcsolat a C++ oldallal
      * QML controlok: listák (model és delegate jelentése), rajzolás (onPaint működése, Context szerepe)
    * A signals and slots mechanizmus célja, működése, mi mire fordul le (emit, signal, slot kulcsszavak, a működés alapgondolata és a MOC szerepe)
    * A QRC mechanizmus jelentése, milyen fájlok és hogyan ágyazhatók be az exe fájlokba? Mit hoz létre ehhez a Meta-object compiler?
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
