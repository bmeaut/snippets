A joancornella csapat összefoglalója a 2016 őszi félév Alkalmazásfejlesztés házi feladat tanulságairól

Qt Creator telepítése 
A fejlesztés alatt belefutottam abba a hibába, hogy regisztráltam a Qt oldalán, amire nem is lenne szükség, ahhoz, hogy használjuk a programot. Érdemes a következő lépések szerint letölteni és telepíteni a Qt alkalmazást ahhoz, hogy ne kelljen 30 nap után licenszt vásároljunk.
A „qt download”-ra rákeresve, az első találatok közt szerepel a „Start for free…” link, amire kattintva a következő válaszokat adjuk: 
1.	In-house deployment, private use, or student use
2.	No
3.	Yes
Ha jól csináltuk, akkor a megjelenik a „Get Qt Open Source” felirat a „Get started” gomb fölött. Kattintsunk a „Get started”-ra, majd a „Download Now” gombra, így egy online downloadert töltünk le amit indíthatunk is.
A telepítés során, amikor lehetőség van beírni az e-mail címet és jelszót, akkor a „Skip” gombra kattintsunk, ne regisztráljuk a honlapon. Amikor eljutottunk ahhoz a részhez, hogy ki lehet választani, hogy milyen egyéb komponenseket szeretnénk feltelepíteni, akkor gondoskodjuk róla, hogy a MinGW 5.3.0 32bit-t válasszuk ki (pl. Qt5.7 alatt). Nálam ez automatikusan nem volt bepipálva, így a fordításnál problémákba ütköztem. 

![alt tag](https://raw.githubusercontent.com/lehoGH/alkfejlhf-joancornella-1/doc/snippet0.png)
![alt tag](https://raw.githubusercontent.com/lehoGH/alkfejlhf-joancornella-1/doc/snippet1.png)

Első fordítási problémák
Belefutottunk abba a problémába, hogy a „unique_ptr” elnevezésre hibát dobott. Ez csak a c++11-től lehetséges, ezért gondoskodjunk róla mi magunk, hogy ezt le tudja fordítani a fordítónk. Ehhez a következő két sort elegendő ha kézzel bemásoljuk a „.pro” fájlunkba:
 
![alt tag](https://raw.githubusercontent.com/lehoGH/alkfejlhf-joancornella-1/doc/snippet2.png)

Resource fájlok hozzáadása
Amennyiben valaki saját projektet készít, akkor a következőképpen adhat hozzá source fájlokat:
1.	Projekt név jobb klikk -> Add new és a képnek megfelelőt válasszuk:

![alt tag](https://raw.githubusercontent.com/lehoGH/alkfejlhf-joancornella-1/doc/snippet3.png)

Ha „.qml” fájlt szeretnénk hozzáadni, akkor az elkészített .qrc fájlunkon kattintsunk jobb klikkel és itt adjunk hozzá újat… majd válasszuk az előző képen is látható QML opciót.
Ha így készítjük el a resource fájljainkat, akkor fájlok hierarchiája átlátható és jól használható lesz.
Csapatlogó beszúrása
Ha szeretnénk csapatlogót az alkalmazásunkon belül, akkor ezt is érdemes berakni a resource fájlokhoz. Ehhez csak annyit kell tennünk, hogy a projekt mappájába helyezzük el a képünket, majd az elkészített „.qrc” fájlunkhoz adjunk hozzá egy létező fájlt, és kiválasztjuk a könyvtárban található „.jpg” képet. Figyeljünk arra, hogy milyen kiterjesztésű képet szeretnénk használni, mert nem mindent támogat a Qt!
Ha jól csináltuk a következő hierarchiát láthatjuk:
Ha be szeretnénk szúrni a képünket, akkor már csak meg kell hívnunk a következő két sort a megfelelő helyen:
 
![alt tag](https://raw.githubusercontent.com/lehoGH/alkfejlhf-joancornella-1/doc/snippet4.png)

![alt tag](https://raw.githubusercontent.com/lehoGH/alkfejlhf-joancornella-1/doc/snippet5.png)
A resource fájlok URL-je másolható, ha jobb klikkelünk a fájlon.

Egyéb tanulságok
•	Tanácsoljuk a házi feladatot minél korábban elkezdeni, főleg ha az ember BSc második féléve óta nem programozott C++-ban
•	Ugyanez hatványozottan igaz a RobonAUT-on résztvevő csapatok számára, már az élesztés során is nagyon jól használható, ha van egy jól átgondolt diagnosztikai alkalmazásunk. Természetesen, amikor az autón már „csak” hangolni szeretnénk paramétereket, akkor is elengedhetetlen.
•	A git használatát érdemes készségszinten elsajátítani. Sok időt lehet vele megspórolni, ha már nem kell komolyan átgondolni minden egyes merge/checkout/… folyamatot.
•	A Qt és QML oldal közötti hívásokkal nem árt tisztában lenni. A QML oldalról „ctrl+klikk” kombináció nem használható, így nehezen kereshető vissza, hogy mi is honnan érkezik valójában.
•	UML diagram szerkesztéséhez érdemes alaposan átnézni a Qt által biztosított lehetőségeket, mert jobb lehetőségeket tartalmaz mint pl. a Visio.
