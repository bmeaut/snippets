---
layout: default
codename: Tessera
title: Tessera — Habit tracker fejlesztése és tesztelése LLM eszközökkel
tags: snippets mieset
authors: Várhegyi Melinda
---

# Tessera — Habit tracker fejlesztése és tesztelése LLM eszközökkel

## A feladat leírása

A feladat egy szokáskövető webalkalmazás elkészítése volt, amely alkalmas különböző szokások nyilvántartására és azok teljesítésének követésére.
A projekt fő témája a **különböző tesztelési módszerek megvalósításának vizsgálata 
LLM-ek segítségével**.

A fejlesztés során alkalmazott MI eszközök:

- **GitHub Copilot Chat (Claude Haiku 4.5)** — kódgeneráláshoz, tesztek írásához, hibák javításához
- **Claude Sonnet 4.6** — tervezéshez, architektúra döntésekhez, prompt íráshoz és hibakereséshez

A projekt célja, hogy minél több különböző tesztelési megközelítést alkalmazzunk ugyanazon 
alkalmazáson, és értékeljük azok hatékonyságát LLM-asszisztált fejlesztési környezetben.

---

## A megvalósított rendszer

### Tech stack

| Réteg | Technológia |
|---|---|
| Backend | ASP.NET Core Web API, .NET 8, SQLite, EF Core |
| Frontend | React + TypeScript + Vite, Bootstrap |
| Tesztelés (backend) | xUnit, Moq, FluentAssertions, FsCheck, RestSharp |
| Tesztelés (frontend) | Vitest, React Testing Library, Playwright |
| Terheléstesztelés | k6 |
| IDE | Visual Studio 2022 (backend), VS Code (frontend) |

### Solution struktúra

```
Tessera/
├── Tessera.Api/               ← ASP.NET Core Web API
├── Tessera.Core/              ← Domain modellek, interfészek (pure C#)
├── Tessera.Data/              ← EF Core + SQLite, repository implementációk
├── Tessera.Tests.Unit/        ← xUnit, Moq, FluentAssertions, FsCheck
├── Tessera.Tests.Integration/ ← WebApplicationFactory + RestSharp
└── load-tests/                ← k6 terheléstesztek
    └── habits-load-test.js

tessera-frontend/              ← React + TypeScript + Vite + Bootstrap
├── src/components/__tests__/  ← Vitest + React Testing Library
└── e2e/                       ← Playwright E2E tesztek
```

### Domain

- **Habit:** Id (Guid), Name, Description?, Color (hex), CreatedAt
- **HabitCompletion:** Id (Guid), HabitId, Date (DateOnly)
- **Streak:** egymást követő teljesített napok sorozata
- **Unique constraint:** (HabitId, Date) — egy napot csak egyszer lehet teljesíteni

---

## A projekt beüzemelése

### EF Core migrations — hiányzó Design csomag

A `Microsoft.EntityFrameworkCore.Design` csomagot a `Tessera.Data` projektbe telepítettük
(ahol a `DbContext` él), de a `dotnet ef` eszköz a startup projekten — vagyis a
`Tessera.Api`-n — keresztül dolgozik, és ott is elvárja ugyanezt a csomagot. A Copilot
ezt nem jelezte előre a kód generálásakor, a hiba csak a migrációs parancs futtatásakor
derült ki. Megoldás: a `Microsoft.EntityFrameworkCore.Design` csomag telepítése a
`Tessera.Api` projektbe is.

**Tanulság:** Az EF Core tooling és a projekt referencia struktúra közötti összefüggést
a Copilot nem kezeli proaktívan, a `.csproj` fájlokat és a NuGet függőségeket mindig
kritikusan kell ellenőrizni.

### CustomWebApplicationFactory — in-memory SQLite kapcsolat életciklusa

A `CustomWebApplicationFactory` első Copilot-generált verziója nem működött: a tesztek
500-as hibával buktak el. A probléma gyökere az volt, hogy az in-memory SQLite adatbázis
azonnal megsemmisül, amint a kapcsolat bezárul, ugyanis a Copilot a `DbContext`
regisztrációján belül hozta létre a kapcsolatot, amely így rövid életű volt.

