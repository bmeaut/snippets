---
layout: default
codename: Wordle
title: Test-Driven Wordle klón fejlesztés MI segítségével
tags: snippets mieset
authors: Várhegyi Melinda
---

# Test-Driven Wordle klón fejlesztés MI segítségével

## A feladat leírása

A feladat egy Wordle szójáték klón elkészítése volt .NET MAUI keretrendszerben, C# nyelven,
Windows platformra célozva (`net8.0-windows10.0.19041.0`), Visual Studio 2022-ben.
A fejlesztés során használt MI eszközök:

- **GitHub Copilot Chat (Claude Haiku 4.5)** — a kód generálásához és a TDD ciklus végrehajtásához
- **Claude Sonnet 4.6** — tervezéshez, architektúra döntésekhez, prompt íráshoz és
  hibakereséshez

A projekt MVVM architektúrán alapul, a fejlesztés TDD (Test Driven Development)
módszerrel történt, xUnit, Moq és FluentAssertions könyvtárak használatával.

---

## Tanulságok

- **A kontextus átadása kulcsfontosságú.** Minél részletesebb és pontosabb promptot kap a Copilot,
  annál jobb kódot generál. Az egyszerű, rövid kérések általában rossz vagy hiányos eredményt adnak.
- **A TDD workflow jól kombinálható az MI-vel**, de egyes tesztek megírása emberi feladat marad —
  különösen az összetett edge case-ek esetén (pl. duplikált betűk kezelése a Wordle logikában).
- **Copilot nem látja a renderelt UI-t**, így vizuális hibák debuggolásában (pl. gomb layout)
  korlátozott a segítsége. Az ilyen problémákat sajátkezűleg kell megoldani.
- **A Copilot hajlamos hibás architektúra döntéseket javasolni** — pl. rossz target framework,
  felesleges `<RuntimeIdentifier>` a `.csproj`-ban, inkompatibilis NuGet csomagok.
  Ezeket mindig kritikusan kell értékelni.
- **Az összetett logikai edge case-eket a Copilot nem kezeli helyesen** — a duplikált betűk
  Wordle szabály szerinti kiértékelési logikáját kézzel kellett megírni.
- **A kontextus elvész** — ha a Copilot Chat ablak bezárul (pl. VS összeomlás vagy fájlok
  áthelyezése után), az összes korábbi kontextus elveszik. Érdemes a kontextus promptot
  külön fájlban tárolni és újra beadni.
- **Claude és Copilot jól kiegészítik egymást** — Claude erős volt a tervezésben,
  architektúrában és hibakeresésben, a Copilot pedig a kód generálásban.
- **A mutációs tesztelés és az MI jól kombinálható** — a Stryker által talált túlélő
  mutánsokat Copilottal hatékonyan meg lehet ölni, de a promptot pontosan kell
  megfogalmazni: meg kell adni a mutáns pontos helyét és viselkedését.
- **A Copilot törlési feladatoknál megbízhatatlan** — amikor kódot kellett törölni,
  Copilot váratlan módosításokat végzett más fájlokban is. Törlési feladatokat
  érdemes kézzel elvégezni.

---

## A megvalósított rendszer

### Projektstruktúra (4 projekt)

```
WordleMAUI/              ← .NET MAUI alkalmazás — csak nézetek (XAML)
WordleMAUI.Core/         ← Class Library — modellek és szolgáltatások (pure C#)
WordleMAUI.ViewModels/   ← Class Library — GameViewModel (CommunityToolkit.Mvvm)
WordleMAUI.Tests/        ← xUnit tesztprojekt
```

**Projekt hivatkozások:**
- `WordleMAUI` → `WordleMAUI.ViewModels` → `WordleMAUI.Core`
- `WordleMAUI.Tests` → `WordleMAUI.ViewModels` és `WordleMAUI.Core`
- `WordleMAUI.Tests` nem hivatkozik `WordleMAUI`-ra (WinRT inicializálási hiba miatt)

### Főbb komponensek

