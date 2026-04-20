---
layout: default
codename: RAGCourseMaterial
title: RAG pipeline laborgyakorlat generálása Claude-dal
tags: snippets mieset
authors: Domonkos Ádám
---

# RAG pipeline laborgyakorlat generálása Claude-dal

Claude segítségével egy 90 perces egyetemi laborgyakorlat teljes anyagát állítottam elő RAG pipeline és LangChain témakörben, mesterszakos hallgatók számára. A végeredmény: előlaboratóriumi szillabus, négyrészes Jupyter notebook feladatsorral, CLI és Streamlit alkalmazáscsonkok, automatizált tesztfájlok és oktatói megoldások. Az MI eszköz: Claude Sonnet 4.5 (claude.ai, ~99 üzenetváltás).

A modell által generált feladatsor használható volt és teljes mértékben megfelelt az elvártaknak. A dokumentumban felsorolt nehézségek és limitációk miatt azonban egy ez csak egy iránymutatás volt a feladatkidolgozás során mintsem egy kész, használható kimenet.

---

## Tanulságok

* A könyvtárverziót érdemes a legelső promptba belefoglalni (pl. `langchain>=0.2.0`). Enélkül a modell vegyes verziókból merít, és deprecated importokat generál. Az eltérő vagy hibás verzió nagyon gyakori hibaforrás volt.
* A kérdéseket és a szerkesztési kéréseket érdemes élesen szétválasztani. A „Don't modify anything, just tell me..." formula hatékonyan megakadályozta, hogy a modell kéretlen módosításokat végezzen, miközben egy kérdésre válaszol.
* Ha megakad a hibakeresés, érdemes kimondani, mi az, ami biztosan működik: „We know for sure that Ollama and vector store works correctly." Ez azonnal leszűkíti a keresési teret.
* Hosszú munkamenetben a Claude időnként egy korábbi állapotra „emlékezik" vissza, nem a legutóbbira. Ha elhúzódó hibakeresésnél elakad a folyamat, érdemes teljes resettel újraindítani: csatolni a fájl aktuális verzióját, és tiszta utasításlistával folytatni.
* A Claude alapértelmezés szerint bőkezűen magyaráz, ez oktatási szövegekben különösen szembetűnő. A hintek majdnem teljes megoldások lettek, a válaszok pedig belső gondolkodást is tartalmazták. Ezt érdemes explicit utasítással visszafogni, de hosszabb kontextusablakoknál hajlamos ezt elfelejteni.
* Elnevezési konvenciót érdemes a munkamenet elején rögzíteni. A tesztfájl és a notebook külön iterációs körökben születtek, ezért eltérő változóneveket használtak (`similarity_1_2` vs. `sim_cat_feline`), ami teszthibákat okozott.
* A statikus átnézés nem helyettesíti az éles futtatást. Rengeteg futásidejű hibát kellett javítani, ami különösen feltűnő volt a kézi kódolással való összehasonlításkor. 

---

## Kimenet

A generált fájlok:

| Fájl | Tartalom |
|------|----------|
| `RAG_Lab_Syllabus.md` | Feladatokat és tananyagot bemutató dokumentum |
| `RAG_Lab_Notebook.ipynb` | Fő feladatsor |
| `rag_cli_exercise.py` | CLI alkalmazás |
| `rag_cli_solution.py` | CLI megoldás |
| `rag_streamlit_exercise.py` | Streamlit alkalmazás |
| `rag_streamlit_solution.py` | Streamlit megoldás |
| `test_rag_lab.py` | pytest tesztcsomag az exportált notebookhoz |

A labor felépítése:

| Rész | Cím | Időkeret |
|------|-----|----------|
| 1. rész | Vektortárak és FAISS | 25 perc |
| 2. rész | RAG pipeline nulláról | 25 perc |
| 3. rész | LangChain integráció | 25 perc |
| 4. rész | Alkalmazásfejlesztés (CLI + Streamlit) | 15 perc |

---

## A munkafolyamat tanulságos részletei

### Téma- és keretmeghatározás

A munkamenet egy tág kéréssel indult: tervezzük meg a labor témaköreit, javasoljunk formátumot, és döntsünk a PyTorch vs. TensorFlow kérdésben.

