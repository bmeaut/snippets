---
layout: default
codename: GitBev
title: Git bevezető
tags: alkfejl git
authors: Csorba Kristóf
---

# Git bevezető

A verziókezelés a szoftverfejlesztési folyamatok egy igen fontos része: ezzel biztosítjuk többek között az alábbiakat:

  * Mindig tudjuk, melyik a forráskód legfrissebb verziója. Akkor is, ha egyszerre nagyon sokan dolgoznak rajta.
  * Több verziót is karban tudunk tartani. Például egy fejlesztői, egy tesztelési, valamint egy éles használatra kiadott verziót. És akkor sem lesz káosz, ha az éles verzión gyorsan ki kell valamit javítani, amit aztán később nyilván a fejlesztői és tesztelői verziókba is át kell venni.
  * Bármikor vissza tudunk térni korábbi verziókhoz. Péládul ha a nagy bemutató előtt 4 órával hirtelen semmi nem működik, akkor a pánikhangulat helyett bármikor vissza lehet térni egy korábban agyontesztelt verzióhoz, mely ugyan nem tud még mindent, de akkor legalább működött.

## Hogy néz ki valami, amit verziókövetünk

A GIT un. repository egy olyan tároló, mely például egy program forráskódjának minden korábban elmentett állapotát tárolja. Ez általában úgy néz ki, hogy a forráskód mellett van egy misztikus .git nevű könyvtár, amiben fura dolgok vannak.

A programunk könyvtára ebben az esetben a munkakönyvtár (working directory), vagyis ahol dolgozunk. Ha elértünk egy olyan állapotba, amikor szépen fordul a program és valami logikai blokk határán vagyunk (elkészült valami), akkor azt az állapotot el tudjuk menteni. Ez az un. commit (más rendszerek snapshotnak is hívhatnák). Ezek a commitok szépen gyűlnek a repositoryban, a GIT-et pedig bármikor megkérhetjük arra, hogy a munkakönyvtárat állítsa vissza egy korábbi commit formájában elmentett állapotra.

A GIT eredeti formájában egy parancssoros alkalmazás. Sokan máig ezt a formáját használják. Ezen kívül van egy kicsit minimál designos grafikus felülete is. Ennek kiváltására aztán készült egy csomó másik front end alkalmazás is, mint például a GitExtensions és a SourceTree. Ezek semmi mást nem csinálnak, csak elfedik a GIT parancssoros interfészét és begépelik helyettünk. Ezek mellett természetesen a modern fejlesztő környezetek (pl. Visual Studio, Eclipse, Qt Creator stb.) szintén rendelkeznek GIT integrációval, így onnan is elérjük a legfontosabb funkciókat.

## Mit verziókövetünk

Verziókövetni elsősorban forráskódot szoktunk, de bármilyen szöveges anyag könnyen követhező. Például ha valaki LaTeX alatt készíti a szakdolgozatát, akkor azt is be lehet rakni GIT alá. Így ha a konzulensünk belejavít egy verzióba, miközben mi már továbbmentünk, akkor az anno odaadott verzióhoz visszatérve végrehajtuk a változtatásokat (mert itt még a "lásd 5. oldal" megjegyzés a margóra írva stimmel is, nem úgy, mint a legutolsó verziónkban, ahol 12 oldalt már beszúrtunk ide-oda). Utána pedig a változásokat át lehet venni az aktuális verzióhoz is.

Bináris fájlokat a GIT ugyan el tud tárolni, igazi ereje azonban nem érvényesül. Ettől függetlenül például a szakdolgozat PNG ábráit nyugodtan belerakjuk a dolgozat mellé.

Fontos azonban, hogy olyan dolgot soha nem szoktunk verziókövetni, ami fordítás eredménye, vagy bármilyen más módon generált fájl. Ezeket mindenki magának generálja majd le. Ezzel elsősorban a repository (a "tároló") méretét csökkentjük, másrészt lehet, hogy az egyes fejlesztők gépein a környezeti eltérések miatt bizonyos generált dolgok el fognak térni. Ha ezeket utána a GIT-en keresztül megosztanák egymással, folyton ide-oda módosítgatná mindenki a generált fájlokat, mert mindig csak egy valakinél lenne pont jó. Ugyanez igaz az olyan beállításokat tartalmazó fájlokra, melyek csak egy fejlesztőnél érvényesek (pl. Qt alatt a projekt beállítások helyi kiegészítéseit tartalmazó .user fájlok). Azokat mindenki majd magának beállítja.

