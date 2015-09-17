---
layout: default
---

## Prototype

Erőforrásigényes példányosítás és inicializálás helyett egy konkét prototípus példány klónozása.

### Bevezető példa

Tegyük fel, hogy egy labirintusos-szörnyes-szaladgálós játokhoz készítünk pályaszerkesztőt. Az ellenséges szörnyeknek számos beállítása (okosság, megjelenés, sebesség, étvágy, percenkénti osztódások száma stb.) van. Ha ezeket beállítjuk egyszer, utána számos példányt pakolhatunk le a pályára. Utána módosítunk kicsit a beállításokon és az új verzióból is lerakunk egy csomót.

Ha ezt sima példányosítással oldanánk meg, akkor vagy minden alkalommal át kellene adnunk az összes paramétert a konstruktornak, vagy a létrehozás után kellene beállítani őket, felülírva az alapértelmezett beállításokat.

Ehelyett a szörny konfigurációnál beállíthatjuk egy konkrét példány (a prototípus) paramétereit is, majd a konkrét példányok lerakásánál ezt a prototípust klónozzuk le minden alkalommal. Ha pedig a prototípus paraméterei változnak, akkor a további klónok már azokat fogják átvenni.

### Részletek

A prototype olyasmi, mint a factory, csak egy kezdeti mintapéldánnyal adjuk meg, hogy milyeneket szeretnék majd gyártani, és nem pedig azzal, hogy a factory method leszármaztatott osztályai közül választunk egyet. (A fenti példában például a sok beállítás miatt vagy sokféle factory kellene, vagy a példányosítás után amúgy is át kellene állítani egy csomó mindent.)

Megjegyzések

  * Tipikus alkalmazási eset az, amikor a példányosítás valamiért költséges folyamat, így sokkal jobban megéri egy példányt létrehozni, utána pedig már csak azt másolni. (Például ha a példányosítás bonyolultan, a Builder minta alapján készül.)
  * Composite és Decorator patternekkel együtt gyakran használják, mivel ezeknél a példányosítás nem egy triviális folyamat, így ha egyszer valamit már sikerült összeállítani, hasznos lehet, ha könnyen lehet másolni. Ezen kívül a számos konfigurációs lehetőség miatt (mint a composite objektumgráfjának összeállítása) nem egyszerű még egy ugyanolyan példányt létrehozni, kivéve, ha lehet klónozni.
  * Kombinálható factory patternnel, ami létrehozza a prototípust, amit utána klónozás előtt még lehet módosítani.
  * Sokszor használják az abstract factory kiváltására olyan esetekben, amikor az abstract factorynak már kezd nagyon sok leszármaztatott osztálya lenni a sok lehetőség miatt.

### Példa: különböző kép típusok

Egy képszerkesztő rendszerben (vagy például az OpenCV osztálykönyvtárban) tipikusan vannak színes és szürke árnyalatos képek, eltérő bitmélységű képek stb. A rajzoló funkciók ezek mindegyikén futnak, belül megoldják a helyes viselkedés kiválasztását. Ha ilyenkor akarunk egy olyan képet, ami a beállításaiban hasonlít egy másik, már létező képhez, akkor a legegyszerűbb lemásolni (klónozni).
