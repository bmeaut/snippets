---
layout: default
---

# Miért kell a verziókezelés?

Munkánk során a forráskód (és dokumentumok is) folyamatosan változnak, viszont néha előfordul, hogy vissza kell tudnunk keresni egy korábbi vagy egy alternatív verziót. Vagy azért, mert valami nem megy és meg akarjuk keresni, hogy hol romlott el ("Tegnap még ment, csak azóta javítottam valamit..."), vagy mert eleve több verziót kell karbantartanunk (használt verzió, teszt verzió, fejlesztői verzió stb.).

A "most jó, ezt most így be-ZIP-elem" megközelítés egy ideig működik, de ha több fejlesztő is van, nagyon hamar káoszhoz vezet. Ráadásul a forráskód egymás közti megosztása sem triviális: szerveren lévő ZIP, forráskód egy Dropbox megosztásban, fejlesztő monogramjával kezdődő és dátumot is tartalmazó ZIP fájlnév... ezeknek nem lesz jó vége.

Egy verzió kezelő rendszertől elsősorban az alábbiakat várjuk el:
* Mindig lehessen tudni, melyek az aktuális verzió. És ha többféle aktuális verzió is van, akkor mindegyiket lehessen követni.
* Több fejlesztő is dolgozhasson egy projekten. Azt, hogy többen egyszerre módosítanak valamit, vagy meg kell akadályozni, vagy kezelni kell az esetleges ütközéseket.
* Vissza lehessen állítani egy korábbi verziót.

Ezen kívül még elvárhatjuk az alábbiakat is:
* Lehessen offline is dolgozni, vagyis amikor nincsen kapcsolat a verziókezelő szerverrel.
* Ideiglenesen félre lehessen rakni változásokat. Vagy azért, mert félkész és még nem alkalmas arra, hogy elmentsük egy új verzióként, vagy egy másik fejlesztőnek akarunk átadni bizonyos módosításokat.
* A verziókezelő nem utolsó sorban a forráskód biztonságos tárolását is gyakran ellátja. A nagy megbízhatóságú tárolás ugyan nem a verziókelés feladat, viszont az esetek nagy részében mégis a központi verziókezelő szerver az, amiről biztonsági mentések is készülnek. (Van bőven olyan cég, ahol akár egész lezárt projekteket dokumentációval együtt egy központi SVN szerverre töltenek fel. Egyrészt így biztos helyen van, másrészt könnyű lekezelni, ha valamiért jön egy "még véglegesebb verzió".)

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

## Verziókezelők összehasolítása (GIT, CVS, SVN, TFS)

TODO: (Ezt a legegyszerubb úgy összerakni, hogy egyszer összehívok mindegyikhez valakit és gyorsan végigbeszéljük.)

* CVS: egy egyetemi projektben készült az első verzió, amikor a prof közösen akart fejleszteni 2 hallgatójával és eltérő volt az időbeosztásuk. 1986, minden verziókezelő atyja.
* SVN: CVS utódja, nagyon elterjedt (de a GIT egyre inkább kiszorítja)
* GIT: Linux kernel fejlesztéséhez alakították ki, elosztott
* Mercurial: letisztult python kód, hasonló a GIT-hez és kb. egyszerre indultak útnak. Egyszerűbb a gitnél (gyorsabb tanulás) és az elsődleges szempont a teljesítmény volt (nagy projektek számára).

http://www.smashingmagazine.com/2008/09/18/the-top-7-open-source-version-control-systems/
