---
layout: default
codename: GitParancssor
title: Git parancssor
tags: alkfejl git
authors: Csorba Kristóf
---

# A Git konzolos használata során gyakran előkerülő parancsok

Változó, hogy ki mennyire szereti a konzolos megoldásokat. Sokak szerint sokkal gyorsabb, mint kattintgatni. Mivel a Git alapvetően egy parancssoros alkalmazás, és a háttérben a grafikus felületei is konzolos parancsokat adnak ki, érdemes összeszedni, mik a leggyakrabban használt parancsok. A leírás feltételezi, hogy a parancsok mögötti koncepciókkal és a működésükkel már tisztában van az Olvasó.

Bármely git parancsról kaphatunk segítséget a ``--help`` opcióval. Pl.

    git commit --help

## Első lépések

Git repository létrehozása az aktuális könyvtárban:

    git init

Amennyiben olyan repositoryt szeretnénk létrehozni, amit csak távolról fogunk elérni és klónozni (ez viszonylag ritka, leginkább szerver oldalon fordul elő, ahol viszont ezt nem parancssorból szokás megtenni), akkor a ``--bare`` kapcsolóval tehetjük ezt meg.

Sokkal gyakoribb, hogy egy már létező repositoryt klónozunk:

    git clone https://github.com/bmeaut/snippets.git

Ha már létrejött a repository, annak állapotát (változott-e valami, stagelve van-e valami) a státusz lekérdezésével tehetjük meg:

    git status

Stagelni fájlokat az add paranccsal lehet:

    git add egyfajl.txt
    git add .

Ez utóbbi minden változást stagel. A stagelt fájlokat commitolni pedig az alábbi módon lehet:

    git commit -m "Üzenet"
    git commit

Az első esetben helyben megadtuk a commit üzenetet is. Ha több sorosat szeretnénk megadni, a második eset feldobja az alapértelmezett szövegszerkesztőnket, megvárja, míg beírjuk a commit szöveget (mentünk és kilépünk), majd azt használja commit üzenetnek.

Ez a szövegszerkesztő feldobás amúgy is gyakori a git világában: ha több soros válasz kell a felhasználótól, létrehoz egy ideiglenes szövegfájlt, beleírja az instrukciókat, majd feldobja szerkesztésre. Ha készen vagyunk (bezártuk a szövegszerkesztőt), akkor a fájl tartalma alapján megy tovább, majd az ideiglenes fájlt eltávolítja. Igen ravasz és kiváló megoldás.

A commitok sorát a

    git log
    gitk --all

parancsok mutatják meg, szövegesen és grafikusan. A gitk-nál az ``--all`` azt jelenti, hogy az összes branchet látni szeretnénk, nem csak az aktuálisat.

Az aktuális munkakönyvtár és commit közötti eltérést (mi változott) a

    git diff

parancs mutatja meg.

## Branch, checkout, reset

Új branchet tipikusan úgy szoktunk létrehozni, hogy checkoutoljuk is, ezért a leggyakrabban a checkout parancsot használjuk erre a ``-b`` mint branch opcióval:

    git checkout -b UjBranchnev
    git checkout -b UjBranchnev a1b2c3

Az első eset az aktuális (HEAD által mutatott) commiton hozza létre az új ágat, a második eset pedig az a1b2c3 commiton.

A fenti példában az a1b2c3 helyén állhat egy távoli branch is, pl. origin/masikBranch. Így létre lehet hozni a távoli branch egy helyi megfelelőjét, ami ráadásul "tracking branch lesz", vagyis push és pull esetén tudni fogja, hogy neki mi a távoli megfelelője és oda fog pusholni, illetve onnan fog pullolni.

Ha pedig csak át akarunk váltani egy másik branchre, azt is a checkouttal tehetjük meg:

    git checkout master

Branchet törölni a

    git branch --delete NemKellBranch

paranccsal lehet. Fontos, hogy ez csak akkor lehetséges, ha a törölt branch minden commitja már mergelve van máshova, vagyis "nem fog leszakadni a commit gráfról". (Ha mégis ezt szeretnénk, arra való a ``--force``.)

Amennyiben el akarjuk dobni az el nem mentett változásokat, azt a reset paranccsal tehetjük meg: a munkakönyvtár állapotát visszaállítjuk arra, ami az adott (vagy aktuális) commitban szerepel. A tényleges visszaállításhoz a ``--hard`` opció is kell.

    git reset --hard
    git reset --hard a1b2c3

## Push, pull, fetch

A push, pull és fetch műveletek alapesetben az aktuális ágra vonatkoznak. Mivel általában erre van szükségünk, ezek sok paraméterezést nem is igényelnek:

    git push
    git pull
    git fetch
    git fetch --all

Az utolsó eset akkor hasznos, ha látni szeretnénk a többi ág fejlődését, esetleg mergelni akarjuk őket.

Ezek a műveletek akkor működnek, ha tracking branchen vagyunk, vagyis a branchről a git tudja, hogy mi a távoli megfelelője. A teljes szintaxis az alábbi:

    git push origin master:origin/master

Ebben az esetben az origin távoli repository master ágára pusholjuk a helyi mastert.

## Merge, rebase, cherry-picking

