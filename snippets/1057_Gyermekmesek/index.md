---
layout: default
codename: Gyermekmesek
title: Személyre szabott gyermekmesék generálása közös felolvasáshoz
tags: snippets mieset
authors: Kövesdán Gábor
---

# Személyre szabott gyermekmesék generálása közös felolvasáshoz

Szülőként szerettem volna több időt tölteni a gyermekemmel közös meseolvasással, és vonzó alternatívát kínálni a képernyős szórakozás mellett. A túlzott képernyőhasználat káros lehet, különösen akkor, ha az alvás, a mozgás vagy a személyes kapcsolatok rovására megy. A megoldást számomra nem csupán az idő korlátozása jelentette, hanem az is, hogy legyen helyette olyan közös tevékenység, amely a gyermek aktuális érdeklődéséhez kapcsolódik.

Az elérhető mesekönyvek között nem mindig találtam elég, éppen megfelelő történetet. Ez saját választási nehézségem volt: nem a gyermekirodalom egészének szegénységét jelentette, hanem azt, hogy a kéznél lévő könyvek témája, szereplői és hossza nem mindig találkozott az aznapi igénnyel. A modern rajzfilmek szereplői vagy egy frissen felmerült érdeklődési téma gyorsabban változhattak, mint az otthoni mesekínálat.

Ezért ChatGPT-vel kezdtem adott témára meséket generáltatni. Fogtündér, Madagaszkár-szereplők, minyonok, varázslatos kristályok és dinoszauruszok is előkerültek. A módszer könnyen adott új szöveget, ugyanakkor azt tapasztaltam, hogy a történetek tanulsága gyakran hasonló irányba futott ki. Az eset fő kérdése így a változatosság lett: hogyan kérjek valóban más történetet, ne csak új szereplőket ugyanahhoz a tanulsághoz?

**Használt eszköz:** ChatGPT, több különálló, magyar nyelvű beszélgetésben. A visszakeresett példák 2024 decemberétől 2025 májusáig terjednek.

## Tanulságok

- **Az aktuális érdeklődés jó kiindulópont.** A gyermek számára ismerős szereplők és kedvelt témák köré gyorsan lehet új, felolvasható történetet kérni.
- **A mese célja a közös élmény.** Az MI a szöveg előkészítését segíti; a felolvasást, a kérdéseket és a gyermek reakcióira adott választ a szülő adja hozzá.
- **A témaváltás önmagában nem biztosít változatosságot.** Egy minyonos és egy dinoszauruszos mese is ugyanarra az együttműködési vagy barátságtanulságra épülhet.
- **A tiltás mellett pozitív irányt is érdemes adni.** A „ne legyen benne kincs” hasznos pontosítás volt, de még jobb kapaszkodó lehet, ha azt is megmondom, milyen konfliktus kerüljön a helyére.
- **A tanulságot cselekvésként is meg lehet határozni.** A „legyen a türelemről” kérés helyett megadható, hogy a hős várjon, figyeljen meg valamit, majd új információ alapján döntsön.
- **Nem minden mesének kell kimondott erkölcsi tanulsággal zárulnia.** Egy humoros félreértés, egy érdekes felfedezés vagy egy megnyugtató hétköznapi történet is értékes közös olvasmány lehet.

## Az eredmény használata

A generált szöveget felolvasás előtt átnézem: megfelelő-e a hangulata, érthető-e a cselekmény, és nem ismétli-e az előző mesék megoldását. A gyermeknek nem kell a képernyőt néznie: a mesét kinyomtathatom, vagy én olvashatom fel az eszközről.

Az alábbi promptminták utólag kidolgozott javaslatok. Nem állítom, hogy a korábbi munkamenetekben már kipróbáltam őket. A céljuk, hogy az egyetlen témamegadás helyett a történet felépítését is irányítsák.

### Egy használható alapminta

```text
Írj felolvasásra szánt mesét egy körülbelül 8 éves gyermeknek.
Téma: dinoszauruszok, egy kíváncsi velociraptorral és egy spinosaurusszal.
Hossz: körülbelül 8–10 perc felolvasás, rövid bekezdésekkel és párbeszédekkel.

Ezúttal az legyen a központi felismerés, hogy első benyomás alapján
tévedhetünk, és új információ birtokában szabad megváltoztatni a véleményünket.
A hős tegyen egy téves feltételezést, próbálja ki, majd a tapasztalata alapján
javítsa ki. A megoldás ebből következzen.

Ne legyen kincs, gonosztevő vagy világmegmentés. A fő megoldás ne az legyen,
hogy mindenki összefog, és ne a barátság fontosságáról szóljon a befejezés.
Legyen humoros és izgalmas, de ne legyen ijesztő.
Ne írj külön tanulságot: a felismerés a szereplők döntéseiből derüljön ki.
A végére adj két nyitott beszélgetési kérdést, egyetlen helyes válasz nélkül.
```

## A munkafolyamat tanulságos részletei

### A rövid promptok gyorsan adtak felolvasható alapanyagot

2024. december 27-én ezt kértem:

> Kérek egy 8 perces mesét a fogtündérről.

A kérés egyszerre nevezte meg a témát és a rendelkezésre álló időt. Nem tartalmazott részletes cselekményt, így annak kialakítása a modellre maradt. Az időtartam praktikus szülői szempont volt, bár a tényleges felolvasási idő a tempótól és a közben kialakuló beszélgetéstől is függ.

