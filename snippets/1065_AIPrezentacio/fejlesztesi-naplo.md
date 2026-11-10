# Fejlesztési napló

Ez a dokumentum követi, hogyan fejlődött a promptsablon és a vele generált prezentáció verzióról verzióra — mit adtunk hozzá, miért, és mi indokolta a változtatást. Minden bejegyzés a hozzá tartozó `output/ppt1_kerti-komposztalas_vN.html` fájlra hivatkozik, hogy a "előtte/utána" ténylegesen összehasonlítható legyen, nem csak leírás.

## v1 — az első működő verzió

**Fájl:** [`output/ppt1_kerti-komposztalas_v1.html`](output/ppt1_kerti-komposztalas_v1.html)

**Mi készült el:** a promptsablon első, legegyszerűbb változata. Cím-dia, majd 5 tartalmi dia egyszerű felsorolásokkal, alap Reveal.js "white" téma, "slide" átmenet. Semmi díszítés, semmi ikon, semmi egyedi vizuál.

**Cél ebben a lépésben:** annak igazolása, hogy a promptsablon egyáltalán helyes, önállóan futtatható (`file://`-kompatibilis, build-lánc nélküli) HTML-t termel, és hogy a CDN-linkek valóban élnek. Ez volt a technikai alapkövetelmény — enélkül semmi értelme a vizuális finomításnak.

**Hiányosság, ami miatt a v2 szükséges volt:** funkcionálisan hibátlan, de vizuálisan semmiben nem különbözik egy alap PowerPoint-sablontól — nincs benne semmi, ami "profi" érzetet keltene. Ezt a felhasználó explicit hiányolta.

## v2 — vizuális gazdagítás, külső képfüggőség nélkül

**Fájl:** [`output/ppt1_kerti-komposztalas_v2.html`](output/ppt1_kerti-komposztalas_v2.html) (jelenleg ez a `output/ppt1_kerti-komposztalas.html`, azaz az aktuális állapot is)

**Mi változott a v1-hez képest:**
- Inline SVG ikon a cím- és záródián (levél-motívum, hajtás-motívum).
- Zöld pipa-ikon minden "mit szabad" listaelem előtt, piros X-ikon minden "mit tilos" listaelem előtt — a puszta szöveges felsorolás helyett vizuálisan is megkülönbözteti a két kategóriát.
- Körforgás-ikon "A folyamat" dián.
- Visszafogott zöld színátmenetes (CSS gradient) háttér a cím- és záródián, a monoton fehér helyett.
- A promptsablonba bekerült egy előírás, hogy számszerű/táblázatos adatnál Chart.js-es diagramot is rajzoljon a puszta táblázat helyett (ebben a konkrét tesztben nem volt numerikus adat, tehát ez a szabály itt nem aktiválódott, de a promptban rögzítve van a következő, adatos szintekhez).

**Miért ezt és miért nem fényképet:** a látványosság kézenfekvő módja lett volna külső fényképek beillesztése, de ezt tudatosan elvetettük. Egy külső kép-URL törhet, eltűnhet, vagy lassíthatja/blokkolhatja a betöltést — ez pont az ellen dolgozna, amit a projekt ígér ("mindig, megbízhatóan működjön, technikai tudás nélkül"). Az inline SVG ugyanazt a vizuális hatást adja, de garantáltan betölt, mert a HTML fájl része, nem külső hivatkozás. Ha valakinek tényleg saját fotó kell, a promptsablon előírja, hogy az AI adjon neki egy rövid, kézzel követhető utasítást, hogyan illessze be utólag — ez egy dokumentált, vállalt korlát, nem elhallgatott hiányosság.

**Eredmény:** ugyanaz a tartalom, ugyanaz a szerkezet, de érzékelhetően "profibb" megjelenés, extra CDN-függőség hozzáadása nélkül (az SVG-k a HTML részei, nem külön betöltött fájlok).

## v3 — interaktivitás, adatvezérelt diagram, kép, LaTeX

**Fájl:** [`output/ppt2_napelem.html`](output/ppt2_napelem.html), bemenet: [`templates/level3_input.md`](templates/level3_input.md)

**Mi váltotta ki:** külső visszajelzés Csorba Kristóftól — jelezte, hogy már fut egy másik próbálkozás is a témában, és hogy a miénk akkor lenne egyértelműen jobb, ha lenne benne "interakció vagy valami programozottabb dolog, pl. egy adatsor betöltése interaktív diagramba". Ehhez jött még saját igény: kép és LaTeX-képlet támogatása is.

**Mi változott a v2-höz képest:**
- A táblázatos/számszerű adatra vonatkozó előírás (6. pont) megerősödött: már nem "opcionális statikus diagram", hanem **kötelező, valóban interaktív Chart.js-diagram** — egérrel rámutatásra tooltip, több adatsornál kattintható jelmagyarázat a sorok ki-/bekapcsolásához. A tesztben ezt egy napelem-megtérülés 5 éves adatsorán mutattam be (oszlop + halmozott vonal, két adatsor, kattintható legend).
- **Saját kép beillesztése** immár dokumentált, kétutas támogatással: (a) relatív fájlútvonal, ha a felhasználónak külön képfájlja van, (b) base64-beágyazás, ha a képet a beszélgetésbe bemásolta/feltöltötte — ez utóbbi esetben a végeredmény továbbra is egyetlen, önmagában hordozható HTML fájl marad. A tesztben egy technikai demó-képet ágyaztam be base64-ként (valódi, dekódolható PNG), jelezve a diában, hogy ez csak a mechanizmus bemutatása, nem a felhasználó tényleges fotója — erre a korlátra explicit rámutattam, nem hallgattam el.
- **LaTeX-képlet renderelés** KaTeX-szel (CDN + auto-render): a megtérülési idő képlete ($T = \text{Beruházás} / \text{Éves megtakarítás}$) most szépen szedett matematikai formulaként jelenik meg, nem nyers szövegként.

**Technikai megjegyzés:** a Chart.js jelmagyarázat kattintható ki-/bekapcsolása alapból is működik, külön bekapcsolás nélkül — az első verzióban feleslegesen felülírtam ezt egy `onClick` beállítással, amit aztán, mivel semmi hozzáadott értéke nem volt, kivettem.

**Eredmény:** a prezentáció most már nem csak vizuálisan gazdagabb (v2), hanem funkcionálisan is: a néző ténylegesen tud vele interaktálni (adatpont lekérdezés, adatsor ki/be), nem csak néz egy állóképet.

## v4 — elrendezési hibák javítása (a strukturális ellenőrzés nem elég)

**Fájlok:** hibás állapot [`output/ppt2_napelem_v3.html`](output/ppt2_napelem_v3.html), javított állapot [`output/ppt2_napelem_v4.html`](output/ppt2_napelem_v4.html) (= jelenlegi `output/ppt2_napelem.html`)

**Mi váltotta ki:** a v3-at csak strukturálisan ellenőriztem (tag-egyensúly, CDN-linkek élnek-e) — böngészőben ténylegesen nem néztem meg, mert nincs hozzá eszközöm. Amikor a felhasználó tényleg megnyitotta, három valós, csak vizuálisan észlelhető hiba derült ki:

