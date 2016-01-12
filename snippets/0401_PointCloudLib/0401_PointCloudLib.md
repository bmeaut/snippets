---
layout: default
---

# Mi a Point Cloud Library?


# PCL telepítése - Windows


## 1. Git repository leszedése
`https://github.com/PointCloudLibrary/pcl.git`
## 2. Visual Studio 2010 telepítése
## 3. Függőségek telepítése
- Boost-1.50.0-vs2010-x64.exe
- cmake-3.1.1-win32-x86.exe
- Eigen-3.0.5.exe
- flann-1.7.1-vs2010-x64.exe
- qhull-6.2.0.1385-vs2010-x64.exe
- VTK-5.8.0-msvc2010-win64_with_qt_support.exe
- Qt_4.8.0_msvc2010_win64.exe
- OpenNI-Win64-1.5.4-Dev.msi
- Sensor-Win-OpenSource64-5.1.0.msi

## 4. CMake
- Forrás és cél könyvtár beállítása, VS 2010 x64 kiválasztása
- Configure, ha kell, paraméterek módosítása, újra Configure
- Generate
- Előállt a VS2010 Solution a fordításhoz

## 5. Boost függőségek javítása
- Az egyik boost lib hiányzik a linkelés beállításainál, ezt kézzel lehet pótolni a projektek beállításainál egyenként, vagy csoportos cserével, pl. Notepad++-szal:
- Csere a *.vcxproj fájlokban:

Keresés (debug):

```
C:\Program Files\Boost\lib\libboost_iostreams-vc100-mt-gd-1_50.lib
```

csere:

```
C:\Program Files\Boost\lib\libboost_iostreams-vc100-mt-gd-1_50.lib;C:\Program Files\Boost\lib\libboost_chrono-vc100-mt-gd-1_50.lib
```

és keresés (release):

```
C:\Program Files\Boost\lib\libboost_iostreams-vc100-mt-1_50.lib
```

csere:

```
C:\Program Files\Boost\lib\libboost_iostreams-vc100-mt-1_50.lib;C:\Program Files\Boost\lib\libboost_chrono-vc100-mt-1_50.lib
```

## 6. Fordítás
- VS 2010 fordítja a solution-t (debug / release!). Ez több órán át is tarthat. A függőségek hiányzó pdb-ire vonatkozó figyelmeztetések normálisak.

## 7. Saját alkalmazás létrehozása
-"CMakeLists.txt" létrehozása (pl. pclproject/src-ben):

```
cmake_minimum_required(VERSION 2.6 FATAL_ERROR)
project(<PROJEKTNÉV>)
find_package(PCL 1.2 REQUIRED)
include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})
add_executable (<PROJEKTNÉV> <PROJEKTNÉV>.cpp <PROJEKTNÉV>.h)
target_link_libraries(<PROJEKTNÉV> ${PCL_LIBRARIES})
```

-CMake indítás, forrás (src) könyvtár megadása, cél (pl. pclproject/build) megadása, Configure, [paraméterek módosítása], Configure, Generate

-Elkészült solution megnyitása VS2010-ben

-Project/Properties/Linker/Input/Additional Dependencies: fel kell venni a chrono függőséget:

Debug:

	C:\Program Files\Boost\lib\libboost_chrono-vc100-mt-gd-1_50.lib

Release:

	C:\Program Files\Boost\lib\libboost_chrono-vc100-mt-1_50.lib

<small>Szerzők, verziók: Kovács Viktor</small>