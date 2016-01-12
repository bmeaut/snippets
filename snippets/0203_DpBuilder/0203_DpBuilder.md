---
layout: default
---

## Builder

A builder tervezési minta szétválasztja a reprezentációt és az őt felépítő (komplex) logikát.

### Bevezető példa: StringBuilder

Számos programnyelvben a string egy olyan objektum, amit gyakran fűzünk össze másik stringekkel, viszont ez a művelet meglehetősen erőforrás igényes. Amennyiben a

```C++
for(int i=0; i<100; i++)
    result = result + string(i) + " és ";
```

minden egyes + műveleténél létre kell hozni egy új (az esetek nagy részében ideiglenes) string objektumot a részeredmény tárolására, akkor az igen nagy erőforrás pazarlás. Erre jött létre a StringBuilder, melynek sorban meg lehet mondani, hogy miket fűzzön hozzá a stringhez, de a tényleges string objektum csak akkor jön létre, amikor készen vagyunk. Addig a tartalma másik formában tárolódik, úgy, hogy ahhoz sokkal könnyebb legyen hozzáfűzni.

(Megjegyzés: Qt alatt az & string összefűző művelet olyan, mint a +, csak pont egy ilyen StringBuilderes megoldásra fordul le.)

Ebben a példában a StringBuilder egy olyan osztály, mely stringek felépítését végzi. Amikor pedig készen van, akkor az ő feladata véget is ért.

### Részletek

Ezt a tervezési mintát akkor használjuk, ha az osztály felépítése (1) összetett és/vagy erőforrás igényes, és a használat közben a felépítő funkciókra már nincsen szükség, vagy (2) a pontos belső felépítés cserélhető az interfésztől függetlenül.

Az 1. esetre példa egy labirintusos játék pályája, mely egy jókora gráf formájában áll össze. Amikor már készen van, akkor már csak használjuk, így a térkép összerakására csak a létrehozáskor van szükség. Ilyenkor a Builder osztály sorban megkapja, hogy mik és hol vannak a játéktéren, létrehozza a szükséges mezőket, majd az átjáróknak megfelelően összekötögeti őket. Végül amikor minden a helyén van, visszaadja az egész játékteret, amit ezután már nem módosítunk az átjárók és mezőtípusok szempontjából.

A 2. esetre példa az, amikor egy adatforrásból (pl. fájlból) olvassuk be egy összetett adatstruktúrát, de a fájlban sokkal több adat van, mint amennyire szükségünk van. Attól függően, hogy melyik buildert választjuk, el tudjuk dönteni, hogy milyen részletezettségi szintű adatstruktúrát akarunk felépíttetni a fájl alapján.
Ebben az esetben többféle Builder osztály van (egy közös ősből leszármaztatva), így a ténylegesen létrehozott eredmény attól függ, éppen melyik Buildert használtuk. (Ez közel áll a factory method mintához is.)

Mindkét esetben a Builder osztály csak a felépítésért felelős, utána már nincsen rá szükség.

További előnyök

  * Egy Builder ősosztályból származtatva a konkrétan felépített reprezentáció cserélhető.
  * A fenti esetekben az építési folyamat és a konkrét reprezentáció szétválasztható: eltérő reprezentációkra is használhatjuk ugyanazt az építési folyamatot (eltérő Builderek azonos interfésszel).

Megjegyzések

  * Composite patternnel gyakran együtt jár, mivel az összetett objektumgráf felpítését lehet, hogy ki lehet szervezni egy builderbe.
  * Olyan builder interface kell, amivel minden szükséges példányt össze lehet rakatni, különben néha meg kell kerülni a buildert és manuálisan összerakni a célobjektumot, ami kód duplázáshoz és káoszhoz vezet.
  * Itt a hangsúly azon van, hogy hogyan rakjuk össze. Az (abstract) factory esetében csak a komponensek létrehozása a kérdés, nem az összerakás módja.
  * Hasznos olyan esetekben, amikor a példányosításnak már sokféle beállítása, paramétere lehet, így a sokféle kombináció miatt rengeteg konstruktor van. Ehelyett a buildernek sorban egymás után meg lehet adni a paramétereket, ő pedig majd összerakja a kért objektumot, amikor végül meghívjuk a "create()" metódust.
  * Hasznos akkor is, ha a létrehozott objektum read-only, így az összeállítása után már nem fogunk (nem lehet) szerkesztő funkciókkal hozzányúlni, ugyanakkor az összerakása több műveletet is igényel.

### Példa: Reader és Builder objektumok

Tegyük fel, hogy több fájlformátumból tudunk beolvasni egy bonyolultabb adatstruktúrát. Ekkor a felépítést egy builderrel végezhetjük, amit átadunk egy a konkrét fájlformátumot ismerő, beolvasó objektumnak (reader). A reader olvassa a fájlt és használja a buildert, hogy a végén a teljes adatstruktúra előálljon.

(Amennyiben többféle belső reprezentációra is van lehetőség, a readernek átadott konkrét builderrel határozhatjuk meg, hogy milyen adatstruktúra épüljön fel.)

### Egyéb példák

  * Jogosultság függően összerakott felhasználói felület (mi jelenjen meg és mi ne).
  * Ha egy adattároló objektumból van csak olvasható (és ezért például gyorsabban kereshető) és szerkeszthető verzió is, két builder közül választva lehet meghatározni, hogy melyik jöjjön létre.
  * A [GrainAutLine](bmeaut.github.io/grainautline) rendszer Blob2, foltokat tároló osztálya rendezett belső reprezentációval rendelkezik, vagyis a folt pixeleit sorba rendezve kell átadni a konstruktornak. Építéskor még nem feltétlenül rendezett az adatsor, utána meg már read-only, így az építés (és benne a végső rendezés) jól leválasztható.
  * Robot pályája mindenféle elemekkel. Létrehozni csak egyszer kell, utána már csak használjuk. (A komponensek felrakása után a véglegesítéskor a maradék kapcsolatokat bekötögeti a builder, például hogy melyik után melyik következik, minden lehetésges irányba.)
  * A Builder akár választhat is optimális reprezentációt. Például ha látja, hogy folytonos vagy ritkás egy mátrix, akkor sima vagy sparse példányt is létrehozhat! (Ez utóbbi nem fogal le minden elemnek helyet, hanem (sor; oszlop; érték) formában tárolja az összes elemet.)

<small>Szerzők, verziók: Csorba Kristóf</small>