A helyes megoldás: a `SqliteConnection`-t a factory konstruktorában kell megnyitni,
és `Singleton`-ként kell regisztrálni a DI konténerbe, hogy a teljes tesztelési
munkamenet alatt életben maradjon. Emellett az összes `DbContext`-hez kapcsolódó
DI regisztrációt el kellett távolítani, és egy
`ResetDatabase()` metódust kellett bevezetni, amelyet minden tesztosztály konstruktora
hív meg a tiszta állapot garantálása érdekében.

A Copilot célzott javító prompttal sem generálta le a helyes megoldást,
 a javítás manuális beavatkozást igényelt.

---

## Tesztelési fázisok

### Phase 1 — Unit tesztek (xUnit + Moq + FluentAssertions)

A unit tesztek a `StreakCalculator` és `StatisticsService` osztályokat fedik le.
A tesztek Moq-kal mockolt függőségeket használnak, és FluentAssertions
segítségével ellenőrzik az elvárt viselkedést.

**Tanulság 1 — Duplikált dátumok kezelése:**
A Copilot a `CalculateLongestStreak` implementációjában nem kezelte helyesen a duplikált
dátumokat. Ha ugyanaz a nap kétszer szerepelt a completion listában, a streak hibásan
számolódott. Célzott javító prompttal, amelyben pontosan leírtam az elvárt viselkedést
és egy konkrét ellenpéldát, a hiba megoldható volt.

Utólag azonban kiderült, hogy ez a védelem dead code: az adatbázis szintű
`(HabitId, Date)` unique constraint, illetve az API szintű validáció (400-as válasz
duplikált completion kísérletekor) együttesen garantálják, hogy a `StreakCalculator`
soha nem kap duplikált dátumokat tartalmazó listát. A duplikált-dátum ág ezért
production-ban elérhetetlen kód, és az azt lefedő tesztek valójában nem éles
viselkedést tesztelnek. Ez architekturális tanulság: ha a rendszer több rétegben is
véd ugyanazon feltétel ellen, a belső réteg védelme feleslegessé válhat.

**Tanulság 2 — A `GetCompletionRate` visszatérési értékének értelmezése:**
A `StatisticsService.GetCompletionRate` metódus 0.0–1.0 arányban adja vissza az
eredményt (nem 0–100 százalékban), ahogy a dokumentációja is leírja. Ennek ellenére
a Copilot által generált tesztek 100.0-t vártak el 1.0 helyett. A hiba csak a
tesztek futtatásakor derült ki. Tanulság: a visszatérési értékek skáláját explicit
módon kell megadni a promptban, különben a Copilot a "természetesebb" százalékos
formátumot feltételezi.

---

### Phase 2 — Integrációs tesztek (WebApplicationFactory)

Az integrációs tesztek `WebApplicationFactory`-val, in-memory SQLite adatbázissal
futnak. Minden tesztosztály konstruktorában `ResetDatabase()` hívás garantálja a
tiszta DB állapotot (*lásd feljebb a projekt beütemezésénél*).

**Tanulság 3 — Az integrációs tesztek olyan hibákat fedtek fel, amelyek unit tesztekkel
nem foghatók meg:**
A `CompletionsController` `Delete` metódusa hibásan volt implementálva:
`GetByHabitIdAndDateAsync`-t hívott `DateOnly.MinValue`-val az ID alapú törlés helyett. 
A Copilot valószínűleg a GET végpont logikájából indult ki (ahol dátum alapú 
keresés teljesen helyes), és ezt a mintát vitte át a Delete metódusba is, DateOnly.MinValue-t 
használva placeholderként. A kód lefordul, unit teszttel nem fogható meg, mivel a mock nem 
ellenőrzi a paramétereket, csak a hívás tényét. Az integrációs teszt fedte fel a hibát: valódi 
adatbázis ellen futva a MinValue-val indított keresés nem talált rekordot, a törlés nem történt 
meg, a teszt elbukott.

---

### Phase 3 — API tesztek (RestSharp)

A RestSharp API tesztek valódi futó szerver ellen dolgoznak. Első kísérletkor az API-t
F5-tel (Debug módban) indítottam el, majd megpróbáltam párhuzamosan futtatni a
teszteket, ezt viszont a Visual Studio nem engedte. A megoldás: Ctrl+F5
(Start Without Debugging), amely a szervert a háttérben indítja el anélkül, hogy a 
debug folyamat lefoglalná a Visual Studio-t.

---

### Phase 4 — Property-based tesztek (FsCheck)

