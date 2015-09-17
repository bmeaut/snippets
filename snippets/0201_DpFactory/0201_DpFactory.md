---
layout: default
---

TODO:
- UML diagram (Factory, ConcreteFactory, Product elnevezésekkel)
- Hivatkozás a példaprogramra, ha lesz

## Factory method

A factory method célja, hogy egy ősosztály leszármazottjai közül az egyiknek létrehozzuk egy példányát, de azt máshol döntjük el, hogy melyiket.

(A factory method mintánál ennél általánosabb Factory tervezési minta egy olyan objektumot takar, ami másik objektum példányokat hoz létre.)

### Bevezető példa: játékprogram pályaszerkesztője

Például egy játék pályaszerkesztőjében kattintásra létre lehet hozni új elemeket. De hogy a kattintás milyen elemet hoz létre, azt az határozza meg, hogy az eszköztárról mit választottunk ki legutoljára. Ennek egy lehetséges megvalósítása az, hogy az egérkattintáshoz "factory objektumokat" lehet hozzárendelni. A kattintás ezután csak azt mondja az éppen aktuális factorynak, hogy hozzon létre egy új elemet. Amikor pedig az eszköztáron kiválasztunk egy másik pályaelemet, akkor lecseréljük a kattintás által használt factory objektumot. (A kattintás eseménykezelője ebből semmit nem vesz észre, mivel a factory objektumokra ő csak a közös ősosztályukra mutató referenciával hivatkozik.)

### Részletek

A Factory method tervezési minta osztálydiagramja az alábbi:

![](images/FactoryMethodClassDiagram.png)

A Factory egy ősosztály, melyre a példányosítást kérő kliens például egy referenciával hivatkozik majd. Ezt a referenciát lehet majd az egyes ConcreteFactory osztályok példányaira állítani. Az ősosztály, mint interface, definiálja a példányosító objektumot (tipikusan tisztán absztrakt, virtuális függvényként, de akár alapértelmezett implementációt is tartalmazhat). A kliens amikor szeretne egy Product példányt, azt nem a konstruktorával hozza létre (new operátorral), hanem a Factory::Create metódus segítségével. Ebből pedig nyilván azé az osztályé fog lefutni, amelyiknek egy példányára a kliens éppen hivatkozik.

Megjegyzések

  * Ha van factory method, akkor nem használunk new operátort, hanem a factory methodokat.
  * Ez a minta akkor hasznos, ha a létrehozás helyén nem akarom eldönteni, hogy pontosan milyen példányt akarok létrehozni. Vagy azért, mert a kliens osztálynak ehhez semmi köze, vagy azért, mert nagyon sok helyen kell példányosítani és macerás mindenhova odarakni a döntési logikát.
  * Szintén hasznos a minta akkor, ha a létrehozás nem triviális folyamat (nem csak a konstruktort kell meghívni), mivel akkor a létrehozási folyamat ahelyett, hogy sok helyen előfordulna a forráskódban, bekerül a factory methodba. (Ez egy kicsit hasonlít a Builder mintához.)
  * Ez a megoldás kapcsolódik a dependency injection koncepcióhoz is. Annak is az a lényege, hogy kívülről kapuk azokat az objektumokat (jelen esetben a factoryt), amire később szükségünk lesz. (Ahelyett, hogy helyben be lenne drótozva.)

### Példa: bemenet kiválasztása

...

### Példa: User input type (konzol, COM, socket (Nightshade példa!))

...
