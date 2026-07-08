---
layout: default
codename: PdfEditorRedesign
title: Android és iOS dizájn készítése és implementálása
tags: snippets mieset
authors: Domonkos Ádám
---

# Android és iOS dizájn készítése és implementálása

Claude Opus modellekkel egy natív iOS és Android PDF-nézegető és szerkesztő könyvtár, illetve a hozzá tartozó demó alkalmazás felületét terveztem újra, majd implementáltam is. A munka két különálló munkamenetre bomlott, egy tervezési fázisra a Claude Design szolgáltatás használatával, és egy implementációs fázisra, ahol Claude Code a meglévő kódbázison dolgozott agentic módon. A könyvtár szinte teljes funkcionalitása és egy hasonló elrendezés már létezett, szóval ez inkább egy ráncfelvarrás, UI-upgrade volt, nem nulláról építés.

Mindkét fázis nagyon jó eredménnyel zárult, a kész design pontosan azt hozta, amit elvártam, modern és könnyen használható lett. Pár tisztázó és magyarázó iteráció kellett a használható állapotig, de összességében gyorsan és jól ment.

---

## A feladat

A könyvtár a következőket tudja:
1) PDF megtekintése
2) szabadkézi rajz (vonalszín és -vastagság állítható)
3) szöveges annotációk (betűméret, szín)
4) Mentés

- **Tervezés:** modern, letisztult natív iOS és Android felület tervezése mindkét platformra, minden képernyő-állapotra, light + dark témában.
- **Implementáció:** a kész design beépítése a meglévő kódbázisba és a demó appokba.

---

## Felhasznált modellek és technológiák

| | Tervezési fázis | Implementációs fázis |
|---|---|---|
| Modell | Claude Opus 4.8 | Claude Opus 4.7 |
| Környezet | claude.ai design vászon (Claude Design) | agentic munka a meglévő kódbázison |
| Kimenet | React/JSX artboardok + HTML design canvas | natív iOS + Android UI a könyvtárhoz és a demó appokhoz |

A design rendszer: szürkeárnyalatos vászon egyetlen kék akcenttel, a PDF dokumentum Georgia betűvel, a UI iOS-en SF Pro (iOS 26 liquid glass), Androidon Roboto (Material 3). Megosztott `shared.jsx` tartalmazta a tokeneket, ikonokat és a teszt PDF oldalt, amit minden képernyő újrahasznosított.

---

## A tervezési munkamenet

### Indító prompt + tisztázó kérdések

A nyitó prompt egyszerű volt: a funkciólista és egy felhívás, hogy Claude kérdezzen, mielőtt nekiáll.

```text
Your task is to design a native ios and android design for a pdf viewer and editor
library. It should be modern and lightweight. the editor has to be WYSIWYG. The
available functionalities are the following: 1. just viewing the pdf file 2.
Adding/editing/removing freeform drawing where the line color and width can be set
3. Adding/editing/removing text annotations where you can set font size, color.
4. Save/Save as buttons.

Feel free to ask clarification questions if it needed before creating the actual designs.
```

Claude egy rövid kérdéssorral indított (platform-megközelítés, esztétika, akcentszín, toolbar pozíció, képernyők, téma stb.). A legtöbbre simán a „Decide for me" választ adtam, így gyorsan eljutottunk a keretekig (clean & minimal, kék akcent, platformonként natív, light + dark, minden állapot).

### Iteratív változtatási kérések

Az első verzióra egy tömör, számozott listával adtam visszajelzést — a konkrét, pontokba szedett feedback nagyon jól működött. A kérések elrendezési és megjelenítési finomítások voltak mindkét platformon, plusz néhány preferencia kimondása (pl. melyik platform megoldását kövesse). Claude minden pontot egy körben átvezetett, és ahol saját döntést hozott, azt külön jelezte, így a kontroll végig nálam maradt.

---

## Az implementációs munkamenet

### Plan-first megközelítés

Az indító prompt itt is analízist és tervet kért, mielőtt Claude bármit módosított volna a kódon:

