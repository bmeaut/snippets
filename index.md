---
layout: default
codename:
title: kutyafulemacskafarka tanulságai
tags: alkfejl afhf skipfromindex
authors: Béres András, Szerencsi László, Virágh Anna
---

Kutyafülemacskafarka tanulságai

 1. Unit teszt:

	- A projektimportálás során fontos, hogy kiválasszuk a fordítót (pl. mingw-t) továbbá konfiguráljuk a projektet
	- Unit tesztről található a honlapon egy videó előadás, ami nagy segítséget nyújt
	- Egy külön projektet kell neki csinálni, ahol fontos, hogy azonos kit-tel készüljön, mint az eredeti projekt, és a többiek is azzal nyissák, különben nem nyílnak meg megfelelően a forrásfájlok

 2. GIT:
 
	- Három különböző branchen dolgoztunk, ezáltal kevés merge-conflict adódott

 3. GUI:

	- Új chart felvételénél lényeges, hogy a signalokat bekössük
	- Ha valami nem működik, aminek látszólag kéne, akkor egy Rebuild all megoldhatja a problémát
	- Ha képet szeretnénk hozzáadni, akkor a munkakönyvtárban helyezzük el külön images mappában és adjuk hozzá a qml.qrc-hez 

 4. Szimuláció:
	- Érdemes minél előbb elkészíteni, mivel szükséges a GUI teszteléséhez
  	- Ha valósághűbb szimulációt szeretnénk, lehet véletlen szám generálást beletenni, azonban ez nem determinisztikussá teszi a szimulációt, ami a Unit teszteknél okozhat fejtörést

	
 5. Telepítés:
	- Telepítést időben kezdjétek el
  	- A complete verziót érdemes telepíteni, még ha sok helyet is foglal
