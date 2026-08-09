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

### (1. tanulsághoz) A teljes technológiai stack és kontextus átadása az indításkor 

A fejlesztés kezdeti fázisában, amikor a konténeres környezetben futtatott telepítők és szkriptek indításakor hibákba ütköztem, csupán az éppen aktuális hibaüzenetet másoltam be az MI-nek. Ez a megközelítés azonban nem hozott tartós eredményt, mivel a modell ilyenkor vakon tapogatózva csak általános Docker- és Linux-adminisztrációs tanácsokat adott (mint a jogosultságok ellenőrzése vagy a konténer manuális indítása).

A valódi fordulatot az jelentette, amikor a problémát nem elszigetelten kezeltem, hanem egyetlen átfogó, strukturált indító promptban adtam át a teljes környezeti kontextust: a bázis operációs rendszert (Ubuntu 22.04 LTS), a ROS2 Humble disztribúciót, a munkaterületem pontos mappastruktúráját ésaz összes integrálandó komponenst. 

Prompt (Docker konténerben Bash script futtatása):
```
DevContaineren belül futtatok egy Ubuntu-t, amelyen belül ROS2 Humble distro segítségével szeretnék Gazebo-n és RVIZ-en belül szimulálásokat futtatni. Jelenleg a root/src mappában található a dgl_ros, moveit_task_conctructor, realsense_gazebo_plugin,Universal_Robots_ROS2_Gazebo_Simulation és a root alatt található a librealsense és a gpd repo.
```

MI (Docker konténerben Bash script futtatása): !!!!!
```
[Keresd ki a Gemini válaszát, amely a megadott egyedi mappaszerkezet alapján meghatározza a model.sdf pontos célútvonalát az src/realsense_gazebo_plugin/models/realsense_camera/ alatt, és megadja a model.config fájl xml kódját!]
```
Ez a rendszerszintű megközelítés azonnal projektspecifikus irányba terelte az MI-t, amely így már képes volt a saját rendszerem alapján megfelelő támogatást nyújtani.

### (2. tanulsághoz) A függőségi lánc felülvizsgálata a forráskód módosítása helyett 

Amikor a colcon build parancsot futtattam, a dgl_ros_models ROS2 wrapper fordítása sikertelen volt, mert a fordító szerint a hívott preprocessPointCloud függvény paraméterszáma nem egyezett a deklarációval ("candidate expects 1 argument, 2 provided").

Az MI legelső reakciója a forráskód módosítása volt, az az töröljem ki a hívásból a második paramétert. Ezt elutasítottam, mivel a kód korábban módosítás nélkül működött. 
Meggyőződésem volt, hogy a hiba nem a kódban, hanem a függőségi lánc valamelyik verzióeltérésében keresendő, ezért elkezdtem visszaterelni az MI-t a rendszerszintű vizsgálat felé.

Prompt (ROS2 Dependency Mismatch Issue V1):
```
i think im using the good version of the gpd
```

MI (ROS2 Dependency Mismatch Issue V1):
```
~itt az kellene, ami elsőre a preprocessPointCloud függvény szignatúraváltozását feltételezte, majd rossz GPD-verzióra gyanakodott~
Elképzelhető, hogy a háttérben a Point Cloud Library (PCL) vagy az Eigen inkompatibilitása okozza a hibát, vagy a nemrég telepített RealSense plugin írt felül egy rendszerszintű include fájlt. Érdemes lenne symlinket létrehozni a PCL könyvtárhoz.
```

A javasolt symlink-hack nyilvánvalóan nem oldotta volna meg a problémát, mert egy hiányzó könyvtár #include hibát adna, nem paraméterszám-eltérést. Ehelyett egy grep -R "preprocessPointCloud" . paranccsal bizonyítottam, hogy a workspace-be klónozott GPD valóban csak egyparaméteres függvényt tartalmaz, majd felvetettem, hogy nem a GPD, hanem a wrapper csomag lehet a hiba forrása. Az MI erre egy régebbi GPD-commit kipróbálását javasolta, ami azonban új hibát hozott elő.

Prompt (ROS2 Dependency Mismatch Issue V1):
```
nem jó, hogy visszaváltottam, mivel itt kér olyat, hogy catkin...
```

MI (V1): !!!!
```
~itt az kellene, ami egy régebbi GPD-commit kipróbálását javasolta~
A catkin a ROS1 build-rendszere. Ez azt jelenti, hogy a GPD régebbi commitjai még ROS1-eshez készültek, így nem használhatók a jelenlegi ROS2 Humble / colcon alapú környezetedben.
```

