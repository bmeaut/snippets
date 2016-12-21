---
layout: default
codename: AlkFejlHf13
title: Beta Romeo csapat tanulságai
tags: alkfejl afhf skipfromindex
authors: Benedek Ádám, Vicsotka Tamás
---

# Beta Romeo csapat tapasztalatai a BRUTUS telemetria alkalmazás fejlesztése során

A házi feldatban egy telemetria alkalmazást készítettünk, mely a RobonAUT versenyhez is nagy segítséget nyújt. Az alábbiakban néhány tanulságot osztunk meg, amelyek remélhetőleg segítik a későbbi generációkat is. 

### Feladatok ütemezése, határidők

A házi feladatot érdemes időben elkezdeni. Elsőre nem feltétlenül látszik, hogy igen sok munka van vele (három emberes feladat). Ha a csapat igényes munkát szeretne kiadni a kezéből, akkor végtelen időt el lehet tölteni a fejlesztéssel.
Megajánlott jegy akkor szerezhető a tárgyból, ha az alkalmazás határidőre elkészül, ezért érdemes először a kötelező elemeket elkészíteni, aztán időt szánni a továbbfejlesztésre. A vizsgaidőszakban könnyebbség jelent a megajánlott jegy, de ha valaki mégis vizsgázni kényszerül, akkor se csüggedjen el, mert hasznos átnézni a tárgy második felét is. :)

### Osztály változók elérése QML oldalról

A QML oldalon az osztályok változóinak elérése jelentett számunkra problémát. Sokáig nem volt egyértelmű, hogy ha nem rakjuk ki a Q_PROPERTY-ben READ függvényeket akkor nem férünk hozzá QML oldalon az értékekhez.

### UI designer

Megoszlik az emberek véleménye, hogy mennyire hasznos a QT Creator ezen funkciója és ebből kifolyólag mennyire ajánlott egyáltalán a hasznáalata. Véleményünk szerint, inkább az a fontos, hogy tudjuk mi is történik a háttérben. Kézzel is és a designer segítségével is készíthető jó és rossz UI mind kinézet, mind kód szempontjából.

### if(){} else(){} ->  ... ? ... : ...  He? Ha!

Érdemes visszaemlékezni a programozás alapjai tárgyra és felkutatni a fejünkben a ?: operátort(persze csak ha már elfelejtettük). Ennek segítségével egy sorban megvalósíthó egy feltétel vizsgálat, mely átláthatóbb kódot eredményez. Főként GUI fejlesztés során használtuk, például a csatlakozási állapot kijelzéséhez.

```cpp
...
//Kapcsolat állapot visszajelzés
Text
{
	id:		connectionStatusText
	text:	"Status: " + ((serialPortStatus) ?  "connected" : "disconnected")
	color:	(serPortStat) ?  "limegreen" : "orangered"
}
...
```

### Még nincs pédányosítva...

Az alkalmazás konstruktorában végzünk egy historyChanged() hívást, hogy elérhetőek legyenek QML oldalon a változók. Amennyiben egy olyan osztály változóját is elérhetővé tesszük, amely még nincs példányosítva akkor összeomlik a program. Erre mi azt a megoldást találtuk, hogy a history.Add(temp) függvénnyel egy default osztályt már hozzáadunk a historyhoz, így nem egy NULL pointerre mutató osztályt adunk QML oldalra.

### További információk a csapatról

Ha kíváncsiak vagytok a versenyre való felkészülésünkre, kedeveljétek a [Facebook](https://www.facebook.com/BetaRomeoBME/) oldalunkat.

Szerzők: Benedek Ádám, Vicsotka Tamás