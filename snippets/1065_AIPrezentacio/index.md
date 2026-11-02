---
layout: default
codename: AIPrezentacio
title: "AI-alapú prezentáció-készítés kódolás nélkül: promptsablon és útmutató nem mérnök felhasználóknak"
tags: snippets mieset claude-code ai-prezentacio reveal-js accessibility
authors: Panka Szalka
---

# AI-alapú prezentáció-készítés kódolás nélkül: promptsablon és útmutató nem mérnök felhasználóknak

## A szcenárió

Egy nem mérnök felhasználó (pl. más szakos oktató, kutató, TDK-hallgató bölcsész/orvos szakról, kkv-tulajdonos) professzionális kinézetű, animált, tagolt prezentációt akar készíteni HTML/JS-tudás és kódolás nélkül, csak a saját tartalmát megadva.

A tervezés kiindulópontja, hogy egy nem mérnöknek valószínűleg nincs Claude Code-ja, terminálja, API-kulcsa. Ha az eszköz használatához bármi ilyesmi kell, nem oldja meg, aminek szánták, függetlenül attól, hogy a végeredmény HTML fájl maga futtatható-e. Ezért:

- a belépési pont egyetlen, claude.ai chatbe bemásolható promptsablon,
- a kimenet egyetlen, önmagában megnyitható HTML fájl, CDN-ről betöltött Reveal.js-szel, telepítés, build-lánc vagy szerver nélkül.

## Mit tartalmaz ez a snippet

Két termék készült el:

- [`prompt_template.txt`](prompt_template.txt): csak a promptsablon, minden magyarázat nélkül, teljes egészében bemásolható a claude.ai chatbe. Annak, aki már ismeri a claude.ai-t, és nem kell neki a lépésenkénti bevezető.
- [`hogyan-hasznald.md`](hogyan-hasznald.md): lépésről lépésre útmutató, technikai zsargon nélkül, a `prompt_template.txt`-re hivatkozva, a claude.ai regisztrációtól a fájl megnyitásáig minden lépéssel, anélkül hogy a teljes promptot újra leírná.

Ez az esettanulmány a kettő fejlődését dokumentálja: mit teszteltem rajtuk, mi hibázott, mit tanultam. A teljes, verzióról verzióra bontott változásnapló a [`fejlesztesi-naplo.md`](fejlesztesi-naplo.md)-ben van, minden változtatáshoz "előtte/utána" fájlpárral.

Ebben a projektben nincs fizetős API-mérés: nem `claude -p` alapú harness-szel, tömeges, kiértékelt hívássorozattal készült, hanem minden teszt claude.ai/Claude Code munkamenetben, promptsablon-generálással és a kimenet ellenőrzésével.

## Fejlesztési módszer

Nem egyszeri generálásra törekedtem, hanem arra, hogy a promptsablont és az útmutatót fokozatosan javítsam: minden talált hibát a demó fájlban és a promptszabályban is javítottam, hogy a következő, ugyanazzal a sablonnal készült prezentáció eleve elkerülje.

Minden verziólépést három rétegű ellenőrzéssel néztem át:

1. **Strukturális**: HTML tag-egyensúly (Python `HTMLParser`), JS-szintaxis (`node -e "new Function(...)"`), CDN-linkek élő állapota (`curl` státuszkód).
2. **Funkcionális**: ahol a JS-logika nem triviális (QR-kód generálás, visszaszámláló-formázás, kereső/szűrő, pizza-kalkulátor kerekítés, konfetti-részecske generálás, tooltip-pozícionálás), a kivont kódot lefuttattam Node.js-ben, konkrét bemenetekre ellenőrizve a kimenetet.
3. **Vizuális**: a fájl megnyitása böngészőben. Ezzel a réteggel találtam meg a legtöbb hibát (l. lentebb, Módszertani buktatók). Az első két réteggel egyiket sem találtam volna meg, mert mindegyik CSS-elrendezési vagy elrendezés-torzulási probléma volt.

A három réteg mellé egy negyedik is jött: független tesztelők, akik kizárólag az útmutató alapján, technikai segítség nélkül készítenek egy saját prezentációt. Az első tesztelő mérnök volt, a további tesztelők nem mérnökök. Az eredmények a Külső tesztelők visszajelzése szakaszban vannak.

## A promptsablon felépítése

A `prompt_template.txt` négy rétegből épül fel:

1. **Formai alapkövetelmények** (1-3. pont): egyetlen, önállóan futtatható HTML fájl, CDN-betöltés (nem modulként, hogy `file://`-ról is működjön), "6x6-szabály" (diánként max. kb. 6 gondolat, soronként max. 6-8 szó).
2. **Design-alapszabályok** (4. pont): egységes Reveal.js-téma, WCAG kontrasztarány (4.5:1 normál szöveg, 3:1 nagy szöveg), betűméret alsó korlát (0.6em/0.5em), egységes színpaletta, jelentés soha kizárólag színnel, diaelrendezés-váltás, hosszú cím tördelésének kezelése, `flex-shrink: 0` a lista-ikonokon.
3. **Vizuális elemek** (5, 11-14. pont): dia-átmenet, inline SVG-ikonok, kép-beágyazás (relatív útvonal vagy base64), KaTeX-képletek, kód-szintaxis-kiemelés.
4. **22 interaktív/programozott elem** (6-32. pont, a nem-interaktív design-pontok nélkül), mindegyik feltételes ("csak akkor, ha a tartalom X jellegű"), és mindegyikhez van egy konkrét demó, l. alább.

