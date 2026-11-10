---
layout: default
codename: TozsdeiElemzes
title: Tőzsdei döntések előkészítése adatszűréssel és célzott hírelemzéssel
tags: snippets mieset
authors: Kövesdán Gábor
---

# Tőzsdei döntések előkészítése adatszűréssel és célzott hírelemzéssel

Részvényekről és ETF-ekről rendelkezésre álló CSV-listák alapján szerettem volna szűkíteni az opciós kereskedéshez vizsgálandó instrumentumok körét. A ChatGPT-től először számszerű feltételek szerinti válogatást kértem, majd a kiválasztott jelöltek értékelését az aktuális pénzügyi és gazdasági hírek alapján. A beszélgetést később eltérő piaci forgatókönyvekre és opciós stratégiákra vonatkozó kérdésekkel folytattam.

A kiindulópontot saját kereskedési szempontok adták: milyen termékek érdekelnek, milyen likviditási feltételeket várok el, és milyen stratégiákhoz keresek jelölteket. Az MI ennek a keretnek a feldolgozását támogatta. Segíthet összegyűjteni és összevetni a piaci elképzelés mellett és ellen szóló információkat, miközben csökkenti a hírek egyenkénti átnézésére fordított munkát.

Az adatok és a válaszok megbízhatóságát azonban ellenőrizni kell. A piac mozgása sem teljesen megjósolható: legfeljebb feltételekhez kötött forgatókönyveket és valószínűségi várakozásokat lehet kialakítani. Az esetben ezért az MI értékét elsősorban a döntés előkészítésének gyorsításában látom, nem a jövőbeli hozam bizonyításában.

**Használt eszköz:** ChatGPT, feltöltött CSV-listákkal és többfordulós kérdezéssel. A munkamenet dátuma 2026. szeptember 25. Az alábbi leírás történeti esettanulmány, nem mai instrumentumajánlás.

## Tanulságok

- **A saját kereskedési keret pontosabb feladatot ad az MI-nek.** A termékkör, az időtáv, a szűrési feltételek és a preferált stratégiák ismeretében célzottabb összefoglaló készülhet.
- **A számszerű szűrés és a piaci értelmezés eltérő bizonyosságú.** Egy jól definiált táblázatszűrés megismételhető; egy árfolyam-forgatókönyv bizonytalan következtetés.
- **Az MI az elképzelések próbára tételében is használható.** Akkor hasznos igazán, ha a megerősítő érvek mellett ellenérveket és a várakozást érvénytelenítő körülményeket is keres.
- **A hírek célzott összefoglalása időt takaríthat meg.** A széles hírolvasás helyett egy szűkített jelöltlistához kaphatok rendezett kiindulópontot.
- **A kereskedési gyakorlat az eredmény értékelésében kap szerepet.** A tapasztalt felhasználó könnyebben észlelhet irreális feltételezést vagy a saját stratégiájához nem illő javaslatot, de ő is tévedhet.
- **A magabiztos hangnem nem helyettesíti a friss adatot.** Az MI használhat elavult vagy hibás információt, és ellenőrizetlen számadatot is adhat.
- **A hatékonyabb előkészítés nem egyenlő a bizonyítottan jobb kereskedési eredménnyel.** A munkamenetből nem állapítható meg elért hozam, találati arány vagy mért időnyereség.

## Az eredmény használata

Az elemzés eredménye egy további vizsgálatra szánt jelöltlista és az egyes piaci elképzelésekhez kapcsolódó érvrendszer. Ezek alapján a kereskedő eldöntheti, mely termékeket érdemes részletesebben ellenőriznie a saját adatforrásában és kereskedési felületén.

A felhasználás során a CSV időpontját, az oszlopok jelentését, a hírforrásokat és az elemzés feltételezéseit is meg kell őrizni. Így később megkülönböztethető, hogy egy várakozás hibás adatból, hibás értelmezésből vagy a feltételek későbbi megváltozásából adódott-e.

Ebben az esettanulmányban nem számoltam újra a régi CSV-ket, nem ellenőriztem újra az akkori instrumentumajánlásokat, és nem készítettem friss piaci rangsort. A cél az akkori munkafolyamat értékelése.

