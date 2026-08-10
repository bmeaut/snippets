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

**CHAT: Gemini - Docker konténerben Bash script futtatása**

A fejlesztés kezdeti fázisában, amikor a konténeres környezetben futtatott telepítők és szkriptek indításakor hibákba ütköztem, csupán az éppen aktuális hibaüzenetet másoltam be az MI-nek. Ez a megközelítés azonban nem hozott tartós eredményt, mivel a modell ilyenkor vakon tapogatózva csak általános Docker- és Linux-adminisztrációs tanácsokat adott (mint a jogosultságok ellenőrzése vagy a konténer manuális indítása).

A valódi fordulatot az jelentette, amikor a problémát nem elszigetelten kezeltem, hanem egyetlen átfogó, strukturált indító promptban adtam át a teljes környezeti kontextust: a bázis operációs rendszert (Ubuntu 22.04 LTS), a ROS2 Humble disztribúciót, a munkaterületem pontos mappastruktúráját és az összes integrálandó komponenst. 

Prompt:
```
DevContaineren belül futtatok egy Ubuntu-t, amelyen belül ROS2 Humble distro segítségével szeretnék Gazebo-n és RVIZ-en belül szimulálásokat futtatni. Jelenleg a root/src mappában található a dgl_ros, moveit_task_conctructor, realsense_gazebo_plugin,Universal_Robots_ROS2_Gazebo_Simulation és a root alatt található a librealsense és a gpd repo.
```

MI:
```
Ez rengeteget segít! Így már összeállt a kép: egy komplex ROS 2 Humble fejlesztői környezetet (DevContainer) próbálsz felépíteni, ahol a MoveIt, a Gazebo és a RealSense pluginok közötti függőségeket kell feloldanod.
```

Ez a rendszerszintű megközelítés azonnal projektspecifikus irányba terelte az MI-t, amely így már képes volt a saját rendszerem alapján megfelelő támogatást nyújtani.

### (2. tanulsághoz) A függőségi lánc felülvizsgálata a forráskód módosítása helyett 

**CHAT: ChatGPT - ROS2 Dependency Mismatch Issue**

Amikor a colcon build parancsot futtattam, a dgl_ros_models ROS2 wrapper fordítása sikertelen volt, mert a fordító szerint a hívott preprocessPointCloud függvény paraméterszáma nem egyezett a deklarációval ("candidate expects 1 argument, 2 provided").

Az MI legelső reakciója a forráskód módosítása volt, vagyis egyszerűen csak töröljem ki a hívásból a második paramétert. Ezt nem tartottam megfelelő megoldásnak, mivel a kód a RealSense Gazebo plugin telepítése előtt módosítás nélkül működött. Ezért inkább azt feltételeztem, hogy a plugin telepítése során valamelyik függőség verziója vagy a függőségek közötti kompatibilitás változott meg.

Prompt:
```
[...] Before installing the plugin, the code ran perfectly, but now I’m getting an argument mismatch error, which I’ve copied at the end of this message. What could be causing this?
Gemini suggests modifying the functions, but I don’t feel like that is the right approach, since the code worked correctly before I installed the plugin. I also haven’t been able to find many similar problems or solutions online.
Could you please help me figure out what is causing this issue and how I can resolve it? I’d also appreciate it if you could provide some sources that I can read to better understand the issue, preferably discussions or posts from other people who have encountered a similar problem.[...]

```

MI:
```
It’s possible that the issue is caused by an incompatibility in the Point Cloud Library (PCL) or Eigen, or that the recently installed RealSense plugin overwrote a system-level include file. It might be worth creating a symlink to the PCL library.
```

A javasolt symlink létrehozását nem követtem, mivel a hibaüzenet nem hiányzó könyvtárra vagy #include problémára, hanem a preprocessPointCloud függvénynek átadott argumentumok számának eltérésére utalt. Ehelyett a workspace-ben található GPD forráskódot vizsgáltam meg a grep -R "preprocessPointCloud" . paranccsal. Ez megerősítette, hogy a használt GPD-ben a függvény egyparaméteres deklarációval szerepel.

