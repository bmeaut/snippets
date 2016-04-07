---
layout: default
---

# Miért kell a verziókezelés?

Munkánk során a forráskód (és dokumentumok is) folyamatosan változnak, viszont néha előfordul, hogy vissza kell tudnunk keresni egy korábbi vagy egy alternatív verziót. Vagy azért, mert valami nem megy és meg akarjuk keresni, hogy hol romlott el ("Tegnap még ment, csak azóta javítottam valamit..."), vagy mert eleve több verziót kell karbantartanunk (használt verzió, teszt verzió, fejlesztői verzió stb.).

A "most jó, ezt most így be-ZIP-elem" megközelítés egy ideig működik, de ha több fejlesztő is van, nagyon hamar káoszhoz vezet. Ráadásul a forráskód egymás közti megosztása sem triviális: szerveren lévő ZIP, forráskód egy Dropbox megosztásban, fejlesztő monogramjával kezdődő és dátumot is tartalmazó ZIP fájlnév... ezeknek nem lesz jó vége.

Egy verzió kezelő rendszertől elsősorban az alábbiakat várjuk el:

  * Mindig lehessen tudni, melyik az aktuális verzió. És ha többféle aktuális verzió is van, akkor mindegyiket lehessen követni.
  * Több fejlesztő is dolgozhasson egy projekten. Azt, hogy többen egyszerre módosítanak valamit, vagy meg kell akadályozni, vagy kezelni kell az esetleges ütközéseket.
  * Vissza lehessen állítani egy korábbi verziót.

Ezen kívül még elvárhatjuk az alábbiakat is:

  * Lehessen offline is dolgozni, vagyis amikor nincsen kapcsolat a verziókezelő szerverrel.
  * Ideiglenesen félre lehessen rakni változásokat. Vagy azért, mert félkész és még nem alkalmas arra, hogy elmentsük egy új verzióként, vagy egy másik fejlesztőnek akarunk átadni bizonyos módosításokat.
  * A verziókezelő nem utolsó sorban a forráskód biztonságos tárolását is gyakran ellátja. A nagy megbízhatóságú tárolás ugyan nem a verziókelés feladata, viszont az esetek nagy részében mégis a központi verziókezelő szerver az, amiről biztonsági mentések is készülnek. (Van bőven olyan cég, ahol akár egész lezárt projekteket dokumentációval együtt egy központi SVN szerverre töltenek fel. Egyrészt így biztos helyen van, másrészt könnyű lekezelni, ha valamiért jön egy "még véglegesebb verzió".)

## Alapvető fogalmak a verziókezelésben

