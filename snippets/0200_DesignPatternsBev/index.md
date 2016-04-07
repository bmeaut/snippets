---
layout: default
codename: DpDesignPatternBev
title: Tervezési minták bevezető
tags: designpatterns
authors: Csorba Kristóf
---

# Design patterns bevezető

A szoftverfejlesztési gyakorlatban igen gyakran kerülünk szembe nagyon hasonló feladatokkal. Ilyen lehet például egy konfigurációs fájl, melynek tartalmához a rendszer számos pontjáról kell tudni hozzáférni, viszont ezért minden egyes objektum számára átadni a konfigurációs beállításokat elég nehézkes lenne. A Singleton tervezési minta például erre javasol egy megoldást.

A tervezési minták felismerése a tervezési folyamat során számos előnnyel jár:

  * Így követhetjük a már bevált megoldásokat, amik kialakulása során számos olyan veszélyt és problémaforrást is figyelembe vettek, amire esetleg most mi magunk még nem is gondolunk, viszont könnyű beleszaladni.
  * A tervezéshez egységes, mindenki által ismert terminológiát ad, így az összetettebb konstrukciókról is sokkal könnyebb beszélni. "És készítünk egy observert a beállításokhoz." "Az állapotot State tervezési mintával kezeljük."

Valószínűleg már mindenki egész sok tervezési mintával találkozott, mivel ezek nagy része semmi misztikus dolgot nem tartalmaz, de a mintákat igazán kihasználni csak akkor tudjuk, ha ez tudatosul is: akkor tudjuk nevén nevezni és akkor juthat eszünkbe az, hogy az adott minta megvalósításakor mikre szokás, mikre érdemes figyelni.

Amennyiben egy olyan kis programot készítünk, amit csak egyszer fogunk lefuttatni és soha többet nem fog változni, nyilván nem biztos, hogy van értelme nagy tervezési mintákban gondolkodni (bár ekkor sem ártalmas). Viszont ha van rá esély, hogy idővel módosítani kell a programot (változnak az igények), vagy hogy többen dolgoznak majd rajta, akkor nagyon megéri egy kicsit több hangsúlyt fektetni a tervezésre és a minták felkutatására.

Volt már rá példa, hogy egy tanszéki projekt esetében amikor egy új igény felmerült, hamar kiderült, hogy a forráskódban már megvan a helye a megoldásnak, mivel a szükséges interfészek már régen ki vannak alakítva, még ha addig nem is volt rájuk különösebben szükség.

Tervezési minta nagyon sok van, az alábbi gyűjtemény természetesen messze nem teljes. Ezen kívül az egyes helyzetekben és fejlesztési környezetekben az egyes minták megvalósítása is nagyon eltérhet egymástól: vagy a követelmények eltérései miatt, vagy egyszerűen az adott programnyelv és keretrendszer képességeitől függően. Ezen kívül az alábbi minta halmazok mellett is léteznek bőven további tervezési minta fajták.

Az egyes mintákról részletesen külön snippetek szólnak.

## Creational patterns, létrehozási vagy példányosítási minták

A creational design patternek objektumok létrehozására vonatkozó tervezési minták. Akkor jönnek elő, amikor vagy az nem triviális, hogy (1) hogyan kell létrehozni egy objektumot (például mert sok lépésből áll és összetett, mint egy labirintusos játék pályája), vagy (2) mert az nem triviális, hogy egy ősosztálynak pontosan melyik leszármazottjára is van szükség (péládul egy kommunikációs objektum függ a használt protokolltól).

  * Factory, Factory Method: a példányosítást egy cserélhető vagy konfigurálható metódusba, osztályba szervezi ki.
  * Abstact Factory: összekapcsolódó osztályok lehetséges "készletére", halmazára kialakított factory.
  * Builder: összetett példányosítási, felépítési folyamatokat támogató osztály.
  * Lazy Initialization: csak akkor végzi el ténylegesen a példányosítást, amikor már tényleg használnánk az eredményét, egészen addig késlelteti.
  * Singleton: a rendszerben egyetlen példányban létező objektum.
  * Prototype: a példányosítást egy mintapéldány másolásával helyettesítő megoldás.
  * Resource Allocation Is Initialization (RAII): nyelvi szinten garantálja egy erőforrás felszabadítását.

A creational patternek gyakran keverednek, vagy nem annyira triviális, hogy melyiket is kellene használni. A fejlesztés során ahogy egyre nagyobb flexibilitásra van szükség, gyakran készül Factory Method, melyből később Abstract Factory lesz, az pedig belül lehet, hogy Buildert vagy Prototypeot használ. De közben a Builder is használhat Factoryt vagy Prototypeot az egyes részegységek létrehozásához.

A Builder az összeállításra koncentrál, melynek utolsó lépése a tényleges létrehozás és az eredmény visszaadása. Az Abstract Factory általában egy lépésben létre is hozza a kért objektumot és azonnal visszaadja azt.

## Structural patterns, struktúrális minták

A struktúrális minták a rendszer felépítésére tesznek javaslatot, nem pedig egy folyamat leírására.

  * A Composite minta összetett objektumgráfok egyszerűbb kezelését célozza meg.
  * A Decorator új funkciókkal egészít ki egy már létező implementációt, annak módosítása nélkül.
  * A Facade egy már létező interface beburkolását, és ezzel többnyire egyszerűsítését célozza meg.
  * A Proxy egy valamilyen szempontból távoli objektum elérését teszi egyszerűbbé, vagy kiegészíti ezt valamilyen további funkcióval. 

## Behavioral patterns, viselkedési minták

A viselkedési minták bizonyos feladatokra adnak működési javaslatokat.

  * Az Observer célja, hogy egy objektum automatikusan értesüljön egy másik változásairól.
  * A Strategy könnyen cserélhetővé teszi bizonyos részfeladatok megoldási módját.
  * A State eltérő állapotok esetén eltérő viselkedés implementálására ad javaslatot.
  * A Visitor egy új funkcióval egészít ki egy már kész osztályt vagy osztály halmazt.

## További olvasnivaló

  * "GoF", vagyis a Gang of Four könyve: Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides; Design Patterns: Elements of Reusable Object-Oriented Software
  * [Design Patterns WikiBooks](https://en.wikibooks.org/wiki/Computer_Science_Design_Patterns)
  * Dependency injection: [http://en.wikipedia.org/wiki/Dependency_injection](http://en.wikipedia.org/wiki/Dependency_injection)
  * Dependency inversion principle [http://en.wikipedia.org/wiki/Dependency_inversion_principle](http://en.wikipedia.org/wiki/Dependency_inversion_principle)
  * SOLID elvek [http://en.wikipedia.org/wiki/SOLID_(object-oriented_design)](http://en.wikipedia.org/wiki/SOLID_(object-oriented_design))
  * [http://en.wikipedia.org/wiki/Inversion_of_control](http://en.wikipedia.org/wiki/Inversion_of_control)

<small>Szerzők, verziók: Csorba Kristóf</small>

