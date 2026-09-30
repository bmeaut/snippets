---
layout: default
codename: TudastarGeneralas
title: Saját dokumentumtárra épülő kérdezőprogram készítése Claude segítségével
tags: snippets mieset
authors: Kövesdán Gábor
---


# Saját dokumentumtárra épülő kérdezőprogram készítése Claude segítségével

Számos tematikus dokumentumgyűjteményt szereztem be, amelyekkel kapcsolatban kérdezhető tudástárat kívántam kétrehozni. Olyan „személyre szabott” mesterséges intelligencia létrehozása volt a célom, amely a dokumentumtár témáiban magyarul válaszol, és állításait visszakereshető forrásokkal támasztja alá. Ehhez a Claude-ot kértem meg egy helyben futó Python-program elkészítésére.

A kérésemet kezdetben úgy fogalmaztam meg, hogy a program a dokumentumokból építsen nyelvi modellt. A Claude ezt egy dokumentumkereséssel támogatott válaszadó rendszerrel, azaz RAG-megoldással valósította meg. A bemutatott megoldásban egy meglévő nyelvi modell kapja meg a kérdéshez kikeresett dokumentumrészleteket; a PDF-ek feldolgozása keresési indexet épít, nem a válaszadó modell súlyait tanítja újra. Ez a különbség a későbbi hibakeresés és továbbfejlesztés szempontjából is lényeges.

**Használt eszközök:** Claude a kódgeneráláshoz; a generált megoldásban Python, helyi Ollama-modell, szövegbeágyazási modell és utólag beépített OCR.

## Tanulságok

- **A célból érdemes kiindulni, nem egy előre feltételezett technikai megoldásból.** A dokumentumokra alapozott kérdezéshez ebben az esetben keresési index és meglévő nyelvi modell összekapcsolása készült.
- **Az angol prompt segített pontosan megfogalmazni a szoftveres elvárásokat.** Korábbi tapasztalataim alapján ezen a nyelven könnyebben használtam a bevett szakkifejezéseket. Ettől a program bemenete és válasznyelve továbbra is magyar maradt.
- **A dokumentumok tényleges formátumát is fel kell mérni.** A szkennelt PDF-ekhez külön OCR-lépést kellett kérnem, mert a szövegkinyerés önmagában nem volt elegendő.
- **A telepítési leírás a használhatóság része.** A sok függőség ellenére futásra tudtam bírni a szoftvert, mert a Claude dokumentálta a telepítésüket.
- **A működő kérdezőfelület és a megjelenő hivatkozások még nem igazolják a válaszok pontosságát.** A kapott források témájukban kapcsolódtak a kérdésekhez, de nem adtak kellően egzakt alátámasztást.
- **A bizonytalan eredmény okát lépésenként kell feltárni.** Vizsgálni kell a forrásanyag lefedettségét, a szövegkinyerést, a keresést és a válaszadó modell alkalmasságát is.
- **A többórás előfeldolgozás eredményét meg kell őrizni.** A mentés, az inkrementális feldolgozás és a megszakítás utáni folytatás külön ellenőrizendő követelmények.

## Az eredmény használata

A program működéséről adott leírás szerint először a helyi modellfuttató környezetet, a választott modellt és a Python-függőségeket kellett telepíteni. Az OCR-rel bővített változat további Python-csomagokat, Tesseractot magyar nyelvi adatokkal, valamint a PDF-oldalak képpé alakításához Popplert igényelt. A részletes telepítési útmutató segítségével ezeket be tudtam állítani.

A párbeszédben szereplő indítási példa:

```bash
python rag_hu.py --dir "C:/dokumentumok/pdfek" --model llama3.1:8b
```

A könyvtár és a válaszadó modell tehát paraméterezhető volt. Ez a parancs a korabeli beszélgetés példája, nem annak igazolása, hogy végül pontosan ezzel a modellel végeztem a próbát, és nem jelenlegi modellajánlás.

A dokumentumok első feldolgozása több órát vett igénybe. Utána megjelent a kérdések beírására szolgáló prompt, és magyarul kérdezhettem a programot. Válaszokat és dokumentumhivatkozásokat is kaptam, de a válaszok pontossága nem érte el a célként kitűzött szintet.

Az esettanulmány a fejlesztési folyamatot és a kipróbálás tapasztalatait mutatja be. Az esettanulmány a generált program teljes forráskódját nem tartalmazza, ezért a megvalósítás minden részlete ebből önállóan nem ellenőrizhető.

## A munkafolyamat tanulságos részletei

### Angolul írtam le a feladatot, magyar működést kértem

A korábban szerzett tapasztalataimhoz hasonlóan most is angolul promptoltam. Szoftveres feladatoknál számomra így egyértelműbben megfogalmazhatók a követelmények, közismert és világos terminológiával. Ez személyes munkamódszer volt; önmagában nem bizonyítja, hogy egy ugyanolyan pontos magyar prompt rosszabb eredményt adott volna.

