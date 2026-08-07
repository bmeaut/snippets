---
layout: default
codename: KontenerizacioROS
title: MI Esettanulmány Sablon
tags: snippets mieset
authors: Técsi Zsuzsanna Vilma
---

# Konténerizált ROS2 fejlesztői környezet felállítása és debugolása AI-val

## Beveztés (ezt a címet itt törölni!)
A diplomatervezési munka során egy meglévő [ROS2 Humble](https://docs.ros.org/en/humble/index.html) (Ubuntu 22.04 LTS) devcontainer alapú rendszerben dolgozom, mivel így a projekt hordozható marad és platformfüggetlenül, bármilyen host gépen futtatható. Az esettanulmány ennek a rendkívül összetett, konténerizált fejlesztői környezetnek az MI segítségével történő felépítését és stabilizálását mutatja be.

A rendszerbe integráltam egy mélységi kamerát (Intel RealSense D435i), egy megfogástervező algoritmust (Grasp Pose Detection - GPD) és a hozzá tartozó ROS2-es wrappert (dgl_ros_models), valamint szimulációs és vizualizációs szoftvereket (Gazebo, RViz, MoveIt). Mivel ezek a modulok nem „egymásnak készültek", azaz különböző build-rendszereket, függőségi láncokat, szoftververziókat és memóriakezelési konvenciókat használnak, az összeillesztésük során számos rendszerszintű hiba, fordítási inkompatibilitás és grafikai zavar lépett fel. Az esettanulmány fő fókusza az az iteratív mérnöki folyamat, amelyben az MI (Gemini, ChatGPT, Claude) nem kész kódok forrása volt, hanem strukturált, rendszerszintű hibakeresési partner, akinek tévedéseit és túlzott általánosításait folyamatosan és határozottan korrigálnom kellett.

## Tanulságok
1. Egy komplex, több könyvtárat összekötő környezetnél a teljes technológiai stack és mappastruktúra előzetes megadása (nem csak az aktuális hiba) lényegesen pontosabb, projektspecifikus választ eredményez, mint amikor csak egyetlen hibaüzenetre vagy fordítási naplóra támaszkodunk.

2. Fordítási hibák esetén az MI gyakran a forráskód módosítását javasolta, miközben a probléma valójában a függőségi láncban volt. Ilyenkor a verziók, branchek és build-rendszer átvizsgálása megbízhatóbb kiindulópontnak bizonyult.

3. Optimalizált (-Os) build mellett a debugger nem a tényleges végrehajtási sorrendet mutatta, ami megnehezítette egy memóriahiba felderítését. Csak a Debug build (-DCMAKE_BUILD_TYPE=Debug) és a VS Code "Attach to Process" funkciója tette lehetővé, hogy a call stack valóban megbízható legyen a hibakereséshez.

4. Egy framework nem dokumentált vagy szokatlan működését (például hogy egy ROS2 Action eredménye nem úgy jelenik meg, ahol elsőre várnánk) csak akkor sikerült helyesen értelmezni, amikor nem a hibaüzenetből, hanem a működési modellből indultunk ki.

5. Bizonyos hibák esetén a futásidejű naplók, a program kimenete és a rendszer tényleges állapota megbízhatóbb kiindulópontnak bizonyult, mint az MI dokumentációra vagy általános feltételezésekre épülő magyarázatai.

6. Amikor a hiba több könyvtár, build-rendszer vagy keretrendszer együttműködéséből adódott, a teljes függőségi láncot kellett áttekinteni. Ilyenkor nem volt elegendő egyetlen komponenst külön vizsgálni vagy javítani az MI javaslatai alapján.

## A környezet

A fejlesztői és futtatási környezet egy VS Code DevContainerben van elszigetelve a fizikai host géptől, így biztosítva a teljes hordozhatóságot és a laboratóriumi megosztott számítógép rendszerének épségét.

- Host OS: Ubuntu 22.04 LTS (Jammy Jellyfish)
- Robotikai middleware: ROS2 Humble Hawksbill
- Grafikus szimuláció és tervezés: Gazebo, RViz2, MoveIt2
- Hardver és SDK: Intel RealSense D435i mélységi kamera, librealsense SDK
- Megfogástervezés: a C++ alapú gpd (Grasp Pose Detection) könyvtár és a hozzá tartozó dgl_ros_models (a dgl_ros könyvtárban található csomag) ROS2 wrapper


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

### (1. tanulsághoz) Kontextusátadás és a projektspecifikus MI-válaszok [!!!]
A fejlesztés kezdeti fázisában, amikor a konténeres környezetben futtatott telepítők és szkriptek indításakor hibákba ütköztem, csupán az éppen aktuális hibaüzenetet másoltam be az MI-nek. Ez a megközelítés azonban nem hozott tartós eredményt, mivel a modell ilyenkor vakon tapogatózva csak általános Docker- és Linux-adminisztrációs tanácsokat adott (mint a jogosultságok ellenőrzése vagy a konténer manuális indítása).
A valódi fordulatot az jelentette, amikor a problémát nem elszigetelten kezeltem, hanem egyetlen átfogó, strukturált indító promptban adtam át a teljes környezeti kontextust: a bázis operációs rendszert (Ubuntu 22.04 LTS), a ROS2 Humble disztribúciót, a munkaterületem pontos mappastruktúráját, és az összes integrálni kívánt szoftverkomponenst. Ez a rendszerszintű megközelítés azonnal projektspecifikus irányba terelte az MI-t, amely így már képes volt a saját rendszerem alapján megfelelő támogatást nyújtani.

Prompt (Docker konténerben Bash script futtatása):
```
DevContaineren belül futtatok egy Ubuntu-t, amelyen belül ROS2 Humble distro segítségével szeretnék Gazebo-n és RVIZ-en belül szimulálásokat futtatni. Jelenleg a root/src mappában található a dgl_ros, moveit_task_conctructor, realsense_gazebo_plugin,Universal_Robots_ROS2_Gazebo_Simulation és a root alatt található a librealsense és a gpd repo.
```

MI (Docker konténerben Bash script futtatása):
```
[Keresd ki a Gemini válaszát, amely a megadott egyedi mappaszerkezet alapján meghatározza a model.sdf pontos célútvonalát az src/realsense_gazebo_plugin/models/realsense_camera/ alatt, és megadja a model.config fájl xml kódját!]
```

### (2. tanulsághoz) Kódmódosítás vs. függőségi lánc: a hibaforrás félreazonosítása [!!!]
--- 1. verzió:
A GPD és a dgl_ros_models közötti API-eltérésnél (a preprocessPointCloud függvény más paraméterszámot várt, mint amit a kód hívott) az MI első reakciója a saját kód átírása volt. Ezt nem fogadtam el, mert a kód korábban módosítás nélkül működött, így helyette arra kértem, nézzük végig, mi változhatott a függőségekben.

Prompt:
```
ez a kód korábban módosítás nélkül működött, szerintem nem ott van a hiba - nézzük végig inkább, hogy jó branch-en vagyunk-e, és hogy a gpd verziója egyezik-e azzal, amit a dgl_ros vár
```

Ez a visszakérdezés a beszélgetést egy tünetszintű patch-elésből egy rendszerszintű vizsgálattá alakította: a branch, a ROS_DISTRO, illetve a catkin/colcon különbség is terítékre került, mielőtt bármilyen kódmódosítás megtörtént volna.

--- 2. verzió:
A GPD és a dgl_ros_models közötti API-eltérésnél az MI első reakciója a saját kód átírása volt. Ezt nem fogadtam el, mert a kód korábban módosítás nélkül működött.

Prompt (V1):
```
i think im using the good version of the gpd
```

MI (V1):
```
~itt az kellene, ami elsőre a preprocessPointCloud függvény szignatúraváltozását feltételezte, majd rossz GPD-verzióra gyanakodott~
```

Ezután egy grep -R "preprocessPointCloud" . paranccsal ellenőriztük, hogy a workspace-ben lévő GPD ténylegesen csak az egyparaméteres függvényt tartalmazza. A vizsgálat váratlan irányba fordult:

Prompt (V1):
```
i closed and shut off my laptop yesterday... what if another repo should be changed, like for example dgl_ros?
```

MI (V1):
```
~itt az kellene, ami egy régebbi GPD-commit kipróbálását javasolta~
```

A régebbi commit viszont új hibát hozott elő:

Prompt (V1):
```
nem jó, hogy visszaváltottam, mivel itt kér olyanot, hogy catkin...
```

Ez egyértelművé tette, hogy a régebbi commit még ROS1-es, tehát ROS2 Humble alatt eleve használhatatlan. A tényleges megoldást végül nem a kód módosítása, hanem a dgl_ros repository megfelelő branch-re állítása jelentette.

### (3. tanulsághoz) Optimalizált build és a megtévesztő debugger-viselkedés [!!!]
A GPD pontfelhő-objektum megsemmisülésekor a program rendszeresen double free or corruption hibával elszállt. Ez nem egy az egyben megoldható hiba volt: a debugger lépésenkénti követése is furcsán "ugrált", ami külön kérdést vetett fel.

Prompt:
```
a debugger valamiért teljesen máshogy lépked a kódban, mint ahogy elvárnám, ez miért lehet, és emiatt nehéz megtalálni pontosan hol száll el
```

MI:
```
Ez klasszikus jele annak, hogy a build optimalizált (pl. CMake -Os), ami átrendezi a végrehajtási sorrendet. Váltsunk tiszta Debug buildre (-DCMAKE_BUILD_TYPE=Debug), utána a debugger a tényleges forráskódi sorrendet fogja követni.
```

Miután a hibát a debugger sor szerint visszakövette az aligned_free(ptr) hívásig, közösen jutottunk el odáig, hogy ez egy ismert Eigen-probléma, ami a vektorizációval és a memóriaigazítással (alignment) függ össze — ezt az MI a probléma megértetése után, GitHub issue-k alapján kötötte össze a -DEIGEN_DONT_VECTORIZE fordítási kapcsolóval. A megoldás tehát nem egy azonnali válasz volt, hanem egy lépésről lépésre felépített magyarázat eredménye.


### (4. tanulsághoz) Framework-sajátosságok feltárása a működési modell felől [!!!]
--- 1. verzió
Az Action-alapú hívások a terminálban CANCELED státusszal és üres eredménnyel tértek vissza, annak ellenére, hogy a grasp detection ténylegesen lefutott. Ez nem hibaüzenet volt, hanem egy működésbeli félreértés, amit csak a framework felépítésének megkérdezésével sikerült tisztázni.

Prompt:
```
miért kapok CANCELED státuszt és üres result-ot, holott a terminálban látom, hogy a grasp detection lefutott és van eredménye - hol landolhat ez az adat?
```

MI:
```
A dgl_ros implementációjában a kiszámított koordináták nem a Result, hanem a Feedback üzenetekben érkeznek vissza. Ha csak a Result-ot nézed, üresnek fog tűnni, pedig az adat korábban, a Feedback callback-ekben megérkezett.
```

Ez a felismerés csak azért jöhetett létre, mert a kérdés a rendszer felépítésére irányult ("hol landolhat"), nem magára a hibaüzenetre.

--- 2. verzió
A double free hiba megoldása után az Action-hívás továbbra sem tért vissza rendesen: a terminál CANCELED státuszt és üres eredményt adott, annak ellenére, hogy a grasp detection ténylegesen lefutott.

Prompt (GPD Debug Launch és Fordítási Hibák):
```
na, kivettem a gpd-búl azokat a flageket, maikit annál az adott issuenál írták, és az lenne a probléma most, hogy már nem kapok double free errort, de maga az action ezt kapja eredményül: [...] Result: grasp_state: '' Goal finished with status: CANCELED
```

MI (GPD Debug Launch és Fordítási Hibák):
```
~itt az kellene, ami tévesen azt feltételezte, hogy túl korán megszakítottam a futást Ctrl+C-vel~
```

Ezt egyértelműen cáfoltam:

Prompt (GPD Debug Launch és Fordítási Hibák):
```
nem igaz, hogy amiatt nem került átküldésre, ugyanis az actiont elküldtem, vártam, hogy történjenek a dolgok, majd az action-nek megnyitott terminálba visszakaptam ezt az üzenetet. Tehát le se állítottam a gpd futását.
```

MI (GPD Debug Launch és Fordítási Hibák):
```
~itt az kellene, ami feltárta, hogy a dgl_ros wrapper a koordinátákat a Feedback, nem a Result üzenetekben küldi vissza~
```

A hiba tehát nem az Action megszakadásából, hanem a framework egy nem dokumentált, szokatlan adatvisszaadási módjából fakadt.

### (5. tanulsághoz) Futásidejű bizonyíték az elméleti feltételezésekkel szemben [!!!]
A GPD konfigurációs fájljában "Unexpected scalar token in YAML stream" hibát kaptam. Az MI a szabványos YAML-szintaxist kérte számon, miközben a valóság mást mutatott.

Prompt (YAML hiba: Unexpected scalar token):
```
Egyébként azt nem teljesen értem, hogy az error ellenére amikor meghívtam ezt a config fájlt, akkor szépen lefutott minden és kiírásra kerültek a dolgok. Szóval akkor végtére ez nem volt végzetes error, nem?
```

MI (YAML hiba: Unexpected scalar token):
```
~itt az kellene, ami még mindig azt feltételezte, hogy a szoftver a gyári alapértelmezett értékeket használja~
```

Ezt egy tényszerű megfigyeléssel cáfoltam:

Prompt (YAML hiba: Unexpected scalar token):
```
de a saját számaimat látom
```

MI (YAML hiba: Unexpected scalar token):
```
~ itt az kellene, ami elismerte, hogy a szoftver egyedi, nem szabványos C++ beolvasót használ~
```

Amikor a "javítás" szerint mégis lecseréltem a = jeleket :-ra, a program hibásan futott, vagyis a lint-szerű hibaüzenet és a tényleges futásidejű viselkedés két külön dolog volt.

### (6. tanulsághoz) Rendszerszintű hiba: az integráció mint hibaforrás [!!!]
A RealSense kamera és a GPD összekötésénél a hiba nem egyetlen komponensben, hanem több rendszer együttes hibás állapotában rejlett.

Prompt (Docker RealSense DKMS Kernel Probléma):
```
lehet az action nem jó de nincs semmi és most a node graphom is fura. nincs observer már
```

MI (Docker RealSense DKMS Kernel Probléma):
```
~itt az kellene, ami az rqt_graph és a ros2 topic hz alapján rávezetett a duplikált névterű topicra~
```

A konfigurációs káosz feltárásához a fájlok együttes összevetése segített:

Prompt (Docker RealSense DKMS Kernel Probléma):
```
najó vesd összea fájlokat: u5.cfg ..., ros_eigen_param.cfg ...,gpd_config.yaml ...
```

MI (Docker RealSense DKMS Kernel Probléma):
```
~itt az kellene, ami feltárta a 0,5 méteres ujjhossz-értéket a YAML-ban, ami minden megfogási jelöltet kizárt~
```

Egyik hibát sem lehetett volna önmagában megoldani, csak a topic-elnevezés, a TF-keretek és a konfigurációs értékek együttes átvizsgálása vezetett stabil állapothoz.

## Összegzés

A GPD és a ROS2-alapú komponensek integrálása során hamar kiderült, hogy az MI első javaslata sok esetben csak kiindulópontot jelentett a valódi hiba feltárásához. A hibák valódi okát többnyire csak akkor sikerült feltárni, amikor a javaslatokat kritikusan megvizsgáltam, visszakérdeztem az egyes feltételezésekre, és a build-folyamatot, valamint a függőségi kapcsolatokat lépésről lépésre elemeztem. Az MI ebben a folyamatban nem kész megoldásokat szolgáltatott, hanem a hibakeresés és az okok feltárásának strukturálásában nyújtott segítséget, miközben a javaslatok helyességét minden esetben önállóan kellett ellenőriznem. A stabil végeredményt végül nem az első működő javítás, hanem a hiba okának és a mögötte álló rendszerszintű összefüggéseknek a megértése hozta el.
