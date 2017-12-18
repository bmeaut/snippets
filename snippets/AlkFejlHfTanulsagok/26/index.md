---
layout: default
codename: AlkFejlHf26
title: The Solid Guys tanulságok
tags: alkfejl afhf skipfromindex
authors: (nincs kitöltve)
---

# The Solid Guys csapat év végi tapasztalatai

Az év elején úgy döntöttünk, hogy nem fogunk a RobonAUT versenyen részt venni így a projektünk kicsit különbözik a legtöbb csapatétól. Mivel korábban a csapattagok közül már többen is foglalkoztak drónokkal vagy azokhoz kapcsolódó applikációk programozásával, így a választásunk egy drónos alkalmazás elkészítésére esett.

A felhasznált multikopter egy AR Drone 2.0 típusú eszköz volt. Kiindulásképpen megnéztük milyen fejlesztési lehetőségeink vannak, és végül számtalan forrást találtunk a hivatalos SDK-k mellett is, amiből ki tudtunk indulni. Úgy gondoltuk, hogy kezdésnek megteszi, ha van egy SDK-nk amiben meg van oldva a szabályozás (mivel ez önmagában egy elég nagy feladat és valószínűleg a többire, a tárgyhoz jobban kapcsolódó dolgokra kevesebb idő jutott volna). Itt arra gondolok, hogy ha a kvadrokopter felszáll, akkor tudjon stabilan állni egy helyben, ne kelljen egyesével egymáshoz hangolni a rotorokat. Végül a következő SDK-t használtuk fel:

[https://github.com/puku0x/cvdrone](https://github.com/puku0x/cvdrone)

Ez önmagában teljesítette a fenti kikötést, sőt egy konzol applikáción keresztül lehetett parancsokat küldeni a drón felé. A gondok itt kezdődtek mivel ezek nem igazán vagy nem úgy működtek, mint ahogy az elrendeltetett. Itt már belenyúltunk az SDK-ba kicseréltük pl. a karakterbeolvasó függvényt, de végül a szabályozás részét sem úsztuk meg, mert az irányítás eléggé kiszámíthatatlan volt. A részletekbe nem mennék bele, mert azok megtalálhatóak a dokumentációban.

Miután maga a multikopter „használható&quot; lett, elkezdtük a grafikus felület fejlesztését. Az eredeti tervünk az volt, hogy a konzol applikáció és a GUI közötti kommunikációt socketekkel oldjuk meg, de természetesen itt sem volt egyszerű a megvalósítás. A probléma forrása az volt, hogy a konzol applikáció és a GUI egy gépen fut, mindkét oldal küld és fogad üzeneteket, ezért egy gépen kell két szervert futtatni, amik figyelik csatornát (listenning). A szerverek elindításakor egyszerre csak az egyiket tudtuk működésbe léptetni, valószínűleg erre van megoldás, de sajnos rövid időn belül nem találtunk, szóval alternatív módszerhez folyamodtunk. A kommunikációs problémánkra a fájlbaírás jelentette az előrelépést, egy szöveges fájlt használtunk puffernek a két oldal között. Ettől függetlenül a számítógép wifin, TCP socketen keresztül kommunikál a drónnal, így a kiírásban támasztott követelménynek eleget tesz.

Qt Creator telepítése után, nagy örömmel konstatáltuk, hogy számos példaprojekt elérhető, amikből lehet ötletet meríteni, pl. a grafikonunkat is egy ilyen example segítségével valósítottuk meg. A negatív tapasztalatok természetesen itt sem maradtak el, pl. alapértelmezettként nem települt debugger, ami elég zavaró volt. Véleményünk szerint egyrészt hasznos, másrészt viszont eléggé körülményes, hogy lehet használni az általunk megszokott C++ függvényeket, a megfelelő headerek include-álásával. Több esetben is tapasztaltuk, hogy a Qt függvények / típusok nem válthatóak ki egy az egyben az általánosan használt C++ megfelelőjükkel, hanem erre külön függvények alkalmazhatóak.  Belefutottunk olyan kellemetlen szituációba is, hogy amikor a projekt fájlt módosítottuk, hogy megszüntessük a linkelési hibákat, akkor önmagában a fájl elmentése nem volt elég, hanem külön újra kellett futtatni a qmake-t, hogy a változások érvényre kerüljenek. A GUI elemeinek elrendezésének kialakításában viszont nagyon hasznos volt a Creator „drag and drop&quot; jellegű felülete, legalábbis egyes csapattagoknak felüdülést jelentett a HTML világa után. Nemcsak a layout kialakításában segített, de egyszerűbb volt innen módosítani az egyes objektumok paramétereit is.

A GitHubbal kapcsolatban is sokat tanultunk, volt olyan csapattagunk is, aki először találkozott verziókövetéssel. Én, amit külön kiemelnék, hogy ez volt az első olyan projekt, ahol a GitHubnak az asztali alkalmazását használtam, ami meglepően jól működött, számomra sokkal átláthatóbbá és egyszerűbbé tette a fájlműveleteket.

A házi feladat leadásakor, igaz még nem tökéletes az alkalmazásunk, vannak megoldásra váró feladatok, mint pl. a már említet socket-kommunikáció, de úgy érezzük, hogy a félév elején meghatározott feladatokat jórészt teljesíteni tudtuk és egy működő applikációval várjuk az utolsó hetet.

