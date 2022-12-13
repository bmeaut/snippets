---
layout: default
codename: WinVMQemu
title: Windows VM készítése Qemu környezetben
tags: alkfejl
authors: Koloszár Gergely
---

# Windows VM készítése Qemu környezetben

Az Alkalmazásfejlesztés tárgy keretein belül elkerülhetetlenül szükség van
egy windows környezetre az UWP futtatásához. Ez a snippet abban próbál segítséget nyújtani, 
hogy hogyan tudjuk magunknak ezt a VM-et összerakni, hogy lehetőleg jó teljesítmény mellett tudjuk futtatni a `Visual Studio`-t

## Minimal megoldás script és qemu segítségével

### Szükséges előkészületek

Én ahol lehet nem telepítek fel új programot, ha már egy meglévő ökosisztéma képes a feladat elvégzésére. 
Ezért ennek a VM-nek a felállításában is csak egy shellre, és a qemu packagere lesz szükség. 

A qemu egy nyílt forráskódú program, amely virtualizálásra, és rendszer emulálásra képes, így lehet akár 
ARM utasításokat futtatni x86 alapú processzoron, vagy esetünkben egy virtuális gépet létrehozni, amelyen egy tetszőleges guest OS-t futtathatunk.
A qemu támogatja a KVM módot, amely a Kernel Virtualization Module kifejezést rejti maga mögött. Ez a kernel modul teszi lehetővé, hogy a kód amelyet qemun keresztül
futtatunk, egyenesen a fizikai processzoron fusson, így jobb teljesítményhez fogunk jutni, amelyre a windows és a VS során szükségünk is lesz.

Feltételezhetően shell mindenkinek áll a rendelkezésére, qemut pedig,
a következő parancsok egyikével fogjuk tudni telepíteni:

*Archlinux*
``` shell
sudo pacman -S qemu-full
```

A megfelelő működéshez szükséges számunkra még a `libvirt` nevű package, amely egy API-t biztosít a virtualizációs eszközök számára.
Ezt a libraryt a fentihez hasonló módon telepítsük.

*Archlinux*
``` shell
sudo pacman -S qemu-full
```

A package telepítése után pedig indítsuk el:

``` shell
sudo systemctl start libvirtd.service
```

### `TODO:` többi distro, debian, fedora

A többi disztribúción nem teszteltem a telepítést viszont a qemu minden nagyobb disztribúcióhoz tartozó package repositoryban elérhető.

### A script

A telepítés és futtatás ettől a ponttól kezdve shellből manuálisan megtehető, viszont a kezelést sokkal kényelmesebbé tudja tenni egy script.

#### Image létrehozása

Az első lépés egy virtuális disk létrehozása, amely gyakorlatilag egy egyszerű file. 
A scriptben ezt a `-c` (vagy `--create`) kapcsolóval tehetjük meg, amelyet követő szám határozza meg a lemez méretét. Amennyiben nem adunk 
meg méretet, a default beállítás 128G. Ez az érték természetesen módosítható a script szerkesztésével.

``` shell
./windows-alkfejl -c 128G
```

#### A Windows telepítése

A következő lépésben szükségünk lesz egy telepítő image-re amelyről a Windowst telepíthetjük. Ezt a Microsoft weboldaláról le tudjuk tölteni. Sajnos ez az oldal
feketemágiát használ így nem tudtam automatizálni a letöltési folyamatot, ezt kézzel kell megcsinálnunk.

Ha ez megtörtént, akkor a telepítést a `-i` (vagy `--install`) kapcsolóval kezdhetjük, amelyhez adjuk meg a telepítő image elérési útját. Ezek után a 
virtuális gép elindul, és telepíthetjük az operációs rendszert ugyanúgy mintha egy fizikai gépen végeznénk a telepítést.

#### A Windows indítása

Az általános indítást a telepítést követően a `-l` (avagy `--launch`) kapcsolóval érhetjük el. A virtuális gép egy új ablakban fog megjelenni, amelyet (az eredeti beállítások mellett) 
az `F11` billentyűvel tehetünk teljes képernyős módba, illetve innen vissza ablakba. A kurzorunkat egyszeri belekattintás után elkapja a rendszer, majd a `shift-F12` 
billentyűkombinációval tudjuk visszairányítani a host OS-be.

#### Konfigurálás

##### Hardver erőforrások

A script 4. - 6. sorában beállítható hogy hány magot használhasson a virtuális gép, illetve hogy mennyi memóriát akarunk a rendszer számára biztosítani. 

##### Windows integrálás

A rendszer jobb integrációja kedvéért javaslom a következő csomag letöltését és telepítését a virtuális gépre: [link](https://www.spice-space.org/download.html)

## Kényelmesebb megoldás VirtManager segítségével

`TODO`

## Források, tutorialok, amik segíthetnek

https://wiki.archlinux.org/title/QEMU
https://www.youtube.com/watch?v=BgZHbCDFODk
https://www.spice-space.org/download.html
https://wiki.gentoo.org/wiki/QEMU/Windows_guest
