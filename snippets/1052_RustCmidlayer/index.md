---
layout: default
codename: RustCmidlayer
title: Rust és C közötti ffi réteg generáltatása MI segítségével
tags: snippets mieset rust ffi biztonság bindgen AUTOSAR memory-safety
authors: Molnár Ferenc Tamás
---

# Rust és C közötti ffi réteg generáltatása MI segítségével

## Összefoglaló

Az esettanulmány egy C -> Rust migrációs feladat egyik lépcsőfokának AI általi generáltatásáról szól, illetve segítséget nyújthat hasonló Rust és C együttélése során fellelhető problémák megoldására. A környezet AUTOSAR, az operációs rendszer C nyelven íródott, és szeretnénk ezeket az operációs rendszer API-kat hívni Rustból. A bindgen nevű tool C-s header fileokból gyártott nekünk Rust-os függvényeket, amik segítségével tudunk alkalmazáslogikát írni Rust-ban, és később a C mainben ezeket meg tudjuk külsőleg hívni. Viszont ezek a függvények rendkívül sok unsafe kódot tartalmaznak, és ezeket a kódokat szeretnénk elrejteni az alkalmazásfejlesztők elől, ezáltal a Rust sajátosságaival biztosítani tudjuk a memóriabiztonságot, kizárni a versenyhelyzeteket, stb. Ez egy köztes réteg létrehozásával lehetséges, ami saját függvényeket implementál. Ezt a köztes réteget szeretnénk generáltatni az AI segítségével, mert viszonylag egyszerű a logikája, viszont hosszadalmas, és ezt az időt szeretnénk megspórolni a fejlesztés során.

Az elemzés során egy új köztes Rust forrásfájl elkészítésére került sor, majd ezt összevetettük egy már tesztelt és működő alternatív réteggel. Az összehasonlítás megmutatta, hogy a puszta függvényburkolás mellett az eredménykezelés, a kimeneti paraméterek kezelése, az elnevezések és a hibás használat korlátozása is alapvető tervezési szempont.

A köztes réteg generálására GPT-5.6 Luna-t használtam.
## Alapprobléma

Az automatikusan generált bindings.rs fájl elsődleges feladata, hogy pontosan tükrözze a natív interfészt. Ez a cél a gépi generálás miatt jól teljesül, alkalmazási kódból használva azonban több nehézséget okoz:

- a nem biztonságos hívások közvetlenül elérhetővé válhatnak,
- a natív típusok és nyers pointerek részletei beszivároghatnak az alkalmazási logikába,
- a kimeneti paraméterek életciklusát a hívónak kell helyesen kezelnie,
- a generált elnevezések technikailag pontosak, de alkalmazási szinten nehezen olvashatók;
- a generált fájl változásai közvetlenül nagyobb felületet jelenthetnek az alkalmazás számára.

Az alapprobléma tehát nem az volt, hogy az alsó szintű interfész nem működik, hanem az, hogy a működő interfész és az alkalmazási logika között hiányzott egy egyszerűbb, világos réteg.

## A célkitűzés

A feladat egy köztes réteg létrehozása volt, amely:

- egyetlen helyen tartja a low-level, nem biztonságos hívásokat,
- az alkalmazási oldal számára biztonságosabb Rust-felületet biztosít,
- lefedi a natív interfész alkalmazás által igényelt műveleteit,
- az eredményeket és hibákat egységesen kezeli,
- nem módosítja a generált bindings.rs fájlt,
- könnyebben tesztelhető és karbantartható, mint a közvetlen bindings.rs használata.

Külön elvárás volt, hogy a réteg a lehető legtöbb natív műveletet elérhetővé tegye, de az alkalmazásfejlesztőnek ne kelljen nyers mutatókkal vagy nem biztonságos blokkokkal dolgoznia.

## A megoldás megközelítése

Első lépésként elkészült egy önálló köztes Rust fájl, amely a generált kötéseket privát modulként tölti be. A nyilvános felületen típusok, konstansok és biztonságos wrapper-függvények jelentek meg. Ahol a natív oldal kimeneti címet vár, ott a köztes réteg Rust-referenciát fogad, ahol egy cím visszatérési értékként érkezik, ott a null érték kezelhető formává alakult.

Ez a megoldás világos réteghatárt hoz létre:

A generált réteg a natív deklarációk technikai leképezéséért felel.
A köztes réteg a nem biztonságos hívásokért, a paraméterek átalakításáért és az eredmények egységesítéséért felel.
Az alkalmazási logika csak a köztes réteggel kommunikál.

## A két köztes réteg összehasonlítása

Az elkészült első változatot összehasonlítottam egy korábban létrehozott, tesztelt és működő változattal.

### Közös jellemzők

