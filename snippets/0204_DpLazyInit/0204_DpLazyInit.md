---
layout: default
---

## Lazy initialization (FONTOS)

### Bevezető példa

Kiindulási probléma, amin keresztül bemutatom: dilated blob2 cache

* Cachelt tároló: ha még nem áll rendelkezésre az, amit kértünk, akkor létrehozza, egyébként gyorsan visszaadja. Például a GrainAutLine dilated blob container.

### Részletek

(Virtual proxy néven is ismert.)
Létrehozás vagy kiszámítás (erőforrás igényes dolgok) csak akkor, amikor már tényleg kell.

Például egy tároló, mely ha eddig ismeretlen elemet akarunk lekérni, akkor gyorsan készít egyet, egyébként meg mindig visszaadja ugyanazt. (Lazy factory method!)

### Példa:

* Bluetooth modul Facade-je: csak akkor inicializáljuk teljesen a BT kommunikációt, ha tényleg szükség van rá. (Akkor van igazán értelme, ha az alkalmazás során jó esély van rá, hogy nem is fog kelleni, amikor meg kell, akkor nem kell azonnal mennie.)
