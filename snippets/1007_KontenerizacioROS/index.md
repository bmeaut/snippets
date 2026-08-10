---
layout: default
codename: KontenerizacioROS
title: Konténerizált ROS 2 fejlesztői környezet felállítása és debugolása MI-val
tags: snippets mieset
authors: Técsi Zsuzsanna Vilma
---

# Konténerizált ROS 2 fejlesztői környezet felállítása és debugolása MI-val

A diplomatervezési munka során egy meglévő [ROS 2 Humble](https://docs.ros.org/en/humble/index.html) (Ubuntu 22.04 LTS) devcontainer alapú rendszerben dolgozom, mivel így a fejlesztői környezet és annak függőségei reprodukálhatóbbá és hordozhatóbbá válnak különböző host gépek között. Az esettanulmány ennek a rendkívül összetett, konténerizált fejlesztői környezetnek az MI segítségével történő felépítését és stabilizálását mutatja be.

A rendszerbe integráltam egy mélységi kamerát (Intel RealSense D435i), egy megfogástervező algoritmust (Grasp Pose Detection - GPD) és a hozzá tartozó ROS 2-es wrappert (dgl_ros_models), valamint szimulációs és vizualizációs szoftvereket (Gazebo, RViz, MoveIt). Mivel ezek a modulok nem „egymásnak készültek", azaz különböző build-rendszereket, függőségi láncokat, szoftververziókat és memóriakezelési konvenciókat használnak, az összeillesztésük során számos rendszerszintű hiba, fordítási inkompatibilitás és grafikai zavar lépett fel. Az esettanulmány fő fókusza az az iteratív mérnöki folyamat, amelyben az MI (Gemini, ChatGPT, Claude) nem kész kódok forrása volt, hanem strukturált, rendszerszintű hibakeresési partner, akinek tévedéseit és túlzott általánosításait folyamatosan és határozottan korrigálnom kellett.

## Tanulságok
1. Egy komplex, több könyvtárat összekötő környezetnél a teljes technológiai stack és mappastruktúra előzetes megadása (nem csak az aktuális hiba) lényegesen projektspecifikusabb választ eredményez, mint amikor csak egyetlen hibaüzenetre vagy fordítási naplóra támaszkodunk.

2. Optimalizált (-Os) build mellett a debugger nem a tényleges végrehajtási sorrendet követte, ami megnehezítette egy memóriahiba felderítését. Csak a flag kikommentezése után vált megbízhatóvá a hibakeresés. A végleges megoldás megtalálásában az bizonyult különösen hatékonynak, hogy egy konkrét GitHub issue-t adtam az MI-nek ellenőrzésre, így a nyers hibaüzenetből történő spekuláció helyett egy már dokumentált megoldást lehetett a saját környezetemre alkalmazni.
   
3. Egy framework nem dokumentált vagy szokatlan működését (például hogy egy ROS 2 Action eredménye nem úgy jelenik meg, ahol elsőre várnánk) csak akkor sikerült helyesen értelmezni, amikor nem a hibaüzenetből, hanem a működési modellből indultam ki.

4. Bizonyos hibák esetén a futásidejű naplók, a program kimenete és a rendszer tényleges állapota megbízhatóbb kiindulópontnak bizonyultak, mint az MI dokumentációra vagy általános feltételezésekre épülő magyarázatai.

5. Amikor egy hiba több könyvtár vagy komponens együttműködéséből adódott, nem volt elegendő a hibát jelző komponens lokális javítása. A verziók, branch-ek, API-k és a komponensek közötti adat- és függőségi kapcsolatok végigkövetése bizonyult megbízható útnak.

## A környezet

A fejlesztői környezet egy VS Code DevContainerben fut, amely elkülöníti a projekt függőségeit a fizikai host rendszerétől.

- Host OS: Ubuntu 22.04 LTS (Jammy Jellyfish)
- Robotikai middleware: ROS 2 Humble Hawksbill
- Grafikus szimuláció és tervezés: Gazebo, RViz2, MoveIt2
- Hardver és SDK: Intel RealSense D435i mélységi kamera, librealsense SDK
- Megfogástervezés: a C++ alapú gpd (Grasp Pose Detection) könyvtár és a hozzá tartozó dgl_ros_models (a dgl_ros könyvtárban található csomag) ROS 2 wrapper


**A munkaterület (workspace/src) belső struktúrája:**
```
/workspaces/diffrobot_devcontainer/
├── root/
│   ├── src/
│   │   ├── dgl_ros/ (ROS2 interfészek és modellek)
│   │   ├── moveit_task_constructor/
│   │   ├── realsense_gazebo_plugin/
│   │   └── Universal_Robots_ROS2_Gazebo_Simulation/
│   ├── librealsense/ (Workspace gyökerébe klónozott SDK)
│   └── gpd/ (Grasp Pose Detection forráskód)
```

## A munkafolyamat tanulságos részletei

### (1. tanulsághoz) A teljes technológiai stack és kontextus átadása az indításkor 

A fejlesztés kezdeti fázisában, amikor a konténeres környezetben futtatott telepítők és szkriptek indításakor hibákba ütköztem, csupán az éppen aktuális hibaüzenetet másoltam be az MI-nek. Ez a megközelítés azonban nem hozott tartós eredményt, mivel a modell ilyenkor vakon tapogatózva csak általános Docker- és Linux-adminisztrációs tanácsokat adott (mint a jogosultságok ellenőrzése vagy a konténer manuális indítása).

A valódi fordulatot az jelentette, amikor a problémát nem elszigetelten kezeltem, hanem egyetlen átfogó, strukturált indító promptban adtam át a teljes környezeti kontextust: a bázis operációs rendszert (Ubuntu 22.04 LTS), a ROS 2 Humble disztribúciót, a munkaterületem pontos mappastruktúráját és az integrálni kívánt főbb komponenseket. 

Prompt:
```
DevContaineren belül futtatok egy Ubuntu-t, amelyen belül ROS 2 Humble disztribúció segítségével szeretnék Gazebo-ban és RViz-ben szimulálásokat futtatni. Jelenleg a root/src mappában található a dgl_ros, moveit_task_constructor, realsense_gazebo_plugin, Universal_Robots_ROS2_Gazebo_Simulation és a root alatt található a librealsense és a gpd repo.
```

MI:
```
Ez rengeteget segít! Így már összeállt a kép: egy komplex ROS 2 Humble fejlesztői környezetet (DevContainer) próbálsz felépíteni, ahol a MoveIt, a Gazebo és a RealSense pluginok közötti függőségeket kell feloldanod.
```

Ez a rendszerszintű megközelítés azonnal projektspecifikus irányba terelte az MI-t, amely így már képes volt a saját rendszerem alapján megfelelő támogatást nyújtani.


### (2. tanulsághoz) A fordítási optimalizációk feloldása a megbízható debuggoláshoz

A GPD program tesztelése során a pontfelhő objektumok felszabadításakor a szoftver rendszeresen double free or corruption hibával elszállt. A hiba pontos helyének felderítését megnehezítette, hogy a VS Code-ba ágyazott GDB debuggerrel lépkedve a kód végrehajtása kaotikusan ugrált a C++ sorok között, a launch fájlból indított debug session pedig nem állt meg a breakpointoknál.

Prompt:
```
Ez a dgl_ros_models-nek CMakeLists.txt-je: [...]
```

MI:
```
Megvan a bűnös! A CMakeLists.txt fájlodban van egy sor (add_compile_options("-Os")), ami kifejezetten arra utasítja a fordítót, hogy még ha Debug módban is indítod a buildet, bizonyos optimalizációkat hajtson végre. Ez az -Os (Optimize for Size) kényszeríti a fordítót a bináris méretének csökkentésére, emiatt összevon sorokat és ugrál a kód a debuggerben. Kommenteld ki ezt a sort (# add_compile_options("-Os")), töröld a build mappát, és építsd újra a csomagot.
```

A javaslat után a debugger végre stabilan követte a C++ sorokat, és elvezetett a valós hibahelyig. Az összeomlás a gpd::util::Cloud objektum destruktorában, az aligned_free(ptr) hívásánál történt. Ahelyett, hogy az MI-vel kísérleti memóriakezelő kódot írattam volna, rákerestem a hivatalos GitHub issue-k között, és a találatot beküldtem kiértékelésre.

Prompt:
```
Ennél az issue-nál azt írták, hogy a CMakeLists.txt-ből kell kivenni valamit, de nem tudom, hogy ez mennyire releváns az én esetemben: https://github.com/atenpas/gpd/issues/141
```

MI:
```
Ez a GitHub issue releváns és tűpontosan rátapint a te problémádra is. Az issue-ban tárgyalt hiba oka az Eigen memóriahierarchia igazítása (alignment). Ha a GPD könyvtár és a ROS-csomagod eltérő igazítási/vektorizációs flag-ekkel lett lefordítva, a destruktor hívásakor az Eigen 'összezavarodik', és double free or corruption hibát dob. Add hozzá a GPD saját CMakeLists.txt fájljához az add_definitions(-DEIGEN_DONT_VECTORIZE) sort, majd futtass egy cmake .., make -j és sudo make install sorozatot.
```

A flag beépítése és a külső GPD library újrafordítása után a double free hiba véglegesen megszűnt. Ez a tanulság két irányba mutat: egyrészt komplex C++/ROS 2 rendszereknél a fordítási optimalizációs flag-ek, jelen esetben különösen az -Os, megnehezíthetik a pontos hibakeresést, ezért ilyen helyzetben a debug buildből történő átmeneti eltávolításuk jelentősen megkönnyítheti a hibakeresést, másrészt az MI akkor volt igazán hatékony, amikor nem a nyers hibaüzenetet kapta meg, hanem konkrét, külső forrást (a GitHub issue-t) is, így a spekuláció helyett egy már tesztelt megoldást tudott adaptálni a saját projektstruktúrámra.

### (3. tanulsághoz) A hibajelenség értelmezése a rendszer működési modellje alapján 

A double free hiba elhárítása után a GPD node már stabilan futott, azonban az Action-hívás CANCELED státusszal és üres eredménnyel tért vissza. Mivel a kamera előtt ekkor nem volt tárgy, elsőként én is felvetettem, hogy az üres asztal okozhatja-e a problémát.

Prompt:
```
Annyi a problémám, hogy a kamera előtt most nincs semmi az asztalon, mert valaki elvette a dobozt, ez lehet ennek az oka?
```

MI:
```
Ez egy hatalmas mérföldkő! Gratulálok, a `double free` hiba megszüntetése (az `EIGEN_DONT_VECTORIZE` flag-gel) a diplomatervezés egyik legnehezebb technikai akadálya volt. Az, hogy a kód lefut a `return`-ig és nem omlik össze, azt jelenti, hogy a memóriakezelésed most már stabil. 
A rövid válasz a kérdésedre: Igen, 99%, hogy az üres asztal az oka.
```

Az MI ezt követően azzal magyarázta a problémát, hogy az üres asztal miatt ugyan a GPD feldolgozása lefut, de nem keletkezik érvényes fogás, ezért üres eredmény kerül visszaadásra. Ezt azonban nem tartottam elegendő magyarázatnak a CANCELED státuszra, ezért ellenőriztem a GPD node termináljának naplóját is.

Prompt:
```
És itt nem kéne valaminek megjelennie abban a terminálban, ahol a launch fájl fut, és a graspokat számolja?
```

A napló alapján a GPD ténylegesen végrehajtotta a pontfelhő feldolgozását, a felületi normálisok számítását és a fogási pozíciók keresését:

[gpd-4] Processing cloud with 324504 points.
[gpd-4] Voxelized cloud: 279475
[gpd-4] Calculating surface normals ...
[gpd-4] Calculated 279475 surface normals in 0.7592s (mode: OpenMP).
[gpd-4] Sampling above plane ...
[gpd-4] Plane fit succeeded. 203296 samples above plane.
[gpd-4] Estimating local reference frames ...
[gpd-4] Estimated 100 frames in 0.0002s.
[gpd-4] Finding hand poses ...
[gpd-4] Found 100 hand sets in 0.02s

A napló tehát azt mutatta, hogy a feldolgozás nem egyszerűen egy üres bemeneten állt meg. Ennek ellenére az MI továbbra is az üres asztalból vezette le az üres eredményt és a CANCELED státuszt.

MI:
```
Mivel az asztal üres: 
A GPD valószínűleg a szűrési fázisban az összes (100 db) jelöltet eldobta, mert vagy az üres levegőt markolászták, vagy az asztallapba ütköztek volna. Ha az eredményül kapott lista üres, a program nem ír ki további "Selected grasps" üzenetet, hanem egyszerűen visszatér a hívóhoz egy üres eredménnyel.
```

Ezt az értelmezést azonban a futás tényleges menete nem támasztotta alá. Az Action-hívást elküldtem, megvártam a teljes feldolgozást, és nem állítottam le a GPD node-ot. A CANCELED státusz magától jelent meg az Action kliens termináljában.

Prompt:
```
Nem igaz, hogy amiatt nem került átküldésre, ugyanis az Actiont elküldtem, vártam, hogy történjenek a dolgok, majd az Actionhöz megnyitott terminálban visszakaptam ezt az üzenetet. Tehát le sem állítottam a GPD futását.
```

MI:
```
Igazad van, elnézést a félreértésért! Ha az action termináljában magától megjelent a CANCELED státusz anélkül, hogy te leállítottad volna a futást, az egy nagyon fontos nyom.

Ez azt jelenti, hogy a gpd.cpp Action Server oldalán valaki (vagy valami) szándékosan megszakította a folyamatot, miközben a számítások valójában lefutottak (ahogy a pufferek ürülése után láttuk is).

Nézzük meg, hol lehet a hiba a kódodban: [...]
```

A hibakeresés ezzel a ponttal váltott át a bemeneti adatok vizsgálatáról az Action Server működésének elemzésére. Az MI a gpd.cpp implementációját kezdte vizsgálni, különösen azt, hogy a számítás eredménye milyen módon kerül az Action result-jába, és milyen ponton változik meg az Action állapota. A további vizsgálatban így már nem pusztán a CANCELED üzenet jelentéséből próbáltam következtetni, hanem a teljes adat- és vezérlési folyamatot kellett követni a GPD számításától az Action kliensnek visszaadott eredményig.

A hibakeresés során ez azért volt lényeges, mert a CANCELED státusz önmagában félrevezető tünetnek bizonyult. A GPD háttérben végzett számítása és az Action kliens által érzékelt végállapot nem ugyanazt az állapotot tükrözte. A probléma feltárásához ezért a rendszer belső működési modelljét és az Action Server forráskódját kellett összevetni a tényleges futási naplókkal.

### (4. tanulsághoz) A valós rendszerállapot és kimenetek prioritása az elméleti feltevésekkel szemben

A fejlesztés során többször bebizonyosodott, hogy a futásidejű naplók, a program kimenete és a rendszer tényleges állapota sokkal megbízhatóbb kiindulópontot jelentenek, mint az MI kizárólag elméleti szabványokra vagy dokumentációkra épülő magyarázatai.

Erre jó példát szolgáltatott a GPD konfigurációs fájljának esete. A VS Code folyamatosan aláhúzta a sorokat, és az alábbi szintaktikai hibát jelezte: Unexpected scalar token in YAML stream

Amikor megadtam az MI-nek a hibaüzenetet és a fájl tartalmát, az a szabványos YAML-szintaxisból kiindulva arra jutott, hogy a konfiguráció hibás, mivel a kulcs-érték párok elválasztására kettőspont „:” helyett egyenlőségjelet „=” használtam. Ennek megfelelően azt javasolta, hogy minden „=” jelet cseréljek „:”-ra.

A futtatás azonban már ekkor ellentmondott ennek a feltételezésnek, mivel a konfigurációs fájl használata mellett a szimuláció elindult és lefutott, ezért ezt jeleztem az MI-nek.

Prompt:
```
Egyébként azt nem teljesen értem, hogy az error ellenére, amikor meghívtam ezt a config fájlt, szépen lefutott minden, és kiírásra kerültek az értékek. Szóval akkor végtére ez nem volt végzetes error, nem?
```

MI:
```
Valószínűleg azért futott le hibátlanul, mert a program nem tudta beolvasni a szintaktikailag hibás fájlt, és a szoftver gyárilag beégetett alapértelmezett értékeivel dolgozott tovább.
```

Ezt a magyarázatot azonban a futásidejű kimenet nem támasztotta alá, mivel a terminálban nem gyári, hanem a saját konfigurációmban megadott értékeket láttam. Ezért ezt külön visszajeleztem az MI-nek.

Prompt:
```
de a saját számaimat látom
```

MI:
```
Ez egy klasszikus eset: a szoftvered "okosabb" (vagy hanyagabb), mint a hivatalos YAML szabvány.
Ha látod a saját számaidat a kimeneten, az azt jelenti, hogy a programod belső beolvasó egysége (a parser) nem egy szigorú YAML-értelmező, hanem valószínűleg egy egyedi szövegbeolvasó script.
```

Ezen a ponton az MI már korrigálta az eredeti feltételezését, és azt kezdte gondolni, hogy a GPD konfigurációs fájlját nem szabványos YAML-formátumként dolgozza fel. A végső ellenőrzést azonban nem ez az elméleti magyarázat, hanem egy egyszerű gyakorlati próba adta: az „=” jelek „:”-re cserélése után a konfiguráció nem működött megfelelően. Ezzel szemben az eredeti, „=” jeleket használó konfiguráció a saját paraméterértékeimmel futott.

MI:
```
Ez egy nagyon fontos tanulság: a robotikában (különösen a régebbi C++ alapú kutatási kódoknál, mint amilyen a GPD) a fájl kiterjesztése hiába `.yaml`, a kód mögötte gyakran nem egy valódi, szabványos YAML-értelmezőt használ, hanem egy saját "házilag barkácsolt" beolvasót. 
Ha a kettősponttal nem működött, de az egyenlőségjellel igen, akkor az a helyzet, hogy a programod nem YAML-ként kezeli a fájlt, hanem egy sima konfigurációs (pl. `.cfg` vagy `.ini` jellegű) fájlként, ahol az `=` az elválasztó.
```

A gyakorlati teszt tehát felülírta az eredeti, szabványos YAML-szintaxisból kiinduló feltételezést. A VS Code által jelzett hiba valós volt a YAML-szabvány szempontjából, de nem jelentett futásidejű hibát a GPD saját konfiguráció-beolvasója számára. A fejlesztőeszköz által jelzett szintaktikai probléma és a tényleges programfutás ezért két különböző szinten jelentkezett: az egyik a fájl szabványos YAML-ként való értelmezését, a másik pedig a GPD saját konfigurációs formátumát tükrözte.

### (5. tanulsághoz) A függőségi és rendszerlánc végigkövetése a lokális javítás helyett

A RealSense, a GPD és a dgl_ros wrapper összekötésekor a rendszer egymás után több ponton is elakadt. A hibák nem egyetlen komponensre korlátozódtak: előbb a pontfelhő nem jutott el a GPD-hez, majd a megfelelő topic beállítása után a GPD hiányzó  Transform (TF) keret miatt omlott össze, végül a konfigurációs paraméterek okoztak problémát. A hibakeresés ezért nem egyetlen hibaüzenet javítását, hanem a teljes lánc állapotának végigkövetését igényelte.

Elsőként azt kellett tisztázni, hogy a RealSense valóban azon a topicon publikál-e, amit a GPD figyel.

Prompt:
```
Lehet, hogy nem jó topicot használ az Action, mert most nincs semmi, és az rqt_graph-ban is furcsán néz ki a node-ok kapcsolata. A GPD-hez tartozó topicot sem látom rendesen. Meg tudjuk nézni, hogy a RealSense pontosan melyik topicon publikálja a pontfelhőt, és a GPD melyik topicot figyeli?
```

MI:
```
A számok nem hazudnak: a /camera/camera/depth/color/points az élő topicod, hiszen ott stabil ~23-24 Hz-et látsz.
A másik csak egy üres "szellem" topic, amit valószínűleg a wrapper hozott létre, de nem küld rá semmit.
Ezért nem láttál korábban vonalat az rqt_graph-ban, és ezért várt hiába a GPD az adatokra.
```

A topic rendezése után a GPD egy nem létező camera_locobot_link koordinátarendszert keresett, majd Segmentation fault hibával leállt. A paraméterrel történő felülbírálás megpróbálása sem hozott megoldást. Végül egy statikus TF létrehozása oldotta meg a problémát a hiányzó és a valós frame között. A rendszer ezt követően már feldolgozta a pontfelhőt, viszont minden fogási jelöltet kiszűrt, ezért a különböző konfigurációs fájlokat egymás mellé téve kezdtem el vizsgálni őket.

Prompt:
```
Vesd össze a fájlokat: u5.cfg ..., ros_eigen_param.cfg ..., gpd_config.yaml ...
```

MI:
```
A fájlban ezeket látom: finger_width = 0.5 (50 cm széles ujj?!), hand_outer_diameter = 0.5, hand_depth = 0.5.
Ezek az értékek méterben vannak megadva, egy átlagos gripper ujjai kb. 1-2 centiméter szélesek. 
Írd át őket reális értékekre (pl. 0.01 vagy 0.02) – 0.5-ön hagyva a GPD egy félméteres "szörnyet" próbál ráilleszteni a
pontfelhőre, ami sehol nem fér el.
```

A hibakeresés így egymás után több, különböző absztrakciós szinten jelentkező problémát kapcsolt össze: a topic nevét, a TF-fát, a GPD futtatási konfigurációját és a gripper geometriáját. Ez a tanulság rávilágít arra, hogy összetett robotikai rendszerben a hibát nem érdemes annál a komponensnél keresni, ahol a végső hibaüzenet megjelenik, hanem a teljes adat- és vezérlési láncot kell végigkövetni és egymással összefüggésben értelmezni, ezáltal az MI válaszait is a lokális quick-fixek helyett a teljes rendszer kontextusának vizsgálata felé terelve.

## Összegzés

A GPD és a ROS 2-alapú komponensek integrálása során hamar kiderült, hogy az MI első javaslata sok esetben csak kiindulópontot jelentett a valódi hiba feltárásához. A hibák valódi okát többnyire csak akkor sikerült feltárni, amikor a javaslatokat kritikusan megvizsgáltam, visszakérdeztem az egyes feltételezésekre, és a build-folyamatot, valamint a függőségi kapcsolatokat lépésről lépésre elemeztem. Az MI ebben a folyamatban nem kész megoldásokat szolgáltatott, hanem a hibakeresés és az okok feltárásának strukturálásában nyújtott segítséget, miközben a javaslatok helyességét minden esetben önállóan kellett ellenőriznem. Az egyes hibák stabil megoldását végül nem az elsőként javasolt javítások, hanem a hiba okának és a mögötte álló rendszerszintű összefüggéseknek a megértése hozta el.