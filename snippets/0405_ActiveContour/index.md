---
layout: default
codename: ActiveContour
title: Active Contour
tags: szegmentáció
authors: Urbanovics Péter
---

# Active Contours

## Bevezetés


Active contour-t másnéven Snake-t a számítógépes látásban arra használják, hogy objektumok határát meg tudják állapítani. Ezt a model nagyon
népszerű a számítógépes látásban, sokféle alkalmazási területe van például objektum követés, alak felismerés, szegmentáció, él detektálás.
A művelet alapja, hogy egy berajozolt görbét úgy változtassunk, hogy ha a képen az jelent minél kisebb értéket, hogy változás van, tehát egy él
, akkor azt szeretnénk elérni, hogy a görbe mentén összeadva (integrálva) az értékeket, a legkisebb értéket kapjuk. Ezen kívül a
görbe formáját is figyelembe vesszük, hogy minél inkább szép íve legyen.

## Algoritmus

### Energiák

Az algoritmus működése energia minimalizáláson alapszik. Vannak külső illetve belső energiák. Külső energiák azok, melyeket a kép alapján
határozunk meg. Belső energiákat pedig a görbe rugalmasságából kapjuk. Ezeknek az energiáknak az összege lesz a görbe energiája.
Ezt az energiát szeretnénk minimalizálni az Active contour algoritmus során.

### Gradient descent optimization

Az eljárás lényege, hogy az energiát úgy minimalizáljuk, hogy a görbét a meghatározott energiák deriváltjával mozgatjuk. Ezt úgy tudjuk
könnyedén elképzelni mint egy fizikai húrkot, erre a hurokra erők hatnak, vannak amik befelé mozgatják illetve vannak amik visszatartják.
Az erőket pedig úgy határozzuk meg, hogy a mindegyik erő a neki megfelelő külső vagy belső energiát csökkentse. Ezáltal végül egy
locális minimumba érkezünk. Mivel az energia függvények úgy vannak meghatározva, hogy akkor a legkisebbek, ha megfelelő alakja van
a görbének, illetve, hogy a görbe energiája a változásoknál alacsony, így egy szép formával a kép határain fog megállni.

### Néhány eredő erő

* Elastic Force
* Curve Force
* Center Force
* Derivative Force

#### Elastic Force

Ez az energia ami a gumi rugalmasságát adja meg. Az az erő ami egy gumit összehúz. Ez az erő a hurkot összehúzza, elősegítve 
hogy rásimuljon az alakzatra a kígyó

#### Curve Force

Ez az energia ami a gumi alakjának C kettő folytonoságát biztosítja. Úgy húzza a gumi alakját, hogy minél inkább kör alaku maradjon.
Ezzel biztosítva azt, hogy ne legyen a kígyóban tüske.

#### Center Force

Ez egy statikus erő, arra használható hogy a gumit az átlagos pont felé húzza, így még gyorsabban húzódik össze, gyorsabban rásimulva
az alakzatra.

#### Derivative Force

Ez az erő tartja vissza a gumi összehúzódását. Emiatt az erő miatt áll meg a gumi ott, ahol a képen éles váltás van.


### Diszkrét approximáció

Mivel a képeken diszkrét környezetben dolgozunk ezért a görbénk is diszkrét pontokból áll, így a görbe energiáját úgy tudjuk, meghatározni, hogy
a görbén található pontjaint energiáját összegezzük. Illetve ezeket a pontokat módosítjuk aszerint, hogy görbén minél kisebb legyen ezeknek az 
energiáknak az összege. Így ezeket a pontokat mozgatjuk az energiák által meghatározott erőkkel. A diszkrétség miatt még egy olyan megközelítést
is lehet használni, hogy az egyes pontokat amik a görbén vannak, változtatjuk, újakat hozunk létre, illetve össze olvasztjuk őket ha nagyon közelvannak
egymáshoz, ezen kívül még egy olyan műveletet használtam, hogy a pontokat körbe körbe keringetem a görbén, így egy tényleges minimumot tudok, meghatározni.


## Algoritmus eredménye

![Festmeny Active contour](image/festmenyActiveContours.jpg)
