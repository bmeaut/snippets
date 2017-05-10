---
layout: default
codename: GitGyakorlat
title: Git gyakorlat
tags: alkfejl git
authors: Csorba Kristóf
---

# Git gyakorlat

Ennek a gyakolatnak a célja a git alapok és, a branchek, mergelés és rebaseelés használatának kipróbálása, gyakorlása.

A gyakorlat során egy Visual Studio alatt, C#-ban fejlesztett alkalmazás fejlesztésében veszel részt, melyet másik két fiktív fejlesztővel együtt fogsz elkészíteni. Az "alkalmazás" egyszerű matematikai műveleteket használ, melyek működését unit tesztekkel is ellenőrizzük. A feladat sikeres elvégzése esetén a master ágon minden unit teszt zöld lesz és lesz közöttük olyan, mely a többi fiktív fejlesztő munkájának eredménye.

Előfeltételek:

  * Telepített [git kliens](https://git-scm.com/)
  * Merge tool (pl. KDiff3)
  * Igény szerint grafikus git frontend (pl. [GitExtensions](https://sourceforge.net/projects/gitextensions/), [SourceTree](https://www.sourcetreeapp.com/)...)

A feladatokhoz további anyagokat találsz az oldal végén.

## 1. feladat: Klónozás és futtatás

  * Klónozd le a [kiinduló repositoryt](UUUURRRRRLLLL). (Éles feladat esetében később rendszeresen ide pusholnád a változásokat, ettől itt most eltekintünk.)
  * Visual Studioban megnyitva a solutiont futtasd le az alkalmazást (Application projekt) és a unit teszteket (Tests projekt).
  * Nézd át a forráskódot! A műveletek a Common (class library) projektben találhatóak, erre hivatkozik az Application és a Tests is.
  * Nézd meg a repository commit gráfját. A master ágból fogsz most elindulni, a többi ág a képzeletbeli fejlesztők munkája, akik majd veled párhuzamosan dolgoznak. (Vagyis tegyél úgy, mintha azok az ágak most még nem léteznének.)

## 2. feladat: Saját branch és új kód

  * A master ágról kiindulva hozz létre egy saját ágat (mindegy, milyen néven) és válts át rá!
  * Futtasd le a unit teszteket! A TestAdd teszt nem fut le. Tegyél bele breakpointot és debuggerrel nézd meg, hogy mi az Operations.Add visszatérési értéke.
  * A saját ágadon készítsd el az Operations.Add metódust! (Igen, a visszatérési érték legyen a két paraméter összege. :) )
  * Ellenőrizd le, hogy a TestAdd unit teszt sikeresen lefut-e.
  * Commitold a kiegészítésedet. Érdemes minél hamarabb megszokni, hogy a commit üzenetek legyenek kifejezőek és tömörek, pl. "Operations.Add added".

## 3. feladat: Már létező kód módosítása

  * Az Operations.IsPrime metódus ugyan már készen van, viszont messze van az optimálistól. Módosítsd, hogy a lehetséges osztókat csak a paraméter négyzetgyökéig vizsgálja végig. (Figyelj rá, hogy négyzetszám esetén a négyzetgyököt még ellenőrizni kell, mint osztó!)
  * Commitold a kiegészítésedet.

## 4. feladat: Rebase

Közben kiderül, hogy Andezit is szorgalmasan dolgozik a projekten, így az ő munkáját érdemes átvenni, mert elkészült az Operations.Sub metódussal, így azt nem neked kell megírni. (Valós helyzetben ha most fetch-elnél a szerverről, akkor jelenne meg az a commit, ami Andezit ágán szerepel.)

Itt lehetne mergelni is, de a gyakorlás érdekében most törekedjünk inkább arra, hogy egy elágazásoktól mentesebb, egyenes commit gráfunk legyen. Vagyis helyezd át az eddigi munkádat Andezit ágának a végére.

  * Rebaseld a saját branchedet Andezit munkájára!
    * A rebase közben kiderül, hogy Andezit a Sub elkészítése mellett észrevette IsPrime hiányosságát is és ő is javította, bár ő csak annyit tett meg, hogy a paraméter feléig vizsgálja az osztókat. Mivel mindketten ugyanazt a sort módosítottátok, a merge tool nem tudja eldönteni, melyik a helyes.
  * Nézd meg a commit gráfot! A saját ágad commitjai átkerültek, mintha Andezit munkája után, onnan kiindulva dolgoztál volna. (A valóságban a commit nem helyeződik át, ez már egy új, csak úgy néz ki, mint a régi. Vagyis ha nagyon összekuszálódott valami, a reflog segítségével még vissza lehet nyerni az előző állapotot is és ha oda reseteled az ágadat, olyan lesz minden, mint a rebase előtt.)
  * A rebase után ellenőrizd a unit teszteket! (Ezt egyébként érdemes gyakran megtenni, pont erre vannak.) Ideális esetben látni fogod, hogy az IsPrime továbbra is működik (nem romlott el) és most már a Sub funkció is működik.

## 5. feladat: Andezit is átveszi a változtatásaidat

Most egy kicsit megszemélyesítjük Andezitet, aki feltételezzük, hogy tovább akar majd dolgozni. Ehhez ő nem onnan kellene, hogy tovább dolgozzon, ahol az ő ága van, hanem szerencsés lenne átvennie a frissen elkészült rebase eredményét.

  * Menj át Andezit ágára.
  * Mergeld Andezig ágába a te ágadat, hogy a továbbiakban innen induljon ki Andezit fejlesztése (ami egyébként már nem lesz része ennek a gyakorlatnak). Ez a merge legyen fast forward, mivel felesleges a merge commit, csak az andezit branch referenciáját kell előrébb rakni.
  * Ez után a kitérő után térj vissza a saját ágadra.

## 6. feladat: Új funkció és hozzá unit teszt készítése

A következő feladatod az osztás funkció implementálása, amihez még unit teszt sincsen. A Test Driven Development irányelve szerint ehhez először készítünk egy unit tesztet, ami elszáll (mivel még hiányzik a funkció) és utána azon dolgozunk, hogy ez a teszt zöld legyen.

  * Készítsd egy unit tesztet, ami letesztel egy Operations.Div funkciót. A teszt most még nem csak elszáll, de le se fordul.
  * Készítsd el a Div metódust.
  * Futtasd le a unit teszteket, elvileg minden zöld ami eddig az volt és most már az új, Div-et ellenőrző is zöld.
  * Commitold a változásokat a saját branchedre.

## 7. feladat: Merge

Időközben kiderül, hogy Bazalt is dolgozott, ő meg az Operations.Mul funkciót készítette el. Azt állítja, hogy nála már zöld az erre vonatkozó unit teszt is, így ideje átvenni a fejleményeket.

Ebben az esetben a rebase művelet nem lenne nyerő dolog: a saját ágad eredményeit Andezit is használja! Éles feladat esetében a rebase után pusholtad volna, hogy Andezit is át tudja venni fast forwarddal. Ha most rebase művelettel a saját ágadnak azt a részét áthelyeznéd bazalt ágára, azzal áthelyeznéd azt a commitot is, amiből Andezit folytatni fogja a munkát. Ennek ő nagyon nem örülne! (Kiegészítő feladatként kipróbálhatod, mit látna Andezit, ha most rebaseelnél. Ha az egész munkakönyvtárat a benne lévő .git könyvtárral együtt be-ZIP-eled, később vissza tudsz térni erre az állapotra.)

Most mergelünk, hogy semmilyen korábbi commitot ne módosítsunk.

  * Mergeld Bazalt ágát a sajátodba.
  * Ellenőrizd a unit teszteket. Ha minden jól megy, most már a TestMul teszt is zöld.
  * Commitold a mergelés eredményét. (Ilyenkor .orig kiterjesztésű fájlok is megjelennek, ezeket ne commitold, hanem ha minden jól sikerült, nyugodtan törölheted őket.)
  * Nézd meg a commit gráfot, ahol egy merge commitban szépen összefut az Andezittel közös munkád és Bazalt alkotása.

## 8. feladat: Revert commit

Tegyük fel, hogy a projekt vezetés úgy dönt, az Application üdvözlő szövegei mégsem kellenek. Persze egyszerűen ki is lehetne törölni őket, de most inkább használjuk ki, hogy azon anno egy külön commitban kerültek be. (Ezért érdemes gyakran commitolni úgy, hogy egy commitban csak logikailag egybe tartozó modosítások legyenek.) Ha ez az üdvözlő szöveg egy bonyolultabb funkció lenne és nem lenne olyan triviális az eltávolítása, sokkal kényelmesebb lenne azt a régi commitot visszavonni, mintha meg sem történt volna.

Egy commit visszavonása nem módosítja a history (korábbi commitokat és így a commit gráf már elkészült részét), hanem egyszerűen a jelenlegi pontban létrehoz egy olyan commitot, ami a visszavonandó inverze: ami ott új kódsor volt, az itt most törlődik, ami pedig akkor törlődött, az most visszakerül.

  * A revert commit funkcióval hozd létre annak a régi commitnak az inverzét, ami az üdvözlő szövegeket hozra létre!
  * Nézd meg a commit gráfot és a revert commit által behozott módosításokat.
  * A biztonság kedvéért futtasd le a unit teszteket.

## 9. feladat: A master ág frissítése

A fejlesztésnek ez a szakasza most véget ért. Miven unit teszt zöld, ideje publikálni kiváló alkalmazásunkat. Ehhez szerencsés, ha a master ág is az új, stabil állapotra mutat. Ezzel jelezzük másoknak, hogy a mostani állapotra már ők is építhetnek, mert nem egy köztes, fejlesztés alatti valamit találnak ott.

  * Válts át a master ágra.
  * Nézz rá a forráskódra, eltűnnek az Operations-ből a műveletek, mivel most visszatértünk egy olyan időpontra, amikor azok még nem voltak készen.
  * Mergeld a master ágba a saját ágadat. Működik a fast forward is, de itt most határozottan add meg a gitnek, hogy hozzon létre merge commitot.
  * Nézd meg a commit gráfot!

Az a csapaton belül egyeztetett "branching policy" kérdése, hogy ez az utolsó merge lehet-e fast forward. Ha az a célunk, hogy a mester ág csak olyan commitokat tartalmazzon, amik stabil (kiadható) állapotok voltak, akkor a fast forward itt nem jó, mert akkor a master referencia csak előrekerül a te ágad végére, de előtörténetként tartalmazni fogja a fejlesztés minden lépését. Ha ilyenkor előírod a gitnek, hogy mindenképpen hozzon létre merge commitot, akkor látszani fog, hogy a master ágba itt visszakanyarodott egy több oldalágból álló fejlesztés.

## Kész! :)

Ha minden jól sikerült, mostanra a master ágon minden unit teszt zöld, de ebből nem mindent neked kellett megoldani, hanem benne van Andezit és Bazalt munkája is.

Az, hogy valaki a merge vagy rebase műveletet szereti, sokszor csak csapaton belüli megegyezés kérdése. A merge után jobban látszik, milyen ágakon folyt a munka, viszont ha már nagyon sok ág van, a rebase segít egy lineárisabb commit gráf fenntartásában. (Akik a .NET világ TFS verziókezelőjéhez szoktak hozzá, nekik a rebase hozza majd a már megszokott munkafolyamatot.) Amire mindenképpen figyelni kell, hogy rebaseelni csak olyan munkát szabad, amit még nem pusholtál, mert különben lehet, hogy valaki már munkát alapoz arra a commitra, amit később áthelyezel.

## Gyakoran Ismételt Kérdések

További anyagok a témához:

  * A Git használatával kapcsolatban számos leírás és példa található a [snippet gyűjteményben](http://bmeaut.github.io/snippets/#git).

TODO:
  * A kiinduló repóban a commitok ténylegesen andezittől és bazalttól származzanak!

További kérdések esetén írj!
[Csorba Kristóf](https://www.aut.bme.hu/Staff/kristof)