Ez a felismerés hozta meg a végső áttörést: a GPD legfrissebb, ROS2-kompatibilis verziója már az új, egyparaméteres API-t használja, a hibát pedig az okozta, hogy a dgl_ros wrapper nem volt szinkronban ezzel. A megoldást a dgl_ros repository humble branch-re állítása jelentette, nem a forráskód módosítása.

### (3. tanulsághoz) A fordítási optimalizációk feloldása és a VS Code "Attach to Process" használata
A GPD program tesztelése során a pontfelhő objektumok felszabadításakor a szoftver rendszeresen double free or corruption hibával elszállt. A hiba helyének felderítését megnehezítette, hogy a VS Code-ba ágyazott GDB debuggerrel lépkedve a kód végrehajtása kaotikusan ugrált a sorok között.

Prompt (GPD Debug Launch és Fordítási Hibák):
```
A debugger valamiért teljesen máshogy lépked a kódban, mint ahogy elvárnám. Ez miért lehet, és hogyan tudnám pontosan nyomon követni, hogy hol száll el a program?
```

MI (GPD Debug Launch és Fordítási Hibák):
```
Ez a CMake alapértelmezett fordítási optimalizációja (pl. -O2 vagy -Os) miatt van — a compiler átrendezi a gépi utasításokat, ezért a debugger nem tudja hűen lekövetni a forráskód sorait. Váltsunk tiszta Debug buildre (-DCMAKE_BUILD_TYPE=Debug), és a launch fájl helyett használd a VS Code "Attach to Process" funkcióját a már futó node-hoz csatlakozáshoz.
```

A javaslat után a debugger végre stabilan követte a C++ sorokat, és elvezetett a valós hibahelyig: a crash az objektum destruktorában, az aligned_free(ptr) hívásánál történt. Ahelyett, hogy az MI-vel kísérleti memóriakezelő kódot írattam volna, rákerestem a hivatalos GPD repó issue-i között, és a találatot beküldtem kiértékelésre.


Prompt (GPD Debug Launch és Fordítási Hibák):
```
A GDB segítségével azonosítottam, hogy a crash az aligned_free(ptr) hívásnál történik. Találtam egy GitHub issue-t, ahol a CMakeLists módosítását javasolják: https://github.com/atenpas/gpd/issues/141 — értékeld ki, releváns-e ez az én Eigen-t használó DevContaineres környezetemben!
```

MI (GPD Debug Launch és Fordítási Hibák):
```
Igen, teljesen releváns — az Eigen vektorizációs és memóriaigazítási mechanizmusai gyakran ütköznek a modern compilerek memóriaallokációs logikájával, izolált Docker-környezetben különösen. Add hozzá a -DEIGEN_DONT_VECTORIZE fordítási kapcsolót a CMakeLists.txt-hez.
```

A flag beépítése után a double free hiba véglegesen megszűnt, így bizonyítva, hogy a nehezen felderíthető memóriahibáknál a fordítási optimalizációk feloldása és a közösségi hibajegyek bevonása gyorsabb utat jelent, mint az azonnali kódátírás.

### (4. tanulsághoz) Nem dokumentált működések feloldása a működési modell alapján
A double free hiba elhárítása után a GPD node stabilan futott, de az Action-hívás CANCELED státusszal és üres eredménnyel tért vissza, miközben a háttérnaplók szerint a fogási pontok számítása sikeresen lezajlott.

Prompt (GPD Debug Launch és Fordítási Hibák):
```
Eltávolítottam a GPD forráskódjából a felesleges CMake flageket a javasolt issue alapján. A double free hiba valóban megszűnt, de az action továbbra is ezt adja eredményül: [...] Result: grasp_state: '' Goal finished with status: CANCELED Miért kapok CANCELED státuszt és üres eredményt, ha a háttérben a grasp detection sikeresen lefutott?
```

MI (GPD Debug Launch és Fordítási Hibák):
```
~itt az kellene, ami tévesen azt feltételezte, hogy túl korán megszakítottam a futást Ctrl+C-vel~
A CANCELED státusz leggyakrabban akkor fordul elő, ha az action kliens vagy a felhasználó manuálisan megszakítja a folyamatot, esetleg hálózati timeout lépett fel a DDS kommunikációban. Ellenőrizd, nem zártad-e be túl korán a futtató terminált.
```

