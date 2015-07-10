# Git haladó

A kiindulási alapunk Andezit és Bazalt projektje a demo1 tag kirakása után.

Mivel a demo1 tag kirakása után még létezik az origin/QueryFunction, de már nincsen rá szükség, Andezit megszünteti. Erre a GitExtensions még képes, így parancssorból adja ki az alábbi parancsot:

    git push origin :QueryFunction

Bazalt helyi repositoryjában természetesen ettől még ott szerepel az origin/QueryFunction tracking reference, bár a remote oldalon már nincs megfelelője, így mérsékelten hasznos. Bazalt az olyan branch hivatkozásoktól, melynek már nincsen megfelelője a remote oldalon, az alábbiak szerint tud megszabadulni:

    git fetch --prune origin
        x [deleted]         (none)     -> origin/QueryFunction

## Andezit: új állapotátmenetek és szépítés

---- TODO kellene egy ábra az állapotgépről!

Andezit úgy dönt, hogy hiányzik néhány állapot átmenet. Konkrétan ha pánik gombot nyomunk, akkor annak bármelyik várakozó állapotban át kellene ugrania pánikjelzésre. Akkor is, ha például éppen arra várunk, hogy a Sick jelzésünkre megjöjjön a megerősítés (AwaitSickAck állapot).

A módosításokat Andezit egy új, NewTransitions branchre commitolja és egyelőre még nem pusholja a szerver oldalra. Azt tervezi, hogy még egy kicsit szépít a kódon, majd utána rebaseli a munkáját a master ágra, akkor pedig a rebase előtt nem szabad pusholni. (Hogy miért nem, arról később lesz szó.)

![](image/100_AndezitAddedNewTransitions.png)

A szépítés abban nyilvánul meg, hogy a bsp.c-ben a handleCommunication által kiírt szövegben az "awaiting" el volt írva, ezt most javítja és commitolja.

![](image/101_AndezitTypoFix.png)

## Bazalt: közben kibővíti a logolást

Bazalt egy MoreLogging ágat hoz létre, majd oda commitolja a módosításait, hogy minden állapotváltozás kerüljön bele a logba.

![](image/102_BazaltCommitsLogging.png)

Majd pusholja is a fejleményeket az originra.

![](image/103_BazaltPushesMoreLogging.png)

## Andezit rebasel

Andezit mielőtt pusholná az állapotátmenetes munkáját, nyom egy fetch all-t.

![](image/104_AndezitFetchAll.png)

Ekkor látja, hogy Bazalt is dolgozott. Most tegyük fel, hogy Andezit nem a merge mellett dönt, hanem rebaselni akar, hogy a repository history ne legyen olyan kusza.

![](image/105_AndezitRebase1.png)

![](image/106_AndezitRebase2.png)

A merge sikeres:

![](image/107_AndezitRebase3.png)

(Látszik, hogy mivel a main.c-t ketten is módosították párhuzamosan, a GIT merge toolnak a 3-way-merge üzemmódra kellett átváltania, mivel fájlon belüli konkurrens változásokat is ki kellett bogoznia. De ez ütközés nélkül sikerült neki.) 

![](image/108_AndezitRebaseEredmeny.png)

Andezit pusholja a NewTransitions ágat. Ezután Bazalt nyom egy fetch all-t és az alábbiakat látja:

![](image/109_BazaltFetchAll.png)

## Bazalt bővíti a logolást

Tegyük fel, hogy Bazalt még mielőtt mergelné Andezit új állapotátmeneteit, kiegészíti a főciklus switch-ét egy default case-szel.

![](image/110_BazaltDefaultState.png)

Majd Bazalt úgy dönt, hogy a default state jó lenne, ha assertelne is, így ezt is commitolja:

![](image/111_BazaltAssert.png)

![](image/112_BazaltPushed.png)
 
Ezután Bazalt szól Andezitnek, hogy miket készített. 

## Andezit cherry pickel


Andezit úgy dönt, hogy kiegészíti az új állapot átmeneteit log bejegyzésekkel.

![](image/113_AndezitNewTransitionsLog.png)

![](image/114_AndezitCherryPickElott.png)

És hogy a log így teljes legyen, át akarja venni Bazalt default állapotát, viszont az assert használatot még nem.

![](image/115_AndezitCherryPick1.png)

![](image/116_AndezitCherryPick2.png)

A cherry pick sikeres:

![](image/117_AndezitCherryPickSuccessful.png)

Mivel Andezit nem kérte a cherry picknél, hogy automatikusan commitolódjon is, most az átvett változások stagelve vannak, de nem commitolva. A commithoz rányom a Commit gombra, ahol már minden elő van készítve (Bazalt eredeti commit szövegével együtt):

![](image/118_AndezitCherryPickCommit.png)

Pusholva a fejleményeket Andezitnél a végeredmény így néz ki:

![](image/119_AndezitCherryPickEredmeny.png)

## Bazalt mergel és kész a demo2

Bazalt ezután úgy dönt, hogy készen állnak az új demóra, így először a MoreLogging ágba mergeli az origin/NewTransitions ágat (a merge folyamatot nem zavarja, hogy magába mergel egy olyan commitot, amit ő maga készített korábban, mivel a merge tool csak konstatálja, hogy ezügyben nincsen eltérés.)

![](image/120_BazaltMerged.png)

Ekkor Bazalt még utoljára ellenőrzi, hogy tényleg minden szépen fut-e. Sajnos kiderül, hogy a program nem is fordul, ugyanis sikerült duplázni a switch default ágát:

        default:
            addLogEntry("Unknown state", LogLevelNormal);
            break;
        default:
            addLogEntry("Unknown state", LogLevelNormal);
            assert(0);
            break;

Még jó, hogy ellenőrizte. A merge még sem volt olyan zökkenőmentes. Semmi gond, gyors javítás, utána pedig commit. Jobban belegondolva ez a merge része kellett volna, hogy legyen. Mivel a merge commitot még nem pusholta, éppen módosíthatja is. Erre való az "amend commit": a mostani commitot beleolvasztja az előzőbe. Tipikusan akkor használjuk, ha valami lemaradt:

![](image/121_BazaltAmendMergeCommit.png)

A GIT azonnal figyelmeztet, hogy ezt csak akkor tegyük, ha mások még nem látták az előző commitot, mert módosítjuk azt is:

![](image/122_AmendCommitWarning.png)

Miután Bazalt meggyőződött róla, hogy a program most már tényleg helyesen működik, átvált a master ágra, mergeli bele a MoreLogging-ot (új merge commitot hozva létre, a fast-forward a master esetében nem olyan nyerő). Pusholja a master branchet és rárakja a Demo2 taget is (és azt is pusholja):

![](image/123_BazaltMergesIntoMasterAndAddsDemo2Tag.png)

Befejezésül Andezit és átvált a master branchére és mergeli bele (fast-forwarddal) az új origin/master-t.