## A munkafolyamat tanulságos részletei

### Konkrét adatokból és feltételekből indultam

A munkamenetben egy részvény- és egy ETF-listát csatoltam CSV-formátumban. Az első kérésben az alábbi feltételekkel szűkítettem a vizsgálatot:

| Szempont | Az eredeti kérésben megadott feltétel |
| --- | --- |
| Ár | A `mid price` legalább 10 dollár legyen. |
| Nyitott opciós állomány | Az `option open interest` legalább körülbelül 10 000 legyen. |
| Forgalom | A napi `volume` legalább néhány száz legyen. |
| Piaci elképzelés | A hírek alapján jelentős felfelé mozdulásra érdemes jelöltek keresése. |

Ezek az adott feladatban választott szűrők voltak, nem általános szabályok arra, hogy mivel érdemes kereskedni. Az eredeti válasz a „néhány száz” kifejezést 300-as minimumként kezelte. Ez apró, de fontos értelmezési lépés: a természetes nyelvű kérés egy programozható küszöbértékké alakult.

Egy következő használatnál előbb visszakérném a szűrés pontos szabályait. A `mid price`, a forgalom és az open interest oszlopoknál azt is tisztáznám, hogy milyen termékre, időpontra és összesítési szintre vonatkoznak. Az elnevezés önmagában nem elég az adatok helyes értelmezéséhez.

### A szűrés után piaci magyarázatot kértem

A számszerű válogatás után azt kértem, hogy a modell a pénzügyi és gazdasági hírek alapján értékelje a jelölteket. Ezzel a feladat egy ellenőrizhető adatműveletből átment egy bizonytalanabb elemzési lépésbe.

A felhasználási cél az volt, hogy ne minden terméknél külön kelljen végignéznem a híreket, és fejben összevetnem az eltérő szempontokat. Az MI egy helyre rendezheti a fontos eseményeket, a pozitív és negatív tényezőket, valamint azt, hogyan kapcsolódnak a vizsgált időtávhoz.

Ehhez ugyanakkor a hírek tényleges megnyitása és keltezése szükséges. A „friss hírek alapján” felszólítás önmagában nem igazolja, hogy a válasz friss forrásokra támaszkodik. Ugyanígy egy vállalatról szóló kedvező hír sem azonos a következő időszak árfolyam-emelkedésének bizonyítékával: az elemzésnek a várakozások és az ellenérvek szerepét is meg kell vizsgálnia.

### A további kérdésekkel a saját stratégiáimhoz igazítottam az elemzést

A beszélgetésben a calendar spread jelöltek, a volatilitási eltérések és az S&P 500 kéthetes kilátása is előkerült. Később a felfelé irányuló várakozás helyett más forgatókönyvhöz kértem jelölteket:

> És melyek azok az instrumentumok, amelyekre oldalazás vagy enyhe csökkenés várható nagy bizonyossággal? Emeld ki ezekből is a legjobb jelölteket opciós kereskedéshez, és hogy milyen stratégiával kereskednél. Indokold ugyanilyen részletességgel.

Ez az új kérdés megváltoztatta a rangsorolás célját. Ugyanaz az instrumentum más megítélést kaphat attól függően, hogy emelkedésre, oldalazásra vagy enyhe csökkenésre keresek lehetőséget. A stratégiai elképzelés megadása tehát a feladat lényegi része volt.

A „nagy bizonyossággal” megfogalmazás viszont túl erős elvárást jelentett. A helyes munkamód az, hogy a modell ne erőltessen bizonyosságot a kérdés kedvéért: nevezze meg a feltételezéseit és azokat a körülményeket, amelyek mellett más kimenetel várható. Kalibrált számítás nélkül egy százalékos valószínűség sem válik attól megbízhatóvá, hogy pontosnak látszik.

### A megerősítés mellett cáfolatot is érdemes kérni

Ha már van piaci elképzelésem, az MI segíthet ellenőrizni, milyen információk támasztják alá és melyek gyengítik. Ennek akkor van értéke, ha valóban nyitva hagyom a lehetőséget arra, hogy az eredeti elképzelésem hibás.