Az első kérésem teljes szövege:

```text
Write me a Python program that reads all PDF files in a specific directory,
learns that content of those building a language model and lets me ask
questions based on the processed content. The questions are answered in
natural language citing and referencing the processed documents. The PDF
content is in Hungarian language so the questions will be in Hungarian
and the program must answer them in Hungarian too.
```

Ebben megadtam a programozási nyelvet, a forrásfájlok típusát és helyét, a kérdezés módját, a hivatkozások igényét és a magyar nyelvű működést. A Claude visszakérdezett, hogy felhős API-t vagy helyben futó modellt szeretnék-e használni. A helyi modellt választottam. Ez a pontosítás érdemben meghatározta a telepítési és futtatási környezetet.

### A „modellépítés” valójában dokumentumindexelést jelentett

Claude kifejezetten jelezte, hogy nem a nulláról tanít nyelvi modellt. A válaszában leírt feldolgozás a következő volt:

1. A program kinyeri a PDF-ek szövegét, majd kisebb részletekre bontja.
2. Egy többnyelvű beágyazási modell a részletekből kereshető számszerű reprezentációt készít.
3. A program a kérdéshez hasonló tartalmú részleteket keresi ki.
4. A helyi nyelvi modell ezekből fogalmaz választ magyarul, számozott hivatkozásokkal.
5. A hivatkozások mellett megjelenik a forrásfájl és az oldalszám.

A két modell szerepe eltér: az egyik a releváns szöveg megtalálását segíti, a másik a választ fogalmazza meg. A beszélgetésben a beágyazási modell neve `paraphrase-multilingual-mpnet-base-v2` volt. A válaszadó modell az indításkor megadható paraméterként szerepelt.

Ez közelebb vitt a személyre szabott tudástár céljához: a rendszernek a saját dokumentumaimból kellett dolgoznia. A hitelességet azonban továbbra is az dönti el, hogy az állítás valóban következik-e az idézett forrásból.

### A szkennelt dokumentumok miatt OCR-rel egészítettem ki a kérést

Az első változat után felismertem, hogy egyes PDF-ek nem kinyerhető szöveget, hanem beszkennelt oldalképeket tartalmaznak. A Claude már az első válaszában felhívta a figyelmet erre a korlátra. A következő promptban kértem a bővítést:

```text
Ok but some of the PDF files do not contain text but images so they need
to use OCR before teaching. Modify this program accordingly.
```

A Claude leírása szerint a módosított program oldalanként ellenőrizte a kinyert szöveget. Ha az húsz karakternél rövidebb volt, az oldalt képpé alakította, majd magyar nyelvű Tesseract OCR-rel dolgozta fel. Az így kapott szövegrészletek és hivatkozások `[OCR]` jelölést kaptak.

Ez a jelölés hasznos volt a tervezett ellenőrizhetőség szempontjából: megmutatta, ha egy válasz gépi karakterfelismeréssel előállított szövegre támaszkodik. A rövid szövegre építő felismerés ugyanakkor egyszerű heurisztika; önmagában nem garantálja minden problémás oldal felismerését.

A leírás szerint hiányzó OCR-eszközök esetén a program figyelmeztetett a kihagyott oldalakra. Egy következő ellenőrzésnél ezért a feldolgozási naplót is áttekinteném: a program sikeres elindulása még nem jelenti automatikusan az összes oldal sikeres beolvasását.

### A szoftver működött, a válaszminőség elmaradt a várakozástól

A telepítés és a többórás előfeldolgozás után valóban eljutottam az interaktív kérdezésig. Ez kézzelfogható eredmény: a Claude olyan programot generált, amelyet a dokumentált függőségekkel futtatni tudtam, és amely a dokumentumtárhoz kapcsolódó válaszokat adott.

A kérdéseimre azonban nem kaptam kellően egzakt válaszokat. A hivatkozott dokumentumokban voltak kapcsolódó témák és kifejezések, de a kapcsolat sokszor laza maradt. Ebből még nem állapítható meg, melyik feldolgozási lépés okozta az eltérést.

| Lehetséges ok | Hogyan különíteném el? |
| --- | --- |
| A dokumentumtár nem tartalmazza a keresett választ. | Kézzel megkeresném a választ, és összeállítanék néhány biztosan megválaszolható mintakérdést. |
| A szükséges szöveg kimaradt vagy hibásan került be. | Összevetném a forrásoldalt a kinyert, illetve OCR-rel előállított szöveggel. |
| A keresés csak témájában hasonló részleteket talált. | Megnézném, milyen szövegrészleteket kapott ténylegesen a válaszadó modell. |
| A modell megkapta a megfelelő részletet, mégsem válaszolt pontosan. | Ugyanazt a kérdést ugyanazzal a forrásszöveggel több válaszadó modellel is kipróbálnám. |

