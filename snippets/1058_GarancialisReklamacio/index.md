---
layout: default
codename: GarancialisReklamacio
title: Mesterséges intelligencia használata egy cipőreklamáció érveléséhez
tags: snippets mieset
authors: Kövesdán Gábor
---

# Mesterséges intelligencia használata egy cipőreklamáció érveléséhez

Egy cipőkereskedésben vásárolt Tom Tailor bakancs minőségi kifogásának elutasítása után a ChatGPT segítségével kerestem érveket a reklamációm alátámasztásához. Először alkalmazható szabványt szerettem volna találni, amely objektív, kézzelfogható ellenérvet adhat a kereskedő által beszerzett szakvéleménnyel szemben. Mivel ezen az úton nem jutottam az esetemre elég konkrét válaszhoz, a téli cipőktől általában elvárható tartósságra kérdeztem rá, majd pontosítottam a márkát és a terméktípust.

A válaszokat felhasználtam a panaszomban, és a Budapesti Békéltető Testülethez fordultam. A kereskedő végül felülvizsgálta a panaszt, és vállalta a 17 990 Ft-os vételár visszafizetését. A testület az egyezséget 2025. május 26-án jóváhagyta. Megítélésem szerint az MI segítségével megfogalmazott érvek hozzájárultak ehhez az eredményhez, bár az egyes érvek döntésre gyakorolt hatása külön nem állapítható meg.

**Használt eszköz:** ChatGPT, szöveges, többfordulós beszélgetésben. A vizsgált beszélgetés 2025. április 9-én zajlott, az akkori ingyenesen elérhető modellel.

## Tanulságok

- **Érdemes a kérdezés irányát az eredményekhez igazítani.** A szabványokra irányuló keresés nem adott használható kapaszkodót, a várható élettartamra vonatkozó általános kérdés viszont segített megfogalmazni a fogyasztói elvárásaimat.
- **A rövid, egymásra épülő promptok is célravezetők lehetnek.** A termékkategóriától a tartósságon át a konkrét márkáig haladtam, végül az információk forrására is rákérdeztem.
- **Az MI az érvelés kialakításában is hasznos.** A panasz tényei mellé közérthető összehasonlítási szempontokat adott: milyen használhatóságot és tartósságot várhat el egy vásárló egy ilyen cipőtől?
- **A meggyőző megfogalmazás és a bizonyítottság különbözik.** A modell által megadott élettartam-becslést nem lehetett termékvizsgálatként, gyártói vállalásként vagy igazolt statisztikaként kezelni.
- **A közvélekedésre emlékeztető válasz érvelési kiindulópont lehet, de önmagában nem méri a közvélekedést.** Az MI megfogalmazhat széles körben ismerős fogyasztói elvárásokat, ugyanakkor ezek reprezentativitását és helyességét a válasz ténye nem igazolja.
- **A sikeres egyezség nem hitelesíti automatikusan az MI minden állítását.** Az igazolható eredmény a vételár visszafizetésének vállalása és az egyezség jóváhagyása; a határozat nem döntött az MI által közölt tartóssági becslés helyességéről.

## Az eredmény használata

Az eset eredménye egy panaszba beépített érvelés és az azt követő egyezség. A módszer más reklamációk előkészítésénél is követhető:

1. Összegyűjtöm a saját ügyem tényeit: a vásárlás és a meghibásodás időpontját, a használat körülményeit, a hiba leírását és az elutasítás indokait.
2. Megpróbálok ellenőrizhető, a konkrét termékre alkalmazható követelményt találni.
3. Ha ez nem ad megfelelő választ, külön megvizsgálom az észszerű fogyasztói elvárásokat, és pontosítom a terméket, valamint a használat módját.
4. Rákérdezek az állítások forrására, és elkülönítem a dokumentált tényeket az általános becslésektől.
5. A panaszba csak az ügyhöz kapcsolódó megállapításokat építem be, az ellenőrizetlen becsléseket pedig becslésként jelölöm.

