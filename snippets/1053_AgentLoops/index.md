---
layout: default
codename: AgentLoops
title: "Agent loopok: inner loop, outer loop, planner és workerek"
tags: snippets mieset
authors: Domonkos Ádám
---

# Agent loopok: inner loop, outer loop, planner és workerek

Az agentic coding egyik új iránya, hogy az agent nem egyetlen beszélgetésen belül old meg egy feladatot, hanem órákig, akár napokig dolgozik rajta. Egy viszonylag egyszerű modell kap egy célt (pl.: kijavítani a hibás teszteket, feldolgozni egy ticketet, frissíteni egy függőséget), és a harness újra és újra elindítja, amíg egy külső ellenőrzés szerint el nem készül. Egy-egy iteráció önmagában lehet sikertelen. Az eredményt az ismétlés, a fájlokban megőrzött állapot és a megbízható ellenőrzés adja ki.

Ez az esettanulmány ezt a működést három egymásra épülő szinten mutatja be:

1. **Inner loop (agent loop).** Egy session, amelyben a modell toolokat hív, amíg kész nincs.
2. **Outer loop.** Az inner loop friss kontextussal újraindul, az állapot fájlokban él, és a tesztek döntik el, mikor van vége.
3. **Planner és workerek.** Egy planner részfeladatokra bontja a munkát, és mindegyikre külön loop indul.

A szintek egymásba ágyazódnak. Az outer loop inner loopokat futtat egymás után, a planner pedig részfeladatonként egy-egy outer loopot indít. Minden szint az alatta lévőt használja, és egy új réteget tesz köré.

A végén mindhárom szintet ugyanazon a feladaton próbálom ki egy lokálisan futó, 7 milliárd paraméteres modellel, hogy kiderüljön, mennyit tud kihozni a harness egy gyenge modellből.

---

## 1. Az inner loop

Az alapötlet egyszerű. A modell toolokat hív egy loopban, amíg a feladat el nem készül. A [Claude Agent SDK dokumentációja](https://code.claude.com/docs/en/agent-sdk/agent-loop) öt lépésre bontja. A modell megkapja a promptot, a system promptot és a toolok leírását, majd eldönti, mi a következő lépés. A harness lefuttatja a kért toolokat, és visszaírja az eredményt. Ez addig ismétlődik, amíg a modell tool hívás nélkül nem válaszol, és ezzel a loop véget ér. Egy kör (modellhívás, toolok futtatása, eredmény visszaírása) egy *turn*.

```python
messages = [system_prompt, user_request]
for turn in range(MAX_TURNS):
    reply = model.chat(messages, tools=TOOLS)
    messages.append(reply)
    if not reply.tool_calls:          # nincs több tool hívás: kész
        break
    for call in reply.tool_calls:
        result = execute(call.name, call.arguments)
        messages.append({"role": "tool", "content": result})
```

A modell maga semmit nem futtat. Csak strukturált szöveget generál arról, melyik toolt milyen argumentumokkal hívná meg. A végrehajtás, a jogosultságok ellenőrzése és a leállás eldöntése a harness dolga.

Ennek a szintnek két gyenge pontja van, és mindkettő a következő szintek motivációja.

**A leállásról a modell dönt.** A loop akkor ér véget, amikor a modell nem hív több toolt. Ez jelentheti azt, hogy tényleg végzett, de azt is, hogy leírta, mit *fog* csinálni, és elfelejtette meghívni a toolt, vagy egyszerűen tévesen hiszi, hogy kész. A lenti kísérletben a gyenge modellnél mindkettő előfordult.

**A kontextus folyamatosan nő.** Az LLM API-k állapotmentesek, ezért minden turnben a teljes eddigi beszélgetést újra el kell küldeni, az összes korábbi tool hívással és kimenettel együtt. Egy hosszú sessionben a kontextus megtelik régi, részben már érvénytelen információval, elavult fájltartalmakkal, sikertelen próbálkozásokkal és rossz hipotézisekkel. A kis modellek ebben gyorsan elvesznek. A Claude Code erre automatikus compactionnel reagál, ami segít, de a korai részletek egy része elveszhet.

---

## 2. Az outer loop

Az outer loop az inner loopot nem egyszer futtatja, hanem sokszor, egymás után. Minden iteráció:

- **friss kontextussal indul.** A modell nem emlékszik az előző próbálkozásra, így nem cipeli magával annak zavarodottságát sem.
- **fájlokból olvassa az állapotot.** A kód aktuális állapota, egy notes fájl az eddigi próbálkozásokról, a git előzmények és egy feladatlista viszi át a haladást iterációk között.
- **külső ellenőrzés alapján ér véget.** A loop akkor áll le, ha a tesztek átmennek (vagy elfogy a keret), nem akkor, ha a modell azt mondja, hogy kész.

A mintát a közösség „Ralph loopnak" is nevezi. Az Anthropic [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) című írása részletesen leírja, hogyan épül fel egy ilyen harness, ha a munka sok context windowon át, órákig vagy napokig tart. A kiindulópont ott is az, hogy minden új session emlékezet nélkül indul. A megoldás elemei:

- Egy **initializer agent** az első sessionben felállítja a környezetet. Létrehoz egy JSON feature-listát (a példájukban több mint 200 elemmel, mindegyik „failing" állapotban), egy `claude-progress.txt` naplót, egy `init.sh` indítószkriptet és a git repót. JSON-t használnak, mert a modell kisebb eséllyel írja át vagy rontja el, mint egy Markdown listát.
- A későbbi **coding agentek** minden sessiont ugyanúgy kezdenek. Ellenőrzik a munkakönyvtárat, elolvassák a naplót és a git logot, kiválasztják a legfontosabb nyitott feladatot, elindítják a környezetet, és egy gyors teszttel meggyőződnek róla, hogy nem törött állapotból indulnak.
- Minden session **commitolható, tiszta állapotban** ér véget, és frissíti a naplót.

Az írás hibatáblázata jól mutatja, mire kell az outer loopnak felkészülnie. Az agent idő előtt késznek nyilvánítja a projektet, félkész és dokumentálatlan állapotot hagy maga után, vagy csak unit tesztekkel ellenőriz, miközben a funkció a felhasználó szemével nézve nem működik. Mindháromra a válasz a harness oldalán van: részletes feladatlista, amit csak ellenőrzés után lehet kipipálni, kötelező commit és naplófrissítés, valamint end-to-end tesztelés.

### Mi indítja a loopot?

A Claude Code csapata a [Loop engineering: getting started with loops](https://claude.com/blog/getting-started-with-loops) című írásban négyféle loopot különít el aszerint, hogy mi indítja és mi állítja meg:

| Típus | Indítás | Leállás | Claude Code eszköz |
|-------|---------|---------|--------------------|
| Turn-based | Felhasználói prompt | A modell szerint kész | Egy sima session |
| Goal-based | Felhasználói prompt egy mérhető céllal | Teljesül a cél, vagy elfogy a turn limit | `/goal` |
| Time-based | Időzítés | A felhasználó leállítja, vagy elfogy a munka | `/loop`, `/schedule` |
| Proactive | Esemény vagy ütemezés, ember nélkül | A rutin addig fut, amíg ki nem kapcsolják | `/schedule` + `/goal` + skillek |

A proactive loopra az írás példája az, hogy a loop óránként végignéz egy Slack-csatornát hibajelentésekért, és addig nem áll meg, amíg minden talált jelentést nem osztályozott, javított és válaszolt meg. Ugyanez a minta működik egy Jira boarddal, egy CI-vel vagy egy függőségfrissítő bottal. A LangChain ezt [ambient agentnek](https://www.langchain.com/blog/introducing-ambient-agents) hívja: az agentet nem egy ember indítja egy chatablakban, hanem egy eseményfolyam, és egyszerre több eseményen is dolgozhat. Az emberi beavatkozásnak itt három formáját írják le: *notify* (az agent csak jelez), *question* (kérdez, ha bizonytalan) és *review* (a kockázatos lépést jóváhagyásra bemutatja).

Az indítás módja a loop működésén nem változtat. Az esettanulmány kísérletében a loopot egyszerűen kézzel indítom, egy rögzített feladattal.

### „Ellenőrzés"

Az outer loop annyit ér, amennyit az ellenőrzése. Ha a leállási feltétel megbízható (tesztek, típusellenőrzés, egy mért érték egy küszöb fölött), akkor a sikertelen iterációk nem rontanak semmit: a harness eldobja őket, és újrapróbálkozik. Ha nincs megbízható ellenőrzés, a több iteráció csak több költséget jelent, és a modell előbb-utóbb talál egy módot arra, hogy a feltétel teljesüljön anélkül, hogy a feladat elkészülne. A klasszikus példa a teszt átírása vagy törlése. Ezért kell a tesztfájlt a harness oldalán védeni, és ezért érdemes a visszalépést (a korábban átmenő tesztek elbukását) automatikusan visszavonni.

A LangChain [The Art of Loop Engineering](https://www.langchain.com/blog/the-art-of-loop-engineering) című cikke ugyanezt rétegekként írja le: az agent loop fölé egy verification loop kerül (egy értékelő vizsgálja a kimenetet, és hiba esetén visszajelzéssel újrapróbál), afölé egy event-driven loop (webhook vagy ütemezés indítja), legfelül pedig egy hill climbing loop, amely az éles futások trace-eiből a promptokat, toolokat és értékelőket javítja.

---

## 3. Planner és workerek

A következő lépés, hogy egy nagy feladatot ne egyetlen loop vigyen végig. Egy planner agent részfeladatokra bontja a munkát, és a harness minden részfeladatra külön agentet, akár külön outer loopot indít. A workerek csak a saját részfeladatukat látják, tiszta kontextussal indulnak, és csak egy rövid eredmény kerül vissza a plannerhez. A planner ellenőrzi az eredményeket, és ami nem sikerült, azt újratervezi.

Az Anthropic [multi-agent kutatórendszerében](https://www.anthropic.com/engineering/multi-agent-research-system) egy Claude Opus 4 lead agent és Claude Sonnet 4 subagentek 90,2%-kal jobban teljesítettek a belső értékelésükön, mint egy önálló Opus 4. Az ára a tokenfelhasználás: a mérésük szerint egy agent nagyjából 4-szer, egy multi-agent rendszer 15-ször annyi tokent használ, mint egy sima chat. Ugyanez az írás arra is figyelmeztet, hogy a legtöbb programozási feladatban kevesebb a valóban párhuzamosítható rész, mint egy kutatásban, és ahol a részfeladatok erősen függenek egymástól, ott a felbontás többet árt, mint használ.

Kis modelleknél a felbontásnak van egy külön előnye. Egy 7B-s modell hosszú kontextusban és többlépéses feladaton könnyen elveszik, de egy rövid, egyértelmű részfeladatot („csak a `mean` függvényt javítsd, hogy ez az egy teszt átmenjen") sokkal megbízhatóbban old meg. A felbontás egy nehéz feladatot több könnyűvé alakít. A planner az a szerep, ahová leginkább megéri erősebb modellt tenni, ahogy az Anthropic rendszere is nagyobb modellt használ lead agentként.

---

## Létező megoldások

Az outer loop és a planner–worker minta mára a legtöbb agentic coding eszközben elérhető:

| Eszköz | Mit ad | Lokális Ollama modellel |
|--------|--------|-------------------------|
| Claude Code | `/loop` (ismétlés időközönként), `/goal` (cél és turn limit), `/schedule` (felhős rutinok), subagentek | Igen, az Ollama v0.14 óta [Anthropic-kompatibilis API-t](https://docs.ollama.com/integrations/claude-code) ad (`ollama launch claude`) |
| Goose | Hivatalos [Ralph loop útmutató](https://goose-docs.ai/docs/tutorials/ralph-loop/), egy implementáló és egy másik, ellenőrző modellel | Igen |
| OpenCode | [opencode-ralph-rlm](https://github.com/doeixd/opencode-ralph-rlm) plugin, a loopot egy kis lokális modell futtatja | Igen |
| Általános Ralph szkriptek | Pl. [syuya2036/ralph-loop](https://github.com/syuya2036/ralph-loop), agenttől független wrapper feladatlistával és progress fájllal | Igen, bármilyen CLI agenttel |
| Aider | `--auto-test`: szerkesztés után lefuttatja a teszteket, és a hibákat visszaadja. Inkább rövid újrapróbálkozás, mint valódi outer loop | Igen |

A kísérlethez mégis saját, néhány száz soros harnesst írtam. Egyrészt így minden lépés látszik, ami egy `/goal` parancs mögött rejtve marad, másrészt a nagy eszközök hosszú system promptot és sok toolt adnak a modellnek. Az Ollama saját útmutatója legalább 32K kontextust és 20B körüli modelleket ajánl Claude Code-hoz. Egy 7B-s modell ott valószínűleg a keretrendszer miatt bukna el, nem a loop miatt.

---

## Előnyök

**A kitartás pótolja a képességet.** Egy gyenge modell egy-egy próbálkozása gyakran sikertelen, de ha van megbízható ellenőrzés, a sikertelen próbálkozások ára csak idő és token. A harness eldobja őket, és a jó lépések megmaradnak. Így olyan feladat is megoldható, ami egyetlen sessionben a modell képességei fölött van.

**A friss kontextus nem romlik.** A hosszú sessionök legnagyobb gyengesége, hogy a kontextus megtelik elavult és téves információval. Az outer loop ezt minden iterációban eldobja, és csak a fájlokban rögzített, ellenőrzött állapotot viszi tovább.

**Az állapot átlátható.** A haladás fájlokban, commitokban és egy notes fájlban él, nem egy modell belső állapotában. Egy megszakított futás ugyanonnan folytatható, és egy ember bármikor megnézheti, hol tart a munka.

**Felügyelet nélkül fut.** Egy ütemezett vagy eseményre induló loop éjszaka, hétvégén, napokon át dolgozhat, és az ember csak a végén, a review-nál kapcsolódik be.

---

## Hátrányok

**Megbízható ellenőrzés nélkül nem működik.** Az outer loop egyetlen erőssége az, hogy a tesztek döntenek. Ahol nincs gépileg ellenőrizhető kritérium (UX, szövegminőség, architekturális döntések), ott a loop vagy korán leáll, vagy vég nélkül fut.

**A rossz állapot is öröklődik.** Ha egy iteráció hibás kódot hagy maga után, és a harness ezt megtartja, a következő iteráció már a hibás alapról indul. A lenti kísérletben pontosan ez történt az outer loop első változatával. Checkpoint és visszaállítás nélkül a loop a saját hibáit halmozza.

**A hibák összeadódnak.** Ha egy lépés 95%-os valószínűséggel sikerül, 20 egymásra épülő lépés után már csak kb. 36% az esélye annak, hogy minden rendben ment. 90%-nál ez 12%. A loop ezt csak akkor ellensúlyozza, ha a rossz lépéseket észreveszi és visszavonja.

**Beragadás.** Egy kis modell turnökön és iterációkon át ismételheti ugyanazt a sikertelen hívást. Turn limit, iterációs és költségkorlát nélkül ez addig fut, amíg valaki észre nem veszi.

**Biztonság.** A loop valódi parancsokat futtat, felügyelet nélkül, órákig. A toolok kimenete (egy ticket szövege, egy weboldal, egy fájl) utasításként is értelmeződhet. Elszigetelt futtatókörnyezet, szűk jogosultságok és a kockázatos lépések előtti emberi jóváhagyás itt alapkövetelmény.

**A review szűk keresztmetszet.** Egy napokig futó loop rengeteg változtatást termel. Ha minden eredményt embernek kell átnéznie, a gyorsaság a review-nál elveszik.

### Idő és költség

Egy sessionön belül a költség négyzetesen nő. Minden turnben a teljes eddigi kontextus újra elmegy a modellnek.
Az outer loop ezt linearizálja. Mivel minden iteráció friss kontextussal indul, egy iteráció költsége korlátos, és `k` iteráció költsége nagyjából `k`-szorosa egy iterációénak. Egy hosszú feladatot sok rövid sessionre bontani ezért olcsóbb is, nem csak megbízhatóbb, mint egyetlen, egyre hosszabb sessionben végigvinni. A planner–worker minta ugyanezt teszi: sok kis kontextus egy nagy helyett.
De a loop sokszor fut. Egy napokig futó loop sok száz iterációt jelenthet. Egy 5 percenként ellenőrző time-based loop naponta 288-szor indul el, akkor is, ha nincs új munka. Ha minden ilyen indulás egy frontier modell hívásával kezdődik, a „nincs új ticket" válasz is pénzbe kerül. A bevett megoldás, hogy a triviális ellenőrzést (van-e új ticket, elbukott-e a CI) egy szkript végzi, és a modell csak akkor indul, ha van mit csinálni.
Az idő is összeadódik. A turnök és az iterációk szigorúan egymás után futnak, mert minden döntés az előző eredményére épül. Ha egy turn 10 másodperc, egy 8 turnös iteráció másfél perc, 50 iteráció több mint egy óra. A reasoning modellek turnönként további, láthatatlan tokeneket generálnak, ami az időt és a költséget is növeli.

A fentiekből következik, hogy a long-running loopokat nem frontier modell hajtja végig.

- **A szorzó minden iterációra érvényes.** Egy 4–10-szer olcsóbb modell az egész, akár napokig tartó futást teszi 4–10-szer olcsóbbá. A Fable 5.1 és a Haiku 4.5 között tízszeres a különbség, a kisebb modellek jellemzően gyorsabban is válaszolnak.
- **A legtöbb lépés rutin.** Egy fájl beolvasása, egy teszt lefuttatása vagy egy egysoros javítás nem igényel csúcsminőségű következtetést.
- **A drága modell a plannerhez kell.** A bevett minta, hogy egy erősebb modell bont és koordinál, a végrehajtást pedig olcsóbb modellek végzik. Az Anthropic kutatórendszere is Opus lead agentet és Sonnet subagenteket használ. A Claude Code blog szerint a modell és az effort szint megválasztása az egyik legnagyobb hatású költségtényező.
- **Lokális futtatás.** Egy saját gépen futó open-weight modellnek nincs hívásonkénti díja, az adat nem hagyja el a gépet, és egy hosszú loop költsége csak az áram és a gépidő.

Azonban a kis modellek pont abban gyengébbek, amire a loop épül, vagyis a következetes toolhasználatban, pontos argumentumok előállításában és annak felismerésében, hogy mikor van kész a munka. A helyes mérőszám ezért a *sikeres feladatonkénti* költség, nem a tokenár. Egy kis modell akkor olcsóbb, ha a harness pótolja, amit a modell nem tud: kevés, egyszerű toolt ad, egyértelmű hibaüzenetet küld vissza, checkpointot tart, korlátozza a turnöket, és a végeredményt maga ellenőrzi.

---

## Gyakorlati példa: három szint egy gyenge lokális modellel

A kérdés az, hogy egy gyenge, ingyenes, lokálisan futó modell eljut-e helyes eredményig pusztán azáltal, hogy a harness sokszor és okosan futtatja. A kísérlethez egy kb. 300 soros, csak a Python standard könyvtárára épülő harnesst írtam. Mindhárom szint ugyanazt a feladatot és ugyanazt a modellt kapja.

| Elem | Választás |
|------|-----------|
| Hardver | Apple M3, 24 GB RAM |
| Modellfuttatás | Ollama 0.33.3, `/api/chat` natív tool callinggal |
| Modell | `qwen2.5:7b-instruct` (4,7 GB) |
| Toolok | `read_file`, `replace_in_file`, `run_tests` |
| Korlátok | 1024 token válaszonként, 8 turn iterációnként (az 1. szinten 15), legfeljebb 10 iteráció |

### A feladat

A harness egy ideiglenes könyvtárba létrehoz egy `stats.py` modult három hibával és egy tesztfájlt négy teszttel:

```python
def mean(values):
    return sum(values) / (len(values) - 1)        # eggyel kevesebbel oszt

def median(values):
    n = len(values)                                # nem rendezi a listát
    mid = n // 2
    if n % 2 == 0:
        return (values[mid - 1] + values[mid]) / 2
    return values[mid]

def normalize(values):
    lo, hi = min(values), max(values)
    return [(v - lo) / hi for v in values]         # (hi - lo) helyett hi
```

A tesztfájlt a modell nem módosíthatja, ezt a harness kényszeríti ki. A futás végén a harness a modell állításától függetlenül maga futtatja le a teszteket.

### A harness három szintje

A három szint nem három külön megoldás, hanem egyetlen implementáció egymásba ágyazott rétegei. Minden réteg az alatta lévőt hívja:

```
planner (1 structured output hívás)            ← csak --mode hier
 └─ worker = egy outer loop részfeladatonként   ← --mode outer és hier
     └─ iteráció = egy inner loop session       ← mindhárom módban
         └─ turn = egy modellhívás + a kért toolok futtatása
```

`--mode outer` esetén egyetlen outer loop fut a teljes feladattal, `--mode hier` esetén a planner után minden részfeladatra egy-egy. A kísérletben a `--mode` kapcsoló tehát azt dönti el, melyik réteg a legfelső. A három futás egymástól független. Mindegyik új ideiglenes könyvtárban, ugyanabból a hibás `stats.py`-ból indul, és egyik sem folytatja a másik eredményét.

**Inner loop**: Ha a modell válasza üres, a harness visszajelez és folytatja. A válaszonkénti tokenkorlát pedig egy korábbi futásból jön, ahol a modell egyetlen válaszban közel 6 000 tokent generált, és kézzel kellett leállítani.

**Outer loop**: Minden iterációban új inner loopot indít. A kontextust a harness rakja össze a fájlokból. Bekerül a feladat, az aktuális tesztkimenet, a `stats.py` aktuális tartalma és a `NOTES.md`, amibe minden iteráció után a harness feljegyzi, mi történt.

**Planner és workerek**: Szinten a planner egyetlen structured output hívással részfeladatokra bontja a munkát. A harness a tervet is ellenőrzi, és csak a ténylegesen létező függvényekre vonatkozó feladatokat tartja meg. Minden részfeladatra külön outer loop indul, amelynek a célja csak az adott függvény tesztjeinek átmenése, a visszalépés figyelése viszont a teljes tesztkészletre vonatkozik.

### Eredmények

A táblázat minden sora egy teljes, önálló futás összesített adata, a legfelső rétegtől lefelé mindent beleszámolva. Az outer loop sora tehát nem az inner loop sorára épül rá. Az inner loop sora egy külön futás, az outer loop sorában pedig a saját hét inner loop sessionjének összege szerepel.

- **Végeredmény.** A futás végén a harness maga futtatja le a teszteket. Ez számít, nem az, amit a modell a saját munkájáról állít.
- **Inner loop sessionök.** Hányszor indult friss kontextusú inner loop a futás alatt.
- **Modellhívás.** Az összes Ollama hívás. Minden turn egy hívás, a planner módban ehhez jön a planner egy hívása.
- **Bemeneti token.** Az összes hívás prompt tokenjeinek összege. Mivel minden turnben a session teljes addigi kontextusa újra elmegy, ugyanaz a szöveg többször is beleszámít. Egy fizetős API is pontosan ezt számlázná.
- **Kimeneti token.** A modell által generált tokenek összege.
- **Idő.** A teljes futás ideje az indítástól a leállásig.

| Futás | Rétegek | Végeredmény | Inner loop sessionök | Modellhívás | Bemeneti token | Kimeneti token | Idő |
|-------|---------|-------------|---------------------:|------------:|---------------:|---------------:|----:|
| `--mode inner` | inner loop | 1/4 teszt | 1 | 11 | 21 422 | 2 278 | 3 perc |
| `--mode outer` | outer → inner | 4/4 teszt | 7 | 43 | 52 990 | 6 773 | 13 perc |
| `--mode hier` | planner → 3 worker (outer) → inner | 4/4 teszt | 5 | 30 | 38 853 | 5 600 | 13 perc |

Az outer loop hét sessionje 8, 3, 4, 8, 7, 8 és 5 turnből állt, ez adja a 43 hívást. A planner futásban a 30 hívás egy planner hívásból és a workerek 29 turnjéből jön össze. A `mean` worker egy sessiont futtatott (7 turn), a `median` worker négyet (5, 8, 6 és 3 turn), a `normalize` worker egyet sem, mert mire sorra került, a tesztjei már átmentek.

A kérdés tehát az, hogy melyik konfiguráció milyen áron jut el a 4/4-ig. Az inner loop azért volt a legolcsóbb, mert hamar feladta. Az outer és a planner futás költsége a sikertelen és visszavont iterációkat is tartalmazza, ez az ára annak, hogy a végén átmentek a tesztek. A planner futás azért lett olcsóbb az outer loopnál, mert kevesebb session kellett hozzá (5 a 7 helyett). Hívásonként nagyjából ugyanakkora kontextussal dolgozott, kb. 1 300 bemeneti tokennel, az outer loop kb. 1 230-cal.

Érdemes a hívásonkénti átlagot az inner loop futással is összevetni. Ott kb. 1 950 bemeneti token jutott egy hívásra, mert egyetlen session nőtt 11 turnön át. Az outer loopban ez kb. 1 230 volt, pedig ott minden iteráció promptja a teljes forrásfájlt, a tesztkimenetet és a notes fájlt is tartalmazza.

**Az 1. szinten** a modell beolvasta a fájlt, egyszerre három helyen módosított, és szintaktikai hibát hagyott. Egy részét kijavította, de utána hat turnön át olyan szövegrészeket próbált cserélni, amelyek nem voltak a fájlban, és hiányos argumentumokkal hívta a toolt. A 11. turnben kijelentette, hogy a `median` és a `normalize` már helyes, csak a tesztek buknak valamiért, és leállt. Ugyanez a modell a harness korábbi változataival, több futásban sem jutott 2/4 fölé.

**A 2. szinten** ugyanez a modell hét iteráció alatt megoldotta a feladatot. A haladás így alakult:

```
1. iteráció: kept, 1/4
2. iteráció: kept, 2/4
3. iteráció: kept, 3/4
4. iteráció: REVERTED (2/4 tests, previous best was 3/4)
5. iteráció: REVERTED (2/4 tests, previous best was 3/4)
6. iteráció: kept, 3/4
7. iteráció: kept, 4/4
```

Egyik iteráció sem volt különösebben jó. Az első a turn limit elérésével ért véget, közben kétszer szintaktikai hibát okozott, és négyszer hiányos argumentummal hívta a toolt. A negyedik és ötödik iteráció el is rontott egy már működő tesztet. A loop mégis előre haladt, mert minden iteráció az utolsó jó állapotból indult, és a rossz lépéseket a harness visszavonta. A notes fájl két bejegyzése, ahogy a harness a modell záró üzenetével együtt rögzítette, és ahogy a következő iteráció megkapta:

```
- Attempt 3: kept, 3/4 target tests pass. Agent said: Let's correct the `median`
  function directly in the `stats.py` file. I will modify the `median` function
  to handle both odd and even lengths correctly.
- Attempt 4: REVERTED (2/4 tests, previous best was 3/4). Agent said: (turn limit reached)
```

**A 3. szinten** a planner pontosan a három hibás függvényt adta vissza, mindegyikhez egy értelmes, egymondatos utasítással (pl. a `mean`-hez: „Change the divisor from (len(values) - 1) to len(values)"). A `mean` worker egy iteráció alatt végzett. A `median` workernek négy iteráció kellett, és a másodikban a harness egy `IndentationError`-t vont vissza. A `normalize` workernek nem maradt dolga, mert a `median` worker az utasítás ellenére azt is kijavította. A részfeladat határát a harness csak a promptban kérte, nem kényszerítette ki, és egy kis modell ezt nem tartja be.

---

## Tanulságok

* A long-running agentek három szintből épülnek fel. Az inner loop hajtja végre a lépéseket, az outer loop friss kontextussal újraindítja és tesztekkel ellenőrzi, a planner pedig kisebb, jobban kezelhető részekre bontja a munkát.
* Egy gyenge, 7B-s lokális modell egyetlen sessionben nem oldotta meg a feladatot, outer loopban és részfeladatokra bontva viszont igen. A kitartás pótolhatja a képességet, de csak megbízható ellenőrzés mellett.
* Az outer loop legfontosabb eleme a checkpoint. Ha a harness megtartja a törött állapotot, minden további iteráció a hibát örökli. A kísérletben egyetlen hiányzó feltétel miatt tíz iteráció ment el eredmény nélkül.
* Amit a harness nem kényszerít ki, azt egy kis modell nem tartja be. A részfeladat határát a promptban kértem, és a worker átlépte.
* A friss kontextusú iterációk költsége lineárisan nő, egyetlen hosszú session költsége négyzetesen. Long-running munkához sok rövid session olcsóbb és megbízhatóbb.
