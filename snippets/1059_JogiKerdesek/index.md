---
layout: default
codename: JogiKerdesek
title: Jogi segítségkérés és hibás MI hivatkozások ellenőrzése
tags: snippets mieset
authors: Kövesdán Gábor
---


# Jogi segítségkérés és hibás MI hivatkozások ellenőrzése

Több munkamenetben kértem ChatGPT-től segítséget jogi kérdések megértéséhez, az érveim rendezéséhez és jogszabályi hivatkozások kereséséhez. A kérdések között szerepelt ideiglenes intézkedés elleni jogorvoslat, hangfelvételek bizonyítékként történő felhasználása, a bírói mérlegelés jogszabályi kerete és a közigazgatási perben alkalmazható bizonyítás.

A válaszok rendezett, magabiztos megfogalmazása mellett hibás hivatkozásokkal is találkoztam. Saját visszaemlékezésem szerint külön kérnem kellett, hogy a modell a hatályos jogszabály szövegét használja. Az utólag visszakeresett példák között valóban van hatályon kívül helyezett törvényre történő hivatkozás, de más típusú hiba is előfordul: rossz paragrafushoz társított állítás és jogszabályidézetként előadott, téves mondat.

Az eset fő tanulsága ezért nem pusztán az, hogy frissebb információt kell kérni. A hivatkozás létezését, időbeli alkalmazhatóságát és az abból levont következtetést külön-külön kell ellenőrizni.

**Használt eszköz:** ChatGPT, magyar nyelvű, több különálló munkamenetben. A bemutatott hibákat 2026. szeptember 26-án, a Nemzeti Jogszabálytár elérhető szövegeivel összevetve ellenőriztem.

## Tanulságok

- **A paragrafusszám nem bizonyítja a válasz helyességét.** Egy konkrét törvényszám és bekezdés erős hitelességérzetet kelthet akkor is, ha az adott helyen más áll.
- **Valóban előfordult elavult jogszabályra hivatkozás.** Egy 2025-ös válaszban az MI olyan törvényt nevezett meg, amelyet 2012-ben hatályon kívül helyeztek.
- **Nem minden tévedés magyarázható elavult tudással.** A fellebbezhetőségre adott hibás választ nem támasztotta alá a vizsgált korábbi Pp.-szöveg sem.
- **Az idézetet szó szerint is ellenőrizni kell.** A modell által idézőjelbe tett mondat nem feltétlenül található meg a jogszabályban.
- **A hatályos szöveg kérése szükséges lehet, de önmagában nem elég.** Megnyitott hivatalos forrást, azonosított hatályállapotot és az állítást ténylegesen alátámasztó rendelkezést kell kérni.
- **Régebbi ügyben az alkalmazandó időállapotot is tisztázni kell.** Nem minden esetben a mai szöveg az irányadó; az ügy időpontja és az átmeneti szabályok is számíthatnak.
- **A javításnak a következtetésekre is ki kell terjednie.** Ha egy jogszabályhely hibás, nem elég a számát átírni: az arra épített érvelést is újra kell vizsgálni.

## Az eredmény használata

Az esettanulmány három konkrét hibát mutat be, és egy ellenőrizhetőbb kérdezési módszert javasol. A példák a korábbi MI-válaszok értékelésére szolgálnak; nem valamely folyamatban lévő ügy teljes jogi elemzései.

Egy új jogi kérdésnél ezt a promptmintát használnám:

```text
Magyar jog alapján vizsgáld meg az alábbi kérdést: [kérdés].
Az ügy releváns időpontja: [dátum]. Az eljárás típusa és szakasza: [adatok].

Először azonosítsd, melyik jogszabály melyik időállapota alkalmazandó.
Ha ehhez hiányzik adat, kérdezz rá. A mai és az ügyben alkalmazandó
szöveget ne keverd össze.

A jogszabályt hivatalos forrásban, lehetőleg a Nemzeti Jogszabálytárban
nyisd meg. Minden döntő állításhoz add meg a pontos jogszabályhelyet,
a releváns rövid szövegrészletet, a forrás linkjét és az ellenőrzött
hatályállapotot. Az idézetet és a saját értelmezésedet válaszd külön.

Ne a korábban megfogalmazott álláspontomat próbáld igazolni:
mutasd meg az ellene szóló rendelkezéseket és a kivételeket is.
Ha valamit nem tudsz ellenőrizni, ezt jelezd, és ne állíts elő
idézetet vagy paragrafusszámot emlékezetből.
```

