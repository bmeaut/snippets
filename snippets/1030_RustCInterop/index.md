---
layout: default
codename: RustCInterop
title: C és Rust interoperabilitás beágyazott (no_std) rendszerekben
tags: rust c ffi interop embedded no_std
authors: Molnár Ferenc Tamás
---

# C és Rust interoperabilitás vizsgálat beágyazott (no_std) rendszerekben

A vizsgált feladat: két minimális példaprojekt elkészítése a Rust/C interoperabilitás
összehasonlítására beágyazott rendszerek esetén. Az első (1) egy C `main()`
függvény hívjon egy `no_std` Rust statikus könyvtárat, illetve (2) egy
bare-metal `no_std` Rust firmware hívjon egy C könyvtárat, továbbá a
Rust és C memóriaelrendezés közötti különbségek bemutatása az FFI határon,
valamint a két irány bináris méretének és megvalósítási komplexitásának
összehasonlítása. Használt MI eszköz: Claude Code (Claude Sonnet 5), egy
agentikus kódoló asszisztens shell és fájlhozzáféréssel. Nem csak forrást
írt, hanem buildelt, linkelte és ténylegesen futtatta mindkét
példát, nem csupán olyan kódot adott, ami "elméletileg" működik.

## Tanulságok

- Ha a Rust statikus könyvtár a hívott fél (egy `no_std` statikus könyvtár egy meglévő,
  hosztolt C build-be linkelve), az szinte probléma nélkül megvalósítható,
  `#[repr(C)]`/`extern "C"`/`#[no_mangle]` segítségével, illetve egy szokásos
  `cargo build`. Ha viszont a Rust birtokolja a `main`-t bare metal
  környezetben, ott van a valódi komplexitás: kézzel írt vector table,
  reset handler (`.bss`/`.data` inicializálás) és linker script. Ezek
  egyike sem FFI-specifikus, hanem a `#![no_main]` bare-metal ára.
- Minden típusnak, ami átmegy az FFI határon, `#[repr(C)]`-nek kell lennie,
  a sima Rust struct-oknak nincs garantált elrendezésük. A "fat"
  pointereknek (`&[T]`, `&str`) nincs C megfelelőjük, ezeket nyers pointer és explicit hossz párra kell bontani.
- A bináris méret összehasonlításnál ugyan arra a targetre, 
  illetve ugyan azzal az optimalizációs szinttel kell fordítani a két eshetőséget.
  Az első próbálkozás alapján egy hosztolt Windows
  exe-t (46 KB, jórészt `printf` overhead) hasonlított össze egy
  bare-metal ARM ELF-fel (2 KB), és ezt Rust-vs-C méretösszehasonlításnak
  nevezte, de már csak a méret különbségből is adódott hogy a függvények,
  a target és az optimalizációs szint sem egyezett a két projektben.
  Ezután egy újabb prompttal sikerült ugyan azokkal a függvényekkel, 
  ugyan arra a targetre, ugyan azzal az optimalizációs szinttel elkészítenie a projekteket.
- Ezen az összehasonlításon a C bizonyult tömörebbnek: egy egyszerű,
  más függvényt nem hívó ("leaf") függvény C-ben 4 byte bináris kódra
  fordult, ugyanaz a függvény Rust-ban 8 byte-ra, pontosan a duplájára.
  Az okát több prompttal próbáltam megkerestetni a Claude-al, és megkértem hogy dokumentálja:
  
  Először egy ígéretesnek tűnő fordítói kapcsolót próbált
  (`-C force-frame-pointers=no`, ami elvileg kikapcsolja a "frame
  pointer" mentését, ez egy extra utasítás-pár a függvény elején és
  végén, ami a hívási verem (call stack) nyomon követését segíti, pl. hibakereséshez),
  de ennek semmilyen hatása nem volt a lefordított kódra. Ezután a
  `--emit=llvm-ir` kapcsolóval kiíratta, hogy a fordító belsőleg milyen
  tulajdonságokat rendel az adott függvényhez, és itt látszott, hogy
  minden Rust-függvényen ott van a `"frame-pointer"="all"` beállítás,
  vagyis a fordító mindig elmenti ezt a frame pointert, függetlenül
  attól, hogy szükség van-e rá. Kiderült, hogy ez nem egy kikapcsolható
  opció, hanem bele van égetve magába a `thumbv7em-none-eabihf` nevű
  célplatform (target) Rust-beli definíciójába, azért, hogy beágyazott
  rendszereken hiba esetén is lehessen hívási verem szerinti
  visszafejtést (stack backtrace-t) készíteni, még akkor is, ha egyébként
  a teljes hibakezelési infrastruktúra (unwind tábla) ki van kapcsolva.
  Emiatt semmilyen, a fordítási parancsban megadható kapcsoló nem tudja
  ezt felülbírálni. A tényleges javításhoz egyedi target-specifikációt
  (JSON fájlt) kellene írni, és azzal újra le kellene fordítani a Rust
  standard könyvtár egy részét (`core`) is a `-Z build-std` kapcsolóval,
  ehhez viszont egy kísérleti ("nightly") Rust fordító kellene, ami nem
  volt telepítve. Mivel a nyereség mindössze 4 byte lenne
  függvényenként, ami egy valós, nagyobb programnál elhanyagolható, ezt
  a lépést nem hajtotta végre.