A verziókezelők világában gyakori fogalmak az alábbiak:

  * repository: az a tároló, amiből minden korábbi verzió kinyerhető. A változásokat ide mentjük le. Ez valójában lehet egy háttérben lévő adatbázis (pl. TFS esetén), egy sima könyvtár a fájlrendszerben (pl. GIT, SVN).
  * working directory, munkakönyvtár: ebben a könyvtárban van az aktuális verzió, amin dolgozunk. Erről tudunk egyfajta állapotmentéseket készíteni a repositoryba. Ha vissza kell térnünk egy korábbi verzióhoz, a munkakönyvtár tartalma fogja felvenni a kiválasztott korábbi állapotot.
  * commit, changeset: egy változás csomag, ami két egymás utáni verzió különbségét tartalmazza. A verziókezelők általában csak a változásokat mentik el helytakarékossági okokból. Ezek a commitok a projekt előre haladtával hosszú láncokat, vagy egyes esetekben ennél bonyolultabb (irányított) gráfokat alkotnak, ahogy egymásra épülnek, szétválnak több irányba, néha pedig újra összeolvadnak.
  * check in, commit, mint művelet: szintén commitnak hívjuk azt a műveletet, amikor a munkakönyvtár egy állapotát elmentjük, "commitolunk". Ekkor a repositoryban létrejön egy új commit és az lesz az új aktuális verzió.
  * revert: az a művelet, amikor visszavonunk egy commitot, vagyis visszatérünk egy korábbi verzióra. Például azért, mert negyed óra múlva demózni kell és éppen semmi nem működik.
  * branch: A commitok gráfjának egy ága, aminek van egy aktuális verziója, valamint annak ősei. Sok esetben egyetlen egy branch van, de előfordul, hogy például megkülönböztetünk egy fejlesztői és egy éles branchet, mivel a fejlesztők nem azon a verzión dolgoznak, ami éles környezetben, éppen használatban van. A projekteknek komoly branchelési stratégiájuk szokott lenni, mely leírja, hogy milyen céllal tartanak fenn külön brancheket.
  * trunk: több rendszerben van egy "fő branch", melyet trunknak neveznek. E mögött az a koncepció, hogy itt folyik a fő fejlesztés, a többi branch csak ideiglenes, rövidebb távra készült leágazás, ami aztán vagy megszűnik, vagy visszaolvad a trunkba.
  * merge: ha több fejlesztő dolgozik együtt, rendszeresen össze kell olvasztani a változtatásaikat. Ez a merge, vagyis összefésülés művelete. A verziókezelők nagyon sok esetben ezt automatikusan meg tudják oldani (auto merge). Gond tipikusan akkor van, ha a két fejlesztő ugyanannak a fájlnak ugyanazt a sorát módosította, és ezért a merge tool nem tudja eldönteni, hogy mit tegyen. (Nyilván nem lehet az egyiket eldobni, de az sem feltétlenül jó megoldás, ha simán egymás mögé másoljuk a két módosítást.)
  * merge conflict: ez az az eset, amikor ütközés van a merge folyamat során. Ezt általában kézzel kell megoldania a fejlesztőknek, aminek nagyon nem szoktak örülni. Érdemes gyakran mergelni, mert akkor az egyes fejlesztők munkája nem távolodik el nagyon egymástól.
  * 3-way-merge: a mergelési folyamat egyik széles körben alkalmazott módszere. Lényege, hogy a két összefésülendő verzió (X és Y) közös ősét (A) is megkeresi (amikor még a két ág megegyezett), majd minden ettől való eltérésről el kell dönteni, hogy az A-beli, X-beli, vagy az Y-beli verzió maradjon meg. Ha a kérdéses sorban X vagy Y közül az egyik megegyezik A-val, akkor a másik az újabb, így azt választjuk. Ha viszont X és Y is változott, akkor van merge conflict, amikor általában a felhasználóra bízzuk a döntést.
  * tag: egyes verziókezelők megengedik, hogy bizonyos állapotokat megjelöljünk. Ilyen tag vagy címke lehet például az a verzió a szakdolgozatból, mely felkerült a diplomaterv portálra, vagy az a firmware verzió, melyet a RobonAUT kvalifikáción használtunk. Nem árt tudni, hogy ha hirtelen kell egy működőképes verzió, akkor melyik volt az.

## Verziókezelők összehasonlítása

A verziókezelők összehasonlításával kapcsolatban most elsősorban az eloszott és a centralizált verziókövetők két neves képviselőjét, a Git-et és a Team Foundation Servert fogom röviden összehasonlítani, mivel ennek a két kategóriának a többi képviselője alapvetően nagyon hasonlóan működik.

  * CVS: egy egyetemi projektben készült az első verzió, amikor egy professzor közösen akart fejleszteni két hallgatójával és eltérő volt az időbeosztásuk. 1986, minden verziókezelő atyja, máig lehet vele találkozni.
  * SVN: A CVS utódja, nagyon elterjedt (de a GIT egyre inkább kiszorítja). Nagyon sok cégnél lehet vele találkozni, ahol centralizált verziókezelőt szerettek volna és nem akartak Microsoft technológiára építeni.
  * GIT: Eredetileg a Linux kernel fejlesztéséhez alakították ki, ahol nagyon-nagyon sok fejlesztő munkáját kellett összefogni.
  * Mercurial: letisztult python kód, hasonló a GIT-hez és közel egyszerre indultak útnak. Egyszerűbb a gitnél (gyorsabb tanulás) és az elsődleges szempont a teljesítmény volt (nagy projektek számára).
  * TFS: A Team Foundation Server a Microsoft technológiai vonalának (centralizált) verziókezelője. Rengeteg integrációs és kollaborációs szolgáltatása van. A TFS jelenleg már támogatja a git repositorykat is, így git szerverként is kiválóan működik.