A sablon 3 körben, fokozatosan bővült 4, majd 6, majd 12 új elemmel.

## Interaktív elemek, mindegyikhez példával

Minden sor egy megnyitható demóra mutat. Mind a 22 elemhez van élő, beágyazott bemutató is lentebb, "Minden elem élőben, beágyazva" cím alatt, ugyanebben a sorrendben.

| Pont | Elem | Demó |
|---|---|---|
| 6 | Automatikus léptetés (autoSlide) | [`output/ppt4_varoterem.html`](output/ppt4_varoterem.html) |
| 7 | Reveal.js fragments | [`output/ppt3_evszakok.html`](output/ppt3_evszakok.html) |
| 8 | Animált számláló | [`output/ppt2_napelem.html`](output/ppt2_napelem.html) |
| 9 | Interaktív kvíz | [`output/ppt3_evszakok.html`](output/ppt3_evszakok.html) |
| 10 | Csúszkával vezérelt élő diagram | [`output/ppt2_napelem.html`](output/ppt2_napelem.html) |
| 16 | Előadói jegyzet | [`output/ppt2_napelem.html`](output/ppt2_napelem.html) |
| 17 | QR-kód | [`output/ppt7_ai-workshop.html`](output/ppt7_ai-workshop.html) |
| 18 | Fülek (tabs) | [`output/ppt5_csomagok.html`](output/ppt5_csomagok.html) |
| 19 | Vizuális visszaszámláló | [`output/ppt6_workshop.html`](output/ppt6_workshop.html) |
| 20 | Gépelés-effekt | [`output/ppt5_csomagok.html`](output/ppt5_csomagok.html) |
| 21 | Személyre szabható kalkulátor | [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html) |
| 22 | Sorsoló/randomizáló | [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html) |
| 23 | Kattintható checklist | [`output/ppt8_faq.html`](output/ppt8_faq.html) |
| 24 | Drag-and-drop párosítás | [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html) |
| 25 | Előtte/utána kép-csúszka (ismert, megoldatlan hiba, l. Módszertani buktató 5) | [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html) |
| 26 | Kereshető/szűrhető lista | [`output/ppt8_faq.html`](output/ppt8_faq.html) |
| 27 | Konfetti-effekt | [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html) |
| 28 | Saját videó beágyazása | [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html) |
| 29 | Nagyítható kép (lightbox) | [`output/ppt8_faq.html`](output/ppt8_faq.html) |
| 30 | Interaktív idővonal | [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html) |
| 31 | Kifejezés-magyarázó tooltip (glossary) | [`output/ppt8_faq.html`](output/ppt8_faq.html) |
| 32 | Rajzolható mini-vászon | [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html) |

Egy külön demó, [`output/ppt7_ai-workshop.html`](output/ppt7_ai-workshop.html), 8 elemet mutat be egyetlen, koherens prezentációban (fragments, kvíz, fülek, csúszkás diagram, animált számláló, visszaszámláló, gépelés-effekt, QR-kód). Ez nem az egyenkénti tesztek helyett készült, hanem azért, hogy leellenőrizzem: az elemek kombinálva is működnek-e.

### Minden elem élőben, beágyazva

Minden elem saját alcím alatt, közvetlenül a hozzá tartozó beágyazott diával és leírással szerepel, ugyanabban a sorrendben, mint a fenti táblázat. A beágyazott dia kattintható/nyíllal léptethető, mert a beágyazott fájl ugyanaz a HTML, ami önállóan is fut.

#### Automatikus léptetés: autoSlide (6. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt4_varoterem.html#/0" style="width:100%;height:480px;border:0;" loading="lazy" title="Automatikus léptetés"></iframe>
</div>

A teljes 5 diás kijelző `autoSlide: 7000, loop: true` beállítással fut: minden dia 7 másodperc után magától tovalép, a sorozat végén elölről kezdi. Élő, előadó által tartott bemutatónál ez a beállítás tiltott (l. 6. pont feltétele), csak felügyelet nélküli kijelzőnél használható.

**Próba:** ha nem történik kattintás a beágyazott demóban, néhány másodperc után magától lapoz tovább. Teljes fájl: [`output/ppt4_varoterem.html`](output/ppt4_varoterem.html).

#### Reveal.js fragments (7. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt3_evszakok.html#/1" style="width:100%;height:480px;border:0;" loading="lazy" title="Reveal.js fragments"></iframe>
</div>

A "Tavasz" dián a felsorolt pontok `class="fragment"` miatt egyesével jelennek meg, nem mind egyszerre.

**Próba:** a beágyazott demóba kattintva, jobbra nyíllal léptetve minden lépés egy új sort fed fel, mielőtt a dia továbblép. Teljes fájl: [`output/ppt3_evszakok.html`](output/ppt3_evszakok.html).

#### Animált számláló (8. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0 0.5em 0;">
<iframe id="frame-counter" src="output/ppt2_napelem.html#/4" style="width:100%;height:480px;border:0;" loading="lazy" title="Animált számláló"></iframe>
</div>
<button onclick="var f=document.getElementById('frame-counter');f.src='output/ppt2_napelem.html?r='+Date.now()+'#/4';" style="font-size:0.8em;padding:0.3em 0.8em;border:1px solid #999;border-radius:6px;background:#f5f5f5;cursor:pointer;margin-bottom:0.8em;">Animáció újraindítása</button>