Az alábbi promptok a megtörtént eset kérdezési menetét mutatják be. A számszerű élettartam-adatok az akkori érvelés részei, nem általánosan alkalmazható minőségi követelmények.

## A munkafolyamat tanulságos részletei

### A reklamáció kiinduló helyzete

2024. május 5-én vásároltam a kereskedés egyik üzletében egy Tom Tailor magasszárú cipőt, amelyet megjelenése alapján őszi-téli használatra szánt terméknek tekintettem. Először a talpbetét vált el, majd a jobb cipő lépéskor szuszogó, nyikorgó hangot adott, és olyan érzést keltett, mintha levegő mozogna benne. A cipő számomra kényelmetlenné, hordhatatlanná vált; 2025. március 3-án vittem vissza minőségi kifogással.

A kereskedő a Hoffer Minőségügyi Szakértő Bt. szakvéleményét szerezte be. A panaszomban ismertetett szakvélemény a problémát kíméletlen, rendeltetésellenes viselésnek tulajdonította, és külső nedvességre, valamint lábnedvességre is hivatkozott. Ezt vitattam: elmondásom szerint a cipőt hétköznapi helyzetekben, nem mindennap használtam, különösen megterhelő tevékenységet nem végeztem benne, és a talpa alig kopott, amely szintén utal rá, hogy keveset volt használva.

### Első lépésként objektív követelményt kerestem

Az első kérdésem:

> Vonatkozik magyar szabvány magasszárú téli vagy őszi cipőkre?

Olyan külső viszonyítási pontot kerestem, amellyel meg lehetett volna kérdőjelezni az elutasítás indokait. Ez különösen kézenfekvőnek tűnt, mert a szakvélemény maga is szabványokra hivatkozott.

**Az MI válaszának tartalmi összefoglalása:** a modell szabványokról, többek között munka- és védőlábbelikhez kapcsolódó előírásokról, valamint vízzel, csúszással és hőszigeteléssel kapcsolatos tulajdonságokról adott tájékoztatást. Ebből azonban nem kaptam a saját lábbelim tartósságára közvetlenül alkalmazható, ellenőrzött követelményt.

A prompt tárgyszerű és célzott volt, de a termék pontos anyagát, gyártói besorolását és a vitatott szakvéleményben szereplő szabványazonosítókat nem tartalmazta. Emiatt önmagában nem adott elég támpontot annak eldöntéséhez, mely előírás alkalmazható ténylegesen az adott cipőre. A beszélgetésnek ezt a szakaszát ezért tájékozódásként tudtam használni; döntő ellenérvként nem.

### Áttértem az általában elvárható tartósságra

A következő kérdésem:

> Milyen élettartamot várhatunk el egy téli cipőtől?

Ezzel megváltoztattam a megközelítést. Ahelyett, hogy továbbra is egy konkrét szabványt próbáltam volna megtalálni, azt vizsgáltam, mennyire tekinthető észszerűnek a saját tartóssági elvárásom.

**Az MI válaszának tartalmi összefoglalása:** a modell a cipő típusától, minőségétől és használatától függő élettartam-tartományokat adott. A válasz így alkalmas volt arra, hogy a korai meghibásodást egy tágabb fogyasztói elváráshoz viszonyítsam, de a konkrét hibát és annak okát nem bizonyította.

A kérdés nem sugallta, hogy feltétlenül nekem kell igazat adni. Általános viszonyítási pontot kért, ami segített a saját álláspontomat is megvizsgálni. Ugyanakkor a „tél” nem egységes terhelési mérték: a használat gyakorisága és körülményei nélkül az ilyen becslés szükségképpen pontatlan.

### Rövid pontosítással szűkítettem a termékkört

Ezután megadtam:

> Tom Tailor magasszárú bakancs

A rövid kiegészítés az előző kérdésre épült, ezért nem kellett újra leírnom a teljes feladatot. A modell így már a megnevezett márkához és terméktípushoz igazította a választ.

