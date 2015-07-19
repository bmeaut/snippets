---
layout: default
---

## Singleton (FONTOS, bevezető példa is egyben)

* Első példa
* Primitív implementáció, de pl. szálbiztos?
* Több lehetséges implementáció. Az eltérés, hogy miket kezel le és miket nem. Nem kell mindig a nagyágyú. (Pl. mennyi látszik kívülről, szálbiztosság)

### Bevezető példa

### Részletek

* The Abstract Factory, Builder, and Prototype patterns can use Singletons in their implementation.
* Facade objects are often singletons because only one Facade object is required.
* State objects are often singletons.
* Singletons are often preferred to global variables because:
   * They do not pollute the global namespace (or, in languages with namespaces, their containing namespace) with unnecessary variables.[4]
   * They permit lazy allocation and initialization, whereas global variables in many languages will always consume resources.

Abstract factory singleton: Java AWT, getDefaultToolkit().

static Singleton& instance()
{
     static Singleton s;
     return s;
}

Nehezíti a unit tesztelést, mert globális állapotot vezet be a rendszerbe, ezért a teszeléshez a program egy kis részének nehezebb teljesen izoláltan egy olyan kis környezetet szimulálni, melyben a tesztet végre kell hajtani. (**példa kell**)

### Példák

* Log műveletek
* Konfigurációs beállítások (section-key-value hármasok pl. ini fájlból)
* Forgalomszámláló rendszerben
   * a kereszteződés, benne a tipikus mozgási irányokkal, sávok helyével. Videó adatok (FPS, valós kezdeti és befejezési időpont).


### Multiton, mint általánosítása

A skeleton általánosításra az egyetlen példány helyett (1) előre adott számú példány esetére, vagy (2) bizonyos kategóriánként pontosan egy példányra.

Hívják még registry of singletonsnak is, ahol kulcsonként csak egyetlen példány lehet.
Mint egy hash, de (1) nem adhatunk meg új elemeket, (2) soha nem ad vissza nullptr-t, létrehozza, ha kell.

Példák:

* Hardver perifériák, amikből több is lehet.
