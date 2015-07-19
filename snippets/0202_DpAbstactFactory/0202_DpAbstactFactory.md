---
layout: default
---

## Abstract factory (FONTOS)

### Bevezető példa

### Részletek


http://stackoverflow.com/questions/2280170/why-do-we-need-abstract-factory-design-pattern

Egymástól függő objektumok egy családját létrehozó interfészt ad, anélkül, hogy a konkrét osztályokat specifikálná.

Vagyis factory method csoportokat fog össze. Olyan csoportokat, hogy a létrehozott termékek összeférhetőek legyenek. (Mint egy Linux disztribúció: ott is csomagok egy egymással kompatibilis halmazát állítják össze.)

Készít egy "platform vs termék" mátrixot. Minden termékhez készül egy factory method (az abstract factoryban), majd ebből származnak az egyes platformok factoryjai.

További előnyök

* Cserélhető komponensek, de nem lehet őket akárhogy csereberélni, csak bizonyos, egymással összetartozó készletekben!

Hátányok

* Nehéz egy újabb factory methodot (terméket) felvenni

Megjegyzések

* Könnyű lecserélni az egész készletet, mivel csak az abstr.factory példányosításánal kell váltani.
* Az abstract factory gyakran singleton, mivel sok helyen kellhet.
* A kliens ezután ne használjon new operatátort, hanem a factory metódusokat használja új példányok létrehozására.
* (Néha kicsit nagyobb jelentőséget tulajdonítanak neki, mint amilyen gyakran előfordul. (?))
* Abstract Factory classes are often implemented with Factory Methods, but they can also be implemented using Prototype.
* Abstract Factory can be used as an alternative to Facade to hide platform-specific classes.

Külső anyagok:

* https://sourcemaking.com/design_patterns/abstract_factory


### Példa: platform függőség

* Platform függőség: egy abstract factory egy kombinációja az oprendszernek (pl. fájlkezelés), kommunikációs protokollnak, használt adatbázisnak. Amikor már nagyon sok az ifdef (platform feltétellel) a kódban.

### Példa: look-and-feel

* Look-and-feel

### További példák


* FancyDocumentCreator és ModernDocumentCreator. Mindkettő tud készíteni levelet, cikket, könyvet stb.
* Pizza AF: RomePizzaFactory, MilanPizzaFactory

* Factory és Abstr.Factory határán:
  * Ha a konkrét adatbázis fajtája csak a konfigurációból derül ki, futási időben. (Akár azért is, mert az egyes ügyfeleknél kint lévő verziók más adatbázisra épülnek.)
  * Protokollok és esetleg verzióik is
  * Diagnosztikai vagy a versenyen használt protokoll implementáció (loggol, visszaellenőriz, diag vs robusztusság)
