---
layout: default
---

# FÉLKÉSZ

# Design patterns bevezető

**Az elejénre Singleton, azon keresztül bemutatva az egész patternesdit, UML leírást. Azt, hogy sokféle módon meg lehet írni, a kérdés az, hogy mire gondolunk és mire nem. Nem kell mindig a nagyágyú. Lassan, példa centrikusan, problémából kiindulva mutassam meg őket!**

*Ebbe a leírásba fontos az is, hogy mi az, amit majd számon lehet kérni az egyes patternekről!*

*Sokféle módon implementálhatók! Tervezői döntés kérédse, hogy mikor milyen megoldás jó. Az itteni példák egy lehetőséget mutatnak, de természetesen van olyan eset, amikor másképp érdemes megoldani az adott feladatot.*

GoF:
Design Patterns: Elements of Reusable Object-Oriented Software
Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides
The authors are often referred to as the Gang of Four (GoF).[1]


Design Patterns WikiBooks:
https://en.wikibooks.org/wiki/Computer_Science_Design_Patterns


Példák, melyekhez lehet kötni:

  * GrainAutLine
  * SMEyeL rendszer, multi-cam és data streaming
  * RobonAUT robot és hozzá kapcsolódó diagnosztika
  * RobonAUT pályaelektronika

Ismernek sokat, csak nem feltétlenül tudatosan. Azzal, hogy tudatosítjuk ezeknek a mintáknak a létezését, elérjük, hogy a tervezéskor már mintaként jut eszükbe (és van esély rá, hogy így ismerik fel a helyzeteket), amivel együtt eszükbe jutnak a tipikus megoldások, veszélyforrások, mikre kell gondolni stb.

Design patterns és Anti-Patterns
Dependency injection (factory method)
http://en.wikipedia.org/wiki/Dependency_injection

A DI container végzi el magától az összekapcsolásokat. Config mehet abstract factory segítségével!

http://en.wikipedia.org/wiki/Dependency_inversion_principle
Ne függjön egy magas szintű modul alacsony szinű moduloktól, csak absztrakcióiktól. Ugyanez felfelé is. SOLID elvek!

http://en.wikipedia.org/wiki/SOLID_(object-oriented_design)

http://en.wikipedia.org/wiki/Inversion_of_control

tesztelés, mockolás említése? framework nélkül van értelme?

Gondolatok

  * Bővíthetőség növelésére: MemoQ példa, ott minden új feature igénynek már megvan a helye a forráskódban, még ha csak egy üres csonk is.
  * Először keretrendszer, utána konkrét megoldás. A minták segítenek az általánosításban.
  * Tudom, hogy egyenesen is le lehet kódolni, és ha csak le kell egyszer futtatni és kész, akkor ez teljesen jó is. De ha évekig supportolni kell, ráadásul időnként kérnek kiegészítéseket, akkor már nagyon-nagyon nem mindegy, hogy mennyire tudunk bátran belenyúlni a programba. (Ha minden mindenhonnan mindent csinál és elér, akkor sok ideigneles belehekkelés után kockázatos lesz bármihez is hozzányúlni. Sokkal jobb, ha be vannak védve a dolgok a fejlesztők ellen is. Azt fel lehet oldani, de amíg nincs feloldva, addig biztosak lehetünk benne, hogy tényleg nem fordul elő olyan hekkelés, ami megszegi. Hekkelés pedig mindig lesz.)

## Design patterns - Creational patterns

A creational design patternek objektumok létrehozására vonakozó tervezési minták. Akkor jönnek elő, amikor vagy az nem triviális, hogy (1) hogyan kell létrehozni egy objektumot (például mert sok lépésből áll és összetett, mint egy labirintusos játék pályája), vagy (2) mert az nem triviális, hogy egy ősosztálynak pontosan melyik leszármazottjára is van szükség (péládul egy kommunikációs objektum függ a használt protokolltól).

* A creational patternek gyakran keverednek, vagy nem annyira triviális, hogy melyiket is kellene használni. A fejlesztés során ahogy egyre nagyobb flexibilitásra van szükség, gyakran készül Factory Method, melyből később Abstract Factory lesz, az pedig belül lehet, hogy Buildert vagy Prototypeot használ. De közben a Builder is használhat Factoryt vagy Prototypeot az egyes részegységes létrehozásához.
* Builder focuses on constructing a complex object step by step. Abstract Factory emphasizes a family of product objects (either simple or complex). Builder returns the product as a final step, but as far as the Abstract Factory is concerned, the product gets returned immediately.