**A panaszban felhasznált összefoglalás:** intenzív napi használat mellett 1–2, kíméletes használat mellett 2–3 tél tartósságot várhatunk egy ilyen cipőtől. Ezt állítottam szembe azzal a tapasztalatommal, hogy az én cipőm egy téli szezont sem bírt ki megfelelően.

Ez a pontosítás relevánsabbá tette a választ, de nem azonosított konkrét modellt, anyagösszetételt vagy vizsgálati eredményt. A márkanév ismerete tehát növelte a válasz helyzethez illőségét, önmagában azonban nem igazolta a számszerű becslést.

### Rákérdeztem az információk forrására

A következő kérdésem:

> Milyen forrásból veszed az információkat?

**Az MI válaszának tartalmi összefoglalása:** a modell szabványügyi anyagokat, gyártói és kereskedői tájékoztatókat, felhasználói véleményeket és általános modellismeretet nevezett meg. A rendelkezésre álló előzmények alapján azonban a konkrét Tom Tailor-élettartam-becsléshez nem azonosítható ellenőrzött, termékspecifikus forrás.

A forráskérdés fontos ellenőrzési lépés volt. A tanulsága ugyanakkor az, hogy forrástípusok felsorolása még nem teszi visszaellenőrizhetővé az állítást. Egy pontosabb következő kérdés az adott számadatot alátámasztó dokumentumot vagy hivatkozást kérné. Ez utóbbi már utólagos módszertani tanulság, nem a bemutatott beszélgetés további lépése.

### Az MI válaszait beépítettem a panasz érvelésébe

A panaszban saját tapasztalataimra és az ügy konkrét körülményeire támaszkodtam: a vásárlás óta eltelt időre, a használat módjára, a talp csekély kopására és a meghibásodás jellegére. Ezekhez kapcsoltam a ChatGPT által megfogalmazott tartóssági elvárást.

Kifejezetten jeleztem, hogy a ChatGPT válaszait nem tekintem minden szempontból szabatos szakmai vagy jogi információnak. A válaszokra úgy hivatkoztam, mint amelyek érzékeltethetik az átlagos laikus vásárló feltételezhető minőségi elvárásait. Az MI-szöveg tehát a fogyasztói álláspont közérthető megfogalmazását támogatta; nem helyettesítette a cipő vizsgálatát.

E mögött az a megfontolás állt, hogy a nyilvánosan hozzáférhető szövegekből tanult modell válaszaiban megjelenhetnek a közbeszédben gyakori elvárások. Ezeknek akkor is lehet meggyőző erejük egy vitában, ha nem felelnek meg egy műszaki szakvélemény bizonyítási követelményeinek. Ezt azonban pontosan kell értelmezni: a modell hallucinálhat, és a válasza nem reprezentatív közvélemény-kutatás. A használható érv erejét az adja, hogy észszerű, az adott ügy tényeihez kapcsolódik és indokolható, nem pusztán az, hogy a ChatGPT mondta.

### A kereskedő felülvizsgálta a panaszt

A BBT/1544/2025 számú határozat rögzíti, hogy a vállalkozás a válasziratában a panasz felülvizsgálatáról és a vételár visszafizetésének szándékáról tájékoztatta a testületet. Az egyezség szerint a terméknek a vásárlás helyén, a blokkal együtt történő átadásával egyidejűleg 17 990 Ft-ot fizet vissza.

Az egyezség szövegét a felek a meghallgatás előtt megkapták. A 2025. május 26-ra kitűzött meghallgatáson egyik fél sem vett részt; a testület a létrejött egyezséget jóváhagyta. Az eljárás tehát megindult és határozattal zárult, de a hiba okáról és a vitatott szakvélemény helyességéről már nem kellett érdemi vitát eldönteni.

Számomra az MI használatának gyakorlati értéke az volt, hogy segített a reklamáció indokait átgondolni és meggyőzően kifejteni. Az eredmény összhangban áll azzal a tapasztalatommal, hogy ez az érvelés hasznos volt. A határozat ugyanakkor nem részletezi, pontosan melyik érv miatt változott meg a kereskedő álláspontja, ezért az MI önálló hatása nem mérhető ebből az egy esetből.