A további egyeztetés során az MI egy régebbi GPD-commit használatát javasolta. Ez azonban újabb hibát eredményezett, mivel az adott verzió már catkin build-rendszert használt. Ekkor az MI felismerte, hogy a javasolt verzió nem illeszkedik a jelenlegi ROS2 Humble környezethez.

MI:
```
The catkin error is actually a clue: those older GPD commits were designed for ROS1, while your current setup is ROS2 Humble/colcon. So reverting to an older GPD commit is not appropriate for this environment.
```

Ez a felismerés tovább szűkítette a lehetséges okokat, nem egyszerűen egy másik GPD-verzió használatára volt szükség, hanem azt kellett megvizsgálni, hogy a ROS2 wrapper és a hozzá tartozó GPD-verzió ugyanazt az API-t használja-e. A végső megoldás ennek alapján a dgl_ros megfelelő, ROS2 Humble-lel kompatibilis branch-ének használata lett, nem pedig a preprocessPointCloud hívásának módosítása.

### (3. tanulsághoz) A fordítási optimalizációk feloldása és a VS Code "Attach to Process" használata

**CHAT: Gemini - GPD Debug Launch és Fordítási Hibák**

A GPD program tesztelése során a pontfelhő objektumok felszabadításakor a szoftver rendszeresen double free or corruption hibával elszállt. A hiba helyének felderítését megnehezítette, hogy a VS Code-ba ágyazott GDB debuggerrel lépkedve a kód végrehajtása kaotikusan ugrált a sorok között.

Prompt:
```
A debugger valamiért teljesen máshogy lépked a kódban, mint ahogy elvárnám. Ez miért lehet, és hogyan tudnám pontosan nyomon követni, hogy hol száll el a program?
```

MI:
```
Ez a CMake alapértelmezett fordítási optimalizációja (pl. -O2 vagy -Os) miatt van — a compiler átrendezi a gépi utasításokat, ezért a debugger nem tudja hűen lekövetni a forráskód sorait. Váltsunk tiszta Debug buildre (-DCMAKE_BUILD_TYPE=Debug), és a launch fájl helyett használd a VS Code "Attach to Process" funkcióját a már futó node-hoz csatlakozáshoz.
```

A javaslat után a debugger végre stabilan követte a C++ sorokat, és elvezetett a valós hibahelyig. A crash az objektum destruktorában, az aligned_free(ptr) hívásánál történt. Ahelyett, hogy az MI-vel kísérleti memóriakezelő kódot írattam volna, rákerestem a hivatalos GPD repó issue-i között, és a találatot beküldtem kiértékelésre.


Prompt:
```
A GDB segítségével azonosítottam, hogy a crash az aligned_free(ptr) hívásnál történik. Találtam egy GitHub issue-t, ahol a CMakeLists módosítását javasolják: https://github.com/atenpas/gpd/issues/141 — értékeld ki, releváns-e ez az én Eigen-t használó DevContaineres környezetemben!
```

MI:
```
Igen, teljesen releváns — az Eigen vektorizációs és memóriaigazítási mechanizmusai gyakran ütköznek a modern compilerek memóriaallokációs logikájával, izolált Docker-környezetben különösen. Add hozzá a -DEIGEN_DONT_VECTORIZE fordítási kapcsolót a CMakeLists.txt-hez.
```

A flag beépítése után a double free hiba véglegesen megszűnt, így bizonyítva, hogy a nehezen felderíthető memóriahibáknál a fordítási optimalizációk feloldása és a közösségi hibajegyek bevonása gyorsabb utat jelent, mint az azonnali kódátírás.

### (4. tanulsághoz) A hibajelenség értelmezése a rendszer működési modellje alapján 