Azt, hogy mely fájlokat nem akarunk verziókövetni (és így ezt fel se ajánlja a GIT), a .gitignore fájlban adhatjuk meg a working directory gyökerében.

Ezen kívül szintén általános elvárás, hogy olyan állapotot nem mentünk el, ami le sem fordul. Ennek az az oka, hogy ha valaki elkezd dolgozni, tipikusan letölti a többiek munkáit. És nem örül neki, ha kezdené a munkát, de már most nem fordul a program... és ráadásul nem is az ő részében van a hiba.

## A legfontosabb fogalmak röviden

A GIT világában az alábbiak a legfontosabb fogalmak. A fogalmak megértéséhez érdemes a *0103_GitPeldafejlesztes* példát is végigolvasni, az itteni lista inkább referencia célokat szolgál.

  * repository: egy tároló, mely a verzió követett fájlok számos verzióját tárolni tudja
  * working directory: a munkakönyvtár, ahol dolgozunk. Ennek állapotait tárolják a commitok.
  * commit: A working directory egy bármikor visszaállítható verziója. Alapvetően az eltéréseket tárolja az előző commithoz (szülő commithoz) képest.
  * staging: Mielőtt commitoljuk a változásokat, azokat "stageljük". Ez azért fontos, mert a working directorynak nem feltétlenül kell minden változását elmentenünk a commitba.
  * stash: ideiglenesen félrerakhatjuk a working directoryban végrehajtott változásokat, majd azokat visszahozhatjuk. Ez akkor fontos, ha olyan repository műveletet hajtunk végre, mely módosítja a munkakönyvtár tartalmát. (Mivel az felülírná azt, amin éppen dolgozunk.)
  * remote: egy távoli reporitory. Általában egy szerveren van, de éppen lehet egy másik könyvtár is. A push, fetch és pull műveletekkel repositoryk között tudjuk átvinni a változásokat.
  * origin: az a remote, ahonnan eredetileg klónoztuk (letöltöttük) a repositoryt.
  * .gitignore fájl: azon fájlok listája (vagy maszkja), amik ugyan a working directoryban vannak, de nem akarjuk őket verziókövetni. Ilyenek például az összes fordítási eredmény, úgyhogy a \*.obj és \*.exe például általában benne van.
  * elosztott verziókövető rendszer: A GIT esetében minden fejlesztőnél minden adat rendelkezésre áll. Ellentétben a centralizált megoldásokkal, egy git repositoryval akkor is tudunk dolgozni, ha nem érjük el a szervert. Sőt, egy sima könyvtárunkban is létre tudunk hozni egy repositoryt (csak ki kell adni a "git init" parancsot). Csapatban dolgozva mindenkinél van egy lokális repository, amiket néha szinkronizálunk (lásd push és pull műveletek).
  * push: egy remotera feltölti a nálunk létező, de onnan még hiányzó commitokat. Ezzel gyakorlatilag megosztjuk a munkánkat a többiekkel, mert ők meg le tudják majd pullolni a szerverről.
  * pull: a fetch és merge műveletek egymás után.
  * fetch: egy remoteról letölti az ott jelen lévő, de a lokális repositoryból még hiányzó commitokat. Így jut el mások munkája hozzánk.
  * merge folyamat: a mi munkánkba beolvasztja mások munkáját. Ha a fetch során a nálunk aktuális verzióhoz képest jöttek további változások, akkor a merge művelet veszi ezeket hozzá a nálunk aktuális verzióhoz. (A fetch csak letölti és jelzi, hogy ott vannak.)
  * branch (ág): a fejlesztés egymástól függetlenül, több ágon is folyhat. GIT alatt ez teljesen általános, mivel brancheket nagyon könnyű létrehozni. Például ha egy új funkciót fejlesztek, akkor létrehozok egy ágat neki és azon dolgozok, arra commitolgatok. Aztán ha készen vagyok, akkor az én ágamat mergelem (visszaolvasztom) a fejlesztés fő ágába.
  * head: hivatkozás arra a commitra, ami a következőnek létrehozott commit szülője lesz.

A további fogalmakkal menet közben ismerkedünk meg, valamint egy rendszerfüggetlenebb összefoglalás található még a *0114_VerziokezelokOsszehasonlitasa* snippetben.

## A GIT és GitExtensions telepítése

A GIT telepítő készleteit minden platformra a [https://git-scm.com/downloads](https://git-scm.com/downloads) címről lehet letölteni.

A git első konfigurációja a felhasználói nevünk és e-mail címünk megadásából áll:

    git config --global user.name "Andezit"
    git config --global user.email andezit@example.com

További részletek erről itt olvashatók: [https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup)

A GIT telepítése után én még fel szoktam rakni a GitExtensions-t, egy igen népszerű GUI-t hozzá: [http://gitextensions.github.io/](http://gitextensions.github.io/)


További kliensek itt találhatók: [https://git-scm.com/downloads/guis](https://git-scm.com/downloads/guis)

## Egy git repository létrehozása

A legegyszerűbb eset, ha el akarok készíteni egyetlen szövegfájlt és azt verziókövetni is akarom. Ehhez kell egy üres könyvtár, amiben dolgozni fogok, majd ott ki kell adni a

    $ git init
    Initialized empty Git repository in c:/temp/.git/

parancsot. (A GIT Windows alatt felrak egy linuxos shellt, így a parancsokat ne a cmd.exe-n kereszül adjuk ki. Ebben a shellben általában minden működik, ami a cmd.exe-ben, de például a C:\temp könyvtárba "cd /c/temp" paranccsal tudunk belépni, mivel Linux alatt a fájlrendszerben a meghajtók könyvtárakba csatlakoznak be.) 

Ettől már létre is jön a .git könyvtár. Ha létrehozzuk a szövegfájlunkat (akármilyen módszerrel, szövegszerkesztővel), akkor utána megkérdezhetjük a git-et, hogy van-e változás a munkakönyvtárban:

    $ git status
    # On branch master
    #
    # Initial commit
    #
    # Untracked files:
    #   (use "git add <file>..." to include in what will be committed)
    #
    #       elso.txt
    nothing added to commit but untracked files present (use "git add" to track)

Igen, az elso.txt változott, mint untracked fájl. (Untracked, mert még nem adtuk hozzá soha a repositoryhoz, vagyis teljesen újnak számít.) Most adjuk hozzá (stageljük):

    $ git add elso.txt

És újra lekérdezve a helyzetet:

    $ git status
    # On branch master
    #
    # Initial commit
    #
    # Changes to be committed:
    #   (use "git rm --cached <file>..." to unstage)
    #
    #       new file:   elso.txt
    #

Végül commitolva, aminek a -m kapcsolóval egyből megadjuk a szövegét (megjegyzését) is:

    $ git commit -m "Elso commit"
    [master (root-commit) 691c17d] Elso commit
     1 file changed, 1 insertion(+)
     create mode 100644 elso.txt

Megjegyzésnek illik olyasmit írni, amiből kiderül, hogy éppen mit változtattunk meg. Az "asdffsdfgd" szöveg nem egy illendő dolog. Főleg, hogy végleg bent marad a nevünk alatt a repositoryban.

Mostantól ehhez az állapothoz bármikor vissza tudunk majd térni. A commitot a hash kódja (egy SHA1 hash kód) azonosítja, melynek eleje (ez is elegendő az azonosításhoz) most nekem "691c17d" lett.

## Szerver oldalon már létező repository klónozása

Amennyiben úgy kezdjük a munkát, hogy más már létrehozta a repositoryt, akkor nekünk nem kell létrehozni, mindössze klónozni kell. Ehhez adjuk ki a git clone parancsot. Például a

    git clone https://github.com/bmeaut/snippets.git

parancs leklónozza a gépünkre a teljes snippets repositoryt. Az aktuális könyvtárból fog nyitni egy snippets könyvtárat, ami a projekt munkakönyvtára lesz.

## További olvasnivaló

A folytatáshoz az alábbi leírásokat érdemes felkeresni:

* Egy részletes fejlesztési folyamat példa GIT használatával: *0103_GitPeldafejlesztes*
* Pro.Git könyv: [https://git-scm.com/book/en/v2](https://git-scm.com/book/en/v2)
* A verziókezelők összehasonlítása és további fogalmak: *0114_VerziokezelokOsszehasonlitasa*

<small>Szerzők, verziók: Csorba Kristóf</small>
