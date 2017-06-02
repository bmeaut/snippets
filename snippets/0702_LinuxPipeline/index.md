---
layout: default
codename: LinuxPipeline
title: Linux parancshívások
tags: linux
authors: Németh Gergely Dániel, Szántó Tamás
---

# Linux parancshívások

Ebben a snippetben egy-két példa c++ kód segítségével nézzük meg, hogy lehet parancsokat meghívni Linuxban.

### Példakód

Az alábbi példakódot fogjuk használni:

```cpp
include <iostream>

using namespace std;

int main()
{
        cerr << "Ez az A program"<<endl;
        cout << "Az A program fut"<<endl;
        return 0;
}
```

C++ fájlokat lehet fordítani például a g++ fordítóval:

``g++ cpp_a.cpp -o a_try``

Ha abból a könyvtárból akarunk egy fájlt futtatni, amiben állunk ``./`` használatával tehetjük meg: ``./a_try``. Ekkor a kimenet:

![pelda](image/pelda.png "Példakód futtatása")

Amint láthatjuk, alapból mint az error mind a standard output kimenete a konzolra megy.

## Bemenet/kimenet átirányítás

Minden folyamat rendelkezik az alábbi be/kimenetekkel:

 - 0 – standard input
 - 1 – standard output
 - 2 – error output
 
### A kimenet átirányítása

 - ``parancs > fájl`` a kimeneti fájlt felülírjuk
 - ``parancs >> fájl`` a kimenet hozzáfűzzük a fájlhoz
 - ``parancs 2> fájl`` hibakimenet fájlba
 - ``parancs &> fájl`` kombinált

Nézzünk erre példát! Amint az utolsó esetben látjuk, lehet kombinálni is a fentieket.

![kimenetek](image/kimenetek.png "Kimenet átirányítás")

### Bemenet átirányítása
 - ``parancs < fájl``
 
Létrehozunk egy új példakódot:

```cpp
#include <iostream>

using namespace std;

int main()
{
        cerr << "Ez az C program"<<endl;
        int i;
        cin >> i;
        cout << "C program fut "<<i<<endl;
        return 0;
}
```

Teszteljük a bemenet fáljból való olvasását!

![bemenet](image/bemenet.png "Bemenet fájlból")

## Parancsok egymás után

Jogosan felmerülhet a kérdés, hogy mi van akkor, ha én a B programmal írni szeretnék egy fájlba, majd a C programmal olvasni szeretném ezt.

A B program egyszerű kódja:

```cpp
#include <iostream>

using namespace std;

int main()
{
	cerr << "Ez az B program"<<endl;
	int b = 15;
	cout << b <<endl;
	return 0;
}
```
B > temp, majd C < temp:

![temp](image/temp.png "Értékátadás köztes fájllal")

### Parancssorozatok (;)

Nem lehetne ezt egyszerűbben, egy sorban? A válasz természetesen: igen. Ha két utasítást szeretnénk egymás után meghívni, a ``;`` használatával tehetjük meg: ``parancs1 ; parancs2``

![parancssorozat](image/parancssorozat.png "Parancssorozat")

### Csővezeték (|)

Nem lehetne még egyszerűbben? A köztes fájl kihagyásával a b program kimenetét a c program bemenetére irányítani? Természetesen megtehetjük. Erre (is) szolgál a csővezeték: ``parancs1 | parancs2``:

![csovezetek](image/csovezetek.png "Csővezeték")

Nézzük csak meg egy kicsit jobban ezt a kimenetet! Kétszer futtatuk a parancsot, és az error kimentre mindkétszer más érkezett.

Az egyik esetben a B program írt előbb az error kimenetre, a másik esetben a C. Vagy mégsem? A két ``endl`` egymás után lett kiírva az első esetben.

A csővezeték párhuzamosan futtatja a két programot. Amíg teheti, fut egymás mellett a kettő, amikor pedig az egyik bemenetet vár, kénytelen addig várakozni, amíg a másik megadja azt neki.

### Parancscsoportosítás

A B és a C program error kimenetét is az ``error.txt``-be szeretném tenni. Mit tegyek? Csoportosíthatjuk a parancsokat a ``()`` segítségével, és együttesen megadhatjuk nekik az error kimenetre a már megismert utasítást.

![csoportositas](image/csoportositas.png "Csoportosítás")

### Parancsok futtatása a háttérben

Vannak olyan programok amelyektől azt várjuk el, hogy folyamatosan fussanak (webszerver, webes IDE, system monitoring tool, stb.). Mivel parancsokat a Linux alapértelmezetten előtérben futtat, így egy ilyen program futtatásakor "elveszítjük" a parancssori felületet, hisz fut a program és ilyenkor nem tudunk más programot indítani.
Ilyenkor jön jól a háttérben való futtatás. Ezt a következőképp tehetjük meg:

``parancs &``

Ekkor az adott parancs kimenetét ugyanúgy látjuk, viszont új parancsokat is tudunk futtatni (emiatt szokták aszinkron futtatásnak is hívni).
Ha ismét az előtérbe szeretnénk hozni a programot, akkor azt a 

``fg``

paranccsal tehetjük meg.

A ``&`` jellel való futtatás egyik tulajdonsága, hogy amint bezárjuk a terminál ablakot, az összes benne futtatott program is leáll. Ha azt szeretnénk, hogy pl. webszerverünk tovább fusson, akkor azt így tehetjük meg:

``nohup parancs &``

Természetesen az így elindított program sem örökéletű. Ha valamilyen hibába ütközik futás közben, akkor nagy eséllyel ki fog lépni. E probléma megoldására egy lehetőség a [Stackoverflow](https://stackoverflow.com/questions/696839/how-do-i-write-a-bash-script-to-restart-a-process-if-it-dies)-n olvasható.