**CHAT: Gemini - GPD Debug Launch és Fordítási Hibák**

A double free hiba elhárítása után a GPD node már stabilan futott, azonban az Action-hívás CANCELED státusszal és üres eredménnyel tért vissza. Mivel a kamera előtt ekkor nem volt tárgy, elsőként én is felvetettem, hogy az üres asztal okozhatja-e a problémát.

Prompt:
```
Annyi a problémám hogy a kamera előtt az asztalon semmi sincs most ott, mert valaki elvette a dobozt, ez lehet ennek az oka?
```

MI:
```
Ez egy hatalmas mérföldkő! Gratulálok, a **`double free` hiba megszüntetése** (az `EIGEN_DONT_VECTORIZE` flaggel) a diplomatervezés egyik legnehezebb technikai akadálya volt. Az, hogy a kód lefut a `return`-ig és nem omlik össze, azt jelenti, hogy a memóriakezelésed most már stabil. 
A rövid válasz a kérdésedre: **Igen, 99%, hogy az üres asztal az oka.**
```

Az MI ezt követően azzal magyarázta a problémát, hogy az üres asztal miatt ugyan a GPD feldolgozása lefut, de nem keletkezik érvényes fogás, ezért üres eredmény kerül visszaadásra. Ezt azonban nem tartottam elegendő magyarázatnak a CANCELED státuszra, ezért ellenőriztem a GPD node termináljának naplóját is.

Prompt:
```
és itt nem kéne valaminek lennie, abban a terminálban, ahol a launch fileomat futtatom és számolja a graspokat?
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

A log tehát azt mutatta, hogy a feldolgozás nem egyszerűen egy üres bemeneten állt meg. Ennek ellenére az MI továbbra is az üres asztalból vezette le az üres eredményt és a CANCELED státuszt.

MI:
```
Mivel az asztal üres: 
A GPD valószínűleg a szűrési fázisban az összes (100 db) jelöltet eldobta, mert vagy az üres levegőt markolászták, vagy az asztallapba ütköztek volna. Ha az eredményül kapott lista üres, a program nem ír ki további "Selected grasps" üzenetet, hanem egyszerűen visszatér a hívóhoz egy üres eredménnyel.
```

Ezt az értelmezést azonban a futás tényleges menete nem támasztotta alá. Az Action-hívást elküldtem, megvártam a teljes feldolgozást, és nem állítottam le a GPD node-ot; a CANCELED státusz magától jelent meg az Action kliens termináljában.

Prompt:
```
nem igaz, hogy amiatt nem került átküldésre, ugyanis az actiont elküldtem, vártam, hogy történjenek a dolgok, majd az action-nek megnyitott terminálba visszakaptam ezt az üzenetet. Tehát le se állítottam a gpd futását.
```

MI:
```
Igazad van, elnézést a félreértésért! Ha az action termináljában magától megjelent a CANCELED státusz anélkül, hogy te leállítottad volna a futást, az egy nagyon fontos nyom.

Ez azt jelenti, hogy a gpd.cpp Action Server oldalán valaki (vagy valami) szándékosan megszakította a folyamatot, miközben a számítások valójában lefutottak (ahogy a pufferek ürülése után láttuk is).

