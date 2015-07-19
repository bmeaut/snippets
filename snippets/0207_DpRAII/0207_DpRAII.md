---
layout: default
---

## Resource acquisition is initialization (MED)

### Bevezető példa

### Részletek


### Példa:


Guard osztály, amikor az megszűnik, akkor elengedi az erőforrást. (A foglalás egy változó inicializálása.) Mindegy, hogyan lépünk ki a scope-ból!

Objektum életciklushoz köti az erőforrás foglalást.

Managed nyelvekben using, C++-ban simán a stacken létre lehet hozni a guard-ot.


## Összefoglalás, megjegyzések

* A creational patternek gyakran keverednek, vagy nem annyira triviális, hogy melyiket is kellene használni. A fejlesztés során ahogy egyre nagyobb flexibilitásra van szükség, gyakran készül Factory Method, melyből később Abstract Factory lesz, az pedig belül lehet, hogy Buildert vagy Prototypeot használ. De közben a Builder is használhat Factoryt vagy Prototypeot az egyes részegységes létrehozásához.
* Builder focuses on constructing a complex object step by step. Abstract Factory emphasizes a family of product objects (either simple or complex). Builder returns the product as a final step, but as far as the Abstract Factory is concerned, the product gets returned immediately.
