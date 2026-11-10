---
layout: default
codename: AJBHJelentesLetoltes
title: MI segítségével készített script rendészeti jelentések tömeges letöltésére
tags: snippets mieset
authors: Kövesdán Gábor
---

# MI segítségével készített script rendészeti jelentések tömeges letöltésére

Az Alapvető Jogok Biztosának Hivatala honlapjáról a Rendészeti Főigazgatóság jelentéseit szerettem volna letölteni későbbi elemzéshez. A feladatot megnehezítette, hogy a dokumentumok több, lapozható listaoldalon szerepeltek, és a listában található hivatkozások először külön dokumentumoldalakra vezettek. A tényleges letöltési címeket ezeken az oldalakon kellett megkeresni. Az általam kipróbált böngészős tömeges letöltőbővítmények ezt a folyamatot nem tudták megfelelően kezelni.

Ezért a Claude mesterséges intelligenciát kértem meg egy letöltőprogram elkészítésére. A feladatot angolul írtam le, és külön megadtam a köztes dokumentumoldalakat, a letöltési hivatkozás feliratát és a lapozás követelményét. A generált Python-script használható alapot adott, de a tényleges letöltési cím felismerését kézzel hozzá kellett igazítanom az oldal szerkezetéhez. A módosítást követően a script működött, és le tudtam tölteni a jelentéseket.

**Használt eszközök:** Claude, Python, valamint a generált scriptben a `requests` és a `BeautifulSoup` könyvtárak. A kézi javításhoz a Python reguláris kifejezéseket kezelő `re` modulját használtam. A letöltőscript 2026.07.05. napon készült, a Claude akkori, ingyenes verziójával.

## Tanulságok

- **A feladatban a bejárás menetét is érdemes leírni.** A „töltsd le a PDF-eket” kérés önmagában kevés lett volna: a programnak végig kellett járnia a listaoldalakat, megnyitnia a dokumentumoldalakat, majd kinyernie a tényleges letöltési címeket.
- **Az angol szaknyelv számomra megkönnyítette a specifikációt.** A „pagination”, „main listing page” és „download” kifejezésekkel tömören tudtam leírni a működést. Ez saját munkatapasztalatból eredő választás volt; az esetben nem hasonlítottam össze az angol és a magyar prompt eredményét.
- **A generált kód minőségét korlátozza, mit lát a modell a célrendszerből.** Claude jelezte, hogy nem tudta közvetlenül lekérni az oldalt, ezért annak pontos HTML-szerkezetét sem tudta ellenőrizni. A linkkereséshez általános feltételezéseket használt.
- **Egy dinamikus oldalhoz sem feltétlenül kell teljes böngészőt automatizálni.** Ebben az esetben a szükséges letöltési cím megtalálható volt az oldal forrásába ágyazott adatban, ezért elegendőnek bizonyult a címkinyerés módosítása.
- **A célzott kézi javítás tette használhatóvá a megoldást.** A script általános felépítését megtartottam, és a webhely sajátosságát kezelő függvényt módosítottam.
- **Az egyszeri siker és az általános megbízhatóság külön kérdés.** A javított script az adott feladatra működött, de a webhely szerkezetének változása újabb igazítást tehet szükségessé.

## Az eredmény használata

Az eredmény egy helyben futtatható Python-script volt, amely egy megadott könyvtárba gyűjtötte a jelentéseket. A Claude az alábbi telepítési és futtatási parancsokat adta meg:

```bash
pip install requests beautifulsoup4
python download_ajbh_pdfs.py --out "C:/path/to/folder"
```

A `--out` paraméter a célkönyvtárat jelölte. A beszélgetésben szereplő leírás szerint a script a lapozást is kezelte, és alapértelmezésben legfeljebb 50 listaoldalt járt be. Ez hasznos futási korlát, ugyanakkor önmagában nem garantálja, hogy minden elérhető jelentés letöltődik.

Az esettanulmány a megoldás menetét és a lényegi javítást dokumentálja; önmagában nem teljes, futtatható programcsomag.

## A munkafolyamat tanulságos részletei

### Miért nem volt elegendő egy tömeges letöltőbővítmény

