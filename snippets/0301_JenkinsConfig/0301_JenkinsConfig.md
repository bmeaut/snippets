---
layout: default
---

# Jenkins konfiguráció

A Jenkins egy javaban írt nyílt forráskódú folyamatos integrációs eszköz (continous integration tool). A Jenkins folyamatos integrációs szolgáltatást nyújt szoftverfejlesztéshez. Ez egy szerver alapú szolgáltatás, ami a legtöbb verziókezelő (SCM) eszközt támogat (CVS, GIT, Subversion, RTC). Legfontosabb feladata, hogy folyamatosan lefuttassa és tesztelje a szoftver projekteteket, és ezáltal könnyebbé tegye a szoftverfejlesztés folyamatát. Hivatalos honlap: https://jenkins-ci.org/

## Telepítés

A jenkins telepítése rendkívül egyszerű feladat.

![](image/Jenkins_kep_02.png)

Csak le kell tölteni a honlapról a Windows native package-t. Majd egyszerűen a next-next-finish módszerrel telepíthető is. A böngésző http://localhost:8080/ URL-jén futtatható.

## A Jenkins funkciói

„Új item” fül alatt hozhatunk létre projekteket. Itt létrehoztam egy freestyle projectet.

![](image/Jenkins_kep_03.png)
 
„Emberek” fül alatt hozhatunk létre felhasználókat, és itt adhatóak meg a felhasználók jogosultságai is.

![](image/Jenkins_kep_04.png)

A „Build történet” alatt látható egy idődiagram, ahol a megfelelő projektek buildjei látható. Itt a Snippet test projekt legelső buildje látható. Státusza megszakadt (aborted), ugyanis kézzel leállítottam.

![](image/Jenkins_kep_05.png)

A „Jenkins kezelése” fül alatt találhatók a fontosabb beállítások. Számunkra a „Rendszer Beállítások” és a „Kiegészítők Kezelése” gombok lesznek relevánsak. 

![](image/Jenkins_kep_06.png)

## Projekt építése és konfigurálása

Hozzunk létre egy működő projektet, és adjunk hozzá egy buildet.

A kezdeti állapoton látható két projekt. Csináljunk egy harmadikat.

![](image/Jenkins_kep_01.png)
 
Először válasszuk a „Jenkins Kezelése” -> „Kiegészítők Kezelése” pontokat. Itt le kell tölteni a szükséges pluginokat. A repository eléréségez szükségünk lesz a „GIT plugin-ra. Töltsük le, és indítsuk újra a Jenkinst.

Ezután válasszuk a „Jenkins Kezelése” -> „Rendszer Beállítások” pontokat, és keressük meg a Git beállításokat. Itt a „Path to Git excecutable” útvonalat megfelelően kell beállítani, hogy elérhessük a Gitet. A C meghajtóra telepítettem a Git könyvtáramat. Ezenbelül a cmd mappa tartalmazza a szükséges .exe fájlt.

![](image/Jenkins_kep_07.png)
 
„Új item” alatt létrehozhatunk egy „Freestyle project”-et.

![](image/Jenkins_kep_08.png)
 
Válasszuk ki a „Verziókezelő rendszer” alatt a Git-t és adjuk meg a Repository URL-t. Én a GitHub-on létrehoztam egy repositoryt, és ennek az elérési útvonalát adtam meg.

![](image/Jenkins_kep_09.png)
 
Kattintsunk az „Építés Most”-ra és futtassuk le a legelső buildünket.

![](image/Jenkins_kep_10.png)
 
A „Console Output” alatt nézhetjük meg mit is csinált ez az egyszerű „dummy build”.

Létrehozott egy workspacet a számítógépünkön, ahova lefetchelte a távoli Git repository változásait. Mivel ez az első build, letöltötte az egész repositoryt. Így sikeresen lefutott a build.

![](image/Jenkins_kep_11.png)
 
Ha visszamegyünk az irányítópultra akkor elérhetjük a munkaterületet.

![](image/Jenkins_kep_12.png)
 
Itt látható az egyfajl.txt. Nyissuk meg.

![](image/Jenkins_kep_13.png)
 
Hello.

Nézzük meg, mi van a GitHub repositoryban.

![](image/Jenkins_kep_14.png)
 
Ugyanez. Tehát elérte a Jenkins a távoli repositoryt.

![](image/Jenkins_kep_15.png)
 
Tehát Jenkins alatt létrehoztunk egy projektet (Snippet test), azon belül egy buildet, ami képes elérni Giten keresztül a GitHub repositorymat, majd azon lefuttat egy „dummy test”-t.

![](image/Jenkins_kep_16.png)
 
<small>Szerzők, verziók: Almási Péter</small>
