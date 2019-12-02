---
layout: default
codename: QtQmlJavascriptImage
title: Qt Qml image insert to canvas
tags: snippets
authors: Kemenes Ákos
---

# Kép beszúrása grafikonra javascript segítésével

Amennyiben szükségesnek ítéljük, hogy egy gráfra (canvasra) képet tegyünk, és esetleg dinamikusan változtassuk, akkor a QML egy javascript alapú megoldást kínál.
Ahhoz, hogy képünk megjelenjen, elég csak a QML-ben szokásosan használt

```cpp
Image{
        id: image1
        visible: false
        source: 'cat.png'
    }
```
kódsort használni, azonban ha ezt formázni, mozgatni és változtatni is szeretnénk ahhoz egy kicsitvel több kódra van szükség.
Ahogy a fenti kódon látszik, a láthatóság hamisra van állítva. Ez azért szükséges, mert nem ezt a tag-et szeretnénk megjelníteni, csupán csak ebből a képből egy példányt, de módosítva.
Térjünk is a lényegre, az Image{}-el létrehoztuk a képet, megjeleníteni pedig így tudjuk:

```cpp
var context = getContext("2d");
context.drawImage(image1, 0, 0, 100, 100);
```
Ez a kód már javascript, ezáltal ha több funkcióra lenne szükséged, minthogy a kép méretét, pozícióját, vagy magát a képet változtatod, célszerű javascript megoldásokat keresni, mert QML címszóval én nem sok eredményre jutottam.

Jelen esetben a ``context`` nevű változónk egy ``CanvasRenderingContext2D`` típusú objektum mely rengeteg lehetőséget biztosít a 2D megjelenítés sok területén.

A fenti drawImage függvény lehetséges verziói:
```cpp
void ctx.drawImage(image, dx, dy);
void ctx.drawImage(image, dx, dy, dWidth, dHeight);
void ctx.drawImage(image, sx, sy, sWidth, sHeight, dx, dy, dWidth, dHeight);

```
Ez a három lehetőség nyílik kép kirajzolására, én a második verziót használtam. 
A property-k leírása, és sok egyéb hasznos ezzel kapcsolatos dolog a dokumentációban olvasható amelyet itt találsz:

[Dokumentáció](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/drawImage)
