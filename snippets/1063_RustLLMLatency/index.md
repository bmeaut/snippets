---
layout: default
codename: RustLLMLatency
title: LLM API válaszidő mérése Rustból (Gemini API, free tier)
tags: snippets mieset rust llm-api gemini benchmark latency
authors: Molnár Ferenc Tamás
---

# LLM API válaszidő mérése Rustból (Gemini API)

A feladat egy Rust nyelvű benchmark-eszköz elkészítése volt, amivel mérhető, mennyi
idő telik el, amíg egy prompt Rustból egy LLM API-n (Gemini free tier) végigfut,
mind a teljes válaszidőt (nonstream), mind a streaming módban mért TTFT-t (time to
first token) mérve. Az egész projektet a Cargo-projekt felépítését, a HTTP/SSE
hívásokat, a hibák debuggolását és a mérés futtatását is a Claude Code (Claude
Sonnet 5) végezte.

A forráskód és a mért adatok:

- [Cargo.toml](Cargo.toml) — Rust függőségek
- [src/main.rs](src/main.rs) — CLI és a mérési ciklus
- [src/gemini.rs](src/gemini.rs) — a Gemini API hívás (nonstream + SSE streaming), TTFT-méréssel
- [src/stats.rs](src/stats.rs) — mean/median/p95/stddev számítás
- [src/types.rs](src/types.rs) — az eredménysorok típusa
- [results.csv](results.csv) — egy minta mérés nyers eredményei (10 nonstream + 10 stream hívás, `gemini-3.5-flash-lite`)
- [.env.example](.env.example) — a szükséges Gemini API kulcs env-változó sablonja

## Tanulságok

- A `reqwest` alapértelmezett TLS backendje (`native-tls`) Windows alatt ütközhet a
  Smart App Control-lal / alkalmazásvezérlési házirendekkel, mert az a build-script
  natív, aláíratlan exe-jét blokkolja fordításkor. Megoldás: `rustls-tls` feature
  használata, ez tiszta Rust TLS-implementáció, nincs natív build-script, és megkerüli a problémát.
- Streaming (SSE) válaszok parse-olásánál a szabvány szerinti
  `\n\n` eseményhatároló helyett a Gemini API a gyakorlatban `\r\n\r\n`-t küld. Emiatt a
  TTFT-mérés eleinte némán (hibaüzenet nélkül, csak hiányzó adatként) nem működött,
  amíg meg nem néztük a nyers bájtfolyamot debug loggal.
- A modellnevek gyorsan változnak: `gemini-2.5-flash` néhány hónap alatt "no longer
  available to new users" lett. A legmegbízhatóbb forrás maga az API hibaüzenete
  (megmondja a jelenleg ajánlott modellt), illetve a `GET /v1beta/models` lista
  endpoint. Hardvode-olni nem ajánlott modell neveket ebből fakadóan.
- A free tier kvóták modellenként nagyon eltérőek, és nem feltétlenül csak
  percenkéntiek: a zászlóshajó `gemini-3.8-flash` napi 20 darab kérésre volt
  limitálva, míg a `gemini-3.5-flash-lite` sokkal nagyobb napi kerettel rendelkezett. Case
  studyhoz, ahol sok mérési pont kell, érdemes eleve "lite" modellt választani.
- "Gondolkodó" (reasoning/thinking) modelleknél a láthatatlan gondolkodási
  tokenek is beleszámítanak a `max_tokens` keretbe, alacsony limit mellett a
  válasz csonkolva érkezik, mielőtt még érdemi látható szöveg született volna.
  Ehhez képest jóval nagyobb tokenkeret kellett.
- Streaming módban a TTFT (az első token megérkezése) a mérésünkben kb. fele
  volt a nonstream teljes válaszidőnek (695 ms vs. 1205 ms átlagosan). Ha az
  érzékelt gyorsaság a cél, streaminget érdemes használni, még ha a teljes
  válasz generálása (utolsó tokenig) valamivel tovább tart is, mint nonstream
  módban (1363 ms vs. 1205 ms átlagosan a mérésben).
- Nincs hivatalos Google vagy Anthropic SDK Rusthoz, azaz a hívásokat kézzel kell megírni.
  A hivatalos SDK sok problémát kezel, mint például a `\n\n` probléma a második pontban.
- A Claude nem minden esetben kezeli helyesen az API kulcsokat. Például utólagos elemzés során kiderült,
  hogy egy esetleges hálózati hiba esetén, az eredmény fájlba bekerülne a teljes URL paraméter, amiben esetlegesen
  megjelenhet az API kulcs. Ezáltal az eredményeket továbbosztva kitudódhatna az API kulcsunk. Érdemes az AI-al
  többször átnézetni a kódot biztonságtechnikai szempontokat figyelembe véve.

## Az eredmény használata

