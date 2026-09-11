---
layout: default
codename: LokalisLLMErtekelo
title: Lokális LLM-ügynök egyetemi beadandók értékelésére
tags: snippets mieset
authors: Domonkos Ádám
---

# Lokális LLM-ügynök egyetemi beadandók értékelésére

A célom egy lokális LLM-ügynök megépítése volt, amely egyetemi beadandókat értékel, egy saját gépen futó lokális Ollama-modellel. A fejlesztést Claude Code-dal, Opus 4.8 modellel végeztem. A kódolás elkezdése előtt a modellel először egy tervet készítettem, melyhez az agent online kutatására is szükség volt. A fejlesztés során több iteráción keresztül kellett módosítani a terven és implementáción, hiszen a valós adatokon való futtatás folyamatos újdonságokat és edge-caseket hozott be.

A fejlesztés eredményeként egy működő alkalmazás készült, de a tényleges futtatás nagyon időigényes volt, több éjszakán át futott, számos újraindítással.

---

## A feladat

Egy önálló Python CLI-szolgáltatás, amely a következőket kapja meg tetszőleges kombinációban:
- feladatkiírás
- pontozási táblázat
- mintamegoldás
- értékelendő munka, ami lehet teljes mappa, vagy egy konkrét fájl

Ha van megadott értékelési szempont (megoldás, vagy pontozási táblázat), akkor azt követi az értékelő agent, viszont ha nincs, akkor a beadandókból javasol egy értékelési sémát, és a futtatás előtt megerősítést kér.

---

## Használt modellek és technológiák

| Réteg | Választás |
|-------|-----------|
| Fejlesztőeszköz | Claude Code CLI (Opus 4.8) |
| Ügynökkeretrendszer | PydanticAI (strukturált kimenet: `NativeOutput`) |
| Modellfuttatás | Ollama (lokális), OpenAI-kompatibilis `/v1` végponton |
| Kipróbált modellek | `gemma3:12b` (kezdő), `llama3.1:8b` (végső), `qwen2.5`, `mistral:7b`, `llama3.2` |
| Környezet | `uv` + Python 3.12 |
| Fájlolvasás | `nbformat` (notebook), `PyMuPDF` (PDF), `tiktoken` (tokenszámlálás) |
| CLI | `typer` + `rich` |
| Hardver | Apple M3, 24 GB RAM |

---

## Tervezés és prompttechnikák

A munkamenet egyetlen részletes kéréssel indult, ahol még nem volt meghatározva, hogy milyen irányba induljon el a fejlesztés. Először egy általános, kutatási feladatot adtam, hogy kutasson az adott témakörben:

```text
I want to create a local LLM agent and skill that can evaluate student submissions:
1. Specification: The service gets either the raw exercise, a score board or a
solution or none and a folder of submissions or just a single solution. If there is
a solution and/or score board the agent should follow it. If there is none of them,
you can make them up. I think it can even ask clarification questions
2. Technical perspective: I want to have skills and agents with external tools. Also
I would like to try out Openrouter, openclaw, hermes or something like that. Let's do
a thorough online research as well to use the most modern approaches. I want to use a
local model for now.

Analyse the requirements and create the plan for the implementation.
Feel free to ask clarification questions
```

A tényleges specifikáció és implementációs terv előtt a konkrét bemenetekre és kimenetekre vonatkozó kérdéseket tett fel az agent:

```text
User answered Claude's questions:
  ⎿  · What form should this take? "Skill and agent" is ambiguous. → Standalone 
     Python service
     · OpenRouter is a cloud API router, which conflicts with "local model for 
     now." How do you want to handle the model backend? → Local Ollama only
     · What kinds of student submissions must it grade? This drives which tools 
     the agent needs. → Code (read-only), Written / text, Mixed / notebooks
```

Amikor eldőlt minden technikai jellemző, a következő pontosító kérdéseket tette fel a tervező agent a terv elkészítése előtt:

```text
User answered Claude's questions:
  ⎿  · How should the agent handle the case where NO spec/scoreboard/solution is
     provided? → Infer then confirm
     · What should the output look like? → Summary CSV, Markdown feedback 
     report, Structured JSON per student, Ask the user, but support all
     · How strict should grading determinism be? Local models vary run-to-run. →
     Single pass, keep it simple
```


### Hasznos minták, amiket használtam:

- **Tisztázó kérdések előre.** A modell rögtön több kérdést tett fel, és ezek érdemben alakították a tervet.
- **Plan mód.** Először csak tervet kértem, kód nélkül. Így a felépítést még egyszerűen és kevés tokennel lehetett módosítani.
- **Külön review agent.** Egy másik ügynökkel kritikusan átnézettem a tervet. Ez talált is egy kritikus hibát a tervben, a `gemma3:12b` modell nem tud tool-callingot.
- **Empirikus ellenőrzés a kutatás helyett.** A Claude nem hitte el vakon sem a kutatást, sem a review-t, a gépen élesben letesztelte, mely modellek támogatják a toolokat, és leellenőrizte a `pydantic-ai` verzióját. A review egy ponton tévedett is (rossz verziószámot állított), ezt így ki lehetett szűrni.

---

## Tervezési változtatások

A projekt lényege ez a rész volt, szinte minden valós adaton végzett futtatás új problémát hozott:

- **Tool-calling helyett `NativeOutput`.** Mivel a `gemma3:12b` Ollamán keresztül nem támogatta megbízhatóan a tool callingot, törlésre került az `@agent.tool` réteg, és json_schema-kényszerített strukturált kimenet lett helyette. Ez nem okozott problémát, hiszen minden bemenet előre ismert, így beadandónként egyetlen determinisztikus hívás megy ki.
- **`--strictness` flag.** Utólag hozzáadtam egy flaget, mellyel állítható a szigorúság/kedvesség egy skálán (`very_lenient` … `very_strict`), amely meghatározza, hogy mennyire pontos megoldás szükséges maximális eredmény eléréséhez.
- **LLM-es pontozási útmutató beolvasás → determinisztikus parser.** Az LLM a pontozási táblázatból téves kritériumokat hallucinált (pl. a notebook végi visszajelző-kérdésekből). Mivel a pontozási útmutatók jól strukturált Markdownok explicit `[N points]` zárójelekkel, ezeket egy regex-alapú parser 100%-osan, azonnal, modell-szórás nélkül fel tudja dolgozni. Az LLM-út csak tartalék maradt, hogy más formátumot is támogathasson.
- **Opcionális feladat levágása.** A modell a beadott feladatsorba ágyazott visszajelző-kérdőívre fókuszált a feladatok helyett, ezért ezt a szekciót értékelés előtt eltávolítom. A jelenlegi megoldás ugyanakkor továbbra sem tudja automatikusan megkülönböztetni a kötelező és szorgalmi feladatokat, ha ezt a pontozási útmutató nem jelöli egyértelműen.
- **`gemma3:12b` → `llama3.1:8b`.** A 24 GB RAM-mal rendelkező futtató számítógép nem bírta a 12B-t nagy kontextuson, a KV-cache túllépte a memóriát, a gép swappelt, és egy-egy beadandó 40+ percig eredmény nélkül futott. A kisebb 8B modellel viszont érzékelhető minőségromlás nélkül működött.
- **Inkrementális mentés.** Először csak a teljes mappa befejezése után kerültek mentésre az eredmények, így egy megszakítás mindent elvitt. Átalakítottam, hogy minden hallgató JSON/MD-je azonnal mentődjön.
- **Duplikált kritériumnevek egyértelműsítése.** A pontozási útmutatóban több szekció is használ azonos alnevet (pl. „Building and training the model” 3×). A név szerinti összepárosítás ütközött, ezért mindenki *ugyanazt* a pontszámot kapta. A parser mostantól a szülő-szekció nevével prefixeli a leveleket, így minden kritériumnév egyedi.

---

## A jó részek

- A terv + review-ügynök + empirikus ellenőrzés hármas még kódolás előtt megfogta a legnagyobb blokkolót (a tool-calling hiányát).
- A modell csak az egyes kritérium pontokat javasolja, de a végösszeget a saját kódunk számolja újra, nem bízunk a modell számolásában. A gyanús esetek (csonkolt/üres/túl nagy beadandó) `needs_review` jelzést kapnak, nem kapnak hamis pontszámot.
- A determinisztikus pontozási útmutató parser pontos, azonnali és 0 szórású, így nem bíztam LLM-re.
- Nem csak egyes pontszámokat néztem, hanem a pontszám-eloszlást is, ez segített észrevenni a duplikálódó név hibát, ami egyébként észrevétlen maradt volna.
- A modellréteg izolált, így egy későbbi felhős backend (OpenRouter) csak egy env-változó lenne, kódmódosítás nélkül.

---

## Problémák és korlátok

- **Lokális kismodellek megbízhatatlansága.** A 8–12B modellek hajlamosak eltérni a rubrictól: kitalálnak saját kritériumokat, vagy a notebookba ágyazott szövegre hivatkoznak. Ezt csak erős promptolással + előfeldolgozással + kódszintű validációval lehetett kordában tartani.
- **Memóriaplafon.** A 24 GB-os gép a nagyobb modelleket nagy kontextuson nem bírta, a swappelés miatt a futás beragadt. A gép többi alkalmazását be kellett zárni, hogy megbízhatóan fusson.
- **Nagyon lassú futás.** Egészséges esetben is 4–7,5 perc jutott egy beadandóra. A teljes készlet többórás volt, több éjszakai futással és sok újraindítással (memória-beragadás és tervezési hibák miatt).
- **Túl nagy fájlok.** Néhány beadandó (beágyazott kimenetekkel 30k+ token) még nagy kontextuson sem fért be, ezeket az eszköz helyesen kézi értékelésre jelölte, nem tippelt.

---

## Összefoglalás

Az eszköz jól működik, egy újrahasznosítható, lokális értékelő szolgáltatás lett belőle, amely beadandónként JSON-, Markdown- és CSV-kimenetet ad, specifikált vagy utólag meghatározott pontozási útmutató alapján. A tanulság viszont inkább az, hogy egy ilyen lokális pipeline-nál a modell csak az egyik tényező. A valódi korlátok a gép memóriája, a nagy beadandók, és a kismodellek rubric-követése voltak.

A megközelítés ott működik jól, ahol a beadandók nem túl nagyok, a pontozási séma gépi úton is kiolvasható, és a feladat kódból vagy szöveges fájlból egyértelműen ellenőrizhető. Minden más esetben, nagy és hosszú fájlok, kódprojektek, interaktív részek, továbbra is kell az emberi ellenőrzés. A futtatás időigénye miatt pedig ezen a hardveren ez inkább éjszakai batch-feladat, mint interaktív eszköz.