| Komponens | Leírás |
|---|---|
| `LetterState` | enum: Correct, Misplaced, Absent |
| `GuessResult` | record: char Letter, LetterState State |
| `WordValidator` | 5 betűs, csak alfa, szótárban szereplő szavak ellenőrzése |
| `GuessEvaluator` | Betűnkénti kiértékelés, duplikált betűk helyes kezelésével |
| `GameStateManager` | Játékállapot kezelése (6 kísérlet, nyerés/vesztés) |
| `WordSelector` | Véletlenszerű szókiválasztás |
| `GameViewModel` | MVVM ViewModel, összeköti a logikát és a UI-t |

---

## A munkafolyamat tanulságos részletei

### 1. A TDD workflow MI-vel

A fejlesztés az alábbi ciklust követte minden komponensnél:

```
1. Tesztnevek megírása (szándék leírása)
2. Copilot által tesztek generálása
3. Copilot javaslatának kritikus értékelése
4. Tesztek alapján kód generálása
5. Tesztek futtatása, felmerülő hibák javítása
6. Összes teszt zöld -> kész a komponens
```

Ez a workflow az egyszerűbb komponenseknél (pl. `WordValidator`, `GameStateManager`)
jól működött. Copilot gyorsan generált helyes implementációt, mivel a tesztek neve
egyértelműen leírta a szándékot.

**Példa sikeres promptra (Phase 2 implementáció):**

```
The unit tests for Phase 2 — Core Domain Layer are written and finalized.
Now implement the production code to make all tests pass, one class at a time
in the order below. Do not move to the next class until all tests for the
current one are green.

## Rules
- All strings are uppercase — no case conversion needed in any service
- Use the exact class and interface names specified below
- Do not add any methods or properties that are not required by the tests
- All classes are plain C# with zero UI dependencies

## Implementation Order
[...]
```

### 2. A duplikált betűk problémája

A `GuessEvaluator` implementálása során a duplikált betűk helyes kezelése
nem zajlott zökkenőmentesen. A Wordle szabályai szerint:

- Ha a tippben egy betű többször szerepel, mint a feladványban, a felesleges
  előfordulások `Absent` jelölést kapnak
- A helyes pozíciókat (`Correct`) kell először meghatározni, és csak ezután
  a rosszul pozicionált (`Misplaced`) betűket

A Copilot még részletes magyarázat után sem generált helyes
duplikált betű logikát. Az ehhez kapcsolódó teszteket végül kézzel kellett megírni.

**Példa edge case teszt (kézzel írva):**

```csharp
  [Fact]
  public void GivenDuplicateLetterInGuess_WhenOnlyOneExistsInSecret_ShouldMarkSecondAsAbsent()
  {
      var guess = "AWAKE";  // Two A's in guess
      var secret = "STARE"; // Only one A in secret at position 2

      var result = _evaluator.Evaluate(guess, secret);

      result.Should().HaveCount(5);
      // A is in STARE at position 2, BUT the other A in guess at position 2 is correct -> Absent
      result[0].State.Should().Be(LetterState.Absent);
      // W is not in STARE -> Absent
      result[1].State.Should().Be(LetterState.Absent);
      // A is in STARE at position 2 (correct position in guess) -> Correct
      result[2].State.Should().Be(LetterState.Correct);
      // K is not in STARE -> Absent 
      result[3].State.Should().Be(LetterState.Absent);
      // E is in STARE at position 4 (correct position in guess) -> Correct
      result[4].State.Should().Be(LetterState.Correct);
  }
```

**Tanulság:** Az összetett üzleti logikát tartalmazó teszteket nem érdemes
a Copilotra bízni. Az ilyen tesztek megírása emberi feladat, a Copilot feladata az
implementáció generálása a tesztek alapján.

### 3. Architektúra probléma — WinRT hiba a tesztek futtatásakor

Az első megközelítésben a tesztprojekt közvetlenül hivatkozott a MAUI projektre.
Ez `System.TypeInitializationException` hibát okozott, mert a MAUI projekt
betölti a WinRT runtime-ot, ami nem elérhető a tesztfuttató környezetben.