Nézzük meg, hol lehet a hiba a kódodban: [...]
```

A hibakeresés ezzel a ponttal váltott át a bemeneti adatok vizsgálatáról az Action Server működésének elemzésére. Az MI a gpd.cpp implementációját kezdte vizsgálni, különösen azt, hogy a számítás eredménye milyen módon kerül az Action resultjába, és milyen ponton változik meg az Action állapota. A további vizsgálatban így már nem pusztán a CANCELED üzenet jelentéséből próbáltunk következtetni, hanem a teljes adat- és vezérlési folyamatot kellett követni a GPD számításától az Action kliensnek visszaadott eredményig.

A hibakeresés során ez azért volt lényeges, mert a CANCELED státusz önmagában félrevezető tünetnek bizonyult: a GPD háttérben végzett számítása és az Action kliens által érzékelt végállapot nem ugyanazt az állapotot tükrözte. A probléma feltárásához ezért a rendszer belső működési modelljét és az Action Server forráskódját kellett összevetni a tényleges futási naplókkal.

### (5. tanulsághoz) A valós rendszerállapot és kimenetek prioritása az elméleti feltevésekkel szemben

**CHAT: Gemini - YAML hiba: Unexpected scalar token**

A fejlesztés során többször bebizonyosodott, hogy a futásidejű naplók, a program kimenete és a rendszer tényleges állapota sokkal megbízhatóbb kiindulópontot jelentenek, mint az MI kizárólag elméleti szabványokra vagy dokumentációkra épülő magyarázatai.

Erre jó példát szolgáltatott a GPD konfigurációs fájljának esete. A VS Code folyamatosan aláhúzta a sorokat, és az alábbi szintaktikai hibát jelezte: Unexpected scalar token in YAML stream

Amikor megadtam az MI-nek a hibaüzenetet és a fájl tartalmát, az a szabványos YAML-szintaxisból kiindulva arra jutott, hogy a konfiguráció hibás, mivel a kulcs-érték párok elválasztására kettőspont (:) helyett egyenlőségjelet (=) használtam. Ennek megfelelően azt javasolta, hogy minden = jelet cseréljek :-ra.

A futtatás azonban már ekkor ellentmondott ennek a feltételezésnek: a konfigurációs fájl használata mellett a szimuláció elindult és lefutott, ezért ezt jeleztem az MI-nek.

Prompt:
```
Egyébként azt nem teljesen értem, hogy az error ellenére amikor meghívtam ezt a config fájlt, akkor szépen lefutott minden és kiírásra kerültek a dolgok. Szóval akkor végtére ez nem volt végzetes error, nem?
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
Ez egy klasszikus eset: a szoftvered **"okosabb" (vagy hanyagabb), mint a hivatalos YAML szabvány.** 
Ha látod a saját számaidat a kimeneten, az azt jelenti, hogy a programod belső beolvasó egysége (a parser) nem egy szigorú YAML-értelmező, hanem valószínűleg egy **egyedi szövegbeolvasó script**.
```

Ezen a ponton az MI már korrigálta az eredeti feltételezését, és azt kezdte feltételezni, hogy a GPD nem szabványos YAML-parsert használ. A végső ellenőrzést azonban nem ez az elméleti magyarázat, hanem egy egyszerű gyakorlati próba adta: az = jelek : jelekre cserélése után a konfiguráció nem működött megfelelően. Ezzel szemben az eredeti, = jeleket használó konfiguráció a saját paraméterértékeimmel futott.

MI:
```
Ez egy nagyon fontos tanulság: a robotikában (különösen a régebbi C++ alapú kutatási kódoknál, mint amilyen a **GPD**) a fájl kiterjesztése hiába `.yaml`, a kód mögötte gyakran nem egy valódi, szabványos YAML-értelmezőt használ, hanem egy **saját "házilag barkácsolt" beolvasót**. 
Ha a kettősponttal nem működött, de az egyenlőségjellel igen, akkor az a helyzet, hogy a programod **nem YAML-ként kezeli a fájlt**, hanem egy sima konfigurációs (pl. `.cfg` vagy `.ini` jellegű) fájlként, ahol az `=` az elválasztó.
```
A gyakorlati teszt tehát felülírta az eredeti, szabványos YAML-szintaxisból kiinduló feltételezést. A VS Code által jelzett hiba valós volt a YAML-szabvány szempontjából, de nem jelentett futásidejű hibát a GPD saját konfiguráció-beolvasója számára. A fejlesztőeszköz által jelzett szintaktikai probléma és a tényleges programfutás ezért két különböző szinten jelentkezett: az egyik a fájl szabványos YAML-ként való értelmezését, a másik pedig a GPD saját konfigurációs formátumát tükrözte.

### (6. tanulsághoz) Rendszerszintű megközelítés a hiba elszigetelése helyett

**CHAT: Gemini - Docker RealSense DKMS Kernel Probléma**

Amikor a RealSense kamerát, a GPD-t és a dgl_ros wrappert próbáltam összekötni, a rendszer több, egymással összefüggő problémán keresztül akadt el. A hibák nem egyetlen komponensre korlátozódtak, először a pontfelhő nem jutott el a GPD-hez, majd a megfelelő topic beállítása után a GPD a hiányzó TF-keretek miatt összeomlott, később pedig a beérkező pontfelhő feldolgozása során a konfigurációs paraméterek okoztak problémát. A hibakeresés ezért nem egyetlen hibaüzenet javítását, hanem a teljes adatfeldolgozási lánc állapotának vizsgálatát igényelte.

Elsőként azt kellett meghatározni, hogy a RealSense valóban azon a topicon publikálja-e a pontfelhőt, amelyet a GPD használ. Ezt az rqt_graph és a ros2 topic hz segítségével ellenőriztem.

Prompt:
```
Lehet az action nem jó, de nincs semmi és most a node graphom is fura. nincs observer már
```

MI:
```
A számok nem hazudnak: a /camera/camera/depth/color/points az élő topicod, hiszen ott stabil ~23-24 Hz-et látsz. A másik csak egy üres "szellem" topic, amit valószínűleg a wrapper hozott létre, de nem küld rá semmit.