1. **A képlet túl nagy volt, kilógott a képernyőről.** Oka: a `.formula` CSS osztályra sosem került tényleges méret-szabály, így a KaTeX a Reveal.js alapból nagy (kb. 40px-es) betűméretét örökölte, egy beágyazott törttel (`\dfrac`) megszorozva.
2. **A táblázat és a diagram összecsúszott, a dia alja nem látszott.** Oka: a diagram-konténernek nem volt magasság-korlátja, a Chart.js pedig alapból a szélesség/2 arányban nő — ez a táblázattal egymás alá halmozva magasabb lett, mint amennyi elfér egy dián. A Reveal.js nem görget automatikusan, ami nem fér ki, az egyszerűen levágódik.
3. **Hiányzott az egymás melletti (két oszlopos) elrendezés lehetősége** — minden elem egymás alá volt téve, semmi nem futott vízszintesen egymás mellett, pedig ez segített volna elkerülni az 1-2. pontot is.

**Ez fontos módszertani tanulság, nem csak egy bugfix:** a saját ellenőrzésem (HTML tag-egyensúly, CDN-elérhetőség) *strukturálisan* helyes, de *vizuálisan* hibás kimenetet engedett át. A validáció maga volt hiányos, nem csak a generált kód — az automatizált vagy saját kiértékelés maga is hibaforrás lehet, nem csak a tesztelt kód, itt a "kiértékelés" az én saját, böngésző nélküli tesztelésem volt.

**A javítás:**
- A `.formula`-nak explicit, kicsi betűméretet adtam (0.5em), és `\dfrac` helyett `\frac`-ot használtam (kompaktabb).
- A diagram-konténer explicit magasságot kapott (320px) és a Chart.js beállításban `maintainAspectRatio: false`-t, hogy ezt tényleg tartsa is.
- Bevezettem egy `.two-col` flexbox-osztályt, és a diagram+táblázat, illetve a kép+magyarázószöveg párokat egymás mellé (nem egymás alá) rendeztem.
- A promptsablonba és a `hogyan-hasznald.md`-be bekerült egy új, általános szabály (11. pont): a tartalom soha ne lógjon ki a diából, több elemnél mindig két oszlopos elrendezést kell használni, minden vizuális elemnek explicit méretkorlátot kell adni, és inkább több diára kell bontani a tartalmat, mint zsúfolni.

**Amit ez a jövőre nézve jelent:** amíg nincs valós böngészős/emberi tesztelés, a strukturális ellenőrzésem (amit eddig végeztem) *szükséges, de nem elégséges* — ezt a naplóban és majd az `index.md` módszertani buktató szakaszában is így kell feltüntetni, nem szabad úgy tenni, mintha a korábbi "ellenőrizve, minden rendben" üzenetek a vizuális minőségre is vonatkoztak volna.

## v5 — általános prezentáció-design szabályok

**Fájl:** [`output/ppt2_napelem_v5.html`](output/ppt2_napelem_v5.html) (= jelenlegi `output/ppt2_napelem.html`)

**Mi váltotta ki:** a felhasználó kérése, hogy a promptsablon vegye figyelembe az általános, bármilyen prezentációra érvényes design-alapelveket is (betűméret, szövegmennyiség, kontraszt), ne csak a Reveal.js-specifikus technikai követelményeket.

**Mi került be a promptba (4. pont, új):**
- **"6x6-szabály"**: diánként max. kb. 6 gondolat, soronként max. kb. 6-8 szó, rövid kifejezések teljes mondatok helyett.
- **Kontraszt-szabály**: erős szöveg/háttér kontraszt mindenhol, háttér-gradiens csak nagyon halványan, hogy ne rontsa az olvashatóságot.
- **Betűméret alsó korlát**: fő szöveg min. 0.6em, kísérő szöveg min. 0.5em — és explicit kimondva, hogy ha a tartalom emiatt nem férne ki, **a tartalmat kell szétosztani több diára, nem a betűméretet tovább csökkenteni**.
- **Egységes, korlátozott színpaletta**: 1 fő kiemelő szín következetesen a fejléceken, ikonokon és a diagramon.

**Miért fontos ez pont most:** a v4-es javítás (overflow-hiba) technikailag megoldotta a kilógást, de az egyik útja épp a betűméret csökkentése volt (0.45em-ig), ami a probléma tüneti kezelése, nem a valódi oka. Ha ez szabály nélkül marad, a jövőbeli generálások ugyanezt a mintát követhetik: minél sűrűbb a tartalom, annál kisebb a betű, ami idővel olvashatatlan diákhoz vezetne. Az új szabály explicit sorrendet ad: előbb a *tartalom* mennyiségét kell csökkenteni (több diára bontással), és csak másodsorban, egy rögzített alsó korlátig szabad a betűméretet csökkenteni.

**Javítás a meglévő teszten:** a `ppt2_napelem.html`-ben egy 0.45em-es feliratot 0.5em-re emeltem, hogy megfeleljen az új alsó korlátnak (ez volt az egyetlen szabálysértő elem a meglévő teszteken).

## Téma-lefedettségi próbák

Ezek a bejegyzések nem verziólépések (a promptsablon nem változik miattuk), hanem azt igazolják, hogy a **változatlan, v5 állapotú** `prompt_template.txt` egymástól tartalmilag távoli témákon is jól teljesít-e (l. `plan_ai_presentation_tool.md` "Téma-lefedettségi próbák" szakasza). Nem szakma szerint kategorizálunk — a téma önmagában hordozza, kinek szólna.

### Az évszakok

**Fájlok:** bemenet [`templates/evszakok_input.md`](templates/evszakok_input.md), kimenet [`output/ppt3_evszakok.html`](output/ppt3_evszakok.html)

**Mit tesztelt:** gyerekeknek szóló, játékos, kevés szöveg + sok vizuál típusú tartalmat — ez a legtávolabbi eddigi teszt a "napelem/adat" jellegű tartalomtól.

**Eredmény:** a v5 promptsablon módosítás nélkül jól kezelte: 6 dia, egyenként max. 3 rövid pont (jóval a 6x6-szabály alatt), évszakonként egyedi témájú SVG-ikon (nap, virág, falevél, hópehely), egységes fejléc-szín (`#146356`) mindvégig, egyik dián sincs a betűméret-alsó korláton (0.6em) kívüli szöveg. Diagramra/KaTeX-re nem volt szükség (nincs számadat/képlet a tartalomban) — a sablon helyesen nem erőltette be ezeket, a feltételes előírás ("ha van adat/képlet a tartalomban") jól működött üres esetben is.

**Egy tervezési döntés, amit érdemes rögzíteni:** az évszak-ikonok szándékosan kaptak egyedi, évszakhoz illő színt (rózsaszín tavasz, sárga nyár, narancs ősz, kék tél), miközben a fejlécek és a szerkezeti elemek egységesen egy fő színt (`#146356`) használnak. Ez nem ütközik a "korlátozott, egységes színpaletta" szabállyal — a szabály célja a *versengő, véletlenszerű* színhasználat elkerülése, nem a tartalmilag indokolt, jelentéshordozó színkódolás tiltása (itt az évszak-színek maguk is segítik a megértést egy 7-9 éves gyereknek).

**Talált hiányosság:** nincs — ez volt a cél, hogy módosítás nélkül is jól működjön.

## v6 — interaktív/programozott elemek, első lépés: Reveal.js fragments

