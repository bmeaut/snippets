---
layout: default
codename: 1100_ConsultationSentimentMap
title: Lakossági konzultációk hangfelvételéből átirat, szentimentelemzés és problématérkép AI-ágenssel
tags: snippets mieset
authors: Dongó Tamás
---

# Lakossági konzultációk hangfelvételéből átirat, szentimentelemzés és problématérkép AI-ágenssel

Az esettanulmány azt mutatja be, hogyan lett két, egyenként közel kétórás településtervezési konzultáció hangfelvételéből kereshető átirat, szentimentelemzés, konkrét problémalista és interaktív problématérkép. A konzultációk egy magyar kisváros új településtervéhez kapcsolódtak. Az egyiken civil szervezetek, a másikon helyi intézmények és vállalkozások képviselői vettek részt. A beszélgetéseket egyetemi oktató moderálta, én a szervező csapat tagjaként voltam jelen.

A feldolgozást egy AI-ágenssel (Claude) végeztem, beszélgetés formájában. A kiindulópont két MP3-fájl és egy mondat volt: *„Tudsz készíteni egy átiratot a hangfelvétel alapján?”*. Ezt követte: *„Tudsz egy ugyanolyan szentimentelemzést készíteni ehhez, mint ami az előző beszélgetésben is elkészült?”*. Az előző beszélgetésben egy közösségimédia-csoport írott bejegyzéseit elemeztük. Az ágens a kész dashboard szerkezetét vette át, de a módszert a beszélt nyelvhez kellett igazítania.

Az eredmények megbízói titoktartás alá esnek, ezért ez a leírás a települést, az időpontokat, a résztvevőket és a konkrét eredményeket nem tartalmazza. A hangsúly azon van, hogyan dolgozott az ágens, hol hibázott, és hol volt szükség emberi döntésre. A közzétett kód kitalált példaadatokon futtatható.

## Tanulságok

- **A hangfelvétel nehezebb nyersanyag, mint az írott szöveg.** A gépi átirat a tiszta, egyszemélyes szakaszokban (moderátori bevezető, hosszabb hozzászólások) jól olvasható. A közbeszólásoknál, az egyszerre beszélésnél és a csoportos feladatoknál (képválasztás, térképre ragasztás) viszont alig használható. A helyi hely- és személyneveket a modell rendszeresen félrehallja, de mindig hasonló módon, ezért egy javítólistával jól kezelhetők.
- **A javítólista maga is hibát okozhat.** A félrehallásokat az ágens reguláris kifejezésekkel javította. Az egyik szabály egy gyakori szakszó félrehallott alakját tulajdonnévvé alakította, mert az ágens a szót először névnek gondolta. Ez csak az átirat olvasásakor derült ki, ezután az ágens a dokumentumban és a listában is javította. A tanulság: a javításokat ugyanúgy szúrópróbával kell ellenőrizni, mint egy kulcsszavas keresést.
- **Ugyanaz a dashboard, más módszer.** Az írott bejegyzéseknél több ezer elem volt, ezért gépi osztályozó kellett, és azt validálni kellett. Itt egy-egy konzultáció 300 körüli elemzési egységből áll, ezért az ágens mindet egyenként elolvasta és kézzel címkézte. Ez a szövegkörnyezet miatt pontosabb (irónia, egymásra reagáló hozzászólások), de nincs mögötte független mérés. A címkézés és a problémák megfogalmazása is ugyanattól az AI-tól származik.
- **A beszélőket nem lehet szétválasztani.** A gépi átirat nem jelöli, ki beszél. Az ágens ezért minden egységet a tartalma alapján sorolta a moderátorhoz és a szervező csapathoz, a résztvevőkhöz, vagy vegyes (párbeszéd) kategóriába. Ez a szerepek szintjén jól működik, mert a moderátor tájékoztat és kérdez, a résztvevők panaszkodnak vagy javasolnak. Személyekre lebontani viszont nem lehet.
- **Az összehasonlíthatóság a módszerből jön.** Mivel mindkét konzultációt ugyanazzal a módszerrel és ugyanazzal a dashboard-szerkezettel dolgoztuk fel, a két résztvevői kör hangulata, témái és a beszélgetések íve közvetlenül összevethető. Ugyanaz a moderátor és ugyanaz a tervezési anyag mellett a különbségek a résztvevők érintettségéről árulnak el valamit. Ez önmagában hasznos visszajelzés a tervezőknek.
- **A homokozó korlátai itt is alakították a munkát.** A modellmegosztó oldal nem volt elérhető, a teljes felvétel nem fért a memóriába, a háttérben indított folyamatokat pedig a környezet leállította. Az ágens mindhárom akadályt megkerülte (részletek lent), de ezek a megoldások jelentős időt vittek el a munkamenetből.

## Adatvédelem és titoktartás

A hangfelvétel és az átirat személyes adat. A résztvevők név szerint és szervezetük megnevezésével mutatkoztak be, a hangjuk is azonosító adat. Az intézmények képviselői a szerepük alapján egy kisvárosban akkor is könnyen azonosíthatók, ha a nevük nem szerepel. A résztvevők tudtak a felvételről: a moderátor jelezte, hogy felvétel készül, és hogy az összefoglalót a résztvevőknek is visszaküldi.

Ehhez jön a megbízói titoktartás: az eredmények a településtervezési folyamat részei, és a megbízó hozzájárulása nélkül nem közölhetők. Ezért a snippet sem nyers adatot, sem összesített eredményt, sem dashboardot nem tartalmaz, csak a módszert és a kódot.

Az ágens munkája közben is figyelt az adatminimalizálásra:

- a dashboard problémakártyáin a munkaváltozatban rövid idézetek szerepeltek, a továbbadható változatba viszont csak saját szavas összefoglalók kerülnek;
- az egységenkénti címkefájl csak időpontot, szerepet, hangulatot, problémát és helyet tartalmaz, szöveget nem, így az összesítések a nyers átirat nélkül is újraszámolhatók.

Az automatizált feldolgozás nem mentesít a GDPR alól: a kezeléshez jogalap kell (itt a tervezési egyeztetés dokumentálása és a kutatás), az AI-szolgáltató adatfeldolgozóként kezeli a felvételt, a nyers adatot pedig a munka végén törölni kell. A gépi átirat az ágens munkakörnyezetében futó nyílt modellel készült, a felvételt külön átíró szolgáltatásnak nem küldtük el. A felvétel és az átirat ugyanakkor az AI-szolgáltató felhős környezetébe került, az átirat szövegét pedig a nyelvi modell dolgozta fel.

## A folyamat felépítése

### 1. fázis: Gépi átirat

Az ágens a [faster-whisper](https://github.com/SYSTRAN/faster-whisper) könyvtárral, a Whisper large-v3-turbo modell 8 bites változatával készítette az átiratot, processzoron, mert a környezetben nem volt GPU. Közben három akadályba ütközött:

1. **A modell letöltése.** A modellmegosztó oldal (Hugging Face) nem volt elérhető a homokozóból. Az ágens a GitHubon talált egy nyilvános tükröt, ahol a modellfájl több darabra vágva szerepelt. Letöltötte és összefűzte a darabokat, majd egy rövid mintán kipróbálta a kis és a nagy modellt, és a pontosabb nagyot választotta.
2. **Memória és háttérfolyamatok.** A teljes felvétel egyben nem fért a memóriába, a folyamat leállt. A háttérben indított futtatást pedig a környezet a parancs végén leállította. A megoldás: az ágens a felvételt 10 perces darabokra vágta, a futtatást a környezet saját háttérfeladataként indította, és a szkriptet folytathatóra írta (a kész darabokat kihagyja).
3. **Dekódolási hiba.** A faster-whisper beépített hangdekódolója hibát adott. Az ágens ezért a darabokat előre 16 kHz-es WAV-ba konvertálta, és közvetlenül, nyers mintaként olvasta be.

Az átirat egy szerkeszthető dokumentumba került, húszperces szakaszokban, percenkénti időbélyegekkel. Az ágens kiszűrte a Whisper ismert hibáját, a „hallucinációs hurkokat”: egy rövid mondat néha tucatszor ismétlődik egymás után, ott is, ahol a felvételen csak egyszer hangzott el.

### 2. fázis: Elemzési egységek és kézi címkézés

Az átirat szegmensei egyenetlen hosszúak (egy szótól egy bekezdésig). Az ágens ezért 20–25 másodperces egységekbe vonta össze őket. Új egység kezdődik, ha az aktuális 25 másodpercnél hosszabb lenne, vagy ha 3 másodpercnél hosszabb csend van. Így egy kétórás konzultációból 300 körüli egység lett.

Ezután minden egységet egyenként elolvasott, és négy címkét adott:

- **Hangulat:** negatív, semleges vagy pozitív. A „negatív” a hangvételt jelenti (panasz, kritika, bizalmatlanság), nem azt, hogy a felvetés alaptalan.
- **Szerep:** moderátor és szervező csapat, résztvevő, vagy vegyes.
- **Problémák:** a konzultációra összeállított kódkönyv témái közül egy vagy több.
- **Helyek:** a megnevezett városrészek, utcák és nevezetes helyek.

A kódkönyvet az ágens az átirat elolvasása után állította össze, konzultációnként másfél tucat körüli témával, és minden témához saját összefoglalót írt arról, mi hangzott el és mit kérnek a résztvevők. A két konzultáció kódkönyve azért különbözik, mert a két résztvevői kör más ügyekről beszélt. A témákat négy-négy témakörbe sorolta.

### 3. fázis: Dashboard

A dashboard szerkezete a korábbi, írott bejegyzéseken alapuló elemzését követi:

- **kulcsszámok:** egységek, a résztvevők aránya a beszédidőből, negatív és pozitív résztvevői arány;
- **problémakártyák:** összefoglaló, kérések, helyszínek, és egy kis oszlopdiagram arról, a beszélgetés mely szakaszában került elő a téma;
- **problématérkép:** a megnevezett helyek; a körök mérete az említések számát, színük erőssége a negatív arányt mutatja;
- **hangulat szereplők szerint:** moderátor, résztvevők, vegyes szakaszok;
- **a beszélgetés íve:** negatív és pozitív arány tízperces szakaszonként;
- **témakörök és húszperces szakaszok** táblázata.

A második konzultációnál az ágens az első dashboardját vette alapul, és csak az adatokat, a kódkönyvet és a szövegeket cserélte. A térképhez a korábbi elemzéshez letöltött OpenStreetMap-alaptérképet használta újra. A beszélgetés íve bizonyult a leginformatívabb nézetnek: jól látszik rajta, hogy a hangulat a moderátori bevezető után, a hozzászólások megnyitásával hogyan változik, és mely témáknál fordul.

### 4. fázis: Átadás

Mindkét dashboardból az ágens egy-egy önálló HTML-fájlt is készített, amely beágyazva tartalmazza az adatokat és a rajzoló könyvtárat (d3), így internet nélkül is megnyílik, és továbbítható. Átadás előtt fej nélküli böngészőben tesztelte, hogy hiba nélkül renderel-e.

## Hibák és hibakeresés

### A más dashboardból átvett térkép

A második dashboard térképe eleinte nem töltődött be. Az ágens az alaptérképet a korábbi elemzés dashboardjából akarta átmásolni, de a másolást a környezet elutasította, mert abba a dashboardba mások is írtak. Ezért az ágens a régi fájl címére hivatkozott, ami az új dashboardból nem volt elérhető (404-es hiba). A megoldás: kiolvasta a fájl tartalmát, ellenőrző összeggel (SHA-256) megnézte, hogy azonos-e az eredetivel, és újra feltöltötte az új dashboardhoz. A tanulság: a jogosultsági határok a felületen nem látszanak, csak futtatáskor derülnek ki.

### Szerepbesorolás a vegyes szakaszokban

A csoportos feladatoknál (helyek berajzolása a térképre, képválasztás) a moderátor és a résztvevők felváltva, gyakran egyszerre beszéltek, a gépi átirat pedig ezeknél a legrosszabb. Az ágens ezeket nem erőltette egyik szerephez sem, hanem „vegyes” kategóriába tette, és túlnyomóan semlegesnek címkézte. Ez a résztvevői arányokat kissé torzíthatja, de kisebb hiba, mint a téves hozzárendelés.

## Kód

- [`code/`](code/): az átirat, a javítólista, az egységképzés és az összesítés szkriptjei, valamint egy [README](code/README.md) a futtatási sorrenddel, a címkeformátummal és a kimeneti fájlok leírásával.
- [`example/`](example/): egy hatsoros, kitalált példa (egységek és címkék). A [`code/codebook_example.py`](code/codebook_example.py) kitalált kódkönyvével együtt a lánc ezen kipróbálható.

A kódot az AI-ágens írta a munkamenet során. A közzétételhez utólag rendeztük futtatható formába. Kutatási prototípus, nem karbantartott szoftver.

### Adatelérhetőségi nyilatkozat

A hangfelvételek és az átiratok személyes adatokat tartalmaznak, az eredmények pedig megbízói titoktartás alá esnek, ezért egyiket sem tesszük közzé. A nyers adatokat a munka idejére védett tárhelyen őrizzük, és a lezárásakor töröljük. A kód saját, jogszerűen rögzített felvételeken újrafuttatható.

## Korlátok

- **Nincs független validálás.** A hangulati címkéket egyetlen AI-címkéző adta, a pontosságukat emberi címkézővel nem mértük. Ha az eredményeket döntés-előkészítésre használják, egy kis mintát érdemes emberrel is ellenőriztetni.
- **A gépi átirat hiányos.** Az egyszerre beszélős, közbeszólós részek egy része érthetetlen. Ezeknél a címkézés a kivehető tartalomra épül.
- **Egy-egy konzultáció kis minta.** Mindkét alkalmon kevés résztvevő volt, így egy-egy aktív felszólaló sokat mozdít az arányokon. Az eredmény a jelenlévők hangja, nem a településé.
- **A problémaleírások az AI összefoglalói.** Mielőtt hivatalos dokumentumba kerülnének, érdemes őket az átirattal összevetni.
