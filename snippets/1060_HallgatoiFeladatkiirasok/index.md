---
layout: default
codename: HallgatoiFeladatkiirasok
title: Változatos hallgatói szoftverfejlesztési feladatok készítése stílusminta alapján
tags: snippets mieset
authors: Kövesdán Gábor
---

# Változatos hallgatói szoftverfejlesztési feladatok készítése stílusminta alapján

Szoftverfejlesztést tanuló hallgatók számára öt alkalmazás feladatkiírását szerettem volna elkészíteni. A témákat én választottam ki, a megfogalmazáshoz pedig egy meglévő, fuvarozócég adminisztrációjáról szóló mintát adtam a ChatGPT-nek. Azt kértem, hogy az új kiírások kövessék a minta nyelvezetét és részletességét, ugyanakkor mindegyik alkalmazás kapjon néhány érdekes, jelentőségteljes funkciót.

Az ilyen feladatok sok közös elemet tartalmaznak. Gyakran szükséges regisztráció és bejelentkezés, valamilyen adat nyilvántartása, rendezett listázása, keresése és szűrése, esetleg külső szolgáltatás használata. Ez az ismétlődő szerkezet jó alapot ad az MI-vel támogatott szövegalkotáshoz. A kihívás az, hogy a kész kiírások ne csak ugyanazt az adatkezelő alkalmazást írják le eltérő elnevezésekkel.

Ebben a munkamenetben az MI a közös felépítés megfogalmazása mellett a témákhoz illő funkcióötleteket is adott. Így egyszerre szolgálta a követelmények egységességét és a feladatok változatosságát, ami a hallgatók és a konzulensek számára is érdekesebbé teheti a munkát.

**Használt eszköz:** ChatGPT, magyar nyelvű feladatleírással és mintaszöveggel. A munkamenet dátuma 2026. szeptember 16.

## Tanulságok

- **Az ismétlődő követelmények jól újrafogalmazhatók egy adott témára.** A nyilvántartás, a listázás, a keresés és a szűrés több alkalmazásban is megjelenik, csak az adatok és az üzleti szabályok változnak.
- **Egy konkrét minta pontosabban közvetíti az elvárást, mint a „legyen részletes” kérés.** A fuvarozócég feladata megmutatta, milyen nyelvezetet és milyen szintű követelményeket várok.
- **Az MI ötletadóként is hasznos.** A témához illő különleges funkciók segíthetnek abban, hogy a feladat túlmutasson az adatok felvitelén és törlésén.
- **A változatosságot érdemes kifejezetten kérni.** A felhasználó feladata kijelölni, hogy az egyes projektek miben legyenek szakmailag eltérők.
- **Azonos szöveghossz nem jelent azonos nehézséget.** Egy valós idejű többfelhasználós játék, egy OCR-t és nyelvi modellt használó tudástár, valamint egy hagyományos nyilvántartás eltérő terhelést jelenthet.
- **A generált kiírás szerkesztendő alapanyag.** A konzulensnek kell eldöntenie, mi fér bele az időkeretbe, mi kötelező, és hogyan ellenőrizhető a megvalósítás.

## Az eredmény használata

Az öt elkészült feladatleírás további oktatói szerkesztés alapjaként használható. A kiadás előtt át kell nézni a követelmények egyértelműségét, a feladatok terjedelmét, az előzetes tudásigényt és a külső szolgáltatások hozzáférhetőségét.

Hasznos különválasztani a minden hallgatótól elvárt alapfunkciókat és a választható bővítéseket. Az MI által javasolt összetett funkciót így nem szükséges elhagyni, ha túl nagy a kötelező feladathoz: emelt szintű kiegészítésként is megtartható.

## A munkafolyamat tanulságos részletei

### Témákat és stílusmintát adtam egyszerre

Az eredeti kérésben öt témát neveztem meg:

1. Kalóriaszámláló alkalmazás.
2. Szerszámkölcsönző adminisztrációs alkalmazás.
3. Dokumentumtudástár, amely feltöltött dokumentumokat szükség esetén OCR-ez, majd a tartalmuk alapján kérdésekre válaszol.
4. Árukereső jellegű árösszehasonlító oldal.
5. Online póker.

A kérés lényegi mondata így szólt:

> mindegyikhez sorolj fel néhány érdekes és jelentőségteljes funkciót, amelyet meg kell valósítaniuk

Emellett a minta nyelvezetének és részletességének követését kértem. A fuvarozócég mintafeladata többek között telephelyek, járművek, sofőrök, boltok és áruk nyilvántartását, fuvartervezést és külső térképszolgáltatást kapcsolt össze. Ezzel azt is jelezte, hogy az adatkezelés mellé működési szabályok és összetettebb műveletek kellenek.

A prompt így három szinten irányította a generálást: meghatározta az alkalmazások témáját, a szövegek formáját és a funkciók elvárt érdekességét. Nem kellett minden kiírás szerkezetét külön elmagyaráznom.

### A közös követelmények ismétlődése megkönnyítette a generálást

Egy alkalmazás témájának változása sokszor nem változtatja meg teljesen a szükséges szoftveres alapokat. A kereshető lista például ételeket, kölcsönözhető eszközöket, dokumentumokat vagy kereskedői ajánlatokat is tartalmazhat.