Ezek vizsgálati lehetőségek, nem már igazolt hibák. Különösen fontos nyitott kérdés, hogy az általam keresett válaszok egyáltalán szerepeltek-e a feldolgozott anyagban. Ha nem, akkor a helyes működés az információhiány jelzése lenne. Egy pusztán témába vágó hivatkozás nem helyettesíti a választ alátámasztó szövegrészletet.

### A modellválasztást külön feladattá tenném

A paraméterezhető modellhasználatot megtartanám. Egy következő körben azonban külön promptban vizsgálnám az alkalmasságot, magyar mintadokumentumokkal, a belőlük megválaszolható kérdésekkel és az elvárt válaszhelyekkel. A rendelkezésre álló hardvert is megadnám, hogy a javasolt megoldások futtathatók legyenek.

Az alábbi egy új, továbbfejlesztési promptminta, nem a korábbi beszélgetés része:

```text
Help me select and evaluate models for a local Hungarian document Q&A
system. I will provide representative documents, questions answerable
from those documents, and the passages supporting the expected answers.
Ask about my hardware before recommending models.

Evaluate retrieval and answer generation separately. Compare candidate
models using the same documents and questions. Assess factual precision,
Hungarian language quality, citation support, runtime and memory use.
Include questions that the supplied documents cannot answer: the system
should state that the evidence is insufficient instead of guessing.
```

Így a választást ellenőrizhető példákhoz kötném. A tesztben a helyes válasz mellett az is számítana, hogy a hivatkozott oldal valóban alátámasztja-e az állítást.

### Tartós, inkrementális és folytatható feldolgozást kérnék

A többórás előfeldolgozás miatt fontos elvárásom, hogy az eredmény megmaradjon, és később ne kelljen mindent elölről kezdeni. A következő futás használja a már elkészült adatokat, a megszakadt feldolgozás pedig a hátralévő fájlokkal folytatódjon.

A csatolt párbeszédben a Claude már az első változatnál azt állította, hogy a program a PDF-ek mellett egy `.rag_index` könyvtárban tárolja az indexet, és újraindításkor csak az új vagy módosult fájlokat dolgozza fel, de a valóságban azt tapasztaltam, hogy új indításkor is újra feldolgozza a dokumentumokat, így ez a funkció nem működik teljesértékűen. Egy jövőbeni promptban erre nagyobb hangsúlyt fektetnék.

A továbbfejlesztésnél azt kérném, hogy a program tartson nyilván fájlonkénti feldolgozási állapotot, a sikeres eredményeket menet közben mentse, és újraindításkor azonosítsa a hiányzó vagy félbemaradt munkát. Ezt szándékos megszakítással is kipróbálnám. Egy már elkészült index újrafelhasználása és egy félbemaradt indexelés megbízható folytatása két külön követelmény.

### Modellenként elkülönített adatokat és összehasonlítható próbákat szeretnék

A tárolt adatokat modellenként, illetve feldolgozási konfigurációnként elkülönítve kezelném, hogy több változat egymás mellett tesztelhető legyen. Minden változathoz rögzíteném, mely dokumentumokból, milyen OCR-, szövegdarabolási és modellbeállításokkal készült, valamint mely kérdésekre milyen válaszokat adott.

A megvalósításnál figyelembe venném a két modell eltérő szerepét. Ha csak a válaszadó modell változik, a megfelelő keresési index újrafelhasználható lehet. Más beágyazási modellhez viszont külön, azzal kompatibilis index szükséges. A cél az elkülönített, reprodukálható kísérletezés, az indokolatlan újrafeldolgozás elkerülésével.

Egy ezt összefoglaló, még ki nem próbált prompt:

```text
Make document processing persistent, incremental and resumable. Save
completed work during indexing, track each file's processing status,
and recover safely after interruption. Reuse compatible stored data on
later runs and process new, changed or unfinished files as needed.

Keep separate named experiment configurations and results for different
models. Record the embedding model, generation model, OCR settings and
chunking settings. Reuse a compatible index when only the generation
model changes, but never mix incompatible embeddings. Document how to
test interrupted processing and compare model outputs.
```

### Az eredmény értékelése

A Claude jó kiindulási alapot készített: a program telepíthető és futtatható volt, támogatta a dokumentumkönyvtár és a modell megadását, az OCR-rel bővített feldolgozást, valamint az interaktív kérdezést. A saját dokumentumokra épülő válaszadás alapfolyamata működött.

A megbízható, pontosan hivatkozható tudástár célja ugyanakkor még nem teljesült igazoltan. A továbblépéshez ismert válaszú kérdésekkel kell külön ellenőrizni a dokumentumfeldolgozást, a keresést és a válaszgenerálást. Az esettanulmány eredménye ezért egy használható fejlesztési alap, amelynek a minőségét még mérni és javítani kell.