Előfeltétel: telepített Rust toolchain (`rustup`), és egy Gemini API-kulcs a
[Google AI Studio](https://aistudio.google.com)-ból, amit egy `.env` fájlba kell
tenni (lásd [.env.example](.env.example)):

    GEMINI_API_KEY=AIza...

Futtatás:

```bash
cargo run --release -- --mode both --iterations 10
```

Fontosabb kapcsolók:

- `--mode stream|nonstream|both` — melyik módot mérje
- `--model <név>` — Gemini modellnév (aktuálisan elérhető modellek lekérése: `GET /v1beta/models`)
- `--iterations <n>` — hívások száma módonként
- `--max-tokens <n>` — válasz tokenkeret (reasoning modelleknél ne legyen túl alacsony)
- `--delay-ms <ms>` — szünet két hívás között (a free tier kvóta miatt fontos)
- `--prompt "..."` — a tesztelt prompt szövege
- `--output results.csv` — a nyers eredmények kimeneti fájlja

A program minden hívásnál rögzíti a teljes válaszidőt (`total_ms`) és streaming
módban a TTFT-t (`ttft_ms`), majd módonként kiírja az átlagot, mediánt, p95-öt,
min/max-ot és szórást a konzolra, a nyers, soronkénti adatokat pedig CSV-be menti
(lásd [results.csv](results.csv) egy minta futásból).

## A munkafolyamat tanulságos részletei

### A kiindulási kérdés

```
Szeretnénk lemérni, mennyi idő bizonyos API-kat meghívni Rustból. Főleg Claude
code API, Gemini APi-kra lennék kíváncsi, hogy Ruston keresztül mennyi
idő egy promptot lefuttatni. Hogyan állnál neki illetve hogyan állítanád fel a
tesztkörnyezetet?
```

A Claude először röviden felvázolta a megközelítést (async Rust kliens `reqwest` +
`tokio`-val, TTFT és teljes válaszidő külön mérése, kontrollált ismétlésszám a
hálózati jitter kiátlagolásához), majd elkészítette
a teljes Cargo-projektet (Claude + Gemini támogatással), amit később az 
ingyenes verzió elérhetősége miatt leszűkítettünk csak a Gemini API-ra.

### A `native-tls` build blokkolása és a `rustls` váltás

Az első `cargo build --release` egy hibával állt le:

```
error: failed to run custom build command for `native-tls v0.2.18`
Caused by:
  could not execute process ...\build-script-build (never executed)
Caused by:
  Egy alkalmazásvezérlési házirend letiltotta ezt a fájlt. (os error 4551)
```

Ez alapján a Claude azonosította, hogy ez nem kódhiba, hanem egy Windows
rendszerbiztonsági blokk, és mivel rendszerbeállítást nem módosíthat, felajánlotta
a `native-tls` helyett a `rustls-tls` feature használatát, ami tiszta Rust
implementáció, nincs natív build-script:

```toml
reqwest = { version = "0.12", default-features = false, features = ["json", "stream", "rustls-tls"] }
```

Ezzel a fordítás sikeres lett.

### A hiányzó TTFT és a nyers SSE-bájtok megnézése

Miután a program lefutott, a streaming módban a TTFT mindig hiányzott
(`ttft=-`), miközben a teljes válaszidő rendben megjött. Ahelyett, hogy
találgatott volna, a Claude egy ideiglenes debug-ággal kiíratta a nyers,
beérkező SSE bájtfolyamot:

```
DEBUG raw chunk: "data: {\"candidates\": [...]}\r\n\r\n"
```

Ebből kiderült, hogy az esemény-elválasztó `\r\n\r\n`, nem a feltételezett
`\n\n`. A parser javítása után a debug kódot eltávolítottuk, és a TTFT
helyesen elkezdett megjelenni.

### Modellnév-elavulás és a lista endpoint

A futtatás közben az eredetileg beállított `gemini-2.5-flash` modell 404-es
hibát adott:

```
"message": "This model models/gemini-2.5-flash is no longer available to new
users. Please update your code to use models/gemini-3.8-flash ..."
```

Később, amikor a `gemini-3.8-flash` napi kvótája (20 kérés/nap) is elfogyott,
a Claude a `GET /v1beta/models` endpointot hívta meg, hogy
lekérje az aktuálisan elérhető, `generateContent`-et támogató modellek valódi
listáját, és ebből választott egy magasabb kvótájú "lite" modellt
(`gemini-3.5-flash-lite`) a mérés folytatásához.

### Rust használata API hívásokra tanulság
A Rust ebben a feladatban nem adott mérhető sebességelőnyt, mert a válaszidőt a hálózat és a modell határozza meg. Hivatalos SDK hiányában viszont több kézi munkát igényelt (pl. az SSE-parszolás) és több hibalehetőséget hordozott. A Rust/tokio erőssége nagy számú párhuzamos kérésnél jönne ki, de ezt a free tier kvótái mellett nem lehetett kihasználni.
