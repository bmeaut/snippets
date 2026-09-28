---
layout: default
codename: GeminiNyelvtanulas
title: Orosz B2 nyelvvizsgára felkészülés MI-vel (Gemini, ChatGPT, Claude összehasonlítás)
tags: snippets mieset gemini chatgpt claude nyelvtanulas
authors: Barkóczi Alexandra
---

# MI esettanulmány – Orosz B2 nyelvvizsgára felkészülés MI-vel

## Cél

A cél nem egy klasszikus szoftverfejlesztési feladat volt, hanem egy fél éves, strukturált tanulási terv összeállítása egy orosz B2 szintű nyelvvizsgára való felkészüléshez. Mivel korábban nem volt tapasztalatom azzal, hogy egy LLM mennyire alkalmas hosszú távú, több hónapos terv megtervezésére és követésére, három különböző modellt (Google Gemini, ChatGPT, Claude) is bevontam, és összehasonlítottam, melyik ad használhatóbb tervet, illetve hogyan viselkednek, ha hetekkel később visszatérek ugyanahhoz a beszélgetéshez.

## Felhasznált eszközök

* Gemini alkalmazás (böngészőben)
* ChatGPT (Plus előfizetés, GPT-4o/GPT-5 modellek)
* Claude (böngészős alkalmazás)

## Tanulságok

* Mindhárom modell képes volt értelmes, heti bontású tanulási tervet adni (nyelvtani témák, szókincsbővítés, hallás utáni értés, íráskészség, beszédkészség ütemezve), amint megadtam a kiindulási szintemet (B1 közepe) és a célt (B2, adott vizsganappal).
* A Claude adta a legrészletesebb, hétről hétre lebontott tervet, konkrét óraszám-becsléssel és forrásjavaslatokkal, viszont ez a részletesség miatt hosszabb volt, mint amennyit ténylegesen át tudtam venni egyben.
* A ChatGPT inkább konkrét tananyagokat, tankönyveket és online forrásokat javasolt, kevésbé formális heti bontással, ami gyakorlati szempontból hasznosabbnak bizonyult a napi tanuláshoz.
* A Gemini kezdetben hasonlóan jó, strukturált tervet adott, viszont amikor **hetekkel később, ugyanabban a chat-ben** visszakérdeztem a tervre (hogy hol tartok, mi jön a következő héten), a modell már nem emlékezett pontosan az eredeti terv részleteire, és részben ellentmondó, az eredetitől eltérő ütemezést adott vissza – mintha nem lett volna hozzáférése a korábbi, saját maga által adott tervhez.
* Ebből az lett a legfontosabb tanulság, hogy egy több hónapos tervet nem szabad kizárólag a chat-előzményre bízni: a végleges tervet külön, saját dokumentumban (egy Markdown fájlban) kell rögzíteni, és a modellt csak az adott heti/napi konkrét feladatra érdemes rákérdezni, ne a teljes terv "emlékezetére" hagyatkozva.

## A munkafolyamat tanulságos részletei

### Azonos kiinduló prompt mindhárom modellnek

Hogy összehasonlítható eredményt kapjak, mindhárom modellnek szó szerint ugyanazt a kiinduló promptot adtam meg:

```
B1 közepén tartok oroszból, és kb. 6 hónapom van egy B2 szintű nyelvvizsgára felkészülni
(heti kb. 6-8 óra tanulási időm van). Készíts egy részletes, heti bontású tanulási tervet,
ami lefedi a nyelvtant, a szókincsbővítést, a hallás utáni értést, az írást és a beszédet,
és vegye figyelembe, hogy a vizsga mind a négy készséget méri.
```

A három válasz jellemzően eltérő volt:

* **Claude**: 26 hetes, minden egyes hétre lebontott terv, konkrét témákkal (pl. "5. hét: aspektuspárok múlt időben, 2 óra nyelvtan + 1 óra hallás utáni értés hír-anyagon"), órabecsléssel.
* **ChatGPT**: tömörebb, havi bontású terv, viszont konkrét tankönyvekre (pl. adott szintű orosz tankönyv fejezeteire) és online forrásokra (podcastok, hírportálok) hivatkozva.
* **Gemini**: havi célokra bontott terv, hasonlóan a ChatGPT-éhez, konkrét gyakorlási módszerekkel (árnyékolás, shadowing technika a kiejtéshez).

### A tervek kombinálása

Mivel egyik terv sem volt önmagában tökéletes, a Claude heti struktúráját vettem alapul, és ebbe illesztettem be a ChatGPT konkrét forrásjavaslatait:

```
A Claude-tól kapott heti bontású tervet szeretném megtartani, de a benne szereplő általános
"szókincsbővítés" és "hallás utáni értés" feladatokhoz szeretnék konkrét forrásokat rendelni,
hasonlóan ahhoz, ahogy te (ChatGPT) korábban tankönyveket és podcastokat javasoltál.
Írd át a heti tervet úgy, hogy minden egyes heti feladathoz konkrét forrást is rendelj.
```

Ez a kombinált terv lett végül az alap, amit egy külön Markdown fájlban rögzítettem, hogy ne a chat-előzményre kelljen hagyatkoznom a következő hónapokban.

### A Gemini "elfelejtette" a tervet

Körülbelül öt héttel az eredeti terv elkészítése után, ugyanabban a Gemini beszélgetésben visszatértem, hogy pontosítsam a következő heti feladatokat:

```
A korábban adott tervben tartunk most az 5. hétnél. Mi a következő két hét feladata a terv szerint?
```

A Gemini válasza részben ellentmondott az eredeti tervnek: más témákat sorolt fel az 5-6. hétre, mint amit korábban ugyanő adott, és a nyelvtani témák sorrendje is felcserélődött. Rákérdezve, hogy ez hogyan lehetséges:

```
Ez nem egyezik azzal, amit korábban a 3. és 4. hétre írtál. Emlékszel még pontosan az eredeti,
6 hónapos tervre, vagy újragenerálod menet közben?
```

A Gemini válasza szerint igyekezett a korábbi kontextusra támaszkodni, de elismerte, hogy egy ilyen hosszú, sok részletet tartalmazó terv esetén nem garantált, hogy minden korábbi részletet pontosan megőriz, és javasolta, hogy a tervet inkább külön dokumentumként küldjem vissza neki minden alkalommal, amikor a következő szakaszra kérdezek rá. Ez lényegében megerősítette, hogy a hosszú távú konzisztenciáért a felhasználónak kell felelősséget vállalnia, nem a modellnek.

### A dokumentált terv visszaadása kontextusként

Ezt követően a saját Markdown fájlban rögzített tervet mindig visszaillesztettem a promptba, amikor egy adott hétre kérdeztem rá:

```
Itt a teljes 6 hónapos tervem (mellékelve). Jelenleg a 6. hétnél tartok. Mi a pontos feladat
erre a hétre, és van-e olyan rész, amit érdemes lenne a haladásom alapján módosítani?
```

Ezzel a megközelítéssel mindhárom modell (Gemini, ChatGPT, Claude egyaránt) konzisztens, a dokumentált tervhez illeszkedő választ adott – a különbség csak abban volt, hogy a Gemini esetében ezt explicit módon, minden alkalommal meg kellett tennem, mert saját magától nem tartotta meg megbízhatóan a korábbi részleteket.

## Összefoglalás

A három modell összehasonlítása azt mutatta, hogy a kezdeti tervkészítésben mindegyik hasonlóan jól teljesített, a különbség inkább a részletezettségben és a forrásjavaslatok konkrétságában volt. A legfontosabb, hosszú távra szóló tanulság azonban a Gemini-vel szerzett tapasztalat volt: egy több hónapos tervre nem lehet úgy tekinteni, mintha a modell azt megbízhatóan "emlékezetben tartaná" a beszélgetés során, hetekkel később visszakérdezve előfordulhat, hogy a modell ellentmondó vagy újragenerált információt ad. Emiatt a végleges tervet mindig érdemes külön, saját dokumentumban rögzíteni, és minden egyes alkalommal ezt visszaadni a modellnek kontextusként, ahelyett hogy a chat-előzmény "emlékezetére" hagyatkoznánk.
