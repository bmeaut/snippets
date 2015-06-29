---
layout: default
---

# Hibakezelés

Az alkalmazások jelentős része foglalkozik a futás közben kialakuló hibák kezelésével. Főleg kritikus rendszerekben a kódnak akár 80 százalékát is kiteheti azok részek aránya, melyek ideális esetben soha nem fognak lefutni.

Miket szokás tenni a hibákkal?

## A hiba lenyelése

Ez a strucc stratégia: ha hiba van, lenyeljük és megyünk tovább. Általában nem szerencsés abból kiindulni, hogy "ááá, úgyis sikerül megnyitni a fájlt". Mert ha aztán egyszer nem sikerül, akkor 5 függvényhívással később fog elszállni a program valami olyan hibával, ami nem is utal a fájlműveletekre. Tipikus példa, amikor minden exceptiont elkapunk és nem teszünk vele semmit.

## Hibajelzés visszatérési értékkel

Egy régi, jól bevállt módszer: a függvény visszatérési értéke hiba esetén egy hibakód, egyébként meg valami OK. Általában bár a 0 a false, mégis az szokta jelölni a sikert, mivel abból csak egy kell, hibakódból meg sok.

Jó módszer, ha másra nem kell a visszatérési érték.

## Hibajelzés kivételekkel (exception)

Anno a C++ egyik nagy újdonsága volt. Lényege, hogy vannak "dobható" (throwable) objektumok, melyeket eldobva azok a hívási listán visszafelé repülnek egészen addig, amíg valaki el nem kapja őket és le nem kezeli.

Két fontos dologra érdemes figyelni:

  * Az exception kezelés nagyon erőforrás igényes. Ha egy művelet a rendeltetésszerű működés esetén is hol lehetésges és hol nap, semmiképpen ne úgy döntsük ezt el, hogy megpróbáljuk és ha exceptiont dob, akkor elkapjuk, konstatáljuk, hogy most nem ez volt a helyzet, és megyünk tovább. (Péládul klasszikus Java példa, hogy úgy döntjük el egy stringről, hogy szám van-e benne, hogy megpróbáljuk meghívni az Integer.parseInt(input);-et és ha NumberFormatException  jön, akkor nem az volt. Ez nagyon lassú megoldás.)
  * Exception esetén figyelni kell arra, hogy mindent felszabadítsunk, amit kell, annak ellenére, hogy a kódrészlet nem futott végig. Java esetén erre van a try-catch-finally koncepció finally része, ami mindenképpen lefut, akkor is, ha nem volt exception és akkor is, ha volt. C++-ban nincs ilyen, elsősorban azért, mert a "resource acquisition is initialization" jobban lekezeli az ilyen eseteket. (Bjarne Stroustrup tömör magyarázata erre: http://www.stroustrup.com/bs_faq2.html#finally)

## Assert használata

Az assert általában arra kell, hogy a kódomat ne is lehessen rosszul használni: ha valaki hibásan használja (például a képfeldolgozó függvényemet színes képpel hívja meg, pedig szürkeárnyalatosat várok), akkor az azonnal derüljön ki. Ez azért is fontos, mert ha csapatban fejlesztünk és az én függvényem száll el, akkor én kapom a hibajegyet és nem az, aki rosszul hívta meg.

Érdemes megnézni az ST HAL (Hardware Abstraction Layer) megoldásait, ahol például a HAL_ADC_Init függvény ellenőrzi, hogy ha egy Resolution paramétert kell átadni, akkor az tényleg az-e:

    assert_param(IS_ADC_RESOLUTION(hadc->Init.Resolution));

Az ide vonatkozó header fájlban lévő makró pedig:

    #define IS_ADC_RESOLUTION(RESOLUTION) (((RESOLUTION) == ADC_RESOLUTION12b) || \
                                           ((RESOLUTION) == ADC_RESOLUTION10b) || \
                                           ((RESOLUTION) == ADC_RESOLUTION8b)  || \
                                           ((RESOLUTION) == ADC_RESOLUTION6b))

Így bár a vizsgált paraméter uint32_t, mégis kiderül, ha valami érvénytelen szám került bele.

Az, hogy mi történjen akkor, ha az assert feltétel nem teljesül, változó. Asztali környezetben C++ alatt sokszor segmentation faultot vagy kivételt okoz. Beágyazott rendszereknél debug módban fordítva a programot végtelen ciklusba jut (mivel itt a debuggerrel megállítva a call stack alapján kiderül, hogy hol keletkezett a hiba), release módban pedig resetel. Sok környezetben az assertek release fordítás esetén bele sem fordulnak a programba.

# Logolási mechanizmusok

Ha már megtörtént a hiba, azt érdemes rögzíteni is. Főleg, ha fennáll az esélye, hogy bejelentik a hibát és nekünk kell megoldani. Ilyenkor kincset ér egy az "Elindítottam és nem megy!" hibabejelentéshez csatolt logfájl. (Nagyobb rendszereknél van hibabejelentő funkció, ami automatikusan csatolja ezeket, így a felhasználónak nem kell elmagyarázni, hogy mit és hova másoljon.)

A logfájlok igen nagyok lehetnek, ha minden részletre kíváncsiak vagyunk, így általában logolási szinteket is definiálunk a log bejegyzés fontosságára utalva. Tipikus szintek az info, verbose, warning, error, fatal. Így ha például hibát keresünk, akkor bekapcsolhatunk mindent, ha meg kint van az ügyfélnél a program, akkor elegendő, ha az error és fatal szintek kerülnek bele a logba.

További lehetőség a log bejegyzések kategóriákba rendezése, melyek segítségével a log bejegyzéseket az alkalmazás részei szerint lehet csoportosítani.

# Beszédes hibaüzenetek

A felhasználói felületeken megjelenő hibaüzenetekkel kapcsolatban érdemes még megemlíteni, hogy az ilyen hibaüzenetet ne csak a fejlesztő értse, hanem a felhasználó is. Az "Adatbázis kapcsolati hiba, kód 12354H4GGX!" nyilván nem ilyen, de néha egész nehéz átülni a felhasználó helyére. Egy partnernyilvántartó rendszer felhasználójának az sem mond sokat, hogy "Nincs érvényes bejegyzés a szerződés-jogviszony összerendelő táblában." Pedig a fejlesztőnek az már triviális... miután 6 hónapja dolgozik azzal az adatbázissal.