Az "Összegzés" dián a szám 0-ról fut fel 2 680 000 Ft-ig, kb. 1.2 másodperc alatt, `requestAnimationFrame`-mel. A dia betöltésekor egyszer lejátszódik, utána a végértéken marad.

**Próba:** az "Animáció újraindítása" gomb megnyomására a felfutás elölről indul. Teljes fájl: [`output/ppt2_napelem.html`](output/ppt2_napelem.html).

#### Interaktív kvíz (9. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0 0.5em 0;">
<iframe id="frame-quiz" src="output/ppt3_evszakok.html#/5" style="width:100%;height:480px;border:0;" loading="lazy" title="Interaktív kvíz"></iframe>
</div>
<button onclick="var f=document.getElementById('frame-quiz');f.src='output/ppt3_evszakok.html?r='+Date.now()+'#/5';" style="font-size:0.8em;padding:0.3em 0.8em;border:1px solid #999;border-radius:6px;background:#f5f5f5;cursor:pointer;margin-bottom:0.8em;">Kvíz újraindítása</button>

"Melyik évszakban hullanak a falevelek?" kérdés, 4 kattintható gomb. Kattintásra minden gomb letiltódik, a helyes válasz zölddel és ✓ szimbólummal, egy hibásan kattintott gomb pirossal és ✗ szimbólummal jelenik meg, vagyis szín és forma is jelez, nem csak szín (l. Módszertani buktató 4).

**Próba:** egy rossz válaszra kattintva mindkét jelzés egyszerre látszik; a "Kvíz újraindítása" gombbal a helyes válasz is megnézhető. Teljes fájl: [`output/ppt3_evszakok.html`](output/ppt3_evszakok.html).

#### Csúszkával vezérelt élő diagram (10. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt2_napelem.html#/1" style="width:100%;height:480px;border:0;" loading="lazy" title="Csúszkával vezérelt élő diagram"></iframe>
</div>

Chart.js oszlop+vonal diagram egy 5 éves napelem-megtakarítási adatsoron. A dia alatti csúszka a megtakarítás éves növekedési ütemét állítja (0-10%, alapból 5.5%). Mozgatásra a script mértani sorral újraszámolja mind az 5 év adatát, frissíti a diagram mindkét adatsorát (`chart.update()`), és a csúszka mellett számmal is mutatja az aktuális értéket.

**Próba:** a csúszka mozgatására élőben változik a diagram alakja. Teljes fájl: [`output/ppt2_napelem.html`](output/ppt2_napelem.html).

#### Előadói jegyzet (16. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt2_napelem.html#/1" style="width:100%;height:480px;border:0;" loading="lazy" title="Előadói jegyzet"></iframe>
</div>

Minden tartalmi dia kapott egy `<aside class="notes">` jegyzetet, ami csak az előadói nézetben látszik, a közönség nem látja.

**Próba:** a beágyazott demóba kattintva, az `S` billentyű megnyomására egy új böngészőablak nyílik meg az aktuális és a következő dia jegyzeteivel (ehhez a böngészőnek engednie kell a felugró ablakot ezen az oldalon). Teljes fájl: [`output/ppt2_napelem.html`](output/ppt2_napelem.html).

#### QR-kód (17. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt7_ai-workshop.html#/7" style="width:100%;height:480px;border:0;" loading="lazy" title="QR-kód"></iframe>
</div>

A `qrcode-generator` CDN-könyvtárral, futásidőben, kliens oldalon generált, inline SVG-vé alakított kód, nem külső QR-generáló API hívása, ami törhetne vagy nyomon követhetne. 170px, kontrasztos szegélyes dobozban, hogy a Reveal.js kicsinyítése után is beolvasható maradjon. Ez a demó nem lép tovább magától (nincs `autoSlide`), úgyhogy a kód nyugodtan nézhető/beolvasható marad.

**Próba:** telefonnal beolvasva egy valós URL-re mutat. Teljes fájl: [`output/ppt7_ai-workshop.html`](output/ppt7_ai-workshop.html).

#### Fülek (18. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt5_csomagok.html#/1" style="width:100%;height:480px;border:0;" loading="lazy" title="Fülek (tabs)"></iframe>
</div>

3 összehasonlítható előfizetési csomag (Alap/Optimum/Prémium), kattintható fül-fejlécekkel. Vanília JS váltja a kiválasztott panelt (`display: none`/`block`), CDN-függőség nélkül.

**Próba:** a fülek közötti váltásra a dia mérete nem ugrál. Teljes fájl: [`output/ppt5_csomagok.html`](output/ppt5_csomagok.html).

#### Vizuális visszaszámláló (19. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt6_workshop.html#/2" style="width:100%;height:480px;border:0;" loading="lazy" title="Vizuális visszaszámláló"></iframe>
</div>

5 perces gyakorlathoz tartozó visszaszámláló, MM:SS formátumban, start/szünet/reset gombbal. Alapból nem indul el magától, az előadónak kell elindítania.

**Próba:** a "Start" gomb megnyomására elindul a másodperces visszaszámlálás; a "Szünet" és "Újra" gombok is kipróbálhatók. Teljes fájl: [`output/ppt6_workshop.html`](output/ppt6_workshop.html).

#### Gépelés-effekt (20. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0 0.5em 0;">
<iframe id="frame-typewriter" src="output/ppt5_csomagok.html#/2" style="width:100%;height:480px;border:0;" loading="lazy" title="Gépelés-effekt"></iframe>
</div>
<button onclick="var f=document.getElementById('frame-typewriter');f.src='output/ppt5_csomagok.html?r='+Date.now()+'#/2';" style="font-size:0.8em;padding:0.3em 0.8em;border:1px solid #999;border-radius:6px;background:#f5f5f5;cursor:pointer;margin-bottom:0.8em;">Effekt újraindítása</button>

