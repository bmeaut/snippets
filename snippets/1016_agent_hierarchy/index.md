---
layout: default
codename: agent_hierarchy
title: VSCode agentek hierarchiájának bemutatása egy egyszerű játékon keresztül
tags: snippets mieset
authors: Völgyesi Soma
---

# VSCode agentek hierarchiájának bemutatása egy egyszerű játékon keresztül

Négy együttműködő VSCode agent segítségével írtam egy egyszerű, konzolos Sudoku játékot. Az hangsúly nem a játékon, hanem az egyes agentek meghatározott szerepkörén van.

## Tanulságok

* Érdemes először ChatGPT-vel megbeszélni, hogyan is néz ki egy ilyen agent struktúra és hogy milyen nyelvet érdemes választani egy egyszerű demonstrációhoz.
* A VSCode agenteknek szükségük van a 'pwsh' (vagyis PowerShell 7-nél újabb verziója) parancsra, amennyiben például fájlokat kell olvasniuk a projekt mappából. Ezt érdemes előre telepíteni, hogy ne ezzel menjen el több tízezer token, mire az MI rájön, hogy nem tudja megkerülni a problémát és megkér, hogy telepítsük a PowerShell-t.
* Érdemes kézzel létrehozni a projekt alap struktúráját (csak mappa szinten, üres forrásfájlokat nem kell), ezzel könnyebben tudnak dolgozni az agentek.

## A létrehozott (kézzel + agentek által) fájl struktúra
```
projekt/
├── .github/agents/
│   ├──board-worker.agent.md
│   ├──controller.agent.md
│   ├──solver-worker.agent.md
│   └── test-worker.agent.md
├── src/
│   ├── board/
│   ├── solver/
│   └── tests/
└── spec.md
```

Ahol:
| Fájl/könyvtár | Feladata |
| ------------- | -------- |
| .github/agents/ | Az agentek definiálása. Egy-egy fájlban meg kell adni az agent jogosultságait és feladatát |
| board/ | A táblához tartozó fájlok (típusok, validator) |
| solver/ | A megoldóhoz tartozó fájlok |
| tests/ | Az egyik agent által írt tesztek (összesen 37) |
| spec.md | A teljes projekt rövid specifikációja. Ezt olvassa el a controller agent és ez alapján osztja ki a feladatokat a worker agenteknek |

## A munkafolyamat tanulságos részletei

### A struktúra kialakítása, illetve hogyan kell nekiállni egy ilyen feladatnak

Először a VSCode-on kívül, ChatGPT-vel értekeztem arról, hogyan is kell pontosan elkezdeni egy ilyen feladatot.

```
VSCode-ban szeretnék létrehozni 4 Agent-et. 1 vezérlő agent és 3 worker. Íratni akarok velük egy egyszerű sudoku-t, a lényeg az agentek feladatmegosztásán van, nem magán a játékon. Milyen nyelven írassam velük a játékot, és egyáltalán hogy kell ezt az agent hierarchiát kialakítani?
```

Válasz:
1. Közös specifikáció egy spec.md fájlban.
2. Controller prompt: csak feladatokra bontson, ne kódoljon nagyot.
3. Worker promptok: egy-egy konkrét felelősség.

Ezen kívül ajánlott több nyelvet, de végső tippnek a TypeScript-et javasolta. Ezen kívül adott egy mappa struktúrát és részletezte az agentek szerepeit.

### Mit kell nekünk írni, mit az agenteknek

Az előző válaszban adott struktúrában több olyan fájl is szerepelt, amiről erősen gyanítottam, hogy nem kézzel kell írni, ezért rákérdeztem.

```
Ezek a fájlok közül mindet én írom kézzel? Vagy van ami generált?
```

Válasz:

| Fájl | Kézzel írjuk | Agent írja |
| ---- | ------------ | ---------- |
| .github/agents/*.agent.md | X |  |
| spec.md | X | |
| package.json | lehet | lehet | 
| src/**/*.ts | | X |

Ezen kívül megadta a *.agent.md fájlok szövegét.

### A *.agent.md fájlok szerkezete

Ezek a fájlok definiálnak egy "AI persona"-t. Az ilyen formában (és ugyan ilyen mappa struktúra alatt) definiált agentek-et ki lehet választani VSCode Agent módban.

A szerkezet fontosabb részei:
1. YAML header, benne: name (agent neve), description (rövid leírása), tools (jogosultságai, pl. execute commands)
2. Role: Az agent szerepének bővebb leírása, prompt szerűen egyes szám második személyben.
3. Rules: Esetleges megkötések az agenttel szemben, pl. a controller agent ne írjon nagy kódrészleteket, mert nem ez a dolga.
4. Egyéb, specifikusabb részletek, pl. controllerben az egyes worker agenteknek mi a szerepköre, ami alapján tud nekik feladatot kiosztani.

### A tényleges kódolás kezdete

Miután létrehoztam kézzel a projekt vázát, megnyitottam a mappát VSCode Agent Mode-ban, és az agentek közül kiválasztottam az általam definiált `contoller` agentet. Ennek adtam meg a következő prompt-ot:
```
Read spec.md and coordinate the Sudoku project.

Delegate implementation tasks to:

board-worker
solver-worker
test-worker
Do not implement major features directly.
```

Az agent elolvasta a spec.md fájlt és dolgozni kezdett. Valahányszor parancsot akart futtatni, mindig engedélyt kért és kiírta a futtatni kívánt parancsot, valamint ami az eredménye lesz.

Ezután szétválasztotta a feladatokat a három meghatározott agent képességei szerint, majd egymás után futtatta őket. Miután mindhárom elkészült, a controller agent elkészítette a program egységes belépési pontját és elvégezte a végső ellenőrzéseket.

## Korlátok

### Megfelelő részletességű specializáció

Jelen projektben ugyan egyszerű Sudoku játék volt a cél, de talán nem ennyire egyszerű. Az elkészült alkalmazás konzolon kirajzolja a játéktáblát, majd közvetlenül alatta a megoldását. Ez nyilván azért van, mert nem volt kellően részletes a specifikáció, például nem tértem ki benne arra, hogy milyen UI technológiát használjon az agent.

### Tokenek

Egy ingyenes github fiókot használva még egy ilyen végtelenül egyszerű projekt is felhasználta a havi tokenjeim több mint negyedét. Bonyolultabb alkalmazást előfizetés nélkül nem lehet így készíteni.