| Visszatérő követelmény | Témához igazított megjelenés |
| --- | --- |
| Regisztráció és bejelentkezés | Személyes étkezési napló, ügyfélfiók vagy játékosprofil hozzáférése. |
| Adatok létrehozása és módosítása | Ételek, eszközök, dokumentumadatok vagy termékajánlatok kezelése. |
| Rendezett listázás | Napi bejegyzések, foglalások, dokumentumok vagy árak áttekintése. |
| Keresés és szűrés | Tápérték, elérhetőség, dokumentumtartalom vagy terméktulajdonság alapján. |
| Jogosultságkezelés | Felhasználói, adminisztrátori vagy dokumentum-hozzáférési szerepkörök. |
| Külső integráció | Élelmiszer-adatbázis, OCR, nyelvi modell vagy kereskedői adatforrás. |

Ez a táblázat utólagos összevetés: a lehetséges közös szerkezetet mutatja, nem állítja, hogy minden eredeti kiírás minden felsorolt funkciót tartalmazott. Regisztrációra például nem minden belső adminisztrációs alkalmazásnál ugyanúgy van szükség.

Az MI ilyen helyzetben jól tud segíteni az ismert minták következetes megfogalmazásában. A konzulensnek kevesebb időt kell töltenie ugyanazon alapkövetelmények újraszövegezésével, és több figyelme maradhat az alkalmazás saját problémájára.

### A témaspecifikus funkciók adták a szakmai változatosságot

A visszakeresett válaszban az egyes alkalmazásokhoz az alapvető nyilvántartáson túlmutató elemek is megjelentek:

| Téma | A visszakeresett válaszban szereplő funkciópéldák | Az ebből adódó szakmai feladat |
| --- | --- | --- |
| Kalóriaszámláló | Recept- és tápértékszámítás, célok, napló és grafikonok, vonalkódhoz vagy adatbázishoz kapcsolódó integráció. | Számítások és személyes adatok áttekinthető összekapcsolása. |
| Szerszámkölcsönző | Foglalási ütközések, kölcsönzések és késedelmek kezelése, karbantartási jelzések. | Időintervallumok, eszközállapotok és üzleti szabályok kezelése. |
| Dokumentumtudástár | PDF-, szöveg- és képfeltöltés, OCR, szöveges és szemantikus keresés, forrásokat megjelölő válaszok. | Többlépéses dokumentumfeldolgozás és visszakereshetőség. |
| Árösszehasonlító | Ajánlatok összevetése ár, szállítás és készlet szerint; rendszeres árfrissítés és árelőzmény. | Eltérő források adatainak összehasonlíthatóvá tétele. |

Az érdekességet tehát nem pusztán új menüpontok száma jelentette. Egy foglalási ütközés vagy egy dokumentumhoz visszavezetett válasz más gondolkodást igényel, mint egy egyszerű adatlista. Ez a különbség segíthet elkerülni, hogy a hallgató és a konzulens ugyanazt a megoldást lássa új elnevezésekkel.

### Az ötletgazdagságot a megvalósíthatósággal kell összehangolni

A modell sok funkciót tud felsorolni, de a feladatkiírás minőségét nem a lista hossza adja. Ha minden ötlet kötelező, a projekt könnyen túlméretezetté válik. A témák közötti nehézségkülönbséget különösen a külső integrációk és az összetett állapotkezelés növelhetik.

Egy továbbfejlesztett promptban ezért már ezt is rögzíteném:

```text
Az alábbi stílusminta alapján készíts öt hallgatói projektkiírást
a megadott témákra. A közös alap legyen indokolt adatkezelés, rendezett
listázás, keresés és szűrés; felhasználókezelést csak ott írj elő,
ahol az alkalmazás működéséhez szükséges.

Minden témához adj két sajátos funkciót, amelyek valódi üzleti szabályt,
számítást vagy feldolgozási folyamatot valósítanak meg.
Ne csak ugyanazokat a funkciókat nevezd át az öt témára.

A feladatok hasonló időráfordítással legyenek megoldhatók.
Különítsd el a kötelező minimumot és a választható bővítéseket.
A külső szolgáltatásokhoz legyen tesztadatokkal használható helyettesítés.
Minden sajátos funkcióhoz adj egy rövid elfogadási példát.
Ha a hallgatók szintje vagy az időkeret hiányzik, előbb kérdezz rá.
```

Ez új módszertani javaslat, nem az eredeti munkamenet további promptja. Az elfogadási példa arra szolgálna, hogy az olyan általános kérések, mint a „foglaláskezelés”, ellenőrizhető elvárássá váljanak: például ugyanazt az eszközt ne lehessen átfedő időszakra kétszer lefoglalni.

### Az eredmény értékelése

A munkamenetben öt témára készültek feladatleírások egy közös stílusminta alapján. Az MI segítséget adott az ismétlődő követelmények megfogalmazásához és az alkalmazásokat megkülönböztető funkciók összegyűjtéséhez.

Az időmegtakarítás mértékét nem mértem, és a hallgatói fogadtatásról sincs dokumentált eredmény. A felhasználás gyakorlati értéke az, hogy a szerző nem üres lapról indul: egy összevethető, szerkeszthető változatból választhatja ki a szakmailag érdekes és oktatható elemeket.