Ez utólag összeállított minta, nem egy korábbi üzenetem szó szerinti másolata. A kapott linkeket és idézeteket ezt követően saját magam is megnyitnám és ellenőrizném.

## A munkafolyamat tanulságos részletei

### Az MI-t konkrét jogi kérdések tisztázására használtam

A munkamenetek jellemzően gyakorlati kérdésből indultak: van-e jogorvoslat, milyen feltételekkel használható egy bizonyíték, vagy hol található egy érvet alátámasztó jogszabályi rendelkezés. A rövid kérdésre a modell gyakran azonnal szerkesztett, hivatkozásokkal ellátott választ adott.

Ez a munkamód gyorsan áttekinthetővé tette a témát, ugyanakkor könnyen eltakarta a forrásellenőrzés hiányát. A következő példákban a válasz nem egyszerűen óvatos vagy hiányos volt: konkrétan rossz jogszabályi támaszt adott.

### Téves válasz az ideiglenes intézkedés fellebbezhetőségére

2025. május 15-én ezt kérdeztem:

> Fellebezhető-e az ideiglenes gyermekelhelyezésről szóló végzés?

A visszakeresett válasz szerint a végzés „általában nem fellebbezhető”. A modell ezt a Pp. 104. § (6) bekezdésének tulajdonított következő mondattal próbálta alátámasztani:

> Az ideiglenes intézkedés ellen – ha törvény kivételt nem tesz – fellebbezésnek nincs helye.

**Ez a korábbi MI-válasz hibás idézete, nem a törvény szövege.** A válasz a végrehajthatóságot a fellebbezés hiányával és az azonnali jogerővel is összekapcsolta.

