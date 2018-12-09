layout: default
codename: AlkFejlHf
title: Fantaziadus csapatnev tanulságai
tags: alkamazasFejlesztes
authors: Ádám Tibor, Fenyővári Boldizsár, Lakatos Dániel

Fantáziadús Csapatnév tanulságai

 1. UI nehézségek:

	- Ahogyan fejlesztettük a UI-t a QML property-k sajátosságait kellett megismernünk, mit lehet, mit nem kezelni velük.
	- A QT Creator a .qml file-ok változását nem követi le mindig, ezért néha a régi kóddal futott el és számtalanszor
	belefutottunk ebbe a hibába az elején, hogy sikertelenül futtatuk újra az alkalmazást és ugyanazt láttuk a képernyőn újfent.
	- Grafikonok átméretezése trükkös, utólag úgy látjuk, hogy jobban jártunk volna valami külső rajzoló library-vel

 2. Verziókezelés
 
	-Ne felejtsünk el pull-olni mielőtt commit-olnánk valamit mert elég sok idő elment nekünk a merge conflictok feloldásával.

 3. Jó tanácsok

	- Ne próbáljunk .c kiterjesztésű fájlt Sources fájlok között, mert a C++ nyelvi különbségek hibát okoznak.
	- Clean-t nyomjunk Build előtt, párszor nem megy anélkül.
	- Ha van egy classnak public struct-ja, annak az az elemeit nem lehet defaultból elérni a qml oldalon.
	-Ezért mi a struct elemeit kiszerveztük két külön history-ba

 4. ObjectName
	- Azt hittük az ID alapján találja meg cpp oldalról a qml file-okban lévő objektumokat,
	de később rájöttünk az ObjectName property-t kell megadni neki, hogy hivatkozni tudjunk rá.
	
 5. Doksi
	- Sok bosszúságot okozott, hogy az overview.md fájl nem a doxygen által átkutatott mappában volt,
	hanem egy szinttel felette. így egy üres index.html-t generált főoldalnak,
	és nagyon sok időt elvitt a doxygen csillió beállításainak átnézése - pedig az ok csupán egy apró figyelmetlenség volt.
	tanulság: az eszetlen guglizás előtt érdemes az alapvető buktatókat ellenőrizni.
	