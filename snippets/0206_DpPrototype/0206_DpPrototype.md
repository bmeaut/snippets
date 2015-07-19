---
layout: default
---

## Prototype (MED)

Erőforrásigényes példányosítás és inicializálás helyett egy konkét prototípus példány klónozása.

### Bevezető példa

* Játékprogram pályaszerkesztője: kiválasztunk egy új ellenség-fajtát, beállítjuk a sok-sok paraméterét és megjelenését (Builderrel), majd annyi példányt pakolunk le belőle a játéktérre, amennyit csak akarunk.

### Részletek

Olyasmi, mint a factory, csak egy kezdeti mintapéldánnyal adjuk meg, hogy milyeneket szeretnék majd gyártani.


További lehetőség: abstract ősosztály clone() metódussal és registryvel (map<string,baseclass&>). Minden konkrét példány regisztrálja magát, és onnan kezdve new helyett ezzel létre lehet hozni egy példányt úgy, hogy csak a nevét adjuk át stringként.

Megjegyzések

* Composite és Decorator patternekkel együtt gyakran használják.
* kombinálható factory patternnel

### Példa: különböző kép típusok

A műveletek amikor egy származtatott képet készítenek, akkor klónozzák az alapképet. És akkor egységesen lehet rajzolni színtértől és bitmélységtől, csatornaszámtól függetlenül. (Persze az alap metódusokra mindenkinek van megfelelő konverziója.)

### További példák

...
