---
layout: default
codename: MobileManualTesting
title: Mobilalkalmazások manuális tesztelése Claude Code-dal emulátoron és szimulátoron
tags: snippets mieset
authors: Domonkos Ádám
---

# Mobilalkalmazások manuális tesztelése Claude Code-dal emulátoron és szimulátoron

Claude Code-dal, Sonnet 5.5 modellel egy natív iOS és Android PDF nézegető és szerkesztő könyvtár demó alkalmazásait teszteltem "manuálisan". Az agent maga fordította és futtatta az alkalmazásokat egy Android emulátoron és egy iOS szimulátoron, illetve generálta a tesztfájlokat, navigált a felületen. A képernyőképekből és a logokból pedig hibákat keresett. A fő feladat a megjelenítés ellenőrzése volt, különböző méretű és hosszúságú PDF fájlokkal kellett ellenőrizni, hogy a tartalom nemcsak megjelenik, hanem simán mozog és élesen, olvashatóan renderelődik.

A munka nagyjából egy órát vett igénybe, és jóval több valódi hibát talált, mint amennyit egy gyors kézi kipróbálás során vártam.

---

## A feladat

A könyvtár és a demó alkalmazás már működött mindkét platformon, egy jelentős funkciókészlettel. A feladat az volt, hogy az alkalmazásokat az agent kézzel (vagyis a felületen keresztül, nem tesztekkel) végigteszteli, különös tekintettel a megjelenítésre. A következő szélsőséges eseteket hoztam fel tesztelésre:

- normál PDF-fájlok
- változó oldalméretű PDF-fájlok
- nagyon sok oldalas PDF-fájlok
- kis oldalméretű PDF-fájlok
- hatalmas oldalméretű PDF-fájlok

Az elvárás nem csak a működés volt, hanem az is, hogy a megjelenítés sima és éles legyen, így a tartalom kényelmesen olvasható maradjon.

---

## Használt modellek és technológiák

| Réteg | Választás |
|-------|-----------|
| Fejlesztőeszköz | Claude Code (Sonnet 5.5), a Claude desktop alkalmazásban |
| Android | Android Studio emulátor (Pixel 9a AVD, Android 16), `adb`, `logcat`, `dumpsys gfxinfo`, Perfetto |
| iOS | iPhone 16 Pro szimulátor (iOS 18.4), `xcrun simctl`, beépített szimulátor-vezérlő eszköz |
| Teszt PDF-ek | Saját, függőségmentes Python szkript (nyers PDF-szintaxis) |
| Referencia renderelés | Poppler (`pdftoppm`, `pdfinfo`, `pdffonts`) |
| Segédeszközök | Python venv (`grpcio`, `Pillow`, `perfetto`, `numpy`), az emulátor gRPC-vezérlése |

---

## Az indító prompt

A munkamenet egyetlen, viszonylag tág kéréssel indult:

```text
In this repository a pdf editor and view library had been implemented with a usable
demo application for both android and ios.

They have an extensive pdf functionality set:

1. ...
2. ...
3. ...
...

Manually test both applications features extensively by running on an android emulator and on ios simulator. Especially test the rendering part if works with all kinds of pdf files:

1. Normal pdf files
2. Pdf file with varying page sizes
3. pdf files with a huge page number
4. pdf files with small page sizes
5. pdf files with huge page sizes

Make sure that the applications not just works, but works and renders smoothly and sharply so the page content is convenient to read.
Feel free to ask clarification questions
```

Az agent ezúttal nem tett fel kérdést, rögtön nekiállt, és a feladatból maga vezette le a szükséges lépéseket. Először felmérte, milyen emulátor, szimulátor és PDF-eszköz van a gépen, majd erre építette a tesztelést.

---

## A munkafolyamat

### 1. Eszközök és tesztadatok előkészítése

Az első lépésben az agent felmérte, hogy a szükséges ellenőrzések futtatásához mire lesz szüksége, majd összeszedte az ezekhez szükséges eszközöket:
- ellenőrizte az elérhető szimulátorokat és az Android SDK-t, majd elindította az emulátort, és a két alkalmazást lefordította és telepítette;
- a gépen nem volt PDF generáló könyvtár, ezért egy sajátot írt. Egy Python szkriptet, amellyel pontosan szabályozható volt az oldalméret, az oldalszám és a tartalom;
- minden oldalra szöveget, finom rácsvonalakat, oszlopdiagramot, vékony spirált, színes sarokjelölőket, vonalzót és apró lábjegyzetet tett, így egy képernyőképből látszott az élesség, a vágás és az elforgatás;
- 9 fájlt készített: normál A4 (10 oldal), vegyes méretű (15 oldal, `/Rotate` és CropBox is), 3000 oldalas, kis oldalméretű (10×10-től 252×144 pontig), hatalmas oldalméretű (A0-tól 14400×14400 pontig), 400 oldalas vegyes, valamint két külön fájl további, a funkciókhoz tartozó teszteléshez.

### 2. Bemenet szimulálása

Itt jelentkezett az első komoly akadály. Az `adb input` csak koppintást és húzást tud, a nagyításhoz viszont két ujjas mozdulat kell. Az agent először `sendevent`-tel próbálkozott, majd átállt arra, hogy az emulátort gRPC-porttal indítja újra, lefordította az emulátor `.proto` fájlját, és egy kis szkriptet írt, amellyel valódi, két ujjas csípőmozdulatok indíthatók. iOS-en erre beépített eszköz volt (`touch2_path`), a PDF-eket pedig `simctl openurl`-lel lehetett közvetlenül megnyitni, Androidon a rendszer fájlválasztóján keresztül.

### 3. Hibakeresés a képernyőképektől a nyomkövetésig

Ahol valami furcsának tűnt, az agent mélyebbre ásott: `logcat` a kivételekhez, `dumpsys gfxinfo` a képkockaidőkhöz, `Perfetto`-nyomkövetés a főszál és a renderszál terheléséhez, a mentett PDF-ek visszahúzása és Poppler-rel való kirenderelése a mentés helyességének ellenőrzéséhez. Az élesség ellenőrzéséhez a képernyőkép szövegsorainak távolságából kiszámolta az aktuális nagyítást, ugyanazzal a nagyítással kirenderelte ugyanazt a PDF-részletet Popplerrel, és a kettőt egymás mellé téve hasonlította össze.

---

## Mit talált?

A teljes jegyzék hosszú, ezért csak a legfontosabb kategóriákat emelem ki.

- **Dokumentumok kezelése Androidon.** Egy nagy PDF megnyitása a főszálon történt, ez az emulátoron kb. 20 másodpercre lefagyasztotta az alkalmazást (ANR). Egy hibás, 0 bájtos importált fájl pedig összeomlást okozott ahelyett, hogy hibaüzenetet jelenített volna meg.
- **Nagy méretű oldalak kicsinyítése Androidon.** A 14400×14400 pontos oldalak áttekintő nézetében telítették a renderszálat és ANR-t okoztak. A szokásos A4 és A3 méretek rendben voltak. iOS-en ugyanez gond nélkül futott.
- **Élesség.** Androidon bizonyos nagyítási szinteknél nem volt elég éles a megjelenített dokumentum a renderelő rétegben lévő bug miatt.
- **Mentés és exportálás.** Bizonyos, kiegészítő megjelenítési adat nélküli beviteli mezők értéke Androidon elveszett a mentett példányból, ami csak a mentett fájl kirenderelésekor derült ki, a képernyőn minden rendben látszott.
- **Használhatósági apróságok.** Androidon a mentési ablakban az alapértelmezett fájlnév a belső azonosító volt a dokumentum címe helyett, iOS-en a szerkesztő eszköztár egy része hozzáférhetetlenül, a képernyőn kívül, görgetési jelzés nélkül volt.

A javítást ebben a munkamenetben nem kértem, az agent csak jelentést készített, a kódot nem módosította.

---

## A jó részek

- **Az eszközépítés magától jött.** A modellnek nem kellett megmondani, hogy hogyan generáljon tesztfájlokat, hogyan szimuláljon csípőmozdulatot, vagy hogyan mérjen. Ha az egyik megközelítés elbukott (`sendevent`, `simctl` fájlnyitás Androidon), azonnal alternatívát keresett.
- **Önkorrekció a mérésekből.** Az agent az első hipotézisét többször is megcáfolta. Az Android ANR-ről eleinte azt írta, hogy a főszál 50 másodpercre blokkolt, a Perfetto-nyomkövetés viszont megmutatta, hogy a főszál szinte tétlen, a renderszál volt túlterhelve. Hasonlóan, a 3000 oldalas dokumentumnál először egy konkrét funkciót gyanúsított, de újra megnyitva kiderült, hogy maga a dokumentum megnyitása volt a gond, és ezt javította a jegyzetében.
- **A teszteszköz és a tesztelt rendszer megkülönböztetése.** Amikor a szimulátor szövegbeviteli eszköze magyar ékezetes betűket elrontott, az agent ezt az eszköz hibájának minősítette, és nem jelentette az alkalmazás hibájaként.
- **Strukturált jegyzetek.** A munkamenet közben folyamatosan vezetett egy jegyzetfájlt a megerősített és a még ellenőrzendő megfigyelésekről, így a végén használható összefoglalót tudott írni.
- **Valódi, reprodukálható hibák.** A talált problémák többsége pontosan lokalizálható volt (fájl, függvény, ok), nem csak egy "lassúnak tűnik" jellegű benyomás.

---

## Nehézségek és korlátok

- **A teszteszköz is hibaforrás volt.** Az emulátor alapbeállításai (2 GB RAM, 4 mag) mellett önmagától újraindult, és olyan ANR-eket mutatott, amelyek részben a gép terheléséből jöttek. Emiatt újra kellett konfigurálni (4 GB, 6 mag, GPU a gazdagépen), és a korábbi mérések egy részét eldobni.
- **A képkockaidők nem mérvadók.** Az emulátoron még a rendszer Beállítások alkalmazása is ~85%-ban akadozónak mérődött, ezért a mozgás simaságáról csak relatív összehasonlítás mondható, abszolút állítás nem. Valódi eszközön való ellenőrzés kimaradt.
- **A saját mérőszám zajos volt.** Az élességet egy gradiens-alapú mérőszámmal és a Poppler-referenciához való viszonyítással is próbálta mérni, de az eredmények iOS-en és Androidon is nagyon szórtak. A döntő a szemmel való, egymás melletti összevetés volt, nem a szám.
- **Lassú, lépésenkénti vezérlés.** Minden koppintás után képernyőképet kellett készíteni és megnézni, hiszen az ANR után a következő beírt szöveg egy teljesen másik alkalmazásba (Naptár) került. Ez sok időt és tokent vitt el, és ellenőrzések nélkül hibákhoz vezetett.
- **Nem teljes a lefedettség.** Több funkció és fájltípus nem került sorra egyetlen körben sem, a munkamenet végére a megjelenítés és a legfontosabb munkafolyamatok kaptak teljes figyelmet.

---

## Összefoglalás

Claude Code remekül használható manuális tesztelésre, ha a feladat köré megvan az ökoszisztéma (emulátor, szimulátor, nyomkövetés), és az agent szabadon építhet hozzá segédeszközöket. A saját tesztadatot, bemenetszimulációt és mérőszkripteket az agent maga írta meg, és ezekkel olyan hibákat talált, amelyeket gyors, kézi kipróbálással valószínűleg nem vettem volna észre.

A korlátok viszont ugyanolyan fontosak. A mérési eredményeknél érdemes mindig megkérdezni, hogy a hibát a tesztelt alkalmazás, vagy a tesztkörnyezet okozta, az emulátor teljesítményszámai nem helyettesítik a valódi eszközös mérést, és a hibák súlyozását továbbra is az embernek kell elvégeznie. A tapasztalatom szerint a legjobb felállás az, amikor az agent előállítja a hibák listáját és a reprodukciós lépéseket, én pedig eldöntöm, hogy melyik igényel javítást.