Mivel tudtam, hogy a folyamat futása közben semmilyen manuális beavatkozást nem végeztem és végigvártam a teljes ciklust, határozottan cáfoltam az MI egyszerűsítő feltételezését. Ez a szigorú visszacsatolás kényszerítette rá a modellt, hogy elméleti találgatások helyett elkezdje elemezni az egyedi dgl_ros wrapper C++ forráskódját és annak Action-szerver implementációját.

Prompt (GPD Debug Launch és Fordítási Hibák):
```
Nem szakítottam meg a futást, és nem nyomtam meg a Ctrl+C-t. A dgl_ros wrapper háttérlogjaiban látszik, hogy a generált fogási pontok száma nagyobb, mint nulla. Ne a külső megszakítást vizsgáljuk, hanem nézzük meg a dgl_ros action-szerver belső implementációját! Hogyan adja vissza a kiszámított pontokat a kliensnek?
```

MI (GPD Debug Launch és Fordítási Hibák):
```
~itt az kellene, ami feltárta, hogy a dgl_ros wrapper a koordinátákat a Feedback, nem a Result üzenetekben küldi vissza~
Elnézést kérek a téves feltételezésért, a háttérlogok valóban cáfolják a korai leállítást! Átnézve a dgl_ros wrapper belső C++ forráskódját, egy rendkívül szokatlan és nem dokumentált architektúrális sajátosságot találtam.
```

A probléma gyökere tehát nem egy szoftverhiba vagy megszakadás volt, hanem a framework egy nem dokumentált, szokatlan adatvisszaadási logikája, amit csak a hibaüzenet tüneti kezelése helyett, a rendszer működési modelljének közvetlen vizsgálatával sikerült feloldani.

### (5. tanulsághoz) A valós rendszerállapot és kimenetek prioritása az elméleti feltevésekkel szemben

A fejlesztés során többször bebizonyosodott, hogy a futásidejű naplók, a program kimenete és a rendszer tényleges állapota sokkal megbízhatóbb kiindulópontot jelentenek, mint az MI kizárólag elméleti szabványokra vagy dokumentációkra épülő magyarázatai.

Erre a legtisztább példát a GPD YAML konfigurációs fájljának esete szolgáltatta. A VS Code lintere folyamatosan aláhúzta a sorokat, és az alábbi szintaktikai hibát jelezte: Unexpected scalar token in YAML stream

Amikor beküldtem a hibaüzenetet és a fájl tartalmát az MI-nek, az a hivatalos YAML szabványra támaszkodva kategorikusan kijelentette, hogy a fájl hibás, mivel a kulcs-érték párok elválasztására kettőspontok (:) helyett egyenlőségjeleket (=) használtam. Az MI azt javasolta, hogy azonnal javítsam át az összes = jelet :-ra. Megfigyeltem azonban, hogy az aláhúzások ellenére a szimuláció elindult és lefutott. Ezt jeleztem is az MI-nek.

Prompt (YAML hiba: Unexpected scalar token):
```
Egyébként azt nem teljesen értem, hogy az error ellenére amikor meghívtam ezt a config fájlt, akkor szépen lefutott minden és kiírásra kerültek a dolgok. Szóval akkor végtére ez nem volt végzetes error, nem?
```

MI (YAML hiba: Unexpected scalar token):
```
~itt az kellene, ami még mindig azt feltételezte, hogy a szoftver a gyári alapértelmezett értékeket használja ~
Valószínűleg azért futott le hibátlanul, mert a program nem tudta beolvasni a szintaktikailag hibás fájlt, és a szoftver gyárilag beégetett alapértelmezett értékeivel dolgozott tovább.
```

Nem fogadtam el ezt a magyarázatot, mivel a terminállogokban a saját, egyedi beállított értékeimet láttam viszont.

Prompt (YAML hiba: Unexpected scalar token):
```
de a saját számaimat látom
```


MI (YAML hiba: Unexpected scalar token):
```
~ itt az kellene, ami elismerte, hogy a szoftver egyedi, nem szabványos C++ beolvasót használ~
Ha a saját számaidat látod, az azt jelenti, hogy a GPD belső beolvasója nem szabványos YAML parsert használ, hanem egy egyedi C++ szövegolvasót, amely a .yaml kiterjesztés ellenére az egyenlőségjeles szintaxist várja. A hibaüzenetet csak a VS Code lintere generálja, futás szempontjából figyelmen kívül hagyható.
```

