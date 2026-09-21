---
layout: default
codename: 1041_MCPServerforResearch
title: MCP szerver fejlesztése GitHub integrációhoz, kutatási eredmények rendszerezett rögzítésére
tags: snippets mieset
authors: Dongó Tamás
---

# MCP szerver fejlesztése GitHub integrációhoz, kutatási eredmények rendszerezett rögzítésére

A feladat egy olyan személyes AI kutatási asszisztens infrastruktúra kialakítása volt egy PhD projekthez, amely lehetővé teszi a természetes nyelvű beszélgetést egy LLM-mel (pl. Claude), miközben a beszélgetés során hozott döntések és új ötletek automatikusan (de jóváhagyás után) bekerülnek a kutatás hivatalos, GitHub-on tárolt Markdown dokumentációjába. Ehhez egy privát MCP (Model Context Protocol) szerver készült, amit a render.com szerverén kereszül köti össze a kliens által generált eszközhívásokat a GitHub repóval.

Ebben az esettanulmányban részletesen bemutatom, hogyan használtam fel a GitHub Copilot Agentet a rendszer programozására, milyen akadályokba ütközött az MI és hogyan oldotta meg azokat, majd azt is, hogyan néz ki a rendszer a mindennapi használatban immár több hónap távlatából.

## A kódoló ágens (Copilot Agent) működésének mélyreható elemzése

A fejlesztés során megfigyeltem, hogy az MI ágens hogyan "gondolkodik" és hajtja végre a feladatokat. Az alábbi kulcsfontosságú tapasztalatokat szereztem:

### 1. A robusztus, több szekciós promptolás ereje
Az Agentnek egy hatalmas, strukturált promptot adtam át. Ebben nemcsak a feladatot írtam le, hanem kategóriákba szedtem a peremfeltételeket (`HIGH-LEVEL ARCHITECTURE`, `CORE DESIGN PRINCIPLE`, `MCP TOOLS`, `SAFETY / RESEARCH INTEGRITY`, `OBSERVABILITY`, `MVP FIRST`, `HOW I WANT YOU TO WORK`).

**A tanulság:** Mivel kifejezetten tiltottam dolgokat (*"Do NOT build Kubernetes"*, *"Do NOT build a microservice architecture"*), az Agent nem kezdett el "kód-kúszásba" (scope creep). A keretek pontos kijelölése miatt egy letisztult, egyetlen FastAPI fájlból álló alkalmazást generált, ami pontosan azt tudta, amit kértem.

### 2. Belső állapotkezelés és ToDo listák
Az Agent a munkát nem azonnali kódolással kezdte. Először egy beépített `manage_todo_list` tool-t hívott meg, amiben felvázolta a saját feladatait:
1. Inspect repository contents
2. Propose architecture brief
3. Create minimal project scaffold
4. Implement MVP... stb.

**A tanulság:** Az Agentek számára elengedhetetlen egy belső feladatlista. Ez segített a modellnek abban, hogy a 7 lépéses feladatot ne felejtse el a kontextusablak növekedésével sem. A folyamat során (amikor például a teszteket implementálta), visszanyúlt ehhez a listához és frissítette a státuszokat.

### 3. Önjavító mechanizmus az útvonalaknál
Az egyik legérdekesebb hiba az első fájlgeneráláskor (`requirements.txt`) történt. Az Agent az `apply_patch` eszközt relatív útvonallal próbálta meghívni. A rendszer ezt a hibát dobta:
> `ERROR while calling tool: Invalid input path: requirements.txt. Be sure to use an absolute path. Please check your input and try again.`

**A megfejtés:** Az Agent nem állt le, és nem kérte a segítségemet. Létrehozott egy belső gondolkodási (`thinking`) blokkot, majd újra meghívta a `list_dir` tool-ból korábban megismert abszolút útvonalat (`c:\Users\Tamas\Desktop\PhD\AI EDIH\1041_ResearchAssisstant\requirements.txt`). **Ez jól mutatja, hogy a modern kódoló ágensek képesek a saját eszköz-hibáik értelmezésére és emberi beavatkozás nélküli javítására.**

### 4. Egyéb megfigyelések: tesztelés és proaktív implementáció
Az Agent a tesztelésnél is önállóan gondolkodott: mivel tudta, hogy a GitHub API teszteléséhez token kellene (ami a CI környezetben alapból nincs beállítva), nem bonyolult mock-osztályokat gyártott, hanem a saját maga által korábban implementált `LOCAL_REPO_PATH` fallback-et használta fel egy önálló, külső API-hívás nélküli tesztkörnyezet felépítésére. 

Emellett a prompt `OBSERVABILITY` szekciójában leírt, de konkrétan meg nem fogalmazott igényt ("minden módosítás legyen visszakövethető") proaktívan egy strukturált JSON-lines audit-log függvénnyé alakította. 

## Korábbi beszélgetések importálása kötegelt feldolgozással

A rendszer egyik legnagyobb gyakorlati próbája nem az élő, valós idejű használat volt, hanem a múltbeli kutatási beszélgetések archívumának visszadolgozása a dokumentációba. A kutatásom közel két éve alatt három különböző AI-eszközzel (Gemini, ChatGPT, Claude) is folytattam beszélgetéseket, ezek azonban soha nem kerültek be strukturáltan a GitHub-repóba - csak a felhasználói fiókok saját exportjaiban léteztek.

