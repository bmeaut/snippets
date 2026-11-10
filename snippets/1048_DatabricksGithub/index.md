---
layout: default
codename: DatabricksGithub
title: Hardcode-olt Databricks notebookok migrálása GitHub-ra
tags: snippets mieset databricks github
authors: Barkóczi Alexandra
---

# MI esettanulmány – Hardcode-olt Databricks notebookok migrálása GitHub-ra

## Cél

Egy meglévő, éles adatfeldolgozó rendszer Databricks notebookjait kellett verziókezelt, karbantartható állapotba hozni. A notebookok évek alatt, ad-hoc módon nőttek: a workspace-ben közvetlenül szerkesztve, hardcode-olt kapcsolati stringekkel, jelszavakkal, elérési utakkal és környezetfüggő paraméterekkel (dev/test/prod ugyanabban a fájlban, kikommentezve). A cél az volt, hogy ezekből egy GitHub repóban tárolt, Databricks Asset Bundle-ökkel (DAB) deployolható, paraméterezett kódbázis legyen, CI/CD folyamattal.

## Kiinduló állapot

* verziókezeletlen notebookok
* kapcsolati adatok (JDBC connection string, storage account key) közvetlenül a cellákba írva
* a dev/test/prod közötti eltérést if-ágak és kikommentezett sorok jelentették
* nem volt automatizált teszt, a notebookokat kézzel futtatva ellenőrizték

## Elvárások

1. A notebookok tartalmának feldolgozása és modulokra bontása
2. Hardcode-olt értékek kiszervezése Databricks widget/paraméter és Key Vault-backed secret scope-okba
3. Databricks Asset Bundle (`databricks.yml`) létrehozása a jobok és a környezetek (dev/test/prod) deklaratív leírásához
4. GitHub repó és GitHub Actions workflow a bundle validálásához és deployolásához
5. Alapszintű unit tesztek a tisztán Python logikára kiszervezett részekhez
6. A notebookok egy lépésben történő beolvasás-tisztítás-aggregálás logikájának átszervezése medallion (bronze/silver/gold) architektúrára

A munka nagy részét GitHub Copilot Chat-tel végeztem, VS Code-ban, mivel a notebookokat exportálás után helyi `.py` fájlokként (`# Databricks notebook source` formátumban) tudtam szerkeszteni.

## Tanulságok

* Az AI nagyon hatékonyan ismerte fel a hardcode-olt titkokat és javasolt rájuk Key Vault-backed secret scope-os megoldást, viszont a secret scope létrehozásához szükséges Databricks CLI parancsokat mindig ellenőriznem kellett, mert a verziók között (Databricks CLI legacy vs. új, Unity Catalog-kompatibilis CLI) keverte a szintaxist.

* A dev/test/prod közti elágazásokat (if-ágak a cellákban) nagyon jól alakította át bundle-paraméterekre és target-specifikus `databricks.yml` szakaszokra.
* A Databricks CLI-t kifejezetten jól ismerte: a meglévő workspace-erőforrások (jobok, cluster-ek, pipeline-ok) feltérképezéséhez és a bundle-váz generálásához adott parancsok szinte elsőre helyesen és pontosan lehúzták a valós állapotot, ehhez alig kellett utólag javítanom.
* A medallion (bronze/silver/gold) architektúrára való átszervezésben is jó kiindulási javaslatokat adott, bár a rétegek közti idempotens feldolgozásra (duplikátumok, késve érkező rekordok kezelése) elsőre nem gondolt, ezt külön kellett kérnem.
* A GitHub Actions workflow első verziója működött, de nem különítette el megfelelően a service principal jogosultságait környezetenként – ezt biztonsági szempontból mindenképp át kellett néznem és szigorítanom.
* A migrálás nem volt "one-shot" feladat: notebookonként haladtam, és minden lépés után lefuttattam a notebookot a Databricks workspace-ben, mielőtt a következőre léptem volna.

## A munkafolyamat tanulságos részletei

### Hardcode-olt titkok feltérképezése

```
Ez egy exportált Databricks notebook Python forrása. Keresd meg benne az összes hardcode-olt
titkot (jelszó, connection string, storage account key, token), és minden találatnál javasolj
egy Databricks secret scope-ra és kulcsnévre való hivatkozást, ami helyettesítheti.

<notebook forrás beillesztve>
```

Az AI végigment a fájlon és egy táblázatban sorolta fel a talált titkokat, javasolt secret scope neveket (`prod-adls-secrets`, `prod-sql-secrets`), valamint a helyettesítő kódrészletet:

```python
storage_key = dbutils.secrets.get(scope="prod-adls-secrets", key="storage-account-key")
```

Emellett figyelmeztetett arra is, hogy a secret scope-okat előbb létre kell hozni a Databricks CLI-vel vagy a workspace admin felületén, és megadta a hozzá tartozó CLI parancsot – ez azonban a régi (legacy) CLI szintaxisát tartalmazta, amit át kellett írnom az általunk használt új CLI-re.

### CLI-vel a meglévő erőforrások feltérképezése

Mielőtt a notebookokat átszerveztem volna, előbb tudnom kellett, pontosan milyen jobok, cluster-ek és ütemezések élnek már a workspace-ben, mert ezekről sosem készült dokumentáció.

```
Szeretném feltérképezni, hogy a Databricks workspace-ünkben jelenleg pontosan milyen jobok,
cluster-ek és job cluster policy-k vannak beállítva, és ezekből szeretnék egy Asset Bundle
váz-konfigurációt generálni. Milyen Databricks CLI parancsokkal tudom ezt megtenni?
```

Az AI szinte azonnal pontos, aktuális CLI szintaxist adott: a `databricks jobs list` és `databricks clusters list` parancsokkal listázta ki, mi fut éppen, majd a `databricks bundle generate job --existing-job-id <id>` paranccsal minden egyes meglévő jobhoz legenerálta a hozzá tartozó YAML konfigurációt, a hozzá tartozó notebook-hivatkozásokkal együtt. Ez meglepően pontosan tükrözte a workspace tényleges állapotát – korábban ehhez órákig tartó, kézi utánajárás lett volna szükséges (job-onként átnézni a UI-t, kimásolni a cluster-beállításokat), az AI viszont teljesen képben volt azzal, hogy melyik CLI parancs milyen erőforrástípust tud exportálni, és a kimeneteket is helyesen értelmezte.

```
A generált jobs.yml egy régi, már nem használt cluster policy-ra hivatkozik. Hogyan tudom
kideríteni CLI-vel, hogy mely policy-k és instance pool-ok aktívak még, és melyeket lehet törölni?
```

Erre is pontos parancssorozatot kaptam (`databricks cluster-policies list`, `databricks instance-pools list`), amivel könnyen ki lehetett szűrni az elavult, sehol nem hivatkozott erőforrásokat, mielőtt azok bekerültek volna a végleges bundle-be.

### Medallion architektúra kialakítása

A notebookok nagy része egyetlen lépésben olvasta be a nyers adatokat, tisztította és rögtön alá is aggregálta – ezt szerettem volna egy tisztább, réteges (medallion) architektúrára bontani.

```
A notebookjaink jelenleg egy lépésben olvassák be a nyers adatot egy forrásrendszerből, azonnal
tisztítják (null-szűrés, típuskonverzió) és rögtön aggregált üzleti táblákat is előállítanak
belőle. Szeretném ezt bronze/silver/gold (medallion) architektúrára szétbontani Databricks
Asset Bundle alatt. Javasolj réteg-felosztást és job task struktúrát.
```

