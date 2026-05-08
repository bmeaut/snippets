---
layout: default
codename: n8n_basics
title: Email alapú dipterv feladatkiírás generátor n8n-ben, ChatGPT-vel
tags: snippets mieset
authors: Völgyesi Soma
---

# Email alapú dipterv feladatkiírás generátor n8n-ben, ChatGPT-vel

Docker, Node JS, n8n és ChatGPT segítségével létrehoztam egy diplomaterv sablon generátort. Az elkészült feladat: az alkalmazás előre configolt email címre vár egy neptun kód, cím, leírás hármast tartalmazó üzenetet, a neptun kód alapján Excel fájlból kikeresi a hallgató nevét és szakját, majd az adatokkal feltölti a diplomaterv sablont és visszaküldi azt.

## Tanulságok

* Az n8n workflow csak lokálisan hostolva ingyenes, ennek a felépítéséhez van is egy bemutató a hivatalos oldalukon, viszont az a tapasztalatom, hogy érdemes ettől eltérni és magunknak készíteni a docker volume-ot és container-t, ugyanis a Docker Desktop app-ban generáltak tényleges fájljait rendkívül körülményes utólag módosítani (márpedig erre többször is szükség volt).
* Érdemes két külön beszélgetést folytatni az MI-vel, egyet a feladat nagyobb lépéseinek megtárgyalásához (például: "Kész a bejövő emailben kapott adatok feldolgozása, hogyan keresünk ezek alapján az Excel dokumentumban?"), egyet pedig az egyes lépések során felmerülő apróbb kérdések részletezéséhez (például: "Hogyan lehet biztonságosan API key-t tárolni n8n-ben?").
* Nem mindent jó n8n-ben megvalósítani, mert egyes funkciók fizetősek és Function Node-ba nem lehet külső Node modulokat importálni. Helyette használható egy másik docker konténerben futó Node JS szerver, ez egy docker compose fájllal összefogható az n8n konténerével.
* A Word dokumentum sablonban érdemes egyedi placeholdereket használni és ezt a behelyettesítést végző kódban is specifikálni, mert a Word néha nem úgy tördeli a sorokat, ahogy kellene, ezért a standard ' {{ }} ' placeholder-t nem feltétlenül találja meg, ha külön sorba kerül a nyitó és a záró rész.

## A létrehozott fájl struktúra (a teljesség igénye nélkül)
```
projekt/
├── node_modules/
├── nodeapp/
│   ├── index.js
│   ├── students.xlsx
│   └── template.docx
└── docker-compose.yaml
```
Ahol:
| Fájl/könyvtár | Feladata |
| ------------- | -------- |
| node_modules  | Függőségek + verziók |
| index.js      | Template feltöltése  |
| students.xlsx | Hallgatók adatai     |
| template.docx | Feltöltendő sablon   |
| docker-compose.yaml | Konténerek összefogása, endpointok definiálása |

## A munkafolyamat tanulságos részletei

### A pipeline elemeinek meghatározása

Itt szeretném megemlíteni, hogy az eredeti elképzelés szerint nem csak a hallgatók email-jeit fogadta a rendszer, hanem egy Config email is, amivel a hallgatók adatait lehetett felvinni (vagy cserélni) a rendszerbe.

```
My task is to create a workflow with n8n that can accept a configuration email and save its content as a JSON file, and another kind of email, which contains a title, a multi-line description and an ID. Based on the ID, we have to retrieve further data from the JSON file that we saved in the config section, then merge all data and generate a word document from a template. Finally, we have to send the document back to the email address where we got the input data from.
```

Az MI a válaszában megadott egy vázlatot n8n node-okban gondolkodva. Az elképzelése alapvetően jó volt, de az adattárolást fizetős cloud szolgáltatásokkal akarta megoldani, a word dokumentum generálását szintén egy előfizetéshez kötött Microsoft-os API-t használó node-dal akarta megoldani, illetve használt egy, az általam használt n8n verzióban már nem létező node típust is.

### Az adattárolás megoldása ingyenes módszerrel

Miután az email fogadását megvalósítottam egy IMAP Trigger node-dal és a benne lévő információt feldolgoztam és JSON formátumra alakítottam, a következő lépés a config ág véglegesítése volt az adatok elmentésével.

```
Find a solution to store our JSON data locally, without any subscribtion-bound service.
```

A válasz: az n8n-nek nincs beépített lokális adatbázisa, de van a workflow-nak egy statikus storage-je, amit használhatunk. Ez ekkor jó megoldásnak tűnt, de később kiderült, hogy ez a storage nem őrzi meg az adatot két workflow execution között, így nem használható erre a célra.

### A word dokumentum generálás megoldása ingyenes módszerrel

Az adatok elmentése után rátértem a másik ágra, vagyis amikor nem config emailt kap a rendszer, hanem hallgatói emailt amiből Word sablont kell generálni.

```
Generate the word document without utilizing any subscribtion-based API. Use a Function node and solve the generation in JavaScript if neccessary.
```