**Copilot javasolta megoldás:** A tesztprojekt target frameworkjét `net8.0`-ra
állítani — ez hibás volt, mert a framework eltérése miatt a projekthivatkozás
sem működött.

**Helyes megoldás:** Külön osztálykönyvtár projektek
létrehozása (`WordleMAUI.Core` és `WordleMAUI.ViewModels`), amelyek nem
húzzák be a WinRT függőségeket. A tesztprojekt csak ezekre hivatkozik,
a MAUI projektre nem.

**Tanulság:** A Copilot hajlamos a legegyszerűbb technikai megoldást javasolni,
ami nem mindig az architektúrailag helyes döntés. Az ilyen döntéseknél emberi
felülvizsgálat szükséges.

### 4. Projekt konfiguráció hibák — .csproj problémák

Copilot több hibás `.csproj` módosítást javasolt:

| Copilot javaslata | Probléma | Helyes megoldás |
|---|---|---|
| `<TargetFramework>net8.0</TargetFramework>` a tesztprojektben | Framework eltérés, hivatkozás nem működik | `net8.0-windows10.0.19041.0` |
| `<RuntimeIdentifier>win10-x64</RuntimeIdentifier>` | Felesleges, projekt hivatkozási problémákat okoz | Törlés |
| `CommunityToolkit.Maui` NuGet csomag | Verzió inkompatibilitás | Csomag eltávolítása |

**Tanulság:** A `.csproj` fájlokat mindig kritikusan kell átnézni, mielőtt
elfogadjuk a Copilot javaslatát. Ha valami furcsának tűnik, valószínűleg az is.

### 5. A kontextus prompt fontossága

Mivel a Copilot Chat nem őrzi meg a kontextust munkamenetek között (pl. VS
összeomlás, fájlok áthelyezése után), részletes kontextus promptot kellett készíteni,
amelyet minden új munkamenet elején be kellett adni. Ez tartalmazta:

- A projekt teljes struktúráját
- Az összes projekt hivatkozást
- A már implementált komponensek interfészeit
- A fejlesztési konvenciókat (csak nagybetűs szavak, nincs `CommunityToolkit.Maui` stb.)
- Az aktuális fázist és feladatot

**Példa kontextus prompt részlet:**

```
You are helping me build a Wordle clone called WordleMAUI using .NET MAUI
targeting net8.0-windows10.0.19041.0 in Visual Studio 2022 with .NET 8.0.
[...]
Note: CommunityToolkit.Maui is NOT installed due to version incompatibility.
Do not suggest or use any APIs from it.
[...]
We follow strict TDD: tests are always written before implementation.
Never generate implementation before tests unless I ask.
```