**Fájlok:** fragmentek előtt [`output/ppt3_evszakok_v1.html`](output/ppt3_evszakok_v1.html), utána [`output/ppt3_evszakok.html`](output/ppt3_evszakok.html)

**Mi váltotta ki:** a felhasználó explicit kérése, hogy az interaktív/programozott elemek egy önálló, minden témán átívelő design-réteg legyenek (l. `plan_ai_presentation_tool.md` "Interaktív/programozott elemek" szakasza), nem egy különálló, egyszeri teszteset.

**Mi került be a promptba (új 6. pont):** a felsorolt pontok Reveal.js "fragment" osztállyal (`class="fragment"`) egyesével, kattintásra/nyílra jelennek meg, nem mind egyszerre. Ez natív Reveal.js-funkció, nulla extra CDN-függőség — a legkisebb kockázatú tétel a korábban felsorolt interaktív ötletek közül, ezért ez lett az első, amit ténylegesen bevezettünk.

**Validálás:** a meglévő "Az évszakok" teszten alkalmaztam (12 listaelem, mind a 4 évszak-dián) — a tag-egyensúly-ellenőrzés után is hibátlan maradt. A régi állapotot [`evszakok_v1.html`](output/ppt3_evszakok_v1.html) néven archiváltam, hogy a "előtte/utána" itt is összehasonlítható legyen.

## v7 — élő, csúszkával vezérelt diagram

**Fájlok:** csúszka előtt [`output/ppt2_napelem_v6.html`](output/ppt2_napelem_v6.html) (ez maga is már csak archívum, tartalmilag = v5), csúszkával [`output/ppt2_napelem.html`](output/ppt2_napelem.html)

**Mi került be a promptba (7. pont bővítve):** ha az adatban van egy ésszerűen módosítható feltételezés/paraméter, egy `<input type="range">` csúszkát kell mellé tenni, ami mozgatásra újraszámolja és élőben újrarajzolja a diagramot (`chart.update()`), az aktuális értéket is számmal mutatva.

**Validálás a napelem-teszten:** a csúszka az éves megtakarítás növekedési ütemét (0-10%, alapból 5.5%) vezérli. Mozgatásra a JS mértani sorral újraszámolja mind az 5 év adatait, frissíti a Chart.js diagram mindkét adatsorát (`savingsChart.data.datasets[...].data = ...; savingsChart.update()`), és kiírja az 5 éves összeget. A statikus táblázatot szándékosan meghagytam "eredeti becslés" felirattal — nem a táblázatot teszi élővé, hanem egy külön, explicit jelölt "mi lenne, ha" felfedezést ad mellé, hogy ne keveredjen az eredeti, rögzített adat a szimulált verzióval. A HTML tag-egyensúlyt és a beágyazott JS szintaxisát is külön leellenőriztem (Node.js-sel parse-oltattam a script tartalmát) — mindkettő hibátlan.

**Tervezési döntés:** a csúszka alapértéke (5.5%) úgy lett megválasztva, hogy induláskor közel essen az eredeti táblázat első évéhez (480 000 Ft, pontos egyezés), így a felhasználó first impression-je konzisztens, mielőtt elkezdene kísérletezni.

## v8 — animált számláló

**Fájlok:** előtte [`output/ppt2_napelem_v7.html`](output/ppt2_napelem_v7.html), utána [`output/ppt2_napelem.html`](output/ppt2_napelem.html)

**Mi került be a promptba (új 7. pont):** ha a tartalomban van egy kiemelt, figyelemfelkeltő szám, animálja fel 0-ról a valós értékig, amikor a dia megjelenik, kb. 1-1.5 másodperc alatt — explicit figyelmeztetéssel, hogy csak akkor, ha tényleg van ilyen kiemelendő szám, ne animáljon mindent.

**Validálás a napelem-teszten:** az "Összegzés" záródiára tettem egy nagy, animált számot (0-tól 2 680 000 Ft-ig, az 5 éves összesített megtakarítás), a Reveal.js `slidechanged` eseményére indítva, `requestAnimationFrame`-mel, kb. 1.2 másodperc alatt. Figyeltem arra is, hogy ne csak első betöltéskor induljon el, hanem akkor is, ha a felhasználó közvetlenül erre a diára navigál vissza — ezért `Reveal.getCurrentSlide()`-dal induláskor is ellenőrzöm, nem csak a `slidechanged` eseményre hagyatkozom. HTML tag-egyensúly és JS-szintaxis (Node.js-es ellenőrzéssel) is hibátlan.

## v9 — interaktív kvíz/szavazás dia

**Fájlok:** kvíz előtt [`output/ppt3_evszakok_v2.html`](output/ppt3_evszakok_v2.html), kvízzel [`output/ppt3_evszakok.html`](output/ppt3_evszakok.html)

**Mi került be a promptba (új 8. pont):** oktató/ismeretterjesztő tartalomnál egy interaktív kvíz-dia — kérdés + 3-4 kattintható válasz, azonnali vizuális visszajelzéssel, és a helyes válasz mindig kijelölve, akkor is, ha a felhasználó rosszat választott. Explicit megkötve, hogy csak akkor, ha a tartalomból tényleg levezethető egyértelmű kérdés-válasz.

**Validálás az évszakok-teszten:** egy kvíz-dia ("Melyik évszakban hullanak a falevelek?", 4 gomb: Tavasz/Nyár/Ősz/Tél, helyes: Ősz) került a záródia elé. Kattintásra a script minden gombot letilt (`disabled = true`), a helyes gombot zölddel jelöli, a kattintott (ha rossz volt) pirossal, és szöveges visszajelzést ad. A gombok betűmérete (0.65em) a design-szabályok (4. pont) betűméret-alsó korlátján belül van. HTML tag-egyensúly és a beágyazott JS (immár két `<script>` blokkból) szintaxisa is hibátlan.

**Ezzel a négy interaktív/programozott elem mindegyike bekerült a promptba** (fragments, animált számláló, élő csúszkás diagram, kvíz) — mindegyiket önálló témán, egyesével validálva, mindegyiknél megvan az előtte/utána fájlpár.

## v10 — függőleges mikro-túlcsordulás javítása, téves első diagnózis

**Fájlok:** hiba előtt [`output/ppt2_napelem_v8.html`](output/ppt2_napelem_v8.html), javítva [`output/ppt2_napelem.html`](output/ppt2_napelem.html)

**Mi történt:** a felhasználó jelezte, hogy a képlet-dia minimálisan (1-2 mm) görgethető. Az első diagnózisom hibás volt: azt feltételeztem, hogy a hosszú, egysoros KaTeX-formula szélessége lóg ki, és a formulát többsoros (`\begin{aligned}`) elrendezésre akartam átalakítani. A felhasználó ezt elutasította és pontosított: nem vízszintes, hanem **függőleges (Y-tengely)** irányú, minimális túlcsordulásról van szó, és a formulának egysorosnak kell maradnia.

**A valódi ok:** a dián egymás után négy blokkelem van (egy `<h2>` és három `<p>`), mindegyik a böngésző alapértelmezett margóját használta (kb. 1em fent-lent elemenként, semmi explicit felülírás). Ezek összeadva néhány pixellel túlnyúltak a dia magasságán — elég ahhoz, hogy egy alig észrevehető görgetősávot indokoljanak, de nem eleget ahhoz, hogy vizuálisan feltűnő legyen.

