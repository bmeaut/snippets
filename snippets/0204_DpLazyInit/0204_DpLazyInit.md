---
layout: default
---

## Lazy initialization

A lazy initialization az objektum tényleges inicializálását elhalasztja addig, ameddig már tényleg szükség van rá. Ez akkor hasznos, ha az inicializálás egy költésges folyamat.

(Virtual proxy néven is ismert, mivel úgy viselkedik az objektum, mintha ő csak egy proxy lenne a ténylegesen inicializált példányt eltakarva.)

### Bevezető példa

A GrainAutLine rendszer fejlesztése során az alábbi helyzet állt elő: a márvány szemécsket Blob2 objektumokban tároljuk, ami egyfajta pixel lista formájában tárol egy foltot. Számos művelethez (például szomszédok azonosítása) szükség van a blob egy dilatált (minden irányba kicsit megnövelt) verziójára. Ez elég időigényes művelet, így ha nem kell, nem futtatjuk le. Utána viszont ha egyszer már készen van, a blobok read-only tulajdonsága miatt újra lehet őket hasznosítani.

Ha tehát készítünk egy olyan tárolót, mely minden Blobhoz tárolja a dilatált verzióját, de ezt ténylegesen csak akkor generálja le, ha szükség van rá, akkor az első ilyen művelet ugyan kicsit lassabb lesz, utána viszont már minden rendelkezésre áll majd.

### Részletek

A lazy initialization legegyszerűbb esetben úgy valósítható meg, hogy az objektum belül tárolja egy flag formájában, hogy már teljesen inicializálódott-e. A konstruktor ezt falsera állítja. Minden metódus ellenőrzi ezt a flaget és ha még nem inicializálódott (és a metódusnak erre szüksége van), akkor először inicializálja, truera állítja a flaget és megy tovább.

Gyakran előfordul a "Lazy factory" megoldás is, ami egy factory method, egy map és egy lazy initialization kombinációja: a lazy factorytól lehet bizonyos típusú elemeket kérni, de fontos, hogy ha még egyszer ugyanazt a típust kérjük, akkor ugyanazt a példányt adja vissza. (Egyfajta cachelt factory megoldás.) Ehhez a lazy factory amellett, hogy a létrehozáshoz egy factory methodot használ, egy mapben eltárolja a (típusazonosító;objektumpéldány) párokat. Így amikor kérnek tőle egy példányt, először ellenőrzi, hogy a mapben már szerepel-e. Ha nem, akkor létrehozza, ha viszont igen, akkor azonnal azt visszaadja. (Ez a multiton pattern egy lehetésges implementációja is. A multiton a singleton több típusú objektumot tároló verziója.)

### Példák

  * Bluetooth modul Facade-je: csak akkor inicializáljuk teljesen a BT kommunikációt, ha tényleg szükség van rá. (Ennek a megoldának akkor van igazán értelme, ha az alkalmazás során jó esély van rá, hogy nem is fog kelleni, amikor meg kell, akkor nem kell azonnal mennie.)
  * Egy áramkörtervező programban az egyes alkatrészek képét elég egyszer betölteni, minden egyes ellenálláshoz nem kell külön ellenállás képet betölteni. Egy lazy factorytól kérünk egy ellenállás képet, amit ő első alkalommal ténylegesen betölt, később meg már csak visszaadja a tárolt példányt, lévén a megjelenítéshez felesleges több példányt létrehozni.
  * GUI fejlesztéskor szükségünk van Brush objektumokra, amik a kitöltések színét és mintáját határozzák meg. Ezek létrehozása elég költséges, viszont minden megjelenítéskor szükség van rájuk. Ezért érdemes a már létrehozott példányokat elmenteni későbbi használatra is.
  * Egy több képréteget támogató rajzprogram is tárolhatja a rétegeket lazy factoryval: ha kell egy újabb réteg, létrehozza az első hozzáféréskor, később meg már csak az elmentett példányt adja vissza.

<small>Szerzők, verziók: Csorba Kristóf</small>