Az „indokold meg, miért jó ez az ötlet” könnyen egyoldalú választ eredményezhet. Hasznosabb külön kérni a legerősebb ellenérvet, a hiányzó adatokat és azt, milyen esemény után kellene újraértékelni a várakozást. Az MI által talált ellenérv is megtakaríthat időt: segíthet korán félretenni egy további munkára kevéssé érdemes jelöltet.

Egy továbbfejlesztett promptot így fogalmaznék meg:

```text
A mellékelt CSV-listából a saját kereskedési keretem szerint készíts
előszűrést. Termékkör: [megadás]. Időtáv: [megadás].
Preferált stratégiák: [megadás]. Piaci elképzelésem: [állítás].

Először tisztázd az oszlopok jelentését és az adatok időpontját.
Írd le pontosan a használt szűrési szabályokat; a bizonytalan feltételeket
ne alakítsd át észrevétlenül konkrét küszöbökké.

A jelöltekhez keress dátummal és hivatkozással ellátott releváns híreket,
lehetőleg elsődleges forrásokból. Válaszd külön a feltöltött adatot,
a forrásból származó tényt és a saját következtetésedet.

Minden jelöltnél add meg a piaci elképzelésemet támogató legerősebb érvet,
a legerősebb ellenérvet és egy körülményt, amely érvénytelenítené azt.
Jelezd, ha a stratégia értékeléséhez további opciós adat szükséges.
Ne találj ki aktuális árakat, és ne adj ellenőrizetlen valószínűségeket.
Először rövid összehasonlítást adj; részletes elemzést csak a leginkább
releváns néhány jelöltről készíts.
```

Ez utólagos módszertani javaslat, nem az eredeti beszélgetés további lépése.

### Az MI adatainak és értelmezésének korlátai

A feltöltött táblázat lehet hiányos vagy elavult, a modell félreérthet egy oszlopot, a hírösszefoglaló pedig kihagyhat lényeges körülményt. Helyes bemenetből is születhet hibás következtetés. A SEC, a NASAA és a FINRA közös tájékoztatója is kiemeli, hogy az MI által előállított befektetési információ pontatlan, hiányos, félrevezető vagy elavult adatokra épülhet. [Investor.gov, 2024. január 25.](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-alerts/artificial-intelligence-fraud)

A kereskedési tapasztalat abban segít, hogy az elemzést a saját módszeremhez tudjam viszonyítani, és felismerjem, melyik állítást kell még ellenőrizni. Nem teszi tévedhetetlenné sem az MI-t, sem a felhasználót. A végső döntéshez továbbra is szükségesek a tényleges kereskedési feltételek és a saját kockázati korlátok.

### Hol keletkezhet az időnyereség

A legnagyobb gyakorlati előnyt abban látom, hogy az MI egymáshoz kapcsolhatja az előszűrést, a releváns hírek kigyűjtését és az érvek összehasonlítását. A kereskedő így egy rövidebb jelöltlistából indulhat, és a döntő pontok ellenőrzésére fordíthatja a figyelmét.

Ez megspórolhatja a hírek széles körű, ismétlődő átnézésének jelentős részét, és hatékonyabbá teheti a kereskedés előkészítését. Az időnyereség azonban attól is függ, mennyi utóellenőrzést és javítást igényel a válasz. Ebben a munkamenetben nem történt időmérés, ezért feltétlen vagy számszerű megtakarítást nem állítok.

A bemutatott eredmény a célzott szűrés és az elemzési kiindulópont. Nem dokumentált, hogy a javaslatokból tényleges ügylet született-e, illetve milyen eredménnyel. Az eset tanulsága az, hogy saját kereskedési elképzeléssel és ellenőrzési fegyelemmel az MI a tájékozódás és a döntés-előkészítés hasznos eszköze lehet.

A történeti munkafolyamat bemutatása nem igazolja az akkori rangsorok helyességét vagy a stratégiák nyereségességét. Az új promptminta továbbfejlesztési javaslat.