- Mindkettő elrejti a generált kötéseket egy belső modul mögött.
- Mindkettő egy helyre gyűjti a nem biztonságos natív hívásokat.
- Mindkettő alkalmazási szintű függvényeket biztosít az alapvető rendszer, feladat, erőforrás és mérési műveletekhez.
- Mindkettő használja a natív típusok Rust-megfelelőit.
- Mindkettő hozzáférést ad bizonyos állapotértékekhez és rendszerinformációkhoz.

### Lényeges eltérések

Az első változat szélesebb lefedettségű, alacsonyabb szintű adapterként készült. Több rendszerközeli műveletet és állapotot tesz elérhetővé, és sok esetben közvetlenül adja tovább a natív hibakódot.

A tesztelt változat szűkebb, de magasabb szintű alkalmazási felületet ad. A hibakódokat eredmény típussá alakítja, így a hívó egységes sikeres vagy hibás ágat kezelhet. Emellett olvashatóbb, alkalmazási jelentésű elnevezéseket és kényelmi konstansokat használ.

Jelentős különbség a kimeneti adatok kezelése is. A tesztelt változat inicializálatlan, csak kimenetként használt értékekhez külön Rust-eszközt alkalmaz, és csak sikeres natív hívás után olvassa ki őket. Az első változat ezzel szemben már inicializált módosítható referenciát vár a hívótól.

A biztonságos felület szempontjából az első változat a nyers pointerek használatát jobban korlátozza, míg a tesztelt változat egy külön, alacsony szintű nyers hívást is meghagy. Ez utóbbi hasznos lehet speciális integrációs esetekben, de az alkalmazási kód számára nem célszerű elsődleges belépési pontként kezelni.

## Eredmények

Az elemzés alapján a köztes réteg bevezetése több szempontból javítja a rendszer felépítését:

- az alkalmazási kód függetlenebbé válik a generált fájl részleteitől
- a nem biztonságos műveletek egyetlen ellenőrizhető helyre kerülnek
- egységesíthető a hibakezelés
- a natív kimeneti paraméterek kezelése pontosabban modellezhető Rustban
- az olvashatóbb elnevezések csökkentik a félreértések esélyét
- a generált kötési réteg újragenerálása kevésbé veszélyezteti az alkalmazási kódot.

Fontos eredmény az is, hogy a két réteg nem egymás egyszerű alternatívája. Az egyik a lefedettséget és a rendszerközeli hozzáférést helyezi előtérbe, a másik az alkalmazási biztonságot és az egyszerű használatot. A megfelelő végső megoldás ezek tudatos összehangolása.

## Tanulságok

A generált kötési réteg és az alkalmazási réteg közé érdemes külön absztrakciós határt beépíteni.

A nem biztonságos kód elrejtése önmagában nem elegendő; a paraméterek és visszatérési értékek típusos megtervezése legalább ilyen fontos.

A natív hibakódokat célszerű egységes Rust-eredménnyé alakítani, hogy az alkalmazási logika ne ismételje az ellenőrzési mintákat.

A kimeneti paramétereknél különbséget kell tenni az inicializált bemenet és a natív hívás által előállított kimenet között.

A teljes interfész lefedése és az egyszerű alkalmazási felület eltérő célok, a rétegeket ennek megfelelően kell tagolni.

A ritka, rendszerközeli műveleteket érdemes külön, jól láthatóan elkülönített alacsony szintű felületen tartani.

Az automatikus generálást nem célszerű kézzel módosítani, mert a változtatások a következő generáláskor elveszhetnek.

## Mesterséges intelligencia általi generáltatás tanulságai

A köztes réteg generáltatása összességében hasznos volt, mert adott egy olyan alapot, amit kézzel könnyen változtathatunk. Mivel egy operációs rendszernél sok függvény fellelhető ezért a kézzel való megvalósítás hosszadalmas időt vett volna igénybe.

Mindezek mellett a hibakezelésnél, vagy az eredmények kezelésénél is adott többféle tippet hogyan tudjuk ezeket könnyebben implementálni, hogy minél jobban hasonlítson a C-s implementációhoz, illetve minél könnyebben tudjuk használni az alkalmazásfejlesztés során.

Ellenőrizni fontos ezt a réteget, az MI sem tévedhetetlen, és fontos API-hívásokat kezelünk. Azonban több API hívás teszt segítségével ezeket ellenőrizni tudjuk viszonylag könnyen.

Összességében jól teljesített a szerkezeti munka és a kezdeti implementáció felgyorsításában, de nem helyettesítette a szakmai ellenőrzést. A fordítási ellenőrzés és a meglévő, tesztelt réteggel való összehasonlítás nélkül könnyen maradhattak volna benne hibák vagy kevésbé megfelelő tervezési döntések.

## Összegzés

Az eset azt mutatja, hogy egy működő natív interfész önmagában még nem feltétlenül jelent jó alkalmazási felületet. A köztes Rust réteg akkor tölti be jól a szerepét, ha elrejti a nem biztonságos részleteket, közérthető fogalmakat ad, valamint világosan elválasztja a generált kódot az üzleti vagy alkalmazási logikától.