Ez egy rendkívül hosszú beszélgetéssé nőte ki magát a ChatGPT-vel, ugyanis több, továbbra sem ingyenes alternatívát is javasolt, majd olyan node-okat említett amik már nem léteznek, vagy soha nem is voltak. Ezután megpróbálta JavaScript-ben megoldani a feladatot. Ez elsőre sikeresnek is tűnt, de tesztelés során kiderült, hogy az n8n nem engedélyezi külső Node modulok import-ját a Function node-okban (és más nodeban sem). Miután ezt közöltem vele, az MI azt javasolta, hogy töltsem le én magam a szükséges Node modult a docker konténerbe, amiben a workflow fut, így jutottunk a következő problémához: hogyan is tehetem ezt meg egy Docker Desktop-ban generált konténerrel?

### Kitérő: saját Docker környezet létrehozása

Ezen a ponton jöttem rá, hogy tulajdonképpen nem tudom, hová is hozta létre a Docker Desktop alkalmazás a konténeremet (mint utólag kiderült, az alkalmazás letöltésekor létrejött egy külön Linux "meghajtó" a gépen, és valahol ebben jött létre a konténer, de ezzel a tudással sem sikerült megtalálnom).

```
How do I access the folder of my docker container that I generated in the Docker Desktop App?
```

A válasz: csak parancssorból (nehézkes). A ChatGPT említett egyéb módszert a Desktop App-ban, de ezek nem léteztek. Miután emlékeztettem, hogy mi is a teljes projekt célja, azt javasolta, hogy generált konténer helyett csináljak sajátot, és hozzá egy docker compose fájlt, illetve egy .env fájlt, így könnyen módosítható mind a konténer, mind a környezeti változói.

### Word dokumentum generálása folytatás

Az új docker konténerembe letöltöttem a hiányzó Node modult, de szomorúan tapasztaltam, hogy az n8n ezután sem volt hajlandó azt importként elfogadni, így más megoldás kellett.

Erre a problémára nem az MI adott megoldást, hanem a konzulensem, aki azt javasolta, hogy hozzak létre egy lokálisan futó Node szervert, ami az n8n workflow-ból veszi az adatait, legenerálja a Word dokumentumot, majd visszaküldi azt a workflowba.

```
How do I make a local Node server that runs on my PC, accepts data from my n8n workflow in JSON and sends back a Word document in binary?
```

Az AI egész szépen megoldotta a feladatot elsőre, a válaszában már nagyjából a végleges struktúrában szereplő nodeapp mappa volt. Tesztelés közben azonban kiderült, hogy az n8n üres JSON-t küld a szervernek.

### Placeholder jelölés problémája

A node szerver első tesztje során leállt, ugyanis a Word valamiért több sorba tördelte a placeholderek nyitó- és záró tagjeit, emiatt nyilván nem ismerte fel őket az app.

Itt megadtam az AI-nak a docker konténer logját, ez alapján rájött a problémára és azt javasolta, hogy használjak egyedi placeholdert.
A következő kódrészlet a NodeJS szerver kódjában található, ezzel van paraméterezve egy Docxtemplater példány, ami a sablonba való behelyettesítést segíti:
```
     delimiters: {
        start: '[[', 
        end: ']]'
      }
```

Ez a megoldás nem feltétlenül egy sorban keresi a nyitó- és záró taget.

### Pipeline debug

Mikor észrevettem, hogy a válasz emailben üres placeholderek érkeznek, megkérdeztem a ChatGPT-t, hogy mi lehet a hiba oka.

```
In the response email, I receive empty placeholders. What can cause that behaviour?
```

A válaszban több pontos debug tervet kaptam:
1. Megfelelően olvassuk-e be az adatot az emailből?
2. Sikeres-e a mentés config ágon?
3. Sikeres-e a kiolvasás a másik ágon? (itt derült ki a hiba)
4. Az elküldött JSON még tartalmaz-e adatot?

### Workflow refactor

Miután kiderült, hogy a static storage nem alkalmas a céljaimra, kézenfekvő volt, hogy a Config Excel fájlt egyáltalán ne is emailben küldjem a workflow-ba, hanem egyszerűen betegyem a Word dokumentumot generáló noda app mappájába.

```
Modify the nodeapp so that it retrieves the students' data from an Excel file within its folder.
```

Az AI elsőre helyesen megoldotta a feladatot. Értelem szerűen ez a módosítás azzal is járt, hogy az n8n workflow teljes config ága törlésre került.

## Korlátok

### Fogadó email cím beállítása

Jelenleg a saját email címemmel használtam az alkalmazást, ezt átállítani azonban nem olyan egyértelmű feladat, az n8n ugyanis nem az email fiókhoz tartozó jelszót kéri a credential-ök beállításakor, hanem egy, a Gmail fiókban létrehozható, konkrét alkalmazáshoz tartozó jelszót (ez tulajdonképpen egy API key).

### Email formátum

Az emailnek kötött formátuma van:
1. A neptun kód "NK: " után kell, hogy szerepeljen
2. A téma címe "Cím: " után
3. Végül a részletes leírás "Feladat: " után

Mivel a beérkező email nem egy nyelvi modell értelmezi, hanem egyszerű regex-ek alapján történik a feldolgozás, így a formátumtól nem lehet eltérni.

### Word sablon formázása

A jelenlegi projektben a dokumentumot mindenféle formázás (vastagított betű, dőlt betű, több betűtípus, stb.) nélkül használom. Előfordulhat, hogy ezeket nem kezeli helyesen az alkalmazás.