2025. január 4-én Madagaszkár-szereplőkkel kértem mesét, január 13-án pedig kristályos és minyonos történeteket. Az egyik visszakeresett prompt:

> Kérek egy mesét varázslatos kristályokról

A kapott „A Kristályok Birodalma” történetben egy kristálytündér egy ellopott kristálydarab visszaszerzésére indult. A visszakeresett összefoglaló több általános pozitív üzenetet is felsorol: bátorság, remény, szeretet és béke. Ez jól mutatja, milyen sok tartalmi döntést hoz meg a modell, ha a prompt csak egy témát ad meg.

### Egy ismétlődő motívumot kifejezetten kizártam

A minyonos történeteknél újabb, izgalmas mesét kértem, majd pontosítottam:

> Kérek még egyet de ne legyen benne kincs

Az ezt követő történet a visszakeresett előzmény szerint légballon kereséséről szólt. A konkrét kizárás tehát változtatott a cselekmény tárgyán. Ebből ugyanakkor nem következik, hogy a történet mélyebb szerkezete vagy tanulsága is teljesen megváltozott: egy elveszett tárgy felkutatása könnyen ugyanazt a kalandos keresési mintát követheti, mint egy kincskeresés.

Utólag ezért a „ne legyen kincs” mellé ilyen pozitív irányt is adnék: „A konfliktus egy félreértett üzenetből adódjon; ne keresés, hanem a félreértés felismerése oldja meg.” Így nemcsak egy elemet veszek ki, hanem másféle történetmenetet kérek.

### A dinoszauruszos meséknél már a tanulságot is meghatároztam

A 2025. május 21-i munkamenetben először a türelem és a mások iránti szolidaritás témájára kértem dinoszauruszos mesét. Ezt egy T-Rexszel játszódó, nagyvonalúságról szóló kérés követte, majd velociraptor és spinosaurus szerepelt egy újabb tanulságos történet igényében. Ezek a visszakeresés tartalmi összefoglalásai, nem szó szerinti promptidézetek.

Az első történet „Dini, a kis türelmetlen dínó” címmel a várakozásról és mások érzéseinek figyelembevételéről szólt. Az előzményekben a barátság és az együttműködés motívuma is megjelenik. Saját tapasztalatom szerint a tanulságok túl gyakran hasonlóak lettek; a visszakeresett részletek ezt az ismétlődési kockázatot szemléltetik, de nem bizonyítják, hogy minden generált mese egyforma volt.

A tanulság megadása tehát már előrelépés volt, de az olyan tág fogalmak, mint a „szolidaritás” vagy a „nagyvonalúság”, könnyen ugyanarra a segítünk egymásnak típusú lezárásra vezethetnek. A további változatossághoz a döntési helyzetet és a megoldás módját is érdemes váltogatni.

### Változatosságot több külön szempont mentén lehet kérni

| Változtatott szempont | Konkrét promptutasítás |
| --- | --- |
| Felismerés | A hős tanulja meg bevallani, hogy valamit még nem tud. |
| Konfliktus | Két jó, de egyszerre nem teljesíthető terv közül kell választani. |
| Megoldási mód | A hős megfigyeléssel és próbálkozással jusson előre, ne varázseszközzel. |
| Érzelmi téma | Mutasd meg, hogyan lehet csalódottnak lenni anélkül, hogy minden elromlana. |
| Szerkezet | Ne utazás vagy keresés legyen: a történet egyetlen műhelyben játszódjon. |
| Befejezés | Ne minden sikerüljön; egy apró kudarc mellett is legyen megnyugtató a lezárás. |
| Tanulság nélküli változat | Írj játékos, humoros történetet; ne rendezd erkölcsi leckévé. |

Egy másik használható módszer, ha először több rövid tervet kérek:

```text
Még ne írd meg a mesét. Adj öt történetötletet minyonos témában.
Mindegyikhez írj egy mondatot a konfliktusról és egyet a megoldásról.
Az öt ötlet eltérő felismerésre épüljön: kíváncsiság, hibák javítása,
határok tisztelete, veszteség elfogadása, illetve egy tanulság nélküli komédia.
Ne legyen kincskeresés. A megoldások ne mind összefogásra épüljenek.
Várd meg, melyiket választom.
```

Így rövid vázlatokon ellenőrizhetem a változatosságot, és csak utána kérem a teljes szöveget. A gyermek is választhat a számára érthetően bemutatott ötletek közül.

Az ismétlődés csökkentéséhez az előző mesék rövid naplója is használható: téma, fő konfliktus, megoldás és tanulság egy-egy sorban. Ezt a következő promptba bemásolva kérhetem, hogy a modell ne ismételje a legutóbbi három megoldást. Ez pontosabb támpont, mint a puszta „legyen most más”.

### Az eredmény értéke és a még nem mért hatás

A korábbi munkamenetek azt mutatják, hogy rövid kérésekből többféle témájú meseszöveget tudtam előállítani, és az új kérésekkel alakíthattam a kínálatot. Nem áll rendelkezésre mérés arról, hogy ez mennyivel csökkentette a képernyőidőt vagy hogyan hatott a gyermek fejlődésére; ezek nem az eset igazolt eredményei.

A kézzelfogható eredmény a felolvasáshoz rendelkezésre álló, érdeklődéshez igazítható szöveg volt. A továbblépést az jelenti, hogy a kedvelt témák megtartása mellett tudatosabban választom meg a konfliktust, a szereplő döntését és a lezárás hangulatát.

A fenti új promptminták módszertani javaslatok, nem a korábbi beszélgetések rekonstruált részletei.
