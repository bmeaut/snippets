---
layout: default
codename: AgentSkills
title: "Agent Skillek bemutatása"
tags: snippets mieset
authors: Domonkos Ádám
---

# Agent Skillek bemutatása

A skill egy mappa, benne egy `SKILL.md` fájllal, mely tartalmaz egy részletes feladatleírást (promptot) az adott specifikus feladathoz. Az agent induláskor csak a fájl fejlécét látja, és amikor a feladat illeszkedik rá, beolvassa a teljes tartalmat.

---

## Mi az a skill?

A `SKILL.md` elején egy YAML fejléc áll két kötelező mezővel:

```markdown
---
name: pdf-processing
description: Szöveg és táblázatok kinyerése PDF-ekből, űrlapok kitöltése, dokumentumok összefűzése. Akkor használd, ha PDF fájlokkal dolgozol, vagy a felhasználó űrlapokat, dokumentumkinyerést említ.
---

# PDF feldolgozás
...
```

A fejléc alatt sima markdown: munkafolyamat, jó gyakorlatok, példák. A mappába kerülhetnek még szkriptek, referenciafájlok és sablonok is.

### A három betöltési szint

A lényeg a fokozatos feltárás (progressive disclosure). A skill tartalma nem egyszerre kerül a kontextusba, hanem három lépcsőben.

| Szint | Mikor töltődik be | Költség | Tartalom |
|-------|-------------------|---------|----------|
| 1. Metaadat | Mindig, induláskor | ~100 token / skill | `name` és `description` |
| 2. Utasítások | Amikor a skill aktiválódik | 5k token alatt | A `SKILL.md` törzse |
| 3. Erőforrások | Igény szerint | Amíg nem kell, semmi | `references/`, `scripts/`, `assets/` |

Ez az, ami miatt a skill jobban használható, mint egy hosszú system prompt. 10 telepített skill 10 rövid leírást jelent a kontextusban, nem 10 teljes dokumentumot. A szkriptek egyáltalán nem kerülnek be, az ügynök lefuttatja őket bashből, és csak a kimenet foglal helyet.

A `name` mezőre van néhány megkötés, amit figyelembe kell venni:
- Legfeljebb 64 karakter lehet
- Csak kisbetűt, számot és kötőjelet tartalmazhat
- Ékezet nem lehet benne

### Prompt vagy skill?

A prompt egyszeri, a beszélgetés szintjén él. A skill újrahasznosítható, és magától aktiválódik. Ha ugyanazt az utasítást sokadjára kerül bemásolásra egy chatbe, akkor annak már skillnek kéne lennie.

A `description` mező dönti el, hogy a modell ránéz-e a skillre. Ebbe bele kell írni, hogy mit csinál és mikor kell használni. A gyakorlati tapasztalat az, hogy a modellek inkább alultriggerelnek, vagyis nem nyúlnak a skillhez, pedig kellene. Ezért érdemes a leírást kicsit túlmagyarázni, például a konkrét szavak és helyzetek felsorolásával, amiknél érdemes használni.

---

## Kész skillkészletek hozzáadása

Nem kell mindent a nulláról megírni, hasonlóan az általános programozásban használt könyvtárakhoz. A legtöbb gyakori feladatra van már karbantartott skill, sokat közülük maga a termék fejlesztőcsapata ad ki.

### Honnan érdemes válogatni

A [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) a legjobb kiindulópont. Több mint ezer skillt gyűjt össze, a hivatalos csapatok szerint csoportosítva: Stripe, Cloudflare, Vercel, Netlify, HashiCorp, Sentry, Hugging Face, Figma, Microsoft, OpenAI, Trail of Bits, Apollo GraphQL és még jó néhány. A lista kézzel válogatott, nem generált, ami látszik a minőségén.

### Dokumentumkezelés