**A javítás:** a formula maradt egysoros; a `h2`/`p` elemek explicit, szűkebb margót kaptak (`margin: 0.3em 0`, illetve a `h2`-nél `margin-bottom: 0.3em`). A korábbi, téves irányú "biztonsági háló" (`overflow-x: auto` a `.formula`-n, a v4-es javításból) is törölve lett, mert az a rossz tengelyt kezelte, és amúgy is elrejtette volna a problémát ahelyett, hogy megoldaná.

**Promptba bekerült (14. pont pontosítva):** a "sosem lóghat ki, sosem görgethető" szabály most explicit tiltja az `overflow: auto/scroll` megoldásként való használatát, és felhívja a figyelmet arra, hogy sűrű, több szöveges elemet tartalmazó diánál a böngésző alapértelmezett bekezdés-margói önmagukban is elég túlcsordulást okozhatnak — ezért explicit margót kell adni, nem a böngésző alapértelmezésére hagyatkozni. Emellett pontosítottam egy korábbi, most cáfolt állítást is: nem igaz, hogy a Reveal.js minden túlcsorduló tartalmat automatikusan, csendben levág — bizonyos esetekben (mint ez is) inkább egy minimális görgetősávot ad hozzá, ami ugyanúgy nem elfogadható.

**Módszertani tanulság:** ez a harmadik eset ebben a projektben (a v4-es overflow-hiba és a v9 előtti saját tesztelési korlátaim után), hogy egy első benyomás alapú diagnózis tévesnek bizonyult, és csak a felhasználó pontosítása után derült ki a valódi ok. Érdemes ezt is bevenni az `index.md` módszertani buktató-szakaszába: nemcsak a kód, a *saját hibadiagnózisom* is tévedhet, és a pontos hibaleírás (melyik tengely, mekkora mértékben) kulcsfontosságú volt a helyes javításhoz.

## v11 — kontraszt-szám és "ne csak színnel" szabály, külső kutatás alapján

**Fájlok:** kvíz előtt (csak színes jelzés) [`output/ppt3_evszakok_v3.html`](output/ppt3_evszakok_v3.html), utána (szín + ✓/✗ szimbólum) [`output/ppt3_evszakok.html`](output/ppt3_evszakok.html)

**Mi váltotta ki:** a felhasználó kérésére internetes kutatást végeztem általános prezentáció-design ajánlásokról (Design Shack, Forbes) és akadálymentességi irányelvekről (WebAIM, Section508.gov, UCR Student Disability Resource Center).

**Két konkrét hiányosságot talált a kutatás a saját, addig meglévő szabályainkban:**

1. **A "kontraszt" eddig szám nélküli, minőségi elvárás volt.** A WCAG szabvány konkrét, ellenőrizhető számot ad: normál szövegnél min. 4.5:1, nagy szövegnél min. 3:1 kontrasztarány. Ez bekerült a 4. pontba.
2. **A kvíz-funkció (v9) kizárólag színnel jelezte a helyes/helytelen választ** — ez a saját, ekkor még hiányos szabályunk következménye volt, és pont az akadálymentességi alapelvet sértette ("ne bízd a jelentést kizárólag színre", mert színtévesztőknek nem elég).

**Javítás a meglévő kvíz-teszten:** a válaszgombok és a visszajelző szöveg is kapott ✓/✗ szimbólumot a szín mellé, nem helyette. Emellett bekerült egy általánosabb elv is: ne minden dia legyen azonos felépítésű (cím + felsorolás), a tartalomtól függően váltogatni kell az elrendezést, a téma/szín/betűtípus egységessége mellett.

**Módszertani megjegyzés:** ez az első eset, hogy nem a saját teszteléssel vagy felhasználói visszajelzéssel találtunk hibát, hanem külső, publikált szakirodalommal ellenőriztük a már meglévő szabályokat — és ez talált is egy valódi, korábban észre nem vett akadálymentességi rést a saját munkánkban.

## v12 — előadói jegyzet nézet (Reveal.js Notes plugin)

**Fájlok:** előtte [`output/ppt2_napelem_v10.html`](output/ppt2_napelem_v10.html), utána [`output/ppt2_napelem.html`](output/ppt2_napelem.html)

**Mi került be a promptba (új 15. pont):** minden tartalmi dia kapjon rövid előadói jegyzetet (`<aside class="notes">`), ami csak az előadói nézetben (S billentyű) látszik, a közönségnek nem. Ehhez a Reveal.js hivatalos Notes pluginja kell CDN-ről, regisztrálva a `plugins` listában.

**Validálás a napelem-teszten:** mind az 5 dia kapott egy-egy, a diához illő előadói jegyzetet (pl. a csúszkás diánál: "mutasd meg élőben, hogy egy optimistább feltételezés mennyire változtat az eredményen"). A plugin CDN-linkjét külön leellenőriztem (200 OK, a script valóban `RevealNotes` globális nevet exportál). HTML tag-egyensúly (5 aside nyitás/zárás) és JS-szintaxis is hibátlan.

**Ez natív Reveal.js-funkció volt, akárcsak a fragments (v6)** — ezért volt a legkockázatmentesebb választás a bővített menüből.

## v13 — automatikus léptetés (autoSlide), új téma: felügyelet nélküli kijelző

**Fájlok:** [`templates/varoterem_input.md`](templates/varoterem_input.md), [`output/ppt4_varoterem.html`](output/ppt4_varoterem.html)

**Mi került be a promptba (új 6. pont):** `autoSlide`/`loop` csak akkor, ha a tartalomból egyértelmű, hogy felügyelet nélküli, ismétlődő megjelenítésre szánták (pl. váróterem-/recepciós kijelző). Élő, előadó által tartott bemutatóknál **soha nem** szabad automatikus léptetést tenni, mert az elveszi az előadó irányítását.

**Miért új témát igényelt, nem a meglévőket:** ez az első olyan tulajdonság, ami *feltételesen ellentétes* a többivel — egy élő bemutatónál kifejezetten hiba lenne. A meglévő tesztek (napelem-pitch, évszakok-óra) mind élő, előadó által tartott forgatókönyvek, ott az autoSlide helytelen lenne. Ezért egy explicit, felügyelet nélküli kontextusú témát írtam: egy fodrászat váróterem-kijelzője, a bemenetben direkt kimondva ("felügyelet nélkül, folyamatosan ismételve megy"), hogy a feltétel egyértelműen aktiválódjon.

**Validálás:** 5 diás kijelző (nyitvatartás, szolgáltatások, akció, elérhetőség), `autoSlide: 7000, loop: true` beállítással. HTML tag-egyensúly hibátlan.

**Talált finomítási pont a 16. (előadói jegyzet) szabályban:** ennél a témánál nincs élő előadó, tehát az előadói jegyzet funkciónak (v12) nincs értelme — nem is tettem be. A jelenlegi promptszöveg ezt még nem mondja ki explicit feltételként, csak úgy, mint az összes többi diát. Ez egy apró, még javítandó inkonzisztencia a szabályok között — a következő körben érdemes a 16. pontot is feltételhez kötni ("csak élő, előadó által tartott bemutatóknál").

## v14 — a 16. pont javítása, plusz QR-kód