- A Claude Code saját maga telepítette a hiányzó eszközláncokat, amikor
  szükség volt rá (`rustup target add`, az ARM GNU Toolchain `winget`-tel),
  és a helyességet úgy ellenőrizte, hogy `arm-none-eabi-gdb`-t csatlakoztatott
  a QEMU gdbstub-jához, és kiolvasta a ténylegesen kiszámolt eredményt a
  RAM-ból, nem elégedett meg azzal, hogy "lefordul" vagy "elindul"
  összeomlás nélkül.
- Készíttettem vele egy README-t az egész folyamathoz, hogy dokumentálja a feladatokat, néha kicsit bonyolultra sikerült a magyarázat kezdők számára, ezért ha saját dokumentációt kérünk        LLM-ektől érdemes neki előre beadni hogy viszonylag érthetővé tegye, hogy felhasználóbarátabb legyen. Angol nyelven írta alapértelmezetten, viszont az elrendezés és a formálás igényes és szépre sikerült.

## Az eredmény használata

A teljes működő kód és a részletes leírás ezen fájl mellett található:

- [`c_calls_rust/`](c_calls_rust) — C `main()` hív egy `no_std` Rust
  statikus könyvtárat (hosztolt, ezen a gépen lefordítva és lefuttatva).
- [`rust_calls_c/`](rust_calls_c) — bare-metal `no_std` Rust firmware hív
  egy C könyvtárat egy Cortex-M4-en, QEMU alatt elindítva és ellenőrizve.
- [`README.md`](README.md) — a teljes memóriaelrendezés-összehasonlítás,
  a build lépések mindkét irányhoz, valamint a méret/komplexitás
  összehasonlítás részletesen. Ez teljes egészében a Claude code generált dokumentációja.

Aki reprodukálni szeretné: először olvassa végig a `README.md`-t, abban
megtalálható a pontos parancssor, és a használt toolchain verziók.

## A munkafolyamat tanulságos részletei

**1. prompt** — "I need to compare Rust and C interoperability in embedded
systems. Please write 2 different codes: C main call Rust library and
Rust main call C library. It has to be no_std Rust, minimalizing the
binary size. Please outline the differences and walk me through the
steps."
Mindkét könyvtár elkészült. A C-call-Rust irány azonnal lefordult és
lefutott, de egy valódi problémába ütközött: az első linkelés
"undefined reference" hibákkal állt le, ami hiányzó szimbólumnak tűnt,
valójában azonban architektúra eltérés volt. A telepített `gcc`
32 bites MinGW volt, míg a Rust statikus könyvtár 64 bites target-re
készült. 
A Rust-hívja-C bare-metal irányt QEMU szoftver segítségével akarta tesztelni,
ami nem volt megtalálható a számítógépemen, ezért a következő promptnál arra
kértem próbálja meg mégegyszer, telepítés után.

**2. prompt** — "Now QEMU is installed, try again."
A QEMU már telepítve volt, de az `arm-none-eabi-gcc` még nem. Ezt a Claude felajánlotta hogy telepíti magától.
A telepítés után a firmware lefordult, linkelődött és elindult a QEMU-ban.
`arm-none-eabi-gdb`-vel ellenőrizte egy breakpoint elhelyezésével
hogy a firmware elmenti az eredményeit, majd egy nyers
memóriakiolvasás megerősítette a pontos várt értékeket, ami valódi bizonyíték
a helyes futásra, nem csak egy tiszta elindulásra.

**3. prompt** — "The binary size comparison? Which is higher than the
other one or which needs more complexity."
Itt csúszott el a folyamat, a bináris összehasonlításhoz kellett még egy prompt. A különböző
target (hosztolt PE vs. bare-metal ELF) miatt a számok nagyságrendileg eltértek, és miután ezt a 
Claude is észrevette azután újragenerálta a teljes feladatot hogy minden egyezzen az összehasonlításhoz.
Itt derült ki a 4 kB vs 8 kB végeredmény amit az elején már ismertettem, ezért 
megkértem arra a Claude-ot a következő promptban hogy derítse ki az okát a dupla akkora bináris méretnek,
és adjon megoldást arra hogy tudnánk a Rust kódot összezsugorítani a C bináris méretére.

**4. prompt** — "How could we shrink Rust code to match with C?"
A `--emit=llvm-ir` kiíratásával megnézte a tényleges függvény-attribútumokat,
és megtalálta a valódi okot (`"frame-pointer"="all"`, a target
specifikáció kényszeríti ki). A megoldás (egyedi
target + nightly) lett volna, és ezt már nem kértem tőle, csak hogy a README-ben dokumentálja a végrehajtás helyett.

**Tanulság jövőbeli C/Rust interop munkához:** linkelés előtt ellenőrizni kell,
hogy a C fordító architektúrája megegyezik-e a Rust `--target`
triplet-jével. Amikor Rust vs. C dolgokat hasonlítunk össze (méret,
sebesség), fixen kell tartanunk a target-et és az optimalizációs flageket, és
először a lehető legkisebb, egyeztetett példát teszteljük. Ha beágyazott kódot generáltatunk, szükséges lehet minden target,
toolchain, stb információt átadni a Claude-nak, és úgy kevesebb prompttal is sikerülhet egyszerű vizsgálatokat készíttetni.