A merge és rebase művelet parancsa egyszerű, utána viszont lehet, hogy felhasználói beavatkozásra lesz szükség. Ilyenkor azonban a git a válaszában mindig leírja, mi a teendő, ráadásul ezt határozottan érthetően írja le.

    git merge MasikBranch
    git rebase MasikBranch

Fontos, hogy a fentieknél a merge marad a jelenlegi ágon és magába mergeli a másikat, míg a rebase a mostani ág tartalmát áthelyezi (rebaseli) a másik ágra, vagyis annak folytatása lesz a jelenlegi munkánk.

A rebase folyamat több commit "visszajátszását" igényelheti, és ezért minden ilyen visszajátszáskor előfordulhat, hogy ütközés van, vagyis a másik ág módosításai és a mi munkánk ellentmondásos. Ilyenkor a rebase folyamat megáll, megkér minket, hogy oldjuk fel az ütközéseket, utána pedig folytassuk.

Az ütközések feloldása egyrészt mehet kézzel. Ilyenkor az ütköző fájlokba bekerül mindkét alternatíva és nekünk kell kitakarítani, az eredeti verzió pedig .orig kiterjesztéssel áll rendelkezésre. (A .orig fájlokat utána törölni szoktuk.) Amennyiben mergetool-t használunk, akkor is ugyanez történik, csak a sima szövegszerkesztőnk helyett a mergetool indul el, aminek a felülete direkt arra készült, hogy az egyes alternatívák közül könnyen tudjunk választani. A mergetool indítása a

    git mergetool

paranccsal történik. (Az, hogy mi az alapértelmezett mergetool, konfiguráció kérdése. A windowsos telepítő a kdiff3 használatát ajánlja fel.) Természetesen nem csak rebase, hanem merge esetén is ugyanígy működik a kézi mergelés.

A rebase folytatása az alábbi paranccsal megy:  

    git rebase --continue

Végül pedig a cherry-picking az alábbi módon működik:

    git cherry-pick 0f543fe

Ezzel a 0f543fe commitot vesszük át a saját águnkra, amivel egy másolatot készítünk azokról a változtatásokról.

## Squashing

Amennyiben több, tipikusan még nem pusholt commitot akarunk összeolvasztani, erre a squashing való. Ez nem külön git parancs, hanem a rebase egy interaktív verziója: az eddigi munkánkat rebaseljük egy korábbi commitra (ami a mi munkánk őse mellesleg), de minden azóta készített commitra megadhatjuk, hogy az maradjon meg, vagy olvadjon bele az előzőbe.

Tegyük fel, hogy 3 commitot szeretnék összeolvasztani. Az első, amit nem most készítettem, az 5b74f4, vagyis erre szeretném a squashing eredményét rárakni:

    git rebase -i 5b74f4

(A commit hash kódokat egyébként a ``git log`` paranccsal lehet lekérni.)
A git ekkor feldob egy szövegfájlt szerkesztésre, melyben minden commithoz megadhatjuk, hogy mi legyen vele:

    pick e21eac9 UjSor
    pick 9323585 UjSor2
    pick 55c8cf6 UjSor3

    # Rebase 5b74f4a..55c8cf6 onto 5b74f4a (3 command(s))
    #
    # Commands:
    # p, pick = use commit
    # r, reword = use commit, but edit the commit message
    # e, edit = use commit, but stop for amending
    # s, squash = use commit, but meld into previous commit
    # f, fixup = like "squash", but discard this commit's log message
    # x, exec = run command (the rest of the line) using shell
    #
    # These lines can be re-ordered; they are executed from top to bottom.
    #
    # If you remove a line here THAT COMMIT WILL BE LOST.
    #
    # However, if you remove everything, the rebase will be aborted.

Itt a commitok végrehajtási sorrendben szerepelnek, időben az első van az első sorban. (Gyakorlatilag egy parancs scriptet szerkesztünk a git számára.) Mivel kell egy commit, az elsőt meghagyjuk (pick), a második kettőt viszont beleolvasztjuk (squash, vagy röviden s):

    pick e21eac9 UjSor
    s 9323585 UjSor2
    s 55c8cf6 UjSor3

Ezután a fájlt elmentve és kilépve a szerkesztőből, egy újabb szövegszerkesztő ablakot kapunk, amiben az "eredő" commit üzenetét tudjuk összerakni. Amint ezt is elmentjünk és kilépünk a szövegszerkesztőből, létrejön az összeolvasztott commit.

## Egyebek

A parancsok által feldobott szövegszerkesztőt az alábbiak szerint lehet pl. a "nano"-ra beállítani:

    git config --global core.editor "nano"

A kdiff3 beállítása mergetoolnak (ebben a példában Windows alatt):

    git config --global merge.tool kdiff3
    git config --global mergetool.kdiff3.cmd '"C:\\Program Files (x86)\\KDiff3\\kdiff3" $BASE $LOCAL $REMOTE -o $MERGED'

## További információk a szintaxisról

  * [Git dokumentáció](http://git-scm.com/docs/)
  * A legtöbb git parancs a --help opció hatására megmutatja a saját dokumentációját. (Pl. ``git status --help``)
  * Googlelel rákeresve a git parancsokra (pl. git init) általában első helyen az online dokumentációt kapjuk, ami igen részletes és hasznos.
  * Számos "Git Cheat Sheet" található a weben, melyek tömören összefoglalják a legfontosabb parancsokat. [GitHub Training Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

<small>Szerzők, verziók: Csorba Kristóf</small>