A számos másik snippetben bemutatott Git-hez képest a TFS fő eltérései az alábbiak:

  * Centralizált verziókövető, így a munkához alapvetően online kapcsolat kell a szerverrel.
  * Sokkal inkább a lináris (branch mentes) fejlesztést helyezi előtérbe: elágazások és mergelések helyett mindenki ugyanazon ágon dolgozik és gyakran checkin-el (a git-es commit megfelelője).
  * Amennyiben fejlesztők egymás között olyan kódrészletet akarnak megosztani, ami még nem alkalmas arra, hogy a főágba bekerüljön, a shelving segítségével "kirakhatják egy polcra" a változásokat, amiket egy másik fejlesztő levehet. (Git alatt ilyenkor a két fejlesztő nyitna erre a célra egy branchet.) 
  * A központi szerver lehetővé teszi fájlok zárolását, ami megakadályozza, hogy két fejlesztő egyszerre nyúljon egy fájl tartalmához. Ennek van egy árnyaltabb változata is, amit a Visual Studio automatikusan is megtesz: a szerkesztett fájlokat checkout-olja, ami azt jelenti, hogy a fájlt megjelöli szerkesztésre. Ezek a megoldások nagyban hozzájárulnak ahhoz, hogy ritkán legyen merge conflict. Jóval ritkábban, mint például Git esetében.
  * A TFS kiterjedt integrációs lehetőségei például lehetővé teszik a gated checkint, ami azt jelenti, hogy amíg a unit tesztek nem futnak le sikeresen, addig nem lehet a módosításokat checkinelni. Ez nagy segítség a programozási hibák ellen, viszont túlságosan macerássá is teheti a fejlesztést.
  * TFS alatt is van branch támogatás, ez viszont a munkakönyvtárban a forráskód duplázását jelenti: ha két branchen dolgozunk, a gépünkön két teljes munkakörnyvtár jelen lesz. A TFS alapú projektek gyakran használnak brancheket, de csak módjával. (Például egy fejlesztői, egy tesztelői és egy éles verzió gyakran indokolt.) 

TFS alatt a tipikus munkafolyamat a következő:

  * Munka előtt "get latest version". Ha a helyi módosítások ütköznek valamelyik most letöltött változtatással, akkor mergelni kell. Az "auto merge" funkciót nyugodtan lehet használni, az esetek legnagyobb részében gond nélkül megoldja.
  * A munka végeztével "checkin", melyhez a git-es commithoz hasonlóan meg kell adni egy rövid, beszédes leírást. Érdemes gyakran checkinelni, ha éppen használható állapotban van a kód, mert akkor a fejlesztők verziói kevésbbé távolodnak el egymástól és kisebb az esélye, hogy macerásabb mergelésre lesz szükség. (És mergelnie is annak kell, aki később akart checkinelni.)
  * Amennyiben vissza szeretnénk vonni az általunk végrehajtott módosításokat, akkor erre az "undo pending changes" való.

TFS-hez szokott fejlesztők számára a Git-ben főleg a sok branch és merge olykor ijesztő. Számukra az egyik szerencsés Git-es stratégia a gyakori commit és push/pull mellett a merge helyett a rebase használata, mivel a rebase a TFS-es lineáris (branch mentes) repository koncepciójához hasonló eredményt ad.  

<small>Szerzők, verziók: Csorba Kristóf</small>