A FsCheck tesztek a `Tessera.Tests.Unit` projektbe kerültek, `FsCheck.Xunit` csomaggal,
a meglévő 25 xUnit teszt mellé.

A property-based tesztek a következő invariánsokat ellenőrzik véletlenszerűen generált
bemeneten:

- `CalculateLongestStreak` eredménye mindig >= 0 és <= a distinct dátumok száma
- Duplikált dátumok hozzáadása nem változtatja meg a longest streak értékét 
*(lásd Tanulság 1, ez az invariáns production-ban elérhetetlen állapotot fed le)*
- Teljesen egymást követő dátumsorozatnál a streak egyenlő a distinct dátumok számával
- `CalculateCurrentStreak` eredménye mindig <= `CalculateLongestStreak` ugyanarra a bemenetre
- Ha nincs mai vagy tegnapi completion, a current streak mindig 0
- `GetCompletionRate` eredménye mindig >= 0.0 érvényes bemenetre
- Ha a tartományon kívüli dátumok szerepelnek, a completion rate 0.0

**A property-based tesztek cross-method invariánsokat is képesek ellenőrizni:**
Az xUnit tesztekkel nehéz természetesen kifejezni azt, hogy `CurrentStreak <= LongestStreak`
minden lehetséges bemenetre. FsCheck-kel ez egyetlen property, amely automatikusan
több száz véletlenszerű esetet ellenőriz, és képes ellenpéldát generálni, ha az invariáns 
megsérül.

---

### Phase 5 — UI komponens tesztek (Vitest + React Testing Library)

A frontend tesztek a három prop-alapú komponenst fedik le: `CheckInButton`,
`StatisticsPanel`, `CalendarGrid`. A `HabitCard` és `HabitList` komponensek (amelyek
API hívásokat végeznek) szándékosan kimaradtak, ezeket az E2E tesztek fedik le.

**Tanulság 4 — A `vitest/config` import szükséges a `vite.config.ts`-ben:**
Ha a Vitest `test` konfigurációs blokkot a `vite.config.ts`-be helyezzük el,
TypeScript hibát kapunk, mert a `vite` csomag `defineConfig`-ja nem ismeri a `test`
mezőt. A helyes megoldás: `import { defineConfig } from 'vitest/config'` — ez
re-exportálja a Vite `defineConfig`-ot, de kiegészíti a Vitest típusokkal.
A Copilot ezt nem javasolta, saját utánajárás kellett hozzá.

**Tanulság 5 — Az explicit TypeScript típusok fontossága tesztfájlokban:**
A Copilot a tesztfájlokban `any[]`-t használt a completion tömbök típusaként.
Ez TypeScript hibát okozott, mivel a komponens `HabitCompletion[]`-t vár.
Az importot és a típusannotációt explicit módon kellett megadni.

**A komponens tesztelhetőség és az architektúra kapcsolata:**
A három könnyen tesztelhető komponens (`CheckInButton`, `StatisticsPanel`,
`CalendarGrid`) mind tisztán prop-alapú, nincsen bennük API hívás vagy mellékhatás.
A nehezen tesztelhető komponensek (`HabitCard`, `HabitList`) ezzel szemben
`useEffect`-ben végeznek fetch hívásokat. Ez megerősíti azt az architektúrális
elvet, hogy az üzleti logikát és az adatlekérést érdemes elválasztani a
megjelenítési rétegtől, a separation of concerns nemcsak a kód minőségét
javítja, hanem a tesztelhetőséget is.

---

### Phase 6 — E2E tesztek (Playwright)

A Playwright tesztek a teljes stacket fedik le valódi böngészőben: Chromium,
Firefox és WebKit. A tesztek futtatásához mindkét szervernek élnie kell:
a Vite dev szervernek (port 5173) és a Tessera.Api-nak (port 7184).

A tesztek az alábbi felhasználói folyamatokat ellenőrzik:

- Az alkalmazás betölt és a navbar látható
- Az "New Habit" gombra kattintva megjelenik az űrlap
- Új habit létrehozható névvel és színnel
- A "Check in" gomb megnyomásával a completion regisztrálódik, az "Undo" gomb jelenik meg
- A habit kártyára kattintva a részletező oldalra navigál, ahol a statisztikák láthatók