A záródia mondata karakterenként jelenik meg, `Reveal.on('slidechanged', ...)`-re indítva. A dia betöltésekor egyszer lejátszódik, utána a teljes mondat marad kiírva.

**Próba:** az "Effekt újraindítása" gomb megnyomására a felépülés elölről indul. Teljes fájl: [`output/ppt5_csomagok.html`](output/ppt5_csomagok.html).

#### Személyre szabható kalkulátor (21. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt9_csapatesemeny.html#/4" style="width:100%;height:480px;border:0;" loading="lazy" title="Személyre szabható kalkulátor"></iframe>
</div>

Az "Ebédrendelés kalkulátor" dián egy `<input type="number">` mezőbe beírt létszám alapján számol pizzaszámot (3 fő/pizza, felfelé kerekítve).

**Próba:** a mezőbe beírt új létszámra az eredmény azonnal frissül. Teljes fájl: [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html).

#### Sorsoló/randomizáló (22. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt9_csapatesemeny.html#/2" style="width:100%;height:480px;border:0;" loading="lazy" title="Sorsoló"></iframe>
</div>

A "Jégtörő: ki kezdi?" dián egy gombra kattintva 5 névből választ egyet, rövid "pörgés"-animációval (`setInterval`, kb. 1.3 másodperc).

**Próba:** a "Sorsolás indítása" gomb megnyomására elindul a sorsolás. Teljes fájl: [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html).

#### Kattintható checklist (23. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt8_faq.html#/1" style="width:100%;height:480px;border:0;" loading="lazy" title="Kattintható checklist"></iframe>
</div>

A "Mielőtt elkezded" dián 3 kattintható jelölőnégyzet van, fölöttük élő "X/3 kész" számlálóval.

**Próba:** egy-két elem kipipálására a számláló azonnal frissül. Teljes fájl: [`output/ppt8_faq.html`](output/ppt8_faq.html).

#### Drag-and-drop párosítás (24. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt9_csapatesemeny.html#/3" style="width:100%;height:480px;border:0;" loading="lazy" title="Drag-and-drop párosítás"></iframe>
</div>

HTML5 drag-and-drop API-val 3 névhez kell hozzárendelni 3 érdekességet. Sikeres vagy sikertelen párosításnál a rendszer szín + ikon kombinációval jelez, nem csak színnel.

**Próba:** egy nevet egy rossz érdekességre húzva megjelenik a hibás párosítás jelzése. Teljes fájl: [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html).

#### Előtte/utána kép-csúszka (25. pont): ismert, megoldatlan hiba

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0 0.5em 0;">
<iframe src="output/ppt9_csapatesemeny.html#/5" style="width:100%;height:480px;border:0;" loading="lazy" title="Előtte/utána kép-csúszka"></iframe>
</div>

**Ez az egyetlen elem a 22 közül, ami nem működik hibátlanul**: a csúszka húzásakor a bal oldali kép láthatóan elmozdul, ahelyett hogy csak a "felújítás utáni" kép fedné fel fokozatosan a "felújítás előttit". Egy próbált javítás (`draggable="false"`, `pointer-events: none` a képeken) nem oldotta meg, l. Módszertani buktató 5. Az "Iroda felújítás" dián a két kép egyébként valódi fotó (NASA Earth Observatory, Aral-tó 2000 és 2018, [forrás](https://science.nasa.gov/earth/earth-observatory/world-of-change/aral-sea/), közkincs), nem a saját irodáról készült felvétel. Ezek csak a csúszka-funkciót szemléltetik. Teljes fájl: [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html).

#### Kereshető/szűrhető lista (26. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt8_faq.html#/4" style="width:100%;height:480px;border:0;" loading="lazy" title="Kereshető/szűrhető lista"></iframe>
</div>

A "Gyakori kérdések" dián egy 8 elemes lista gépelés közben élőben szűrődik.

**Próba:** a keresőmezőbe beírt szóra (pl. "ingyenes") a lista azonnal szűkül a találatokra. Teljes fájl: [`output/ppt8_faq.html`](output/ppt8_faq.html).

#### Konfetti-effekt (27. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0 0.5em 0;">
<iframe id="frame-confetti" src="output/ppt9_csapatesemeny.html#/8" style="width:100%;height:480px;border:0;" loading="lazy" title="Konfetti-effekt"></iframe>
</div>
<button onclick="var f=document.getElementById('frame-confetti');f.src='output/ppt9_csapatesemeny.html?r='+Date.now()+'#/8';" style="font-size:0.8em;padding:0.3em 0.8em;border:1px solid #999;border-radius:6px;background:#f5f5f5;cursor:pointer;margin-bottom:0.8em;">Demó újraindítása</button>

A záródiára lépéskor egy vanília canvas-animáció lehulló, színes formákat rajzol. Eredetileg csak tényleges dia-váltásra (`Reveal.on('slidechanged', ...)`) indult, de a beágyazott demó közvetlenül a záródián töltődik be, ahol nincs "váltás", ezért a script induláskor is ellenőrzi, hogy a kezdő dia a záródia-e, és ha igen, azonnal elindítja a konfettit.

**Próba:** a beágyazott demó betöltésekor azonnal elindul a konfetti. A "Demó újraindítása" gomb ugyanezt ismétli meg. Teljes fájl: [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html).

#### Saját videó beágyazása (28. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt9_csapatesemeny.html#/6" style="width:100%;height:480px;border:0;" loading="lazy" title="Saját videó beágyazása"></iframe>
</div>

A "Köszöntő videó" dián egy `<video src="koszonto.mp4" controls>` hivatkozás van. A beágyazott demóban a lejátszó üresen jelenik meg, mert maga a `koszonto.mp4` fájl nincs a repóban. Ez dokumentált korlát (l. Korlátok), élesben ezt a felhasználó másolná a mentett HTML mellé, ugyanazzal a névvel. Teljes fájl: [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html).

#### Nagyítható kép: lightbox (29. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt8_faq.html#/3" style="width:100%;height:480px;border:0;" loading="lazy" title="Nagyítható kép (lightbox)"></iframe>
</div>

A "Jóváhagyási folyamat" dián egy kattintható SVG-folyamatábra van, ami kattintásra sötétített háttér előtt, felnagyítva jelenik meg.

**Próba:** a folyamatábrára kattintva megnyílik a nagyított nézet, a sötétített területre vagy Escape-re bezárható. Teljes fájl: [`output/ppt8_faq.html`](output/ppt8_faq.html).

#### Interaktív idővonal (30. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt9_csapatesemeny.html#/1" style="width:100%;height:480px;border:0;" loading="lazy" title="Interaktív idővonal"></iframe>
</div>

A "Csapatunk története" dián 4 kattintható évszám van, mindegyikhez saját részlet-szöveg tartozik alattuk.

**Próba:** egy másik évszámra kattintva (nem csak az alapból kiemelt "2019"-re) megjelenik a hozzá tartozó részlet. Teljes fájl: [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html).

#### Kifejezés-magyarázó tooltip: glossary (31. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt8_faq.html#/2" style="width:100%;height:480px;border:0;" loading="lazy" title="Kifejezés-magyarázó tooltip"></iframe>
</div>

A "prompt" kifejezés a bekezdés bal szélén áll, ezért az eredetileg középre igazított, fix szélességű buborék kilógott volna a képernyő bal széléről. A hover/fókusz eseményre lefutó script `getBoundingClientRect()`-tel megméri a buborék tényleges pozícióját, és ha túllógna, visszatolja a látható tartományba (l. `fejlesztesi-naplo.md` v20).

**Próba:** az egeret a bekezdés elején álló "prompt" szóra víve a buborék nem lóg ki balra. Teljes fájl: [`output/ppt8_faq.html`](output/ppt8_faq.html).

#### Rajzolható mini-vászon (32. pont)

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/ppt9_csapatesemeny.html#/7" style="width:100%;height:480px;border:0;" loading="lazy" title="Rajzolható mini-vászon"></iframe>
</div>

A "Csoportfotó ötlet" dián egy SVG helyszínrajz fölé húzott, átlátszó `<canvas>` rétegre lehet egérrel rajzolni, "Törlés" gombbal.

**Próba:** a helyszínrajzra egérrel rajzolva, majd a "Törlés" gombbal a jelölés eltávolítható. Teljes fájl: [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html).

## Téma-lefedettségi próbák

A fenti táblázat az elemeket teszteli, ez a táblázat azt, hogy a **változatlan** promptsablon tartalmilag különböző témákon is jól teljesít-e. Nem szakma szerint kategorizálva, csak a téma tartalmi jellege szerint.

| Téma | Jellemző tartalom | Amit főleg próbára tesz | Demó |
|---|---|---|---|
| Kerti komposztálás | Egyszerű, szöveges vázlat | Alap diaszerkezet, olvashatóság | [`output/ppt1_kerti-komposztalas.html`](output/ppt1_kerti-komposztalas.html) |
| Napelem-megtérülés | Számszerű adat, képlet, saját fotó | Diagram, KaTeX, kép-beágyazás, elrendezés | [`output/ppt2_napelem.html`](output/ppt2_napelem.html) |
| Az évszakok | Kevés szöveg, sok vizuál, egyszerű nyelvezet | Ikon-sűrű, gyerekbarát tartalom | [`output/ppt3_evszakok.html`](output/ppt3_evszakok.html) |

Az interaktív elemek teszteléséhez emellett 5 további, kifejezetten erre a célra írt téma készült (fodrászat váróterem-kijelző, internet-előfizetési csomagok, workshop-gyakorlat, belső AI-tudásbázis, céges csapatépítő nap). Ezek nem részei a fenti tartalmi lefedettségi táblázatnak, csak az adott elem bemutatásához illő kontextust adnak.

## Külső tesztelők visszajelzése

Az útmutatót és a sablont független tesztelőkkel is kipróbáltattam. Az első tesztelő mérnök volt, a többiek nem mérnökök, mert a sablon őket célozza. Mindenki ugyanazt a csomagot kapta: a `prompt_template.txt`-t, az útmutató PDF-változatát és egy egyoldalas feladatlapot öt kérdéssel. Saját témából kellett prezentációt készíteniük, kizárólag az útmutató alapján, segítség nélkül (egy tesztelő a mentésnél mégis kapott segítséget, l. lent). A tesztelők hozzájárultak a prezentációjuk és a feladatlapjuk összefoglalójának közzétételéhez. A visszajelzések után az útmutatót és a sablont nem módosítottam, hogy az eredmények pontosan az elküldött változatra vonatkozzanak.

### Első tesztelő (mérnök, Mac)

Segítség nélkül sikerült kész prezentációt készítenie, kb. 20 perc alatt, ebből kb. 15 perc volt a válasz generálása (Claude Opus). A saját témája egy Porsche-modellpaletta összevetés lett, 24 dián.

Visszajelzése röviden:

- Egy elakadás volt: Mac-en a TextEdit alapból formázott szövegként mentette a fájlt, nem HTML-ként. Az útmutató csak annyit írt, hogy "sima szöveg módban".
- Szerinte sok helyen kb. másfélszer olyan széles képernyőre készült a tartalom, mint a valós, ezért kilógott. Nálam ugyanez a fájl hibátlanul működött, ezért lehet, hogy a tesztelő képernyőjének mérete okozta (16 colos MacBook Pro).
- A feladatlapból nem derült ki egyértelműen számára, hogy a téma szabadon választható.

Az általa készített prezentáció (a beágyazott dia nyilakkal léptethető, a teljes fájl: [`output/tesztelo1_porsche.html`](output/tesztelo1_porsche.html)):

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/tesztelo1_porsche.html#/0" style="width:100%;height:480px;border:0;" loading="lazy" title="Az első tesztelő prezentációja"></iframe>
</div>

### Második tesztelő (nem mérnök, Windows 11, Chrome)

A témája a koponyák kikészítése (vadásztrófea-készítés) lett, 14 dián, kb. 20 perc alatt. A feladatlapon az első kérdésre ("Sikerült elkészíteni a prezentációt segítség nélkül?") azt írta, hogy nem tudta `.html`-ként elmenteni. A mentésben én segítettem neki, ezért ő nem segítség nélkül jutott el a kész fájlig.

A többi válasza: az útmutató nem volt érthetetlen, a prezentáció használható volt, több észrevétele nem volt. A prezentációt az útmutató alapján készítette, a tartalmát (a szakmai állításokat) nem ellenőriztem. A teljes fájl: [`output/tesztelo2_koponyak.html`](output/tesztelo2_koponyak.html).

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/tesztelo2_koponyak.html#/0" style="width:100%;height:480px;border:0;" loading="lazy" title="A második tesztelő prezentációja"></iframe>
</div>

### Harmadik tesztelő (nem mérnök, Windows 11, Opera)

A témája a hibajavító kódok (lineáris, Hamming- és Reed–Solomon-kódok) lett, 17 dián. A prompt módosításától a generált prezentáció ellenőrzéséig kb. 20 perc telt el. A feladatlap szerint a prezentáció legenerálása megakadás nélkül sikerült, az útmutatót érthetőnek és megfelelően részletesnek találta, a prezentáció megjelenésével nem volt probléma.

Két észrevétele volt:

- Az útmutató részletezhetné, hogy számít-e a kiválasztott modell vagy a gondolkodási szint, és befolyásolja-e a kapott prezentáció minőségét. Ezt nem vizsgáltam, az útmutató erről nem szól.
- Olyan témáknál, ahol egy témakört nem lehet egy diával elintézni (például matematikai témák), a prezentáció inkább keret, amit az előadó a saját magyarázataival egészít ki. A prezentáció az alapinformációkat, összefüggéseket és képleteket tartalmazza, ezért aki az előadó magyarázata nélkül akarna belőle tanulni, nehezen boldogulna.

A prezentáció képleteit és példáit (a Hamming(7,4) kódolás és szindrómás hibajavítás, az RS(4,2) kódolás GF(5) felett, a ráták táblázata) kézi újraszámolással ellenőrizték, mindegyik helyes. A teljes fájl: [`output/tesztelo3_hibajavito-kodok.html`](output/tesztelo3_hibajavito-kodok.html).

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/tesztelo3_hibajavito-kodok.html#/0" style="width:100%;height:480px;border:0;" loading="lazy" title="A harmadik tesztelő prezentációja"></iframe>
</div>

### Negyedik tesztelő (nem mérnök, Windows 11, Chrome)

A témája Bergen (norvég város, látnivalók) lett, 12 dián. A feladatlap szerint sikerült, a prezentáció rendben volt, kb. 10 perc alatt, a Claude-fiók létrehozásával együtt. Az útmutatóban csak azt hiányolta, hogy nem tudta, hol kell a Claude-fiókot létrehozni. Windows 11 és Chrome böngésző.

A prezentáció a dia-képek közül kettőt a fájlba ágyazott, további kilenc képre (`floyen.jpg`, `ulriken.jpg` stb.) külön fájlként hivatkozik. Ezek a képfájlok nem érkeztek meg, ezért az alábbi beágyazott változatban ezeken a helyeken "Hiányzó kép" jelölő látszik. A címdián beágyazott csoportfotót (a tesztelő is szerepelt rajta) adatvédelmi okból eltávolítottam, a helyén "Kép helye" jelölő áll. A prezentáció egyébként változatlan. A teljes fájl: [`output/tesztelo4_bergen.html`](output/tesztelo4_bergen.html).

<div style="border:1px solid #ccc;border-radius:8px;overflow:hidden;margin:1em 0;">
<iframe src="output/tesztelo4_bergen.html#/0" style="width:100%;height:480px;border:0;" loading="lazy" title="A negyedik tesztelő prezentációja"></iframe>
</div>

### A négy visszajelzés összevetése

| | Mérnök | Rendszer | Téma | Dia | Idő | Segítség nélkül |
|---|---|---|---|---|---|---|
| 1. | igen | Mac | Porsche-modellek | 24 | kb. 20 perc | igen |
| 2. | nem | Windows 11, Chrome | Koponyák kikészítése | 14 | kb. 20 perc | nem (a mentésnél segítséget kapott) |
| 3. | nem | Windows 11, Opera | Hibajavító kódok | 17 | kb. 20 perc | igen (a feladatlap szerint) |
| 4. | nem | Windows 11, Chrome | Bergen | 12 | kb. 10 perc | igen (a feladatlap szerint) |

- Mind a négy tesztelő eljutott egy kész prezentációig.
- A `.html` fájl mentése két tesztelőnél okozott gondot (az elsőnél a TextEdit formázott szövegként mentett, de ezt maga megoldotta, a másodiknál a mentésben segítettem neki).
- Egy tesztelő nem találta, hol kell Claude-fiókot létrehozni.
- A prezentációk megjelenésére vagy működésére az első tesztelőn kívül senki nem panaszkodott.

## Módszertani buktató 1: strukturálisan helyes, vizuálisan hibás

A promptsablon 3. verzióját csak strukturálisan ellenőriztem (tag-egyensúly, CDN-elérhetőség), böngészőben nem néztem meg. Amikor tényleges megnyitás történt, három hiba derült ki: a KaTeX-képlet mérethatár nélkül a Reveal.js alap, nagy betűméretét örökölte és kilógott a diából; a diagram-konténernek nem volt magasságkorlátja, ezért a diagram és az alatta lévő táblázat összecsúszott; és semmilyen elem nem került egymás mellé, minden egymás alá volt rendezve.

A javítás: explicit betűméret és `\dfrac` helyett `\frac` a képletnél, rögzített magasságú diagram-konténer `maintainAspectRatio: false`-lal, és egy `.two-col` flexbox-osztály a diagram+táblázat, illetve kép+szöveg párokhoz. A promptba bekerült egy általános szabály: egy dia soha nem lóghat ki, és több elemnél mindig két oszlopos elrendezést kell használni.

A saját ellenőrzésemmel (tag-egyensúly, CDN-elérhetőség) nem vettem észre a vizuálisan hibás kimenetet. Maga az ellenőrzési módszer volt hiányos, nem csak a generált kód.

## Módszertani buktató 2: téves első diagnózis

Egy dia minimálisan görgethetőnek bizonyult. Az első feltételezés az volt, hogy egy hosszú, egysoros KaTeX-formula szélessége lóg ki, ezért a formulát többsoros elrendezésre kellett volna alakítani. Ez tévesnek bizonyult: nem vízszintes, hanem függőleges irányú, minimális túlcsordulásról volt szó.

A valódi ok: négy egymás alatti blokkelem (egy `<h2>`, három `<p>`) a böngésző alapértelmezett margóival együtt néhány pixellel túlnyúlt a dia magasságán. A javítás: explicit, szűkebb margó minden elemen (`margin: 0.3em 0`), a formula pedig egysoros maradt. A promptba bekerült, hogy sűrű, több szöveges elemet tartalmazó dián a böngésző alapértelmezett margói önmagukban is túlcsordulást okozhatnak, és hogy `overflow: auto`/`scroll` nem elfogadható megoldás, mert elrejti a problémát ahelyett, hogy megoldaná.

## Módszertani buktató 3: három hiba egyszerre egy összefoglaló demóból

Egy összefoglaló demó (`ppt7_ai-workshop.html`), ami az addig elkészült elemeket egyben mutatta be, egyszerre három hibát fedett fel.

Egy hosszú, összetett magyar szó a cím dián csúnyán, kötőjel nélkül tört. A Reveal.js saját CSS-e (`word-break: break-word`) és a "white" téma nagybetűssé alakítása együtt okozta. Javítás: `overflow-wrap: normal; word-break: normal; hyphens: auto;` a fejléceken, hosszú címnél explicit kisebb betűméret.

A QR-kódok (110-130px, keret nélkül) könnyen elveszhettek a dián, főleg mivel a Reveal.js a teljes prezentációt kicsinyítheti a néző képernyőjéhez. Javítás: 170px-re növelve, kontrasztos szegélyes dobozban.

A harmadik: az egyik lista leghosszabb szövegű elemének ikonja láthatóan kisebbre zsugorodott, mint a többié. Az ok `flex-shrink: 0` hiánya volt az SVG-ken egy flex-konténerben. Ez a szabály korábban, két másik demóban (`ppt1_kerti-komposztalas.html`, `ppt3_evszakok.html`) már be volt építve, de három újabb fájl (`ppt7_ai-workshop.html`, `ppt4_varoterem.html`, `ppt6_workshop.html`) megírásakor kimaradt. Egy teljes körű, `grep`-alapú audittal megtaláltam és kijavítottam mindhárom hiányzó előfordulást az összes addigi output-fájlon.

A tanulság, elsősorban a harmadik hibából: egy már egyszer megtalált és kijavított hibát nem elég egyszer, egy fájlban kijavítani: ha a szabály nincs a promptban rögzítve, a következő, kézzel írt demó könnyen újra elköveti.

## Módszertani buktató 4: külső szakirodalomban találtam rést a saját szabályaimban

Külső kutatással (WebAIM, Section508.gov, UCR Student Disability Resource Center akadálymentességi irányelvei) két hiányosságot találtam a saját szabályaimban: a "kontraszt" addig szám nélküli, minőségi elvárás volt (a WCAG konkrét, ellenőrizhető 4.5:1/3:1 arányt ad), és a kvíz-funkció addig kizárólag színnel jelezte a helyes/helytelen választ, ami sérti a "ne bízd a jelentést kizárólag színre" elvet (színtévesztőknek a szín önmagában nem elég). Mindkettő bekerült a promptba, a kvíz-demó a szín mellé ✓/✗ szimbólumot is kapott.

Ez volt az egyetlen eset, amikor nem saját teszteléssel, hanem publikált szakirodalommal ellenőriztem a meglévő szabályokat.

## Módszertani buktató 5: egy hiba, amit nem sikerült megoldani

Az előtte/utána kép-csúszkánál (25. pont, `ppt9_csapatesemeny.html`) a csúszka húzásakor a bal oldali (előtte) kép láthatóan elmozdul, ami a funkciót használhatatlanná teszi. Az első hipotézis az volt, hogy a böngésző natív kép-húzás gesztusa (a beépített "kép kihúzása" funkció) ütközik a csúszka mozgatásával, mert a két `<img>` elem nem tiltotta le ezt (`draggable="false"`, `pointer-events: none` hiánya). Ez a javítás megtörtént, de **nem oldotta meg a problémát**, a hiba több iteráció után is fennáll.

Ez a hiba nyitva, megoldatlanul marad ebben a snippetben, mert nem minden talált problémára sikerül javítást találni.

## Korlátok

- **Az előtte/utána kép-csúszka (25. pont) ismerten hibás**: a csúszka húzásakor a bal oldali kép elmozdul, egy próbált javítás (l. Módszertani buktató 5) nem oldotta meg. A többi 21 élő demó ettől függetlenül működik.
- **Kevés tesztelő.** Négy tesztelő (egy mérnök és három nem mérnök) jutott el kész prezentációig az útmutatóból. Ez kevés ahhoz, hogy az eredmény általánosítható legyen a célközönségre. Nem minden adat szerepel mindegyik tesztelőnél (az elsőnél nincs böngésző megadva), és csak Windows 11 és Mac szerepel, más rendszerek nem. A segítség nélküli teljesítés a feladatlapokon alapul, ezt nem ellenőriztem.
- A validáció három rétege (struktúra, Node-futtatás, vizuális ellenőrzés) sem helyettesíti a tényleges felhasználói tesztelést: a vizuális réteg is utólagos, a saját megnyitásomon alapul, nem egy előre rögzített ellenőrzőlistán.

## Összefoglaló tanulságok

1. **A strukturális ellenőrzés (tag-egyensúly, CDN-elérhetőség, JS-szintaxis) szükséges, de nem elégséges.** Több valós hiba (méretezés, elrendezés, tördelés) kizárólag tényleges böngészős megnyitással derült ki.
2. **A tényleges Node.js-futtatás erősebb ellenőrzés, mint a puszta szintaxis-vizsgálat.** Ahol a JS-logika nem triviális volt (QR-generálás, kerekítés, tooltip-pozícionálás), a kivont kód valódi lefuttatása konkrét, számszerű bemenetekre igazolta a helyességet, nem csak azt, hogy nincs benne elgépelés.
3. **Egy megtalált hiba javítása egy fájlban nem elég.** Ha a szabály nincs a promptban rögzítve, egy következő, kézzel írt demó ugyanazt a hibát újra elköveti. Emiatt minden talált hiba mindkét fő fájlba (promptsablon és útmutató) visszakerült.
4. **A saját hibadiagnózis is tévedhet.** Egy tünet rövid leírása (pl. "görgethető a dia") első ránézésre téves feltételezéshez vezethet a hiba irányáról/okáról. A pontos, részletes hibaleírás volt kulcsfontosságú a helyes javításhoz.
5. **Külső, publikált szakirodalom olyan rést is találhat, amit a saját tesztelés nem.** Az akadálymentességi irányelvek (WCAG kontraszt, "ne csak színnel jelölj") ellenőrzése egy korábban észrevétlen hiányosságot tárt fel a kvíz-funkcióban.
6. **A független tesztelők olyan pontokon akadtak el, amelyeket a saját tesztelésem nem találhatott meg.** Mind a négy tesztelő eljutott egy kész prezentációig (kb. 10-20 perc), de a `.html` fájl mentése két tesztelőnél gondot okozott (az elsőnél a Mac-es TextEdit formázott szövegként mentett, a másodiknál a mentésben segítségre volt szükség), egy tesztelő pedig nem találta, hol kell Claude-fiókot létrehozni. Ez négy tesztelő, ezért csak jelzés, nem általánosítható eredmény.

## Fájlok

- Promptsablon: [`prompt_template.txt`](prompt_template.txt)
- Használati útmutató: [`hogyan-hasznald.md`](hogyan-hasznald.md)
- Teljes, verzióról verzióra bontott változásnapló: [`fejlesztesi-naplo.md`](fejlesztesi-naplo.md)
- A külső tesztelők által készített prezentációk: [`output/tesztelo1_porsche.html`](output/tesztelo1_porsche.html), [`output/tesztelo2_koponyak.html`](output/tesztelo2_koponyak.html), [`output/tesztelo3_hibajavito-kodok.html`](output/tesztelo3_hibajavito-kodok.html), [`output/tesztelo4_bergen.html`](output/tesztelo4_bergen.html)
- Minta-bemenetek témánként: [`templates/`](templates/)
- Legenerált, önállóan futtatható prezentációk: [`output/`](output/)