```text
In the Design folder, you can see some design files. Your task is to implement the new UI for the pdf viewer and editor library for android and ios. There are some additional features like the undo/redo and the eraser, they don't have to do anything for now. The currently used Android color picker is strange for me as always start with white color, not the selected. Analyse the entire design and the current implementation and create a plan for implementing the designs. Feel free to ask clarification questions.
```

### Iteratív, számozott kérések

Ahogy a tervezésnél, itt is rövid, számozott listákkal finomítottam. A kérések platformra címkézve, konkrét viselkedéssel megfogalmazva mentek a legjobban. A lista jellemzően így nézett ki (a részleteket itt nem fejtem ki, csak a célzott platformot jelzem):

```text
1. Both platforms: There should be a done button for saving text annotations
2. Both platforms: The page numbers should be displayed as it is on the designs
3. Both platforms: ...
4. iOS: ...
5. Both platforms: ...
6. Both platforms: ...
7. Both platforms: ...
```

A többi pont különböző apró interakciós és megjelenítési finomítás volt, jellemzően egy-egy konkrét viselkedés mindkét platformon, néha csak az egyiken. Minden pont rövid, egyértelmű, és egy jól körülhatárolt dologra vonatkozott, így a modell külön feladatokként pontosan dolgozta fel őket.

Egy következő körben már főleg az animációk és a finom interakciós állapotok jöttek. Ezek igényelték a legtöbb pontosítást, mert sok apró, egymásra épülő állapotról van szó, amiket nehéz egy mondatban teljesen lefedni, illetve az LLM-ek nehezen értelmezik a mobil UI-okat.

---

## Ami jól működött

- A tervezés kezdetén tisztázott kérdések sokat segítettek, a „Decide for me" válaszokkal is el lehetett kerülni a generikus eredményt. Azért hagytam a modellre sok döntést, mert egy teljesen új megközelítést szerettem volna behozni az alkalmazásba.
- Claude egy kompakt, újrahasznosítható design systemet is épített (tokenek, ikonok, közös teszt PDF oldal), nem csak különálló képernyőket.
- Platformhű maradt, iOS 26 liquid glass és SF Pro, illetve Android Material 3 és Roboto stílusokkal és betűtípusokkal, miközben az elrendezést egységesítette.
- Folyamatos önellenőrzést végzett a vászon renderelésével, screenshotokkal végignézte, és a konzolhibákat magától javította. Ez sok időbe, illetve tokenbe került.
- Egy fázisban elkészült mindkét platform, minden állapot, light és dark dizájnja.
- A saját döntéseit explicit jelezte (pl. miért tartotta meg a M3 anyagokat).
- Az implementációnál a plan-first és a számozott visszajelzés pontosan célba ért, a végeredmény modern és könnyen használható lett.

## Nehézségek

- Tervezésnél az első rendereléskor nem jelentek meg az artboardok (egy DCArtboard wrapper hiba miatt), a modellnek saját magát kellett debugolnia.
- A képernyőcímkékben `&amp;` jelent meg escape-elési hiba miatt, ezt külön javítani kellett.
- Néhány szerkesztés (str_replace) nem alkalmazódott elsőre, újra kellett csinálni.
- Implementációnál a finom interakciós állapotok és az animációk több kört igényeltek.
- A meglévő Android színválasztó bugját külön jelezni kellett, magától nem vette észre.

---

## Eredmény

Mindkét munkamenet sikeres volt, bár több iteráción keresztül, de a kívánt eredményt hozta. A tervezés egy teljes, modern natív UI-t adott iOS-re és Androidra, kompakt design systemmel. Az implementáció ezt sikeresen beépítette a meglévő könyvtárba és a demó appokba. Modern, könnyen kezelhető végeredmény született. A pár tisztázó kör és a finomhangolás elhanyagolható a feladat méretét és komplexitását figyelembe véve. A fő folyamatok szinte azonnal jól sikerültek, az idő nagy része az apró interakciós részletekre, illetve dizájnmódosításokra ment el.