**A forrásadat:** a Google Takeout-tal exportált Gemini-aktivitási napló egy 18,8 MB méretű, közel 6100 bejegyzést tartalmazó JSON fájl volt, október 2024 és augusztus 2026 közötti időszakra. A ChatGPT és a Claude exportjai hasonló, bár nem azonos szerkezetű JSON formátumban érhetők el - a lényeg, hogy mindhárom platform strukturált, géppel feldolgozható exportot ad a beszélgetés-előzményekről, így ugyanaz a feldolgozási módszer elvben mindhárom forrásra alkalmazható, csak a nyers adat parse-oló lépését kell platformonként igazítani.

**Miért kellett kötegelni?** Az első próbálkozás - az összes releváns szövegrészt egyszerű kulcsszavas kereséssel kiszűrni - hamar kiderült, hogy nem elég megbízható: pontatlan kulcsszólistával könnyű elveszíteni valódi döntéseket, amiket máshogy fogalmaztak meg, mint ahogy a keresés várta. A megoldás az volt, hogy a teljes archívumot időrendben, kronologikus kötegekbe (batch-ekbe) szeleteltem, minden köteg méretét a felhasználható kontextusablak (context window) feléhez igazítva - ez biztosította, hogy egyetlen kötegen belül is elférjen elég kontextus az AI számára ahhoz, hogy valóban értelmezze, mi történik, ahelyett hogy csak izolált mondattöredékeket látna. 
Egy finomítási körben ezt tovább optimalizáltuk: az egymáshoz időben közeli beszélgetéseket egy "session"-ként kezelve csoportosítottuk, és csak azokat a session-öket tartottuk meg teljes egészében, amik legalább egy releváns technikai kulcsszót tartalmaztak - így a végső feldolgozandó anyag jelentősen csökkent anélkül, hogy bármilyen releváns döntést elveszítettünk volna.

**A végeredmény:** a teljes archívum feldolgozása és a kutatási dokumentáció ez alapján történő frissítése/pontosítása ezzel a módszerrel egyetlen munkamenetben végigvihető volt - AI-asszisztencia nélkül ez gyakorlatilag lehetetlen lett volna, hiszen közel 6100 különálló kérdés-válasz párost kellett volna manuálisan átnézni és értelmezni, hogy kiderüljön, melyik döntés még érvényes, és melyiket írta felül egy későbbi beszélgetés.

## A rendszer élesben: napi használat Claude-dal

A szerver elkészülte óta a gyakorlatban is bevált: mivel MCP szerverként fut, ugyanaz a kapcsolat elérhető webes felületen, asztali alkalmazásban és Android appon keresztül is - így a kutatási döntéseket akár útközben, hangalapú beszélgetés formájában is rögzíteni tudom, anélkül hogy laptopot kellene nyitnom.
Egy tipikus munkamenet így néz ki: hangosan átbeszélem Claude-dal a felmerülő tervezési kérdést (pl. egy hardveres vagy szoftveres architektúra-döntést), az AI a beszélgetés végén összefoglalja a változtatást, branch-et nyit, majd Pull Requestet készít - amit én a GitHubon nézek át és hagyok jóvá, mielőtt a `master` ágba kerülne. Ez a jóváhagyási lépés tudatosan nincs automatizálva: **a kutatási dokumentáció integritása szempontjából kritikus, hogy semmi ne kerüljön be ellenőrizetlenül.**

## A kutatás bemutatása weboldalon keresztül

Mivel a teljes dokumentáció végig egységes, előre meghatározott szerkezetű Markdown fájlokban íródott (mindegyik dokumentum azonos, gépileg feldolgozható metaadat-fejléccel: cím, kategória, dátum, rövid leírás), adta magát az ötlet, hogy ebből **automatikusan generáljunk egy publikus bemutató weboldalt** is - anélkül, hogy a tartalmat máshova kellene átmásolni vagy duplikálni.

Az oldal egy Next.js alapú statikus site, amit a Vercel szolgáltat ki, és build időben közvetlenül a repó Markdown-mappáiból építkezik: a főoldal a kutatási témák (projekt, szakirodalom, szoftver, hardver, kísérletek, publikációk stb.) tartalomjegyzékét adja, minden témakörnek saját aloldala van, minden dokumentum pedig önálló, formázott oldalként jelenik meg - a matematikai képletekkel, táblázatokkal együtt. Így minden GitHubra bekerülő, jóváhagyott változtatás a következő build-del automatikusan megjelenik a nyilvános oldalon is, külön karbantartási munka nélkül.

## Kihívások, amikkel használat közben szembesültem

A fejlesztés és a napi használat során több váratlan probléma is felmerült, amelyek jó tanulsággal szolgáltak:

- **Elavult információ felismerése:** mivel a beszélgetések hónapokon, sőt éveken át húzódtak, ugyanarról a kérdésről (pl. az eszköz fizikai kialakításáról) többször is más-más döntés született. Az AI-nak explicit utasítást kellett adnom, hogy időrendben haladjon végig az archívumon, és a későbbi döntéseket tekintse mérvadónak a korábbiakkal szemben - enélkül a dokumentáció ellentmondásossá vált volna.
- **Szerzői jogi kérdés a forrásirodalomnál:** a szakirodalmi mappába feltöltött, más szerzők által jegyzett cikkek teljes szövege - bár a saját kutatáshoz jogszerűen felhasználható - nem publikálható változatlan formában egy nyilvános weboldalon. Erre megoldásként egy `public: false` jelzőt vezettünk be a dokumentumok metaadatában, amivel az adott fájl a repóban megmarad (saját referenciaként, és így az MI modell is eléri, ha szükség van rá), de a weboldal build folyamata kihagyja a nyilvános megjelenítésből. A cikkek helyett egy önállóan megfogalmazott, publikálható annotált bibliográfia készült.

Az kutatást összefoglaló weboldal ezen a linken keresztül tekinthető meg: https://phd-xi.vercel.app/