**Első rész: a v13-ban talált inkonzisztencia javítása.** A 16. pont (előadói jegyzet) most már explicit feltételhez kötött: csak élő, előadó által tartott bemutatónál kerüljön bele, felügyelet nélküli kijelzőnél ne. Ez mindkét fájlban (`prompt_template.txt`, `hogyan-hasznald.md`) javítva.

**Második rész: QR-kód (új 17. pont).** Ha a tartalomban van weboldal-cím vagy elérhetőség, kerüljön mellé QR-kód — a `qrcode-generator` CDN-könyvtárral (`createSvgTag()`), nem külső QR-generáló API-val (az törhet vagy nyomon követhet).

**Fájlok:** QR nélkül [`output/ppt4_varoterem_v1.html`](output/ppt4_varoterem_v1.html), QR-ral [`output/ppt4_varoterem.html`](output/ppt4_varoterem.html)

**Validálás, két szinten:**
1. Szerkezeti: HTML tag-egyensúly hibátlan, CDN-link él (200 OK).
2. **Tényleges futtatás Node.js-szel**, nem csak szintaxis-ellenőrzés: letöltöttem a `qrcode-generator` fájlt, és ténylegesen lefuttattam ugyanazt a kódot, amit a HTML tartalmaz (`qrcode(0, 'M')`, `addData('https://zsofifodraszat.hu')`, `make()`, `createSvgTag(4)`) — a kimenet egy valódi, 8447 karakteres, jól formázott SVG (`<svg version="1.1" ...>`). Ez erősebb validálás, mint az eddigi "csak szintaxis helyes" ellenőrzés, mert azt igazolja, hogy a kód ténylegesen lefut és helyes kimenetet ad, nem csak hogy nincs benne elgépelés.

**Egy technikai részlet, amit érdemes rögzíteni:** a könyvtár UMD-csomagolása CommonJS-ben (`require()`) csak akkor ad vissza használható értéket, ha elmentjük a `require()` visszatérési értékét — pusztán `require(...)`-t hívni és utána a `qrcode` globálisra hivatkozni Node-ban NEM működik (ezt én magam is elsőre elrontottam a teszt közben). Böngészőben, sima `<script src="...">` taggel viszont működik közvetlenül, mert ott a fájl tetején lévő `var qrcode = ...` a klasszikus (nem modul) szkript-környezetben automatikusan globálissá válik. A HTML-ben használt kód ezt a böngészős útvonalat használja, tehát helyes — de tanulságos volt, hogy a Node-os tesztelési módszer önmagában megtéveszthet, ha nem a tényleges futtatási környezetet (böngésző, plain script) szimulálja pontosan.

## v15 — fülek/accordion összehasonlításhoz, új téma

**Fájlok:** [`templates/csomagok_input.md`](templates/csomagok_input.md), [`output/ppt5_csomagok.html`](output/ppt5_csomagok.html)

**Mi került be a promptba (új 18. pont):** ha a tartalomban 2-4, egymással összehasonlítható opció/csomag/forgatókönyv van, jelenítse meg füles elrendezésben egyetlen dián (kattintható fül-fejlécek, alattuk a kiválasztott opció), sima vanília JS-sel, semmilyen CDN-függőség nélkül.

**Miért új témát igényelt:** a meglévő tesztek egyikében sincs 2-4, valóban egymással párhuzamosan összehasonlítandó opció — ez saját, dedikált tartalmi mintát igényelt. Egy internetszolgáltató 3 előfizetési csomagját (Alap/Optimum/Prémium) írtam meg erre.

**Validálás:** a fülekre kattintva JS cseréli az aktív fület (`.active` osztály) és a hozzá tartozó panelt (`display: none`/`block`). HTML tag-egyensúly és JS-szintaxis hibátlan. Ez a teszt a v12-es előadói jegyzet funkciót is megkapta (élő, előadó által tartott bemutató), ezzel is igazolva, hogy a funkciók egymással kombinálhatók, nem csak külön-külön működnek.

## v16 — vizuális visszaszámláló, új téma

**Fájlok:** [`templates/workshop_input.md`](templates/workshop_input.md), [`output/ppt6_workshop.html`](output/ppt6_workshop.html)

**Mi került be a promptba (új 19. pont):** workshop-/gyakorlat-jellegű tartalomnál, ha van benne időkorlátos feladat, kerüljön a diára egy vizuális visszaszámláló, `setInterval`-lal, de explicit start/szünet/újraindítás gombokkal — ne induljon el magától, az előadó irányítsa.

**Validálás:** egy tréner csapatépítő gyakorlata (5 perces megbeszélés) kapott egy saját visszaszámláló-diát, MM:SS formátumban, start/szünet/reset gombokkal. A `setInterval`-alapú visszaszámláló-logikát nem csak szintaxis szerint, hanem **ténylegesen lefuttattam Node-ban** (a formázó függvényt kezdő-, közbenső-, 1 percen túli és nulla értékekre is), minden eset helyesen formázódott (pl. "61 mp" → "01:01"). HTML tag-egyensúly és JS-szintaxis is hibátlan.

**Ezzel 9 interaktív/programozott elem bekerült a promptba**: 4 az eredeti listából (fragments, csúszkás diagram, animált számláló, kvíz), plusz 5 az újabb menüből (előadói jegyzet, autoSlide, QR-kód, fülek, visszaszámláló). Innentől a további téma-lefedettségi próbák ezzel a teljes, 20 pontos promptsablonnal készülnek.

## v17 — gépelés-effekt, a bővített menü lezárása

**Fájlok:** előtte [`output/ppt5_csomagok_v1.html`](output/ppt5_csomagok_v1.html), utána [`output/ppt5_csomagok.html`](output/ppt5_csomagok.html)

**Mi került be a promptba (új 20. pont):** diánként legfeljebb egyszer, egy rövid (max. 8-10 szavas), kiemelt mondatnál/címnél gépelés-effektus (karakterenkénti megjelenés), explicit korlátozva, hogy hosszú szövegen vagy több helyen egy dián ne alkalmazza.

**Validálás:** a csomagok-teszt záródiája ("Válaszd ki, ami neked megfelel") kapta meg, `Reveal.on('slidechanged', ...)`-re indítva, ugyanazzal a mintával, mint a v8-as animált számláló (csak egyszer indul, akkor is működik, ha közvetlenül erre a diára navigálnak). A karakterenkénti felépülés logikáját **ténylegesen lefuttattam Node-ban** (nem csak szintaxis-ellenőrzés): 30 lépés, az utolsó lépés pontosan egyezik a teljes szöveggel.

**Ezzel lezárult a bővített interaktív/programozott elem menü**: 9 elem, mindegyik egyesével beépítve a promptba, egy-egy odaillő témán validálva (strukturálisan ÉS, ahol értelme volt, ténylegesen lefuttatva Node-dal), előtte/utána fájlpárral dokumentálva, naplózva. A `prompt_template.txt` és `hogyan-hasznald.md` most 21 pontos, mindkét fájl szinkronban.

## Összefoglaló példa: az összes elem egyetlen prezentációban

**Fájlok:** [`templates/ai_workshop_input.md`](templates/ai_workshop_input.md), [`output/ppt7_ai-workshop.html`](output/ppt7_ai-workshop.html)

**Mi ez, és mi nem:** ez nem egy újabb, önálló promptmódosítást validáló verziólépés — a promptsablon nem változott miatta —, hanem egy **összefoglaló bemutató**, ami megmutatja, hogyan néz ki egy olyan valós tartalom, ami elég gazdag ahhoz, hogy a promptsablon legtöbb feltételes szabálya egyszerre aktiválódjon, egyetlen koherens prezentációban.

**8 dia, 8 különböző elemmel:**
1. Cím (gradiens háttér, SVG ikon)
2. Fragments (3 pont egyesével felfedve)
3. Interaktív kvíz (✓/✗ jelzéssel, nem csak színnel)
4. Fülek (3 csomag összehasonlítása)
5. Csúszkás, élő diagram (csapat-hatékonyság módosítja az időmegtakarítás-görbét)
6. Animált számláló (120 résztvevő)
7. Visszaszámláló (3 perces élő gyakorlat, start/szünet/reset gombokkal)
8. Gépelés-effekt (záró mondat) + QR-kód (jelentkezési oldal)

Minden dia előadói jegyzetet is kapott (élő, előadó által tartott bemutató).

**Amit tudatosan kihagytam:** az `autoSlide`-ot (6. pont) — az fogalmilag kizárja a többit, mert felügyelet nélküli kijelzőre való, nem élő, interaktív előadásra. Ez is egy hasznos igazolás: a szabályok helyesen zárják ki egymást ott, ahol tartalmilag ellentmondanának.

**Validálás, a megszokottnál is alaposabban, mert ez az összegző, "mindent összerak" teszt:**
- HTML tag-egyensúly: 8 dia, 8 aside, 4 SVG, 10 gomb, mind pontosan párosítva.
- Mind az 5 CDN-erőforrás (Reveal.js core, theme, Notes plugin, Chart.js, qrcode-generator) élőnek ellenőrizve.
- **Ténylegesen lefuttattam Node-ban** mindhárom számítási logikát, amit ez a teszt újrafelhasznált, de új paraméterekkel hívott: a csapat-hatékonyság szorzó helyes átskálázást ad (70% → arányosan kevesebb, 130% → arányosan több óra), a 3 perces visszaszámláló helyesen formázódik, az új záró mondat karakterenkénti felépülése helyes.
- Önellenőrzés: az összes a fájlban használt betűméret (0.55-0.75em) megfelel a 4. pontban rögzített alsó korlátoknak.

Ez a fájl jó referenciapont lesz, ha valaki egy tömören látni akarja, mire képes a teljes promptsablon egyben — nem helyettesíti az egyenkénti, célzott teszteket, de összegzi őket.

## v18 — három hiba az összefoglaló példából: cím-tördelés, ikon-zsugorodás, láthatatlan QR

**Mi váltotta ki:** a felhasználó ténylegesen megnyitotta az összefoglaló `ppt7_ai-workshop.html`-t, és három valós, csak vizuálisan észlelhető hibát talált — a strukturális ellenőrzésem (tag-egyensúly, CDN, JS-szintaxis) egyiket sem tudta volna elkapni, mert mindhárom vizuális/CSS-elrendezési probléma.

**1. hiba: a cím csúnyán tördelt.** A "Kisvállalkozóknak" szó "KISVÁLLALKOZÓKNA" + "K" (magányos betű a sor végén) formában tört. Ok: a Reveal.js saját CSS-e (`dist/reveal.css`) `word-break: break-word`-öt állít be a fejlécekre, ami hosszú szót is kötőjel nélkül, tetszőleges helyen tördel; ezt a "white" téma nagybetűssé alakítása (`text-transform: uppercase`) tovább szélesíti. Ezt korábban nem ellenőriztem le, mert a korábbi teszttémák címei rövidebbek/kevésbé összetettek voltak.

**2. hiba: az első felsorolás-pont ikonja kisebbre zsugorodott, mint a többi.** A "Miért fontos ez?" dián a leghosszabb szövegű pont ikonja volt a legkisebb. Ok: `flex-shrink: 0` hiányzott az SVG-kről a `.reveal li` flex-konténerben — enélkül a leghosszabb szövegű sor "nyomta össze" az ikont, hogy kiférjen a hely. **Ez valójában egy regresszió volt**: a `ppt1_kerti-komposztalas.html` és `ppt3_evszakok.html` tesztekben ez a szabály már korábban be volt építve, de az `ppt7_ai-workshop.html` (és a `ppt4_varoterem.html`, `ppt6_workshop.html`) megírásakor kimaradt — nem vittem át következetesen egy már egyszer megtalált, helyes mintát.

**3. hiba (visszajelzés, nem konkrét bug): a QR-kódok általánosságban nem elég láthatók.** A korábbi QR-kódok (110-130px, keret/háttér nélkül) könnyen elveszhetnek a dián, főleg mivel a Reveal.js a teljes prezentációt kicsinyítheti a néző képernyőjéhez.

**Javítások:**
- Fejlécekre `overflow-wrap: normal; word-break: normal; hyphens: auto;` CSS, plusz a konkrét hosszú címnél explicit kisebb betűméret (nem csak a hyphenation-re hagyatkozva).
- `.reveal li svg { flex-shrink: 0; }` — pótolva mindhárom fájlban, ahol hiányzott (`ppt7_ai-workshop.html`, `ppt4_varoterem.html`, `ppt6_workshop.html`), miután **teljes körű auditot** futtattam az összes eddigi output-fájlon, hogy hol hiányzik még ez a szabály.
- QR-kódok: 170px-re növelve, kontrasztos szegélyes-hátterű dobozba téve (`ppt7_ai-workshop.html` és `ppt4_varoterem.html`).

**Mindhárom javítás bekerült a promptba (4. pont bővítve, 17. pont bővítve)**, hogy a jövőbeli generálások eleve elkerüljék ezt a három hibát.

**Módszertani tanulság:** a 2. hiba explicit megmutatja, hogy egy már egyszer megtalált és kijavított hibát **nem elég egyszer kijavítani egy fájlban** — ha a szabály még nincs a promptban rögzítve, a következő, kézzel írt teszt-fájl könnyen újra elköveti ugyanazt. Ez pontosan az oka annak, hogy minden talált hibát a promptba is vissza kell írni, nem elég csak az adott teszt-fájlt javítani.

## v19 — 12 új interaktív elem egyszerre, két új demóval

**Mi váltotta ki:** a felhasználó egy második brainstorm-kört is kért, és utána mindet jóváhagyta egyszerre ("mehetnek mind"), azzal a kéréssel, hogy mindegyikhez legyen látható példa is.

**A promptba bekerült 12 új pont (21-32.):** személyre szabható beviteli mezős kalkulátor, sorsoló/randomizáló, kattintható checklist, drag-and-drop párosítás, előtte/utána kép-csúszka, kereshető/szűrhető lista, konfetti-effektus, saját videó beágyazása, nagyítható kép (lightbox), interaktív idővonal, kifejezés-magyarázó tooltip (glossary), rajzolható mini-vászon. A promptsablon így 33 pontos.

**Két új demó, mert 12 elemet egyetlen témába zsúfolni önmagában ellentmondana a 4. pont "ne legyen minden dia egyforma, ne erőltess bele mindent" szellemének:**

### Demo A — [`templates/faq_input.md`](templates/faq_input.md) / [`output/ppt8_faq.html`](output/ppt8_faq.html)
Téma: belső AI-tudásbázis egy irodának. 4 elem: kattintható checklist ("mielőtt elkezded", élő X/N számlálóval), glossary-tooltip (3 szakkifejezés, hover-re felugró magyarázat), lightbox (kattintható SVG-folyamatábra, nagyítva jelenik meg sötétített háttér előtt), kereső/szűrő (8 elemes GYIK-lista, gépelés közben élőben szűrve).

### Demo B — [`templates/csapatesemeny_input.md`](templates/csapatesemeny_input.md) / [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html)
Téma: céges csapatépítő nap napirendje. 8 elem: interaktív idővonal (4 évszám, kattintásra részlet), sorsoló (5 névből "pörgős" animációval választ), drag-and-drop párosítás (3 név — 3 érdekesség, helyes/helytelen vizuális jelzéssel), személyre szabható kalkulátor (beírt létszám → pizzaszám), előtte/utána kép-csúszka (két demó-kép, húzható határvonallal), videó (relatív útvonalas hivatkozás, dokumentált korláttal, hogy a tényleges fájlt mellé kell másolni), rajzolható vászon (SVG helyszínrajz fölött szabadkézi jelölés, törlés gombbal), konfetti (a záródiára érve indul).

**Miért nincs base64-be ágyazott videó-demó**: a kép-beágyazásnál (base64 PNG) sikerült ténylegesen valós, dekódolható demó-fájlt generálnom kódból. Egy valós, lejátszható videofájl (MP4/WebM) programozott előállítása ennél lényegesen bonyolultabb (nincs `ffmpeg` vagy hasonló eszköz elérhető), ezért itt a relatív fájlútvonalas mintát mutattam be dokumentált korláttal, ahelyett hogy egy hibás/hamis fájlt próbáltam volna beágyazni — ez ugyanaz az "ismert korlát explicit vállalása" elv, mint amit a korábbi demó-képnél is követtem.

**Validálás mindkét fájlon:**
- HTML tag-egyensúly és JS-szintaxis hibátlan mindkettőben.
- Minden `id` egyedi (nincs ütközés, pl. a FAQ-nál a lightbox két SVG-jének külön `arrow`/`arrow2` marker-azonosítója van).
- **Ténylegesen lefuttatott Node-tesztek**: kereső/szűrő logika (4 különböző lekérdezésre helyes találati listát ad), pizza-kalkulátor kerekítés (35 fő → 12 pizza, határesetek: 3 fő → 1, 4 fő → 2), idővonal-adatlekérdezés, drag-and-drop egyezés-logika, konfetti-részecske generálás (80 darab, méret- és szín-tartomány ellenőrizve), a két demó-kép PNG-fejléce és mérete.
- Önellenőrzés: minden betűméret (0.5-0.75em) megfelel a 4. pontban rögzített alsó korlátoknak.

## v20 — a glossary-tooltip kilóg a képernyő széléről

**Mi váltotta ki:** a felhasználó a `ppt8_faq.html`-t kipróbálva jelezte, hogy hover-re az egyik tooltip kilóg.

**Hiba:** a "Néhány fogalom" dián a `prompt` kifejezés a bekezdés legelején, a bal széléhez közel áll. A `.tooltip` középre igazítva (`left: 50%; transform: translateX(-50%)`), fix 220px széles — ha a hozzá tartozó szó a szöveg bal szélén van, a buborék bal fele kilógott a látható területről. A másik két kifejezés (`LLM`, `token`) beljebb van, ott a hiba nem jelentkezett, ezért maradhatott észrevétlen a korábbi strukturális ellenőrzések (tag-egyensúly, JS-szintaxis) mellett — ez is vizuális/elrendezési hiba, amit csak tényleges kipróbálással lehet észrevenni.

**Javítás:** [`output/ppt8_faq_v1.html`](output/ppt8_faq_v1.html) → [`output/ppt8_faq.html`](output/ppt8_faq.html). A script végére JS került, ami `mouseenter`/`focus`-kor `getBoundingClientRect()`-tel megméri a tooltip tényleges pozícióját, és ha a bal vagy jobb szélen túllógna, a `transform`-ot ennyivel visszatolja a látható tartományba (10px margóval).

**Validálás:** HTML tag-egyensúly és JS-szintaxis hibátlan. A pozícionáló logikát külön, Node-ban is lefuttattam három szintetikus esetre (bal széli túllógás, középen álló elem — nincs elmozdulás, jobb széli túllógás) — mindhárom a várt irányba és mértékben tolta el a buborékot.

**Bekerült a promptba (31. pont bővítve mindkét fájlban)**, hogy a jövőbeli glossary-tooltipek eleve tartalmazzák ezt a széllenállási logikát, függetlenül attól, hogy a kifejezés hol áll a szövegben.

## v21 — az előtte/utána kép-csúszka valódi fotókat kapott

**Fájlok:** előtte [`output/ppt9_csapatesemeny_v1.html`](output/ppt9_csapatesemeny_v1.html), utána [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html).

**Mi váltotta ki:** a v19-ben dokumentált, tudatosan vállalt korlát volt, hogy az "Iroda felújítás" dia két képe technikai demó-kép (egyszínű téglalap), nem valós fénykép. Ez javításra került: a placeholder képek helyett most valódi, NASA Earth Observatory forrású fotók vannak beágyazva (Aral-tó, 2000 és 2018 — [forrás](https://science.nasa.gov/earth/earth-observatory/world-of-change/aral-sea/), közkincs, amerikai kormányzati munka, szerzői jogi korlátozás nélkül).

**Miért pont ezek a képek:** a felhasználó két konkrét, National Geographic-forrású URL-t adott meg. Mivel azok szerkesztőségi, jogvédett fotók, egy közkincs-forrású, tartalmilag egyenértékű (ugyanaz az Aral-tó előtte/utána jelenet) alternatívát javasoltam és kapott jóváhagyást — ez elkerüli, hogy jogvédett anyag kerüljön be egy publikus repóba.

**Technikai lépések:** a képeket letöltöttem, 400×400px-re és ésszerű fájlméretre (~45-48 KB) tömörítettem (`sips`), az eredeti fájlokat megőriztem forrásként [`image/ppt9_aral_2000.jpg`](image/ppt9_aral_2000.jpg) és [`image/ppt9_aral_2018.jpg`](image/ppt9_aral_2018.jpg) néven, majd base64-be ágyazva lecseréltem velük a placeholder PNG-ket a demóban, hogy az egyetlen-fájlos elv (l. 1-2. pont) ne sérüljön.

**Validálás:** a beágyazott base64 adatot Python-nal visszafejtve mindkét kép valódi, ép JPEG-nek bizonyult (helyes fejléc-bájtok, a fájlméret pontosan egyezik a forrás fájlokéval). HTML tag-egyensúly és a beágyazott JS szintaxisa is hibátlan maradt (a script tartalma nem változott, csak a kép-adat).

**Az `index.md`-ben** ez az elem most élő iframe-ként szerepel a többi 21 elemhez hasonlóan (korábban egy külön, statikus kép-illusztráció volt emellett, de ez redundáns lett, miután a tényleges demó is valódi fotókat kapott).

## v22 — a csúszka helyett a bal oldali kép "mozgott" — megoldatlan maradt

**Mi váltotta ki:** a felhasználó a `ppt9_csapatesemeny.html`-t közvetlenül megnyitva jelezte, hogy a csúszka húzásakor a bal oldali (előtte) kép mozog, tehát a funkció használhatatlan.

**Első hipotézis (téves vagy legalábbis nem elégséges):** feltételeztem, hogy a böngésző natív "kép kihúzása" gesztusa (a beépített, félig átlátszó szellemképes drag) ütközik a csúszka húzásával, mert a két `<img>` elem sosem kapott `draggable="false"`-t vagy `pointer-events: none`-t. Hozzáadtam ezeket (`.ba-wrap img` CSS-hez `-webkit-user-drag: none; user-drag: none; -webkit-user-select: none; user-select: none; pointer-events: none;`, mindkét `<img>`-hez `draggable="false"`), a HTML tag-egyensúly és a JS-szintaxis a javítás után is hibátlan maradt.

**A felhasználó visszajelzése szerint ez a javítás nem oldotta meg a problémát** — a jelenség a fix után is fennállt. Mivel nincs böngésző-eszközöm, amivel magam meg tudnám nézni a tényleges viselkedést, nem tudtam tovább, célzottan diagnosztizálni a valódi okot; több hipotézis (natív kép-drag, Reveal.js gesztuskezelés, a két kép eltérő keretezése) is felmerült, egyiket sem sikerült sem megerősíteni, sem cáfolni élő böngészős teszt nélkül.

**Ez nyitva maradt, dokumentált hibaként.** Nem minden talált probléma oldódik meg elsőre, és ezt a naplónak (és az `index.md` Korlátok szakaszának) ugyanolyan őszintén kell tükröznie, mint a sikeres javításokat — l. `index.md`, Módszertani buktató 5.

## v23 — a konfetti-demó rossz diát mutatott alapból

**Fájlok:** előtte [`output/ppt9_csapatesemeny_v2.html`](output/ppt9_csapatesemeny_v2.html), utána [`output/ppt9_csapatesemeny.html`](output/ppt9_csapatesemeny.html).

**Mi váltotta ki:** a konfetti-effekt (27. pont) élő beágyazása az `index.md`-ben szándékosan az utolsó előtti dián indult, nem a záródián, mert a konfetti csak tényleges `slidechanged` eseményre indult el, egy `#/8`-as (záródiára mutató) közvetlen betöltésre nem — ez a Reveal.js dokumentált viselkedése, a `slidechanged` nem tüzel a kezdő dia hash-alapú betöltésekor. A felhasználó jelezte, hogy ez zavaró: a "Konfetti-effekt" címke alatt egy vele tartalmilag semmi közös nem lévő dia (a rajzolható-vászon demó) jelent meg alapból, konfetti nélkül, amíg a néző nem lépett tovább egy nyíllal.

**Javítás:** a `ppt2_napelem.html`-ben (v8, animált számláló) és a `ppt5_csomagok.html`-ben (v17, gépelés-effekt) már korábban bevált mintát alkalmaztam itt is: a `Reveal.on('slidechanged', ...)` figyelő mellett a script induláskor (`Reveal.initialize(...).then(...)`) is ellenőrzi, hogy a kezdő dia a záródia-e (`Reveal.getCurrentSlide().querySelector('#closingText')`), és ha igen, azonnal elindítja a konfettit. Ezzel a `#/8`-as (tényleges záródia) hash közvetlen betöltése is helyesen kiváltja az effektet.

**Validálás:** HTML tag-egyensúly és a beágyazott JS szintaxisa hibátlan maradt a javítás után.

**Az `index.md`-ben** az iframe és az újraindító gomb célja `#/7`-ről `#/8`-ra változott (a tényleges záródiára), a leírás pedig frissült: a demó betöltésekor most már azonnal, arrow-lépés nélkül elindul a konfetti.

**Módszertani tanulság:** ugyanaz a minta, mint a Módszertani buktató 3-ban — egy már egyszer megoldott probléma (induláskor is ellenőrizni, nem csak a `slidechanged` eseményre hagyatkozni) újra felmerült egy másik fájlban, mert nem volt általános szabályként rögzítve, csak esetenként alkalmazva.

## v24 — a válasz néha letölthető fájlként érkezik, nem kódrészletként

**Mi váltotta ki:** a felhasználó egy tényleges claude.ai-beszélgetésben kipróbálta a promptsablont, és screenshotot küldött: a válasz nem a `hogyan-hasznald.md`-ben leírt szürke kódrészlet-dobozban jött, hanem egy letölthető fájlkártyaként ("Almafa prezentacio", "Code · HTML", "Download" gombbal). A `hogyan-hasznald.md` és a `prompt_template.txt` "Mentés" szakasza csak a kódrészletes esetet írta le (kimásolás, beillesztés egy szövegszerkesztőbe, mentés `.html` kiterjesztéssel) — a letölthető fájlkártya esetére semmilyen instrukció nem volt.

**Javítás:** mindkét fájlban ágazó instrukció került a mentési lépésbe: ha letölthető fájlkártyaként jelenik meg a válasz, elég a "Download" gombra kattintani (a fájl már `.html` kiterjesztéssel érkezik); ha kódrészletként, marad a korábbi kimásolás-beillesztés-mentés folyamat.

**Módszertani tanulság:** a claude.ai felhasználói felülete a válasz formáját (kódrészlet vagy letölthető fájl) nem a promptsablon tartalma alapján dönti el, hanem a chat-kliens saját, a promptsablontól független viselkedése — ezt sem strukturális, sem funkcionális, sem a saját vizuális ellenőrzésem (ami a generált HTML-re irányult, nem a claude.ai chat-felületére) nem tudta volna felfedni, csak egy tényleges felhasználói kipróbálás.

## v25 — a promptsablon duplikációjának megszüntetése a hogyan-hasznald.md-ből

**Mi váltotta ki:** a `hogyan-hasznald.md` a 2. lépéstől kezdve szó szerint tartalmazta a teljes, 33 pontos promptot (ugyanazt, mint a `prompt_template.txt`), csak enyhén eltérő formázással (bold-kiemelések nélkül). Minden promptváltozásnál mindkét fájlt egyszerre kellett frissíteni — ez a duplikáció fölösleges volt, és a szinkron-fenntartás önmagában is hibaforrás lehetett volna.

**Javítás:** a `hogyan-hasznald.md` lépései átalakultak úgy, hogy ne írják le újra a promptot, hanem a `prompt_template.txt`-re hivatkozzanak: (1) nyisd meg a `prompt_template.txt`-t, (2) írd a saját tartalmadat a fájl végén jelölt helyre, (3) jelöld ki és másold ki a teljes fájlt, (4) illeszd be a claude.ai-be. A további lépések (válasz fogadása, mentés, megnyitás) változatlanok, csak a lépésszámozás nőtt 6-ról 7-re.

**Validálás:** a lépések belső hivatkozásait (pl. "folytasd a 7. lépéssel") átnéztem és javítottam, hogy a új számozással is helyesek maradjanak.

**Módszertani tanulság:** ugyanaz a minta, mint a `prompt_template.txt` korábbi (`.md` → `.txt`) átalakításánál — ha egy tartalom két helyen létezik, és az egyik hely mindig a másikat tükrözi, a duplikációt érdemes megszüntetni hivatkozással, nem a szinkronban tartással.