A gyakorlati verifikáció végül teljesen megcáfolta az MI elméleti következtetéseit. Amikor az utasításait követve kísérletképpen mégis lecseréltem az = jeleket :-ra, a GPD parser azonnal összeomlott, és a program nem tudott működni. A fejlesztőeszközök jelezte elméleti hibák és a valós futásidejű viselkedés tehát két teljesen különálló dolog. Ha vakon követtem volna az MI szintaktikai javaslatát, működésképtelen konfigurációt kaptam volna.

### (6. tanulsághoz) Rendszerszintű megközelítés a hiba elszigetelése helyett
Amikor a RealSense kamerát, a GPD-t és a dgl_ros wrappert próbáltam összekötni, egy olyan komplex hibajelenséggel találkoztam, ahol a rendszer látszólag minden hibaüzenet nélkül, csendben leállt. Nem egyetlen komponens hibázott, hanem több rendszer együttes, hibás állapota blokkolta az adatfolyamot.

Prompt (Docker RealSense DKMS Kernel Probléma):
```
lehet az action nem jó de nincs semmi és most a node graphom is fura. nincs observer már
```

MI (Docker RealSense DKMS Kernel Probléma):
```
~itt az kellene, ami az rqt_graph és a ros2 topic hz alapján rávezetett a duplikált névterű topicra~
Az rqt_graph és a ros2 topic list kimenete alapján a RealSense kamera egy duplikált névtér alatt publikálja a pontfelhőt (/camera/camera/depth/color/points a várt /camera/depth/color/points helyett), ezért a dgl_ros node nem kap adatot. Irányítsd át (remap) a topic nevét, vagy szüntesd meg a dupla névteret a kamera indítási paramétereiben.
```

A topic-elnevezés javítása után a GPD egy Segmentation fault hibával állt le, mert a kód a TF-fából hiányzó world és camera_locobot_link koordinátarendszereket kereste. Ezt static transform publisher node-okkal hidaltam át, miután az MI által javasolt parancssori paraméter-felülbírálás a gyakorlatban hatástalannak bizonyult. A pontfelhő és a transzformációk rendbetétele után azonban a rendszer minden megfogási jelöltet elutasított, ami újabb memóriahibát okozott. Hogy átlássam az ellentmondásokat, megkértem az MI-t, hogy vesse össze a rendszer különböző konfigurációs fájljait.

Prompt (Docker RealSense DKMS Kernel Probléma):
```
najó vesd összea fájlokat: u5.cfg ..., ros_eigen_param.cfg ...,gpd_config.yaml ...
```

MI (Docker RealSense DKMS Kernel Probléma):
```
~itt az kellene, ami feltárta a 0,5 méteres ujjhossz-értéket a YAML-ban, ami minden megfogási jelöltet kizárt~
Összehasonlítva a három konfigurációs fájl tartalmát, egy rendkívül súlyos ellentmondást találtam a robotkéz geometriájának megadásában.

Az u5.cfg és a ros_eigen_param.cfg méterben adja meg a gripper méreteit (pl. 0,025 m ujjhossz), a gpd_config.yaml-ban viszont a finger_width és hand_depth értékeknél 0,5 szerepel — ez gyakorlatilag egy félméteres robotujjat jelent, ami miatt a munkatér-szűrő minden pontfelhőt kiszűr. Írd át a YAML értékeit a CFG-ben szereplő reális méretekre.
```

Ez a rendszerszintű hibakeresés bebizonyította, hogy egy összetett, több szoftveres és hardveres réteget integráló projektben semmilyen hibát nem lehet önmagában, izoláltan kezelni. A stabil állapothoz egyszerre kellett szinkronba hozni a topic-elnevezéseket, a TF-kereteket és a konfigurációs fájlokban megbújó, egymásnak ellentmondó paramétereket.

## Összegzés

A GPD és a ROS2-alapú komponensek integrálása során hamar kiderült, hogy az MI első javaslata sok esetben csak kiindulópontot jelentett a valódi hiba feltárásához. A hibák valódi okát többnyire csak akkor sikerült feltárni, amikor a javaslatokat kritikusan megvizsgáltam, visszakérdeztem az egyes feltételezésekre, és a build-folyamatot, valamint a függőségi kapcsolatokat lépésről lépésre elemeztem. Az MI ebben a folyamatban nem kész megoldásokat szolgáltatott, hanem a hibakeresés és az okok feltárásának strukturálásában nyújtott segítséget, miközben a javaslatok helyességét minden esetben önállóan kellett ellenőriznem. A stabil végeredményt végül nem az első működő javítás, hanem a hiba okának és a mögötte álló rendszerszintű összefüggéseknek a megértése hozta el.