**Tanulság 6 — A Playwright szintaxis eltér a Vitest szintaxisától:**
A Copilot a `habits.spec.ts`-ben `describe()` blokkot generált a tesztek köré,
amely Vitest-es szintaxis. A Playwright saját `test.describe()` függvényt használ,
a sima `describe` nem létezik a Playwright kontextusában, és futásidejű
`ReferenceError`-t okoz. A javítás egyszerű volt, de rámutat arra, hogy a Copilot
nem mindig veszi figyelembe, hogy melyik tesztelési keretrendszer aktív.

**Tanulság 7 — WebKit és self-signed SSL tanúsítvány összeférhetetlensége:**
A tesztek kezdetben csak WebKit-ben buktak el `"Load failed"` hibával, miközben
Chromium és Firefox rendben futott. A probléma gyökere: az ASP.NET Core fejlesztői
szerver self-signed HTTPS tanúsítványt használ, amelyet a WebKit nem fogad el
automatikusan, ellentétben a másik két böngészővel. A megoldás az
`ignoreHTTPSErrors: true` beállítás a `playwright.config.ts` `use` blokkjában,
amely minden böngészőre érvényes, és nem igényel backend módosítást.

**Tanulság 8 — Flaky tesztek hálózati függőség esetén:**
Az egyik Firefox teszt időnként `NS_ERROR_CONNECTION_REFUSED` hibával bukott el,
annak ellenére, hogy a Vite szerver futott. Ez flaky viselkedés: a teszt újrafuttatásra
azonnal zöld lett. Az ilyen instabilitás jellemző E2E teszteknél, ahol a tesztek
valódi hálózati hívásokra támaszkodnak. Megoldás lehet `webServer` auto-start
konfiguráció a `playwright.config.ts`-ben, amely garantálja, hogy a szerver
ténylegesen elérhető mielőtt a tesztek elindulnak.

---

### Phase 7 — Terheléstesztek (k6)

A terheléstesztek a projekt utolsó tesztelési fázisát alkotják. Az előző hat fázis
a helyes működést ellenőrizte különböző absztrakciós szinteken; a k6 fázis ezzel
szemben azt vizsgálja, hogy az API egyidejű terhelés alatt is teljesíti-e a
válaszidő-elvárásokat.

#### Eszköz és telepítés

A k6 önálló, Go-alapú bináris, nem Node.js csomag, nem integrálódik a meglévő
`package.json`-ba, és nem igényel futtatókörnyezetet a tesztek végrehajtásához.

A tesztek futtatásának előfeltétele, hogy a `Tessera.Api` élőben fusson
(`https://localhost:7184`) — ugyanúgy, mint a RestSharp teszteknél:
a szervert Ctrl+F5-tel kell indítani a Visual Studióban.

#### Terhelési profil

A teszt három szakaszból állt, összesen 50 másodperc alatt:

| Szakasz | Időtartam | Virtuális felhasználók |
|---|---|---|
| Ramp-up | 10 s | 0 → 10 VU |
| Steady state | 30 s | 10 VU (állandó) |
| Ramp-down | 10 s | 10 → 0 VU |

#### Tesztforgatókönyv

Minden virtuális felhasználó iterációnként az alábbi szekvenciát hajtja végre:

1. `GET /api/habits` — a teljes habit lista lekérése
   - Ellenőrzés: HTTP 200, válaszidő < 500 ms
2. Ha a lista nem üres, az első elem `Id` mezőjével: `GET /api/habits/{id}/statistics`
   - Ellenőrzés: HTTP 200, válaszidő < 500 ms, a válasz tartalmazza a `CurrentStreak` mezőt
3. 1 másodperc gondolkodási idő (think time) az iteráció végén

#### Threshold-ok (pass/fail kritériumok)

```javascript
thresholds: {
  http_req_duration: ['p(95)<500'],
  http_req_failed:   ['rate<0.01'],
}
```

A kérések 95%-a 500 ms alatt teljesülése és a hibaarány 1% alatt maradása jelenti a sikeres 
futást.

#### SSL kezelés

Az ASP.NET Core fejlesztői szerver self-signed tanúsítványt használ — ugyanaz a
probléma, amellyel a Playwright WebKit teszteknél is szembesültünk. k6-ban a
megoldás az `insecureSkipTLSVerify: true` opció az egyes `http.get` hívásoknál,
nem a globális konfigurációban.

**Tanulság 9 — A k6 tooling jellege alapvetően különbözik a többi tesztelési eszköztől:**