Az [anthropics/skills](https://github.com/anthropics/skills) repóban vannak a `docx`, `pdf`, `pptx` és `xlsx` skillek. Ezek hajtják a claude.ai fájlkészítő funkcióját, tehát nem demók, hanem éles kódok. Ugyanitt található a specifikáció és egy üres sablon is.

Claude Code-ban plugin marketplace-ként vehető fel:

```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

Utána elég hivatkozni rá: „a PDF skillel szedd ki az űrlapmezőket ebből a fájlból".

### Kódolás és fejlesztői fegyelem

Az [obra/superpowers](https://github.com/obra/superpowers) nem egy szolgáltatáshoz ad tudást, hanem egy teljes fejlesztési módszertant kényszerít rá az agentre. Húsznál több összekapcsolható skillt tartalmaz: 
- brainstorming a specifikáció kicsikarására
- valódi red-green-refactor TDD
- szisztematikus hibakeresés
- git worktree-k
- ellenőrzés a session befejezése előtt

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

A skillek maguktól aktiválódnak, nevesíteni sem kell őket. Ha a modell elkezd funkciót írni, bejön a TDD skil,; ha hibát keres, a debugging skill.

Ebbe a kategóriába tartozik a TestMu AI közel ötven tesztelési skillje (pytest, Playwright, Cypress, JUnit, Selenium és társai) és a Trail of Bits biztonsági készlete is, statikus analízissel és Semgrep-szabályírással.

### Szolgáltatás-specifikus tudás

Itt van a legnagyobb valódi haszon. A modellek tudása a könyvtárak API-járól elavul, és magabiztosan generálnak deprecated hívásokat. Egy karbantartott skill ezt orvosolja.

A [google/skills](https://github.com/google/skills) repót a Cloud Next 2026-on jelentették be, mely 13 skillel indult: hét termékspecifikus (AlloyDB, BigQuery, Cloud Run, Cloud SQL, Firebase, Gemini API, GKE), három a Well-Architected Framework pillérei mentén (biztonság, megbízhatóság, költségoptimalizálás), három pedig általános jellegű, onboardingra és hálózati megfigyelhetőségre.

A Google Workspace oldalán a `gws-*` skillek fedik le a Drive-ot, Gmailt, Calendart, Sheetset, Docsot és Slidest, mindegyik a `gws` CLI köré építve.

### Rajzolás és diagramok

Az [Agents365-ai/drawio-skill](https://github.com/Agents365-ai/drawio-skill) jó példa arra, meddig lehet elmenni egyetlen skillel. Természetes nyelvből generál `.drawio` fájlt, tud UML, BPMN, C4 és hálózati preseteket, hozzáfér a draw.io tízezer hivatalos alakzatához, és exportál PNG-be, SVG-be, PDF-be.

A legérdekesebb része a visszacsatolás: a skill megnézi a saját PNG kimenetét, és automatikusan javítja az átfedéseket, a levágott feliratokat és az egymásra csúszott éleket. Mindezt MCP szerver nélkül, egyetlen `SKILL.md`-ből.

```
/plugin marketplace add Agents365-ai/365-skills
/plugin install drawio
```

Ugyanebből a családból jön a `mermaid`, `plantuml`, `excalidraw` és `tldraw` változat is. Érdemes tudatosan választani: a draw.io a precíz, exportálható ábrákhoz jó, a mermaid ahhoz, ami gitben él és markdownban renderel.

### Biztonsági kockázat

Skillt csak megbízható forrásból szabad telepíteni. Egy skill utasításokat és futtatható kódot ad az ügynöknek, tehát ugyanaz a kockázati kategória, mint egy szoftvertelepítés.

---

## Saját skill írása

A modellek által generált szövegek nehezebben olvasható hosszuk és természetellenes megfogalmazásuk miatt. Túl sok gondolatjel, mindig hármas felsorolás, „nem csak X, hanem Y" szerkezetek, és a végén egy összefoglaló. Ez a skill ezt próbálja meg javítani.

Jó első skillnek, mert nincs benne szkript, nincs függősége, és az eredménye azonnal látszik.

### A mappa

```
emberi-stilus/
└── SKILL.md
```

### A SKILL.md

```markdown
---
name: emberi-stilus
description: Szövegek írása és átírása természetes, emberi hangvételre. Akkor használd, ha a feladat blogposzt, hírlevél, e-mail, README, dokumentáció, közösségi poszt, jegyzet vagy bármilyen olvasónak szánt prózaszöveg írása, átírása vagy szerkesztése. Akkor is használd, ha a felhasználó azt kéri, hogy a szöveg ne hangozzon gépiesen, legyen természetesebb, olvashatóbb.
---

# Emberi hangvétel

Írj természetes emberi hangon. Igazodj a feladat formalitásához: egy jogi
feljegyzés maradjon hivatalos, egy baráti üzenet laza. Minden típusnál
kerüld viszont azokat a mintákat, amiktől a szöveg gépiesen hangzik.

## Szóhasználat

- Használj egyszerű szavakat: „használ" a „hasznosít" helyett, „segít"
  a „elősegít" helyett, „erről" a „ezzel kapcsolatban" helyett.
- Kerüld ezeket, hacsak nem tényleg ez a pontos szó: kulcsfontosságú,
  elengedhetetlen, zökkenőmentes, letisztult, izgalmas utazás, tárház,
  paletta, mérföldkő, forradalmasít, felszabadít, lehetőségek tárháza.
- Vágd ki a bevezető töltelékeket („Fontos megjegyezni, hogy", „A mai rohanó világban") és a kötőszó-vattát (továbbá, emellett, ezenfelül).

## Amit ne csinálj

- Ne legyen „nem csak X, hanem Y is" és „nem X, hanem Y" fordulat.
- Ne told túl a gondolatjelet. Először vessző, pont, zárójel. Néhány
  bekezdésenként legfeljebb egy gondolatjel.
- Ne erőltesd a hármas felsorolást. Kettő vagy négy elem is rendben van.
- Hagyd el a jelzőtáblákat („Először", „Másodszor", „Végül"), kivéve ha
  tényleg lépéssorozatról van szó.

## Álláspont és forma

- Foglalj állást. Ne tompítsd minden állításodat, és ne gyárts hamis
  kiegyensúlyozottságot.
- Legyél konkrét az általános helyett.
- Hagyd el a szép lezárást. Semmi „Összefoglalva", „Végezetül", és semmi
  önreflexív „Akár kezdő vagy, akár haladó...". Állj meg, amikor elmondtad,
  amit akartál.
- Címsort, félkövért és felsorolást csak akkor használj, ha a tartalom
  megkívánja.

## Ellenőrzés írás után

Olvasd vissza a szöveget, és nézd meg:

1. Van két egymás utáni bekezdés, amiben minden mondat hasonló hosszú?
2. Van a tiltólistás szavakból valamelyik, indoklás nélkül?
3. Van „nem csak..., hanem" szerkezet?
4. Az utolsó bekezdés összefoglal valamit, ami már elhangzott?

Ha bármelyikre igen a válasz, írd át azt a részt.
```

### Telepítés

Claude Code-ban a mappa bemásolása elég:

```bash
mkdir -p ~/.claude/skills
cp -r emberi-hangvetel ~/.claude/skills/
```

claude.ai-n zippeld be a mappát, és töltsd fel a Settings > Features alatt.

### Előtte és utána

Ugyanaz a kérés, egy laborfeladat leírásának megfogalmazása. Skill nélkül:

> A vektoradatbázisok kulcsfontosságú szerepet töltenek be a modern MI-rendszerek ökoszisztémájában. Ebben a feladatban egy izgalmas utazásra indulunk, amelynek során nem csupán megismerkedsz a FAISS könyvtárral, hanem gyakorlati tapasztalatot is szerzel a szemantikus keresés területén. A feladat elvégzése után zökkenőmentesen fogod tudni alkalmazni ezeket az eszközöket.

Skillel:

> Ebben a feladatban egy FAISS indexet építesz fel nulláról. Betöltöd a cikkeket, embeddinget készítesz belőlük, majd megnézed, milyen találatokat ad egy szabad szöveges kérdésre. A cél az, hogy a végén meg tudd magyarázni, miért ad más eredményt a koszinusz-hasonlóság és az L2-távolság.

A második rövidebb, és megmondja, mit kell tudni a végén. Az első csak hangulatot kelt.

### Amire figyelni kell

A `description` sokkal fontosabb, mint a törzs. Az első verzióm csak annyi volt, hogy „Szövegek írása emberi hangvételen", és gyakorlatilag soha nem ugrott be. A felsorolt konkrét formátumok (blogposzt, README, hírlevél) és a felhasználói megfogalmazások („ne hangozzon gépiesen") sokat javítottak a találati arányon.

A szabályokat indokolni is érdemes, nem csak felsorolni. Egy nyers tiltólista alól a modell kibújik szinonimákkal. Ha viszont leírod, hogy mitől gépies egy szöveg, általánosít.

Ha a skill hosszabbra nőne, tedd a példákat külön fájlba. Egy `references/peldak.md` és egy sor a `SKILL.md`-ben arról, hogy mikor kell beolvasni, pontosan az a harmadik szint, amiről a bevezetőben szó volt.

---

## Tanulságok

* A skill nem technológiai szempontból újít, csak egy mappa és egy markdown fájl. Az érték a fokozatos feltárásban van, vagyis abban, hogy sok tudást lehet elérhetővé tenni anélkül, hogy a kontextus tele lenne vele.
* A `description` a triggerelés egyetlen eszköze. Bele kell írni a konkrét szavakat és helyzeteket, amikre akítiválódnia kell, és inkább legyen bőbeszédű.
* A kész készletek közül a szolgáltatás-specifikusak adják a legtöbb előnyt. A deprecated API-hívások és az elavult importok a leggyakoribb hibaforrások, és pont ezeket orvosolja egy karbantartott, first-party skill.
* Skillt csak megbízható forrásból szabad telepíteni, és át kell nézni a szkripteket. Ugyanaz a kockázat, mint bármilyen szoftvertelepítésnél.
* Ha egy utasítás többedjére kerül bemásolásra be egy beszélgetésbe, át kell írni skillnek.