```
I want to create a 90 minute long university laboratory about RAG pipelines and Langchain.
They will have a separate lecture before the class so they will have a basic understanding
of the topic, but I would like to create a syllabus that contains the most important
information in a very compact format. After the practice they should fully understand RAGs
and I would add vector databases too as they are a crucial part of the technology.

Let's collect the main topics and parts we want to teach at the laboratory then find an
interesting form for the laboratory exercise (like jupyter notebook, database inspector,
python scripts and so on...)

We want to use PyTorch or Tensorflow, which one do you recommend?

Ask your clarification questions to plan the initial topic and form.
When everything is set we can create the actual exercise
```

A Claude tisztázó kérdéseket tett fel a hallgatók szintjéről, GPU-elérhetőségről és pedagógiai megközelítésről. Kiderült, hogy sem PyTorch, sem TensorFlow nem szükséges – a SentenceTransformers CPU-n is fut nehéz ML-keretrendszer nélkül. A válaszok rögzítették a főbb korlátokat: mesterszakos hallgatók, laptopok (GPU nélkül), ingyenes, helyi eszközök, nulláról-építős megközelítés.

### Laborszerkezet átalakítása

A Claude ötrészes struktúrát javasolt, amelynek első blokkja (15 perc, RAG-összetevők bemutatása) a 90 percen belül szerepelt volna.

A javasolt tematika nem fedett le elég nagy témakört, így manuális át kellett struktúrálnom a javasolt kimenetet. Az elméleti bevezető kikerült az előlaboratóriumi szilabuszba, a vektortárak önálló témává váltak. Emellett szükséges volt a témakörök további szűkítése is, hogy valóban csak a tananyagra vontakozó feladatok jelenjenek meg.

### Notebook-kérések az első verzió után

Az első notebook-verzió visszaolvasása után tömör, konkrét visszajelzésekkel javítottam a feladatsort:

```
Awesome, just a few feedbacks about the returned ipynb file:
1. Is that possible to include the requirements in the pylab itself? I want to make sure
   students can find all required tools and softwares at the begginning of the file
2. I would like to manually download the wikipedia data source, do not use a library for
   that. Manually load the dataset (and maybe we can show the automatic easy way after that)
3. Import the required packages in the specific code sections (at first usage)
4. Extract Tests to separate sections under code
5. Make hints less obvious. Do not tell the exact solution code
6. Remove all parts under "## 📊 Production Best Practices" line (including this one)
7. Add an 4. exercise that builds an interactive QA interface with CLI or Streamlit
```

### A kérdések és szerkesztések szétválasztása

Sokszor egyértelműen jeleznem kellett, hogy csak kérdezek, nem kérek módosítást, ugyanis sokszor egy kérdésre is elkezdett módosításokat végrehajtani a modell:

```
You don't have to modify any files, just return the required step for the manual dataset
downloading and reading. Users should visit the url to the huggingface dataset,
download it manually and read it.
```

Ez a formula hatékonyan megakadályozza a kéretlen fájlmódosításokat. Hasonló minta ismétlődik a hibakeresési körökben is: „Don't modify anything, just tell me what to fix."

### Skálázás és dimenziószámítás

```
Modify the ipynb file to use all articles from the dataset, but add a warning to tasks
that take more than 10 secs.
Also change the dimension calculation to a sub exercise with option B
(embedding_model.get_sentence_embedding_dimension())
```

A 100 cikkre korlátozott feldolgozás helyett az összes cikk bekerült, figyelmeztetésekkel. A hardcoded `384` dimenziószám helyett a hallgatónak magának kell meghívnia a `get_sentence_embedding_dimension()` metódust.

### Szöveges átnézés és futtatási hibák

```
Deeply analyse the attached file. Check if everything is correct and both grammatically
both in professional AI terms. Also check if it teaches properly RAG for students.
Give me a feedback about the main issues.
```

Amikor egy használható, közel helyes notebook fájlt kaptam, mindig futtattam rajta egy külön ellenőrző feladatot, hogy kiderüljenek az esetleges hibák. Tapasztalataim szerint ezek az ellenőrzések nagyon hasznosak és fel tudják deríteni a hallucinációból és az elavult információk felhasználásából eredő kritikus hibákat.

### Teljes reset és újraindítás

Miután a hibakeresés túltelitett kontextus felett zajlott, teljes resettel, akár új kontextus-ablak nyitásával indítottam újra a feladatot:

```
Forget everything we discussed. Now I attached the final ipynb file which contains
the final exercises for students. You have to add/modify a few things:
1. Add some explanations and context to the parts and exercises where needed.
   (just an example the benefits of langchain after they implemented it manually)
2. Add proper test cases
3. There are some deprecated function calls either in the exercises and the commented
   solution sections. Replace them with the proper usage.

Before you start working, analyse deeply the file I attached and create a step by step
plan for the changes. Include every step in the plan. Also do not use any emoji in the
descriptions.
```

A legújabb fájl csatolásával és tiszta utasításlistával az eredmény sokkal koherensebb lett, mint az addigi inkrementális javítgatással.

### Automatizált tesztelés és változónév-ütközések

```
Don't modify anything, just tell me what to fix. I copied all solutions to the python
file, but two tests are failed:

  Test 1.3: ERROR - name 'similarity_1_2' is not defined
  Test 1.5: FAILED - Expected 2 results, got 1
```

A tesztfájl és a notebook más munkamenet-körökben készültek, eltérő névkonvenciókkal. A tesztfájl `similarity_1_2`-t várt, a notebookban `sim_cat_feline` állt. Emellett két finomabb hiba is előkerült:

- A FAISS `search()` hívás `(n_queries, k)` alakú 2D tömböt ad vissza, de a tesztkód nem indexelt (`distances[0]`), ami `'int' object is not subscriptable` hibát okozott.
- A koszinuszegyezés self-similarity vizsgálatánál az `assert 0.99 < self_sim <= 1.0` feltétel megbukott, mert a float32 kerekítési hiba miatt az érték `1.0000001192092896` lett. A javítás: `pytest.approx` vagy `<= 1.001` felső határ.

---

## Korlátok

### Deprecated LangChain importok

A LangChain 0.0.x, 0.1.x és 0.2.x verzióiban az importútvonalak jelentősen változtak. A Claude következetesen a régi elérési utakat generálta:

```python
# Claude által generált – deprecated a LangChain 0.1.0 óta
from langchain.llms.base import LLM
from langchain.chains import RetrievalQA

# Helyes a LangChain >= 0.1.0-tól
from langchain_core.language_models.llms import LLM
```

A `Chain.__call__` metódus szintén deprecated a 0.1.0 óta, az `.invoke()` javára. A generált megoldásfájlok `chain({"question": ...})` formát használtak, ami újabb telepítésen deprecation-figyelmeztetést adott. A Claude csak akkor jelezte, amikor explicit bemásoltam a warningokat.

Az egymással összeütköző kulcsok (`"query"` vs. `"question"`) szintén ebből erednek: a `RetrievalQA` és a `ConversationalRetrievalChain` más bemeneti kulcsot vár, de a Claude az egyiket a másik helyett használta.

### Nyelvezet

A generált feladatkiírások és magyarázatok nem hatottak természetesnek és egyértelműnek és ezeket különböző promptokkal sem sikerült elérnem, így végül kézzel írtam meg őket, melyek ellenőrzésére és javítására már újra a Claude modellt használtam

### Inkonzisztencia

Mivel komplex, több fájlból álló feladatstruktúrát határoztam meg, a modell által generált kód részletek hibás referenciákat és inkonzisztens elnevezéseket és hivatkozásokat tartalmazott. Sok esetben az eltérő verziókezelés miatt, teljesen más implementációt készítettem a végső feladatsorhoz.

### Felesleges magyarázat

A Claude az oktatási szövegekben alapértelmezésként bőségesen magyaráz. Ez két helyen is problémaként jelent meg:

**Feladatcellákban:** a hintek szinte-megoldásokká váltak, egy korai verzió például:

```python
# TODO: Create a FAISS index
# Hint: Use faiss.IndexFlatL2(dimension) where dimension=384
# Then use index.add(np.array(embeddings, dtype=np.float32))
```

Ez nem volt megfelelő a laborfeladatokhoz, így kézzel a következőre módosítottam:

```python
# TODO: Hozz létre egy sík L2 FAISS indexet a megfelelő dimenziószámmal,
#       és add hozzá az embeddingeket.
#       Nézd meg a FAISS dokumentációban az IndexFlatL2 osztályt.
```
