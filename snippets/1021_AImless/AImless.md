# MI esettanulmány – AImless a programozási módszerek és az ezekhez társított érzések vizsgálata

A feladat célja, annak a felderítése, hogy különböző mértékű AI segítség használata a programozáshoz, mennyire és hogyan befolyásolja a programozás élményét.
A kutatás két részből áll, az első az interneten már meglévő tapasztalokat gyűjti össze, a második részben pedig saját magamat vizsgálom, hogy mik a tapasztalataim a programozáshoz használt különböző mértékű AI segítségekkel kapcsolatban.
Az első részhez a Gemini 3.1 Pro Deep Research funckióját használtam.
A második résznél pedig a vizsgálatot viszonylag egyszerű, ASP.NET Core Web API-ok fejlesztésével végeztem, C# nyelven. Ezeknek a feladatoknak a specifikációját a Gemini segítségével generáltattam le, az elsőhoz egy tárgyalóterem-foglalási API rendszert, a másodikhoz egy IoT szenzor telemetria és riasztó API rendszert, a harmadikhoz pedig egy dinamikus árazási és kedvezmény API rendszert.

## Vizsgált esetek a kódolásnál

1. Teljesen manuális kódolás - azaz AI eszközhasználat szinte nincs, a kódolás kézzel történik, maximum a fejlesztői környezet autocomplete funckiója, például egy for vagy if-hez. Illetve a fejlesztés során felvetődő kérdésekre a válasz keresése hagyományosan, google-ön keresztül.

2. Félautómata kódolás - AI eszközhasználat főként csak a fejlesztés során felvetődő kérdésekre korlátozódik kvázi "advanced google search"-ként, jellemzően az AI webes chates felületén keresztül. Továbbá az AI a kérdések mellett csak kisebb függvények, vagy boilerplate kódok megírására használatos.

3. Teljeskörű AI kódolás - A fejlesztés egy fejlesztői környezetbe integrált Agent módban lévő AI segítségével történik.

## Internetes kutatás eredménye

A első részhez elkészült Deep Research eredménye [itt található](AImless_research.html).

## Saját tapasztalatok

### Teljesen manuális kódolás

A régi hagyományos módszert, ami viszonylag sokáig meghatározó volt a szoftverfejlesztők körében, egészen élveztem. Alapvetően szeretek gépelni, így ez az esetek nagy részében különösebb gondot nem okozott számomra. Csak akkor volt elegem a gépelésből, amikor valami nagyon hasonlót kellett sokszor egymás után leírnom, tehát mondjuk boilerplate kódoknál, vagy egy adott DTO osztály definiálásánál. Mivel minden egyes részt nekem kellett kitalálnom és implementálnom kézzel, így pontosan tudtam, hogy melyik komponens hogyan kapcsolódik a másikhoz, és mi mit csinál. A hibakeresés és debuggolás viszont néha elég körülményes volt, hiszen lehet hogy csak egy nagyon apró hiba van, mégis nagyon sok időt eltöltök ennek a keresésével. Szintén hasonló érzésem volt, amikor valamire rá kellett keresnem, amit nem tudtam, hiszen hiába írtam be a Google-re a problémámat, a megjelent oldalakon hasonló problémákkal találkoztam, de nem teljesen ugyanazzal mint az enyém, így nagyon sokat kellett böngészni mire bármi érdemi információt tudtam volna szerezni a problémám megoldásához. Összességében nagy előnye, hogy az ember flow state-ben tud maradni, hiszen a logikán való gondolkodás kellemesen lefoglalja és lefárasztja az agyat, ugyanakkor mivel közbe gépelni is kell a kódot, figyelve például a szintaxra, az agyunk képes ilyenkor egy picit pihenni, ezáltal hosszútávon is fenntartható lesz a fejlesztés.

### Félautómata kódolás

Ez a módszer hasonló a teljesen manuálishoz, hiszen csak a kódolás unalmas részét veszi át az AI (boilerplate, és monoton osztálydeklarációk, stb.), a többi a lényeges logikai rész továbbra is marad a fejlesztőre. Számomra ez a módszer volt a leginkább élvezhetőbb, az előbb említett érvek alapján, hiszen az összes izgalmas részt megtartja a manuális kódolásból, az unalmas részeket pedig felgyorsítja, megkönnyíti. A hibakeresés sokkal gördülékenyebb, hiszen az AI apró hibákat is nagyon gyorsan ki tud szűrni, illetve ismeretlen dolgok után való keresés is sokkal hatékonyabb, hiszen az AI nagyon jól képes arra, hogy a saját problémánkra pontos választ keressen. Annyi pici probléma szokott lenni, hogy mivel alapvetően webes chat-alapon történik a promptolás, ezért az AI-nak folyton be kell másolgatni a kódrészletet, és néha kontextus hiányában nehezen tudja átlátni, hogy mi is történik valójában, ezért néha sokat kell iterálni, míg kijön a számunkra megfelelő megoldás.

### Teljeskörű AI kódolás

Amennyiben Agent módban használjuk az AI-t, szinte teljes hozzáféréssel rendelkezik, ezért sokkal jobban át tudja látni a kódbázisunkat. Viszont mivel itt már az összes kódolást az AI végzi, így nem csak az unalmas boilerplate kódolásától szabadulunk meg, hanem a számomra legjobb részétől is, ami pedig a logikán való gondolkodást és ennek implementálását jelenti. Sokszor úgy éreztem, mintha nem is igazán programoznék, hanem sokkal inkább olyan volt mintha csak egy tesztelő lennék, aki csak megkéri az AI-t valamire, az csinál valamit, amit letesztelek hogy jó-e, ha nem akkor megmondom neki, hogy ez és ez miatt nem jó, légyszíves javítsd ki, és ezt az idő nagy részében. A másik lényeges rész, hogy ahelyett, hogy az izgalmas implementálással foglalkoztam volna, helyette az AI által kiköpött kódot ellenőriztem, ami elég leterhelő, és unalmas is egy idő után, hiszen korábban közel sem kellett ilyen kevés idő alatt ilyen sok kódot átlátni. Azt is észrevettem, hogy nem csak hogy sokkal kevésbé élvezem magát a folyamatot, ahogy egyre nő a kódbázis, annál kevésbé értem, hogy mi hogy kapcsolódik egymáshoz. Ez alapvetően egy hagyományosabb módszernél is valamennyire megfigyelhető, viszont sokkal kevésbé, hiszen miközbe nő a kódbázisunk, úgy implementálás közben sokkal jobban megértük. Úgy vettem észre, hogy a kódnak a megértését nem lehet megspórolni. Ez fel is vetett bennem egy kérdést, miszerint a nap végén valóban megéri-e, hogy az AI megcsinál nekünk mindent, az izgalmas részeket is beleértve, és nekünk pedig marad az unalmas része (review és tesztelés), ezek által sokkal kevésbé fogjuk megérteni a kódot, és vegezetül lehet, hogy közel azonos teljesítményt nyújtunk, mintha azt saját magunk által implementálva értük volna el, úgy, hogy közben még élveztük is azt, ezáltal hosszútávon is fenntarthatóan tartva a fejlesztést?