**Tanulság:** Minél pontosabb és részletesebb a kontextus prompt, annál kevesebb
hibás javaslatot ad a Copilot. A negatív megszorítások (pl. "ne használd ezt a
csomagot") különösen fontosak.

### 6. A UI fejlesztés kihívásai

A MAUI XAML UI generálásánál a Copilot hasznos volt az alapstruktúra elkészítésében,
de a vizuális hibák javításában korlátozott segítséget nyújtott, mivel nem látja
a renderelt eredményt.

**Konkrét példa — billentyűzet layout:**
A virtuális billentyűzet gombjainak helyes elhelyezése több lépésen keresztül tartott:
- Copilot egymás után javasolt fix pixel szélességeket, padding és margin értékeket
- Ezek egyike sem oldotta meg a problémát
- A végső megoldás a MAUI `Button` vezérlő `MinimumWidthRequest="0"` tulajdonsága
  volt

**Tanulság:** A vizuális UI debuggolás emberi feladat. A Copilot tud XAML kódot
generálni, de a renderelt eredményt nem látja, ezért vizuális javításra
nem feltétlenül alkalmas.


### 7. Mutációs tesztelés Stryker.NET-tel

A fejlesztés végén mutációs tesztelést végeztünk a Stryker.NET eszközzel (v4.14.0)
a `WordleMAUI.Core` projekt tesztelési minőségének mérésére.

**A mutációs tesztelés folyamata:**
A Stryker apró változtatásokat ("mutációkat") végez a forráskódon, majd lefuttatja
a teszteket. Ha egy mutáció nem buktatja el a teszteket, az azt jelenti, hogy
a tesztek nem fedik le megfelelően azt a logikát — ez egy túlélő mutáns.

**Eredmények — a fejlesztés során:**

| Iteráció | Mutáció score | Változás |
|---|---|---|
| Első futtatás | 74.00% | kiindulópont |
| `SelectByDate` eltávolítása után | 80.43% | +6.43% |
| `GameStateManager` tesztek után | 89.13% | +8.70% |
| `WordSelector` tesztek után | 93.48% | +4.35% |
| `WordValidator` + `GuessEvaluator` tesztek után | **100.00%** | +6.52% |

**Végső eredmény — 100% mutáció score:**

| Fájl | Score |
|---|---|
| `GameStateManager.cs` | 100% |
| `WordSelector.cs` | 100% |
| `WordValidator.cs` | 100% |
| `GuessEvaluator.cs` | 100% |

**A Stryker konfigurálásának nehézségei:**
A Stryker beüzemelése számos kihívással járt, amelyek mind a `.csproj` konfiguráció
sajátosságaiból eredtek:
- A `stryker-config.json` helyes formátumát Copilot rosszul generálta
- A `console` reporter neve Stryker 4.14.0-ban `cleartext` — ezt is tévesen adta meg
- A `mutate` path filter nem működött relatív útvonalakkal, csak `**/*.cs` mintával
- A `LinqMutator` érvénytelen kódot generált `List<string>.Count` mutációjakor,
  amit az `ignore-mutations: ["linq"]` beállítással kellett kizárni

**A Stryker + Copilot workflow:**
A leghasznosabb megközelítésnek az bizonyult, amikor a Stryker riportból azonosított túlélő
mutánsokat Copilottal öltük meg. A workflow:

```
1. Stryker futtatása → HTML riport generálása
2. Túlélő mutáns azonosítása a riportban (fájl + sor + mutáció típusa)
3. Copilot Chat: pontos prompt a mutáns megöléséhez szükséges teszttel
4. Teszt hozzáadása → Stryker újrafuttatása → score javulás ellenőrzése
```

**Tanulság:** A mutációs tesztelés hasznos eszköz a tesztek minőségének mérésére,
de a konfigurálása összetett és eszközismeretet igényel. A Copilot segíthet
a tesztek generálásában, de a mutáns azonosítása és a prompt pontos
megfogalmazása emberi feladat marad.

**Megjegyzés:**
A 100%-os mutáció score azt jelenti, hogy minden meglevő kódsor tesztelve
van — de nem jelenti azt, hogy a szoftver helyes. A Stryker csak a meglévő
kódot tudja mutálni, hiányzó funkciókat vagy hibás üzleti logikát nem képes
detektálni. Jó példa erre a duplikált betűk kezelése: ha a `GuessEvaluator`
eleve rossz algoritmust tartalmazott volna, a Stryker azt nem találta volna
meg — csak a kézzel megírt, üzleti logikán alapuló tesztek tudták garantálni
a helyes viselkedést.

---

## Összefoglalás

A TDD és az MI eszközök kombinációja hatékony fejlesztési módszernek bizonyult,
de fontos tanulság, hogy az MI nem helyettesíti a fejlesztői tudást — inkább
egy erős asszisztens, amely felgyorsítja a munkát, de folyamatos emberi
felügyeletet igényel.

A legjobb eredményt akkor értük el, amikor:
1. A fejlesztő írta meg a tesztek leírását
   (NEM az MI dönti el, hogy milyen tesztesetekre lesz szükségünk)
2. A teszteket vagy MI generálta és alaposan ellenőrizte őket a fejlesztő,
   vagy maga a fejlesztő írta
3. A Copilot legenerálta az implementációt a tesztek alapján
4. A fejlesztő itt is kritikusan értékelte és szükség esetén javította a javaslatot
5. Claude segített az összetettebb promptok megírásában és a nehezebb hibák azonosításában

**Szerző:** Várhegyi Melinda