A modell javasolta a szokásos hármas felosztást: a **bronze** réteg a nyers adatot változtatás nélkül, csak hozzáfűzve (append-only) tárolja Delta táblákban, a **silver** réteg végzi a tisztítást, deduplikálást és sématisztázást, a **gold** réteg pedig az üzleti szempontú, aggregált táblákat állítja elő. Ehhez egy Databricks Job-ot javasolt, ahol a három réteg egy-egy task, explicit `depends_on` függőséggel a `databricks.yml`-ben, hogy a silver csak a bronze sikeres lefutása után induljon.

Az első verzióban viszont a silver réteg egyszerű felülírással (overwrite) dolgozott, ami nem kezelte a duplikáltan vagy késve érkező rekordokat:

```
A silver réteg jelenlegi logikája minden futáskor felülírja a teljes táblát. Ha egy forrásrendszer
késve küld egy rekordot egy korábbi napra, vagy ugyanazt a rekordot kétszer küldi el, ezt jelenleg
nem kezeljük. Alakítsd át úgy, hogy egy elsődleges kulcs alapján merge/upsert logikával dolgozzon.
```

Ezt követően a modell a Delta Lake `MERGE INTO` utasítására épülő upsert logikát épített be a silver réteg feldolgozásába, amivel a duplikátumok és a késve érkező rekordok is helyesen kezelve lettek. Ez jó példa volt arra, hogy a réteg-architektúra alapkoncepcióját az AI gyorsan és helyesen javasolta, de az adatminőségi szélső eseteket (idempotencia, késve érkező adat) csak explicit rákérdezésre vette figyelembe.

### `databricks.yml` és környezetek

```
A notebookokban lévő if DEV / if TEST / if PROD elágazásokat szeretném megszüntetni, és helyette
Databricks Asset Bundle target-eket használni (dev, test, prod), ahol a paraméterek (katalógus név,
séma név, storage account) target szintre kerülnek. Mutasd meg, hogyan nézzen ki a databricks.yml.
```

A generált `databricks.yml` targetenként külön `variables` blokkokat definiált, és a notebookok paramétereit widget-ekként kapták meg, amit a job definíció töltött fel target szerint. Ez érdemben leegyszerűsítette a notebookok tartalmát, mert az elágazások helyett egyetlen, paraméterezett útvonalon futottak.

### CI/CD workflow

```
Készíts egy GitHub Actions workflow-t, ami pull requesteken futtatja a "databricks bundle validate"
parancsot, main branch-re mergelve pedig deployolja a bundle-t a "prod" targetre, service principal
hitelesítéssel, a secretet GitHub Actions secret-ként tárolva.
```

A kapott workflow működött, de az első verzióban ugyanazt a service principal-t használta minden target validálásához, ami azt jelentette volna, hogy egy pull request ellenőrzése is elérné a prod hitelesítő adatokat. Ezt szóvá tettem:

```
A PR validáció ugyanazt a service principal secretet használja, mint a prod deploy. Külön kell
választani: a validálás fusson egy korlátozott jogú, csak-olvasás service principal-lal.
```

A modell erre helyesen szétválasztotta a job lépéseket, külön secretekkel a validáláshoz és a tényleges deploy-hoz – ez viszont olyan biztonsági szempont volt, amit alapból nem vett figyelembe, csak explicit kérésre.

## Összefoglalás

A migráció során az AI leginkább a "boilerplate" jellegű részekben (secret scope javaslatok, `databricks.yml` felépítése, GitHub Actions workflow váza) volt igazán hasznos, és jelentős időt spórolt. Kifejezetten erős volt a Databricks CLI ismeretében: a meglévő erőforrások (jobok, cluster-ek, policy-k) lehúzása és a bundle-váz generálása szinte elsőre pontosan tükrözte a workspace valós állapotát. A medallion architektúrára való átszervezésben is jó kiindulási alapot adott, bár az adatminőségi szélső eseteket (duplikátumok, késve érkező rekordok) csak explicit rákérdezésre kezelte helyesen. A biztonsági kérdéseket (jogosultság-elkülönítés, secret scope-ok) szintén explicit kérés nélkül nem javította ki magától, ezekre külön oda kellett figyelni felülvizsgálat közben.