Ezért nem láttál korábban vonalat az rqt_graph-ban, és ezért várt hiába a GPD az adatokra.
```

A topic megfelelő beállítása után a GPD már megkapta a pontfelhőt, azonban újabb hiba jelent meg: a node egy nem létező camera_locobot_link koordinátarendszert keresett, majd Segmentation fault hibával leállt. A parancssori paraméterrel megpróbáltam a használt frame-et camera_link értékre állítani, de a node ezt figyelmen kívül hagyta.

A futási napló ezt mutatta:
```
[INFO] [agent]: Could not transform camera_locobot_link to world: "camera_locobot_link" passed to lookupTransform argument source_frame does not exist. [ros2run]: Segmentation fault
```

MI:
```
Sajnos úgy tűnik, a -p base_frame:=camera_link paramétert egyszerűen nem vette figyelembe a node. Ez azért van, mert vagy más a paraméter neve a kódban (pl. sensor_frame_id vagy camera_frame), vagy a program egy pontján bele van égetve (hardkódolva) ez a camera_locobot_link név. 

Mivel a C++ kód azonnal elszáll (Segmentation fault), amint nem találja ezt a nevet, ne harcoljunk a paraméterekkel, hanem alkalmazzunk "brute force" megoldást: hozzuk létre azt a nevet, amit a szoftver keres!
```

Mivel a paraméter felülbírálása nem bizonyult hatásosnak, a hiányzó TF-kapcsolatot statikus transzformációkkal hidaltam át. Az MI azt javasolta, hogy külön kapcsolatot hozzak létre a world és a GPD által keresett camera_locobot_link, valamint ez utóbbi és a tényleges camera_link között.

MI:
```
A megoldás: Static Transform Bridge

Nyiss egy új terminált, és futtasd ezt a parancsot. Ez azt mondja a ROS-nak, hogy a world koordináta-rendszer és a hiányzó camera_locobot_link pontosan ugyanott van: ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 world camera_locobot_link

