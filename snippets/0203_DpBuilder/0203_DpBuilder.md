---
layout: default
---

## Builder (FONTOS)

### Bevezető példa: StringBuilder

Számos programnyelvben a string egy olyan objektum, amit gyakran fűzünk össze másik stringekkel, viszont ez a művelet meglehetősen erőforrás igényes. Amennyiben a

   for(int i=0; i<100; i++)
       result = result + string(i) + " és ";

minden egyes + műveleténél létre kell hozni egy új (az esetek nagy részében ideiglenes) string objektumot a részeredmény tárolására, akkor az igen nagy erőforrás pazarlás. Erre jött létre a StringBuilder, melynek sorban meg lehet mondani, hogy miket fűzzön hozzá a stringhet, de a tényleges string objektum csak akkor jön létre, amikor készen vagyunk. Addig a tartalma másik formában tárolódik, úgy, hogy ahhoz sokkal könnyebb legyen hozzáfűzni.

*Megjegyzés: Qt alatt a & string összefűző művelet olyan, mint a +, csak pont egy ilyen StringBuilderes megoldásra fordul le.*

Ebben a példában a StringBuilder egy olyan osztály, mely stringek felépítését végzi. Amikor pedig készen van, akkor az ő feladata véget is ért.

### Részletek

Ezt a tervezési mintát akkor használjuk, ha az osztály felépítése (1) összetett és/vagy erőforrás igényes, és a használat közben a felépítő funkciókra már nincsen szükség, vagy (2) a pontos belső felépítés cserélhető az interfésztől függetlenül.

Az 1. esetre példa egy labirintusos játék pályája, mely egy jókora gráf formájában áll össze. Amikor már készen van, akkor már csak használjuk, így a térkép összerakására csak a létrehozáskor van szükség. Ilyenkor a Builder osztály sorban megkapja, hogy mik és hol vannak a játéktéren, létrehozza a szükséges mezőket, majd az átjáróknak megfelelően összekötögetni őket. Végül amikor minden a helyén van, visszaadja az egész játékteret, amit ezután már nem módosítunk az átjárók és mezőtípusok szempontjából.

A 2. esetre példa az, amikor **Cserélhető reprezentáció példa kell**
Ebben az esetben többféle Builder osztály van (egy közös ősből leszármaztatva), így a ténylegesen létrehozott eredmény attól függ, éppen melyik Buildert használtuk.

Mindkét esetben a Builder osztály csak a felépítésért felelős, utána már nincsen rá szükség.

További előnyök

* A Builderből származtatva a konkrétan felépített reprezentáció cserélhető.
* A fenti esetekben az építési folyamat és a konkrét reprezentáció szétválasztható: eltérő reprezentációkra is használhatjuk ugyanazt az építési folyamatot (eltérő Builderek azonos interfésszel).

Hátrányok

Megjegyzések

* Composite patternnel gyakran együtt jár.
* Olyan builder interface kell, amivel minden szükséges példányt össze lehet rakatni.
* Itt a hangsúly azon van, hogy hogyan rakjuk össze. Az (abstract) factory esetében csak a komponensek létrehozása a kérdés, nem az összerakás módja.


### Példa: labirintusos játék

### Példa:

### Példa: Reader és Builder

* Reader+Builder: pl. fájlból a reader olvas (fájl formátumok), majd a Builder épít. Pl. PSD.Load(), bár ott a reader nincs leválasztva, mert csak egy fájlformátum van, a saját. Ilyenkor a Reader megkap egy Buildert, hogy majd azt használja a készítésnél.

### Egyéb példák

* Jogosultság függően összerakott UI (mi jelenjen meg és mi ne)
* Blob2 rendezett belső reprezentáció, építéskor még nem feltétlenül rendezett, utána meg már read-only, így az építés jól leválasztható.
* StringBuilder (Qt & operátor erre fordul le?!)
* Robot pályája mindenféle elemekkel. Létrehozni csak egyszer kell, utána már csak használjuk. (A komponensek felrakása után a véglegesítéskor a maradék kapcsolatokat bekötögeti stb.)
* Blob2Builder! (Pl. mert az összerakás több metódus meghívását igényli, amit meg nem akarunk berakni a célosztályba.)
* A Builder akár választhat is optimális reprezentációt. Pl. ha látja, hogy folytonos vagy ritkás egy mátrix, akkor sima vagy sparse példányt is létrehozhat!