Az ellenőrzött Pp. 105. § (1) külön fellebbezést enged az ideiglenes intézkedés iránti kérelemről hozott végzés ellen; a (2) bekezdés az előzetes végrehajthatóságról rendelkezik. A kettő tehát külön fogalom. Ugyanez a szabály szerepel az NJT megnyitott 2019-es időállapotában is. A tévedést ezért nem indokolt egyszerűen egy közelmúltbeli változás számlájára írni. [Pp., jelenlegi elérhető szöveg](https://njt.jog.gov.hu/jogszabaly/2016-130-00-00), [2019-es időállapot](https://njt.jog.gov.hu/jogszabaly/2016-130-00-00.5).

Ez a példa különösen erős: a modell a kérdés érdemi megválaszolásakor tévedett, és ehhez jogszabályidézetnek látszó megerősítést adott. Az ellenőrzési pont itt az, hogy a megjelölt hely valóban tartalmazza-e az idézetet, majd hogy a jogorvoslat és a végrehajthatóság szabályait külön kezeli-e az elemzés.

### Hatályon kívül helyezett törvényre hivatkozás a bírói mérlegelésnél

2025. október 27-én forrásokat kértem ahhoz, hogy a bíróság mérlegelésének jogszabályi keretei vannak:

> Kérek forrásokat arra, hogy a bíróság csak a jogszabályokban meghatározott jogok mentén hozhat döntéseket, csak a jogszabályi keretek közt van mérlegelési lehetősége.

A ChatGPT az **1997. évi LXVI. törvény 2. § (2) bekezdését és 3. §-át** idézte. Ezek valóban szerepeltek a megnevezett törvényben. A gond a hivatkozás időbeli érvényességével volt: az NJT szerkesztői megjegyzése szerint ezt a törvényt a 2011. évi CLXI. törvény 207. §-a 2012. január 1-jével hatályon kívül helyezte. A 2025-ös kérdésre adott válaszban a régi törvény történeti jellegének és alkalmazhatóságának tisztázása elmaradt. [Régi törvény és hatályon kívül helyezési megjegyzés](https://njt.jog.gov.hu/jogszabaly/1997-66-00-00).

Ez dokumentálható példa elavult jogforrás használatára. Nem pusztán egy hatályos törvény rosszul emlékezett bekezdése szerepelt: a modell egy korábbi törvényt tett meg aktuális érvelési alapnak. A hatályos bírósági szervezeti szabályozást a [2011. évi CLXI. törvényben](https://njt.jog.gov.hu/jogszabaly/2011-161-00-00) kell ellenőrizni, és onnan kell az adott állításhoz megfelelő rendelkezést kiválasztani.

Az azonban ebből sem derül ki, hogy a modell belső működésében pontosan mi idézte elő a tévedést. Elavult jogszabályt használt; hogy ezt milyen tanítási vagy visszakeresési folyamat miatt választotta, nem állapítható meg a beszélgetésből.

### Nem a megjelölt tárgyról szólt a hivatkozott Be. szakasz

A 2025. június 1-jei, hangfelvétel bizonyítékként való felhasználásával kapcsolatos munkamenet visszakeresett összefoglalása szerint a modell a **Be. 168. §-ára** alapozta a jogellenesen szerzett hangfelvétel kivételes felhasználhatóságát. Az eredeti kérdés teljes szövege nem áll rendelkezésre, ezért ezt az esetet tartalmilag foglalom össze.

A Be. 168. § az ellenőrzött szövegben a tanúkénti kihallgatásról és a vallomástételi kötelezettségről szól. Nem az állított kivételes hangfelvétel-felhasználási szabályt tartalmazza. Ezt a hivatkozást tehát nem lehetett a megadott állítás jogszabályi igazolásaként használni. [Be. 168. §, Nemzeti Jogszabálytár](https://njt.jog.gov.hu/jogszabaly/2017-90-00-00).

A hibás jogszabályhely felismerése önmagában még nem dönti el egy konkrét felvétel felhasználhatóságát. A helyes válaszhoz új elemzés kellene az eljárás típusa, a rögzítés körülményei és az alkalmazandó szabályok alapján. A tanulság itt az, hogy a rossz paragrafust nem szabad pusztán egy másik számra lecserélve megőrizni az eredeti következtetést.

### Mit támasztanak alá a példák az elavult jogszabályokról

| Munkamenet | Azonosított probléma | Az elavult jogszabály szerepe |
| --- | --- | --- |
| 2025. május 15. — ideiglenes intézkedés | Téves jogorvoslati állítás és jogszabálynak tulajdonított hibás idézet | Nem igazolt magyarázat; a vizsgált régebbi Pp.-szöveg is ellentmond a válasznak. |
| 2025. október 27. — bírói mérlegelés | Hatályon kívül helyezett törvény aktuális jogforrásként való használata | Közvetlenül dokumentálható. |
| 2025. június 1. — hangfelvétel | Az állítást nem alátámasztó paragrafus | A hivatkozási hiba igazolható; az oka nem. |

Saját tapasztalatom szerint külön kérnem kellett a hatályos jogszabályszöveg használatát. Ennek az utasításnak a pontos korábbi üzenetét a visszakeresés most nem hozta elő, ezért nem kapcsolom kitalált idézetként valamelyik fenti munkamenethez. Az esettanulmányban ez saját beszámolóként szerepel; a három hibás válasz ettől külön ellenőrizhető.

### Hogyan változtatnám meg a kérdezés menetét

Először a tényállást és az alkalmazandó eljárást tisztáznám, utána kérném a forrásokat, és csak ezek ellenőrzése után a kész érvelést. A két lépés különválasztása megkönnyíti észrevenni, ha egy szép mondat mögött nincs megfelelő rendelkezés.

Hiba észlelésekor ezt kérném:

```text
A korábbi válaszodban szereplő [hivatkozás] nem támasztja alá az állításodat.
Ellenőrizd a hivatalos szöveget és az alkalmazandó időállapotot.
Sorold fel, mely korábbi mondataid voltak hibásak, és mely további
következtetéseket érinti a hiba. Ne csak a paragrafusszámot javítsd.
Ezután készíts javított választ, és jelöld, mi maradt bizonytalan.
```

A forráskérés megfogalmazásán is változtatnék. A „keress forrásokat az állításomhoz” helyett előbb azt kérném, hogy a modell vizsgálja meg, igaz-e az állítás, milyen feltételekkel igaz, és mi szólhat ellene. Ez csökkentheti annak esélyét, hogy a keresés kizárólag a már kialakított álláspont megerősítésére szűküljön, de a források ellenőrzését nem helyettesíti.

### Az eredmény értékelése

A visszakeresés alapján az MI használata a jogi tájékozódásban hasznos kérdéseket és rendezett szöveget adott, de a hivatkozások minősége nem volt egyenletes. A bemutatott munkamenetekből nem következik igazolt pernyertesség vagy más eljárási siker, és az sem, hogy minden hibát még felhasználás előtt kijavítottam volna.

Az esettanulmány kézzelfogható eredménye a három azonosított hibaminta és az ezekre válaszoló ellenőrzési módszer. A hatályosság vizsgálata ezek közül egy lényeges elem, de ugyanilyen fontos a valódi szöveg, a helyes eljárási keret és a következtetés ellenőrzése.