A [jelentések gyűjtőoldalán](https://www.ajbh.hu/rendeszeti-foigazgatosag-jelentesek) a kívánt művelet több lépésből állt. Először fel kellett dolgozni az aktuális listaoldalt, majd minden jelentéshez megnyitni a hozzá tartozó dokumentumoldalt. Csak ezután lehetett elérni a PDF tényleges letöltési címét. A következő listaoldalon ugyanezt meg kellett ismételni.

Az általam próbált bővítmények ebben a helyzetben nem oldották meg a teljes bejárást. Nem egyszerűen az aktuális oldalon közvetlenül elérhető PDF-eket kellett összegyűjteni, hanem a dokumentumoldalakat és a lapozást is kezelni kellett. Egy erre készített scriptben ezt a folyamatot pontosan meg lehetett határozni.

### Angolul írtam le a feladatot

A Claude-nak adott promptom a következő volt:

> Write me a simple program that opens https://www.ajbh.hu/rendeszeti-foigazgatosag-jelentesek and downloads the PDF documents to a specific folder. For this, the links pointing to the .pdf documents needs to be followed and then the "DOKUMENTUM LETÖLTÉSE" link must be clicked. There is also pagination on the main listing page and documents need to be downloaded from each page.

A prompt tartalmazta a kezdő URL-t, a letöltendő fájlformátumot, a célkönyvtár igényét, a köztes navigációt és azt, hogy minden listaoldalt fel kell dolgozni. A magyar felületi feliratot változatlanul hagytam benne, mert ez konkrét kapaszkodót adott a letöltési hivatkozás azonosításához.

Az angol megfogalmazást azért választottam, mert tapasztalatom szerint szoftveres feladatoknál egyértelműbbé teszi a bevett terminológia használatát. Arra számítottam, hogy így a modell is pontosabban értelmezi a követelményeket. Ez itt tudatos promptolási döntés volt, nem annak bizonyítása, hogy a magyar nyelvű feladatleírás szükségképpen rosszabb eredményt adna.

A specifikáció a kívánt működést részletezte, a programozási nyelvet és a könyvtárakat viszont nyitva hagyta. A Claude Python-megoldást választott. A „kattintás” szót is funkcionálisan értelmezte: a javasolt program HTTP-kérésekkel követte volna a hivatkozásokat, nem grafikus böngészőben kattintott.

### A Claude használható alapot adott és jelezte a bizonytalanságot

A Claude a válasz elején közölte, hogy az oldalt nem tudta közvetlenül lekérni, ezért nem tud pontos, ellenőrzött HTML-kijelölőket beépíteni. Ehelyett általános linkfelismerési szabályokra támaszkodó scriptet készített, és jelezte, hogy ezeket a tényleges oldal alapján módosítani kellhet.

A válasz leírása szerint a program:

- lekérte a listaoldalt, és annak fő tartalmi részében kereste a jelentésekre mutató hivatkozásokat;
- megnyitotta a dokumentumoldalakat, és a „DOKUMENTUM LETÖLTÉSE” szövegű linket kereste;
- találat hiányában közvetlen `.pdf`-hivatkozással próbálkozott;
- letöltötte a fájlokat, és lehetőség szerint a kiszolgáló által megadott fájlnevet használta;
- megkereste a következő oldal hivatkozását, ennek hiányában pedig egy feltételezett `?page=N` címzési mintával próbálkozott.

A modell tehát a letöltési feladat általános részeit jól felbontotta. A bizonytalan pontot a webhelyhez kötődő felismerési szabályok jelentették. A Claude a válaszban külön megnevezte ezeket, és konzolkimenetet vagy HTML-részletet kért volna a további pontosításhoz. Én a szükséges javítást végül kézzel végeztem el.

### A tényleges letöltési cím más formában szerepelt az oldalon

A webhely dinamikus felépítése miatt a böngészőben látható letöltési lehetőség nem felelt meg annak az egyszerű hivatkozásnak, amelyet a generált függvény keresett. Az eredeti kód az `<a>` elemek látható szövegét vizsgálta, majd közvetlen PDF-linket keresett.

A javítás során ehelyett az oldal forrásába ágyazott `downloadURL` mezőből nyertem ki a címet. Ehhez hozzáadtam az `import re` sort, és lecseréltem a `find_pdf_download_link` függvény aktív részét. A módosítás lényegi részlete:

```python
html_text = str(soup)
first_match = re.search(
    r"\"downloadURL\":\"https:.{4}www.ajbh.hu.*download=true",
    html_text
)
if first_match is not None:
    url = first_match.group().replace(
        "\"downloadURL\":\"", ""
    ).replace("\\/", "/")
    return url
return None
```

A kód az oldal feldolgozott HTML-jét szövegként vizsgálta, megkereste benne a letöltési címet tartalmazó mintát, eltávolította a mezőnevet, majd a `\/` alakban szereplő perjeleket `/` karakterekre cserélte. Így előállt a letöltéshez használható URL.

Ez azért volt elegendő, mert a szükséges adat már a feldolgozható oldaltartalomban szerepelt. A megoldáshoz nem kellett a böngésző teljes működését vagy a JavaScript által létrehozott felületet reprodukálni.

### A módosítás megmutatja melyik változtatás számított

A módosításban a `DOWNLOAD_LINK_TEXT` értéke is megváltozott, és az eredeti keresési rész egy több soros sztringbe került a korai visszatérések után. Ez a régi rész az új változatban már nem futott le. A működést ezért nem a felirat átírása, hanem a `downloadURL` közvetlen kinyerése tette lehetővé.

Nem volt szükséges lapozási javítást eszközölni. A kézi beavatkozás a letöltési cím felismerésére korlátozódott.

A reguláris kifejezés az adott forrásszerkezetre szabott, gyakorlati megoldás volt. Nem általános adatfeldolgozó: például a `.*` mintarész több karaktert is befoghat, ha az oldalon több hasonló adat szerepel, a mező formátumának változása pedig megszüntetheti a találatot. Az adott feladatban működött, de hosszabb távú használatnál ezt a részt is ellenőrizni kellene.

### Az MI és a kézi módosítás együtt vezetett eredményre

A módosításokkal a script működött, és lehetővé tette a jelentések letöltését a tervezett elemzéshez.

A Claude adta a program általános megoldását: a listaoldalak feldolgozását, a dokumentumoldalak követését, a letöltést és a lapozási stratégiát. Nekem a webhely konkrét adatformátumát kellett felismernem és beépítenem. Ez a munkamegosztás használható kiindulópontot adott, miközben az oldalhoz kötődő döntő részlethez saját technikai ellenőrzésre és javításra volt szükség.