A projekt minden korábbi tesztelési eszköze (xUnit, Vitest, Playwright) a
fejlesztői ökoszisztémába (NuGet, npm) integrált csomag volt. A k6 ezzel szemben
önálló rendszerbináris, amelyet külön kell telepíteni és a PATH-hoz adni. Ez azt
jelenti, hogy a `winget install` sikere után a terminált újra kell indítani, és a
`k6` parancs elérhetőségét explicit módon kell ellenőrizni, a Copilot ezt a
kontextusfüggő operációs rendszer-szintű lépést nem tudja kezelni.

**Tanulság 10 — A PascalCase mezőnevek nem magától értetődők JavaScript kontextusban:**
A k6 tesztek JavaScript környezetben futnak, ahol a konvenció általában camelCase.
A Tessera API azonban C# konvenciókat követ, és PascalCase neveket szerializál
(`habit.Id`, `habit.Name`, nem `habit.id`). A Copilotnak a helyes névhasználatot a promptban 
explicit módon kellett specifikálni.

**Tanulság 11 — A cold start torzítja a terhelésteszt eredményeit:**
A futás során 3 check bukott el az `response time < 500ms` kritériumon, miközben
a p(95) csupán 16.31 ms volt, ez látszólagos ellentmondás. A max=2.21s-os kiugró
az ASP.NET Core JIT-fordításának és az EF Core kapcsolat első inicializálásának
együttes hatása: a ramp-up szakasz legelső kérései lassabbak, mert a runtime ekkor
fordítja le a releváns kódot és nyitja meg az SQLite kapcsolatot. Éles terhelési
teszteknél ezt a hatást általában warm-up iterációkkal szokás eliminálni, a
fejlesztői környezetben ez a viselkedés azonban
elfogadható és nem meglepő.

**Mérési eredmények:**

Mindkét threshold teljesült: a 95. percentilis válaszidő (16.31 ms) jóval az 500 ms-os
küszöb alatt maradt, hibás kérés pedig egyáltalán nem volt. A 3 failed check az
`response time < 500ms` ellenőrzésnél keletkezett a cold start hatására. 
A steady state szakaszban ilyen kiugró nem fordult elő.

---

## A névválasztásról

A projekt neve **Tessera** — latin szó, jelentése: kis négyzet, csempe, dominókő.
A domino effect a szokásépítés metaforája; a naptárnézet kis négyzetei vizuálisan
is utalnak a névre. Tagline: *"Your habits, one tile at a time."*

---

## Összefoglalás

| Tesztelési módszer | Eszköz | Lefedett terület |
|---|---|---|
| Unit tesztek | xUnit + Moq + FluentAssertions | StreakCalculator, StatisticsService |
| Integrációs tesztek | WebApplicationFactory | API végpontok, DB műveletek |
| API tesztek | RestSharp | Valódi szerver ellen |
| Property-based tesztek | FsCheck | Streak és statisztika invariánsok |
| UI komponens tesztek | Vitest + RTL | CheckInButton, StatisticsPanel, CalendarGrid |
| E2E tesztek | Playwright | Teljes felhasználói folyamatok, 3 böngésző |
| Terheléstesztek | k6 | GET /api/habits, GET /api/habits/{id}/statistics; p(95)=16 ms, 0% hiba |


Az LLM eszközök jelentősen felgyorsítják a tesztek generálását, de folyamatos 
emberi felügyeletet igényelnek. A leggyakoribb hibamintázat: a Copilot érti az általános 
esetet, de az edge case-eknél pontosabb promptot vagy manuális javítást igényel. A projekt beüzemelési nehézségei (EF Core Design csomag, in-memory SQLite kapcsolat életciklusa) 
szintén rávilágítanak arra, hogy a Copilot a konfigurációs és tooling jellegű problémákat 
kevésbé kezeli megbízhatóan, mint a kódgenerálást.

A projekt egy architekturális tanulsággal is szolgált: a duplikált dátumok kezelése
a `StreakCalculator`-ban utólag dead code-nak bizonyult, mivel az adatbázis és az API
réteg együttesen megakadályozzák, hogy ilyen állapot egyáltalán előálljon. Ez
rámutat arra, hogy LLM-asszisztált fejlesztésben — ahol a rétegek egymástól
függetlenül születnek — különösen fontos a rendszer egészének átlátása: a részek
önmagukban helyesek lehetnek, miközben együttesen ellentmondást alkotnak.

**Szerző:** Várhegyi Melinda