És ami még fontosabb: a kamerád valószínűleg camera_link néven küldi az adatokat, tehát össze kell kötnünk a kettőt.
```
A topic- és TF-problémák rendezése után a rendszer már ténylegesen feldolgozta a pontfelhőt, azonban a GPD minden megfogási jelöltet kiszűrt. A hibakeresés következő szintjén ezért nem egyetlen konfigurációs fájlt vizsgáltam, hanem összehasonlítottam a különböző komponensekhez tartozó konfigurációkat.

ÉN:
```
Vesd összea fájlokat: u5.cfg ..., ros_eigen_param.cfg ...,gpd_config.yaml ...
```
Az összehasonlítás során az MI olyan ellentmondást azonosított, amely az egyes fájlok külön-külön történő vizsgálatából nem feltétlenül lett volna nyilvánvaló: míg a többi konfiguráció reális, centiméteres nagyságrendű gripperméreteket tartalmazott, a gpd_config.yaml fájlban több geometriai paraméter értéke 0.5 volt.

MI:
```
A fájlban ezeket látom:
● finger_width = 0.5 (50 cm széles ujj?!)
● hand_outer_diameter = 0.5 (50 cm átmérő?!)
● hand_depth = 0.5 (50 cm hosszú ujj?!)

Ezek az értékek méterben vannak megadva. Egy átlagos UR5 vagy Panda robot gripper ujjai kb. 1-2 centiméter szélesek.

Javítás: Írd át őket reális értékekre (pl. 0.01 vagy 0.02). Ha 0.5-ön hagyod, a GPD egy félméteres "szörnyet" próbál ráilleszteni a pontfelhődre, ami valószínűleg sehol nem fér el.
```
A naplók ezt a feltételezést is alátámasztották: a pontfelhő feldolgozása és a fogási jelöltek generálása már megtörtént, de a jelöltek szűrése után nem maradt érvényes fogás. Az MI ezt a konfigurációs értékekkel és a munkatér korlátaival hozta összefüggésbe:

MI:
```
● Voxelized cloud: 13782 (Szuper, van adat!)
● Calculated 13782 surface normals (Szuper, látja a felületeket!)
● Found 500 hand sets (Szuper, az algoritmus működik!)
Már csak az a baj, hogy a "0.5 méteres" ujjméret és a szűk munkatér miatt a legvégén mindet elutasítja.
```
A hibakeresés során tehát egymás után több, különböző absztrakciós szinten jelentkező problémát kellett összekapcsolni: a RealSense által publikált topic nevét, a ROS2 TF-fát, a GPD futtatási konfigurációját és a gripper geometriai paramétereit. Az egyes hibák önmagukban csak részleges magyarázatot adtak a rendszer működésére; a tényleges probléma feltárásához azt kellett követni, hogy az adat a kamera publikálásától a GPD feldolgozásáig minden egyes rétegen megfelelően továbbjut-e.

Ez a hibakeresési folyamat megmutatta, hogy összetett robotikai rendszerekben a hibát nem feltétlenül érdemes annál a komponensnél keresni, ahol a végső hibaüzenet megjelenik. A stabil működéshez a teljes adat- és vezérlési láncot kellett vizsgálni, és az egyes komponensek állapotát egymással összefüggésben értelmezni.

## Összegzés

A GPD és a ROS2-alapú komponensek integrálása során hamar kiderült, hogy az MI első javaslata sok esetben csak kiindulópontot jelentett a valódi hiba feltárásához. A hibák valódi okát többnyire csak akkor sikerült feltárni, amikor a javaslatokat kritikusan megvizsgáltam, visszakérdeztem az egyes feltételezésekre, és a build-folyamatot, valamint a függőségi kapcsolatokat lépésről lépésre elemeztem. Az MI ebben a folyamatban nem kész megoldásokat szolgáltatott, hanem a hibakeresés és az okok feltárásának strukturálásában nyújtott segítséget, miközben a javaslatok helyességét minden esetben önállóan kellett ellenőriznem. A stabil végeredményt végül nem az első működő javítás, hanem a hiba okának és a mögötte álló rendszerszintű összefüggéseknek a megértése hozta el.
