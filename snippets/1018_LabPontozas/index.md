---
layout: default
codename: LabPontozas
title: Egyetemi laborfeladatok AI-alapú értékelése Claude segítségével
tags: snippets mieset
authors: Domonkos Ádám
---

# Egyetemi laborfeladatok AI-alapú értékelése Claude segítségével

Claude Sonnet 4.6-tal három egyetemi laborfeladat értékelését automatizáltam párhuzamosan futó AI-ügynökökkel, a Claude Code CLI használatával. A laborok mesterszakos hallgatók számára készültek, a BME villamosmérnöki képzéséhez kapcsolódó AI/MLOps témákban. Összesen 64 beadandót értékeltem ki, a teljes folyamat nagyjából 30 percet vett igénybe. Az AI által adott pontszámok 81%-ban pontosan megegyeztek az emberi értékelő eredményeivel.

---

## A laborfeladatok

Mindhárom labor egy összetettebb AI/MLOps témakört dolgozott fel, különféle programozási és gyakorlati feladatokkal.

| Labor | Témakör | Max pont | Beadások száma |
|-------|---------|----------|----------------|
| **MLOps Lab** | FastAPI REST API + Docker + SQLite + Streamlit + szemantikus cache | 20 | 17 |
| **Local LLM Lab** | Lokális LLM-ek (Ollama/Gemini) + LangChain + Streamlit chatbot | 20 | 23 |
| **RAG Lab** | FAISS vektortár + RAG pipeline + LangChain + CLI/Streamlit alkalmazás | 20 | 24 |

A beadandók Python-alapúak voltak, és Jupyter notebookokat, önálló scripteket, valamint interaktív alkalmazásokat is tartalmaztak.

---

## Az értékelési folyamat

Az értékeléshez a **Claude Code CLI-t** és a **Claude Sonnet 4.6** modellt használtam. Minden laborhoz külön munkamenet tartozott, és laboronként mindössze néhány üzenetváltásra volt szükség:

1. Az értékelési szempontrendszer, a mintamegoldás és a beadandók elérési útjának megadása
2. Néhány kisebb pontosítás (például kerekítési szabályok vagy hiányzó fájlok kezelése)
3. Az eredményfájl formátumának véglegesítése

A kezdeti prompt rendkívül egyszerű volt, különösebb prompt engineering nélkül:

```text
In this folder you can find an exercise folder that contains the laboratory
exercise that needed to be by students. In the solution folder you can find a
solution, but it is not required to follow the solution, the goal is just to
have a valid solution. In the results folder you can find all the submissions.
The folder name indicates the people's name. Also you can find an xlsx file
that contains the final point breakdown. Your task is to check all submissions
and evaluate them based on the point breakdown. Feel free to ask clarification
questions if needed.
```

Az AI-ügynökök párhuzamosan dolgoztak: minden beadandót külön ügynök elemzett közvetlenül a fájlrendszerről olvasva. Így akár 24 hallgató munkája is egyszerre feldolgozható volt.

A három labor teljes értékelése összesen körülbelül 30 perc alatt lefutott, míg ugyanez manuálisan több órás munkát jelentett. A folyamat a Claude Pro órakeretének nagyjából másfélszeresét használta fel, ami jól mutatja, hogy a párhuzamos feldolgozás jelentős kredithasználattal jár. Cserébe viszont drasztikusan csökkenti az értékeléshez szükséges időt.

Az eredmények egy strukturált Excel-fájlba kerültek, amely tartalmazta a részpontszámokat és az összesített eredményeket is.

---

## Eredmények

### Összesített statisztika

| Labor | Hallgatók | Pontos egyezés | AI > Emberi | Emberi > AI | Átlagos eltérés |
|-------|-----------|----------------|-------------|-------------|----------------|
| MLOps Lab | 17 | 16/17 (94%) | 0 | 1 | 0,06 pont |
| Local LLM Lab | 23 | 14/23 (61%) | 4 | 5 | 0,70 pont |
| RAG Lab | 24 | 22/24 (92%) | 0 | 2 | 0,17 pont |
| **Összesen** | **64** | **52/64 (81%)** | **4** | **8** | **0,33 pont** |

Az átlagos eltérés mindössze 0,33 pont volt 20 pontból. Az AI összesített átlagos eltérése −0,06 pontnak adódott, vagyis nem látszott sem túlzott szigor, sem túlzott engedékenység.

