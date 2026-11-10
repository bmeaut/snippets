# Hogyan készíts prezentációt AI-jal, kódolás nélkül

Ez az útmutató lépésről lépésre végigvezet, hogyan tudsz egy saját, jól kinéző, animált bemutatót készíteni AI segítségével — anélkül, hogy bármit is programoznod kellene. Semmi mást nem kell hozzá tudnod, csak azt, hogyan kell másolni-beilleszteni szöveget.

## Amire szükséged lesz

- Egy claude.ai fiók (ingyenesen regisztrálható, ha még nincs).
- A [`prompt_template.txt`](prompt_template.txt) fájl (ugyanebben a mappában) — ez a kész promptsablon, ebbe kell majd beleírnod a saját tartalmadat.
- A tartalom, amiből a prezentáció készül — vázlat, jegyzet, korábbi szöveg, bármi, ahogy megvan, nem kell előre rendezned.
- Kb. 10 perc.

## 1. lépés — nyisd meg a `prompt_template.txt` fájlt egy szövegszerkesztőben

Ez a fájl a teljes, kész promptot tartalmazza. A legalján van egy jól látható jelölt hely:

```
<<< IDE ILLESZD BE A SAJÁT TARTALMADAT (vázlat, szöveg, adatok — bármilyen formában, ahogy megvan) >>>
```

## 2. lépés — a jelölt hely helyére írd vagy másold be a saját tartalmadat

Bármilyen formában jó: pontokba szedett vázlat, összefüggő szöveg, akár egy régebbi Word-dokumentumból kimásolt rész. Nem kell előre strukturálnod, ez az AI dolga. Cseréld ki a `<<< IDE ILLESZD BE A SAJÁT TARTALMADAT >>>` sort a saját szövegedre — a prompt többi részéhez ne nyúlj.

## 3. lépés — jelöld ki a fájl teljes tartalmát, és másold ki

Az egészet: a promptot és a hozzá írt saját tartalmat együtt (Ctrl+A / Cmd+A a teljes kijelöléshez, majd Ctrl+C / Cmd+C a kimásoláshoz).

## 4. lépés — nyisd meg a claude.ai-t, indíts egy új beszélgetést, és illeszd be a kimásolt szöveget

## 5. lépés — küldd el az üzenetet, és várd meg a választ

A válasz kétféleképpen érkezhet: vagy egy hosszú kódrészletként (egy szürke dobozban, `html` felirattal), vagy egy letölthető fájlként megjelenítve (egy kártyán "Download" gombbal, mellette a fájl nevével és "Code · HTML" felirattal). Mindkét esetben ez a teljes prezentációd, csak a mentés módja más.

## 6. lépés — mentsd el fájlba

**Ha letölthető fájlként jelent meg** (kártya "Download" gombbal): kattints a "Download" gombra. A fájl a géped Letöltések mappájába kerül, már `.html` kiterjesztéssel — nincs más dolgod, folytasd a 7. lépéssel.

**Ha kódrészletként jelent meg** (szürke doboz, `html` felirattal):
1. Jelöld ki és másold ki a kód teljes tartalmát (a kód doboz jobb felső sarkában általában van egy "másolás" gomb).
2. Nyiss meg egy sima szövegszerkesztőt (Windows: Jegyzettömb, Mac: TextEdit — sima szöveg módban).
3. Illeszd be a kódot, majd mentsd el `prezentacio.html` néven (ügyelj rá, hogy tényleg `.html`-re végződjön a fájlnév, ne `.txt`-re).

## 7. lépés — nyisd meg

Kattints duplán a mentett fájlra. A böngésződ megnyitja, és készen is van a prezentációd. Nyílbillentyűkkel vagy a diákra kattintva lehet lapozni.

## Ha valami nem tetszik

Ne kezdd elölről! Írj vissza ugyanabba a beszélgetésbe, pontosan mit szeretnél máshogy (pl. "a 3. dia legyen rövidebb", "legyen benne egy táblázat is a számokból", "más színvilágot szeretnék"). Az AI a meglévő prezentációt fogja módosítani, és megint kapsz egy teljes, mentésre kész kódot.

## Amire figyelj

- Internetkapcsolat kell hozzá, amikor megnyitod a fájlt (a formázás egy külső forrásból töltődik be).
- Ha a válasz kódrészlete félbeszakadva érkezik (túl hosszú a tartalom), kérd meg az AI-t, hogy folytassa onnan, ahol abbahagyta.