---

## Az eltérések okai

A különbségek többsége nem az AI hibájából fakadt, hanem abból, hogy az emberi értékelés nem mindig volt teljesen következetes.

### MLOps Lab

Egyetlen eltérés volt, az AI levont 1 pontot a hiányos streaming endpoint és a conversation endpoint hiánya miatt, míg az emberi értékelő ezt nem vette észre.

### Local LLM Lab

Itt jelentkezett a legtöbb eltérés. A labor egyik feladatában két választható megoldási ág szerepelt:

- **Option A:** lokális Ollama modellek összehasonlítása
- **Option B:** Gemini API használata

Az AI minden esetben ellenőrizte, hogy az adott opcióhoz tartozó kód valóban szerepel-e a beadásban. Ha a hallgató csak az egyik opciót oldotta meg, a másikra 0 pontot adott. Ez megfelelt az eredeti pontozási logikának.

Az emberi értékelő ezzel szemben sokszor egyszerűen figyelmen kívül hagyta a nem választott opciót, ezért több esetben eltérő pontszám született.

A Streamlit chatbot feladatnál az AI gyakran szigorúbb volt. Mivel kizárólag a forráskód alapján értékelt, nem tudta ténylegesen futtatni az alkalmazást. Az emberi értékelő viszont működés közben is megnézte a chatbotot, és több részleges megoldást is elfogadott.

### RAG Lab

Két jelentősebb eltérés fordult elő.

- Az egyik beadott munkánál az AI összesen 2,5 pontot vont le a FAISS-keresés, a retrieval függvény és a RAG pipeline hiányosságai miatt, míg az emberi értékelő inkább a végső eredmény alapján pontozott.
- Egy másik esetben az AI 2 pontot vont le a CLI és Streamlit alkalmazás hiányosságai miatt, amelyeket az emberi értékelő teljes értékűnek fogadott el a beadott képernyőképek alapján.

---

## Tanulságok

### Az AI-alapú értékelés gyors és jól skálázható

Párhuzamos feldolgozás mellett az értékelési idő alig függ a beadandók számától. Egy nagyobb hallgatói csoport értékelése így jelentősen felgyorsítható.

### A kód olvasása nem helyettesíti a futtatást

Az AI kizárólag a forráskód alapján dolgozott, ezért az interaktív vagy vizuális feladatoknál — például Streamlit alkalmazások esetében, óvatosabb pontozást adott. Az ilyen feladatoknál továbbra is fontos az emberi ellenőrzés.

### Az opcionális feladatok külön figyelmet igényelnek

A legtöbb eltérés az opcionális feladatrészek értelmezéséből adódott. Ha a prompt már az elején egyértelműen rögzíti az értékelési szabályokat, ezek az eltérések nagyrészt elkerülhetők lettek volna.

### Az AI következetesebben értékelt

Az emberi értékelés során több kisebb hiányosság egyszerűen elsiklott a figyelem elől, míg az AI minden beadandót ugyanazon szabályrendszer szerint vizsgált végig.

### A pontozási séma minősége kulcsfontosságú

Az AI teljesítménye erősen függött attól, mennyire egyértelműek az elvárások. A jól definiált laboroknál 90% feletti egyezés született, míg a több értelmezési lehetőséget tartalmazó feladatoknál jóval nagyobb lett a szórás.

### A gyorsaság ára a magasabb kreditfelhasználás

A teljes folyamat jelentős kreditmennyiséget használt fel, ugyanakkor órák helyett percek alatt lezajlott. A párhuzamos futtatás lényege pontosan ez: több erőforrásért cserébe drasztikusan rövidebb futási idő.

---

## Összefoglalás

A három labor alapján az AI-alapú értékelés összességében 81%-os pontossággal reprodukálta az emberi értékelést. Az eltérések többsége nem az AI hibájából, hanem az emberi értékelés következetlenségeiből adódott.

A módszer különösen jól működik olyan feladatoknál, ahol:

- a megoldás kód alapján ellenőrizhető,
- az értékelési szempontok egyértelműek,
- a feladat lineáris felépítésű.

Az interaktív vagy futtatást igénylő részeknél azonban továbbra is érdemes emberi ellenőrzést bevonni az értékelési folyamatba.