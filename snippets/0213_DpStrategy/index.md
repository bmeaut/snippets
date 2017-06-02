---
layout: default
codename: DpStrategy
title: Strategy tervezési minta
tags: designpatterns alkfejl
authors: Csorba Kristóf
---

## Strategy

A strategy tervezési minta célja, hogy egy osztály működésének egy részét (a tudtán kívül) le lehessen cserélni, vagyis a használt stratégiák közül lehessen választani.

### Bevezető példa

A GrainAutLine rendszerben képeken kell kalcitszemcse határokat keresni. Amennyiben két szemcse között halvány a határ, a kontúrkereső eljárások nem mindig találják meg. Ezért készült egy automatikus "kettévágó" algoritmus, mely gráfként értelmezi a képet és minimális vágásokat keres (max-flow-min-cut módszer). Ehhez több gráf bejárási módszert is fel lehet használni, ami a módszer többi része szempontjából bármi lehet, csak találjon legrövidebb utat.

A jelenlegi implementációban két lehetőség közül is lehet választani: lehet két oldalról induló szélességi vagy A* kereséssel is használni. A két algoritmusnak ugyanaz az interfésze (közös ősosztályuk van), a vágást kereső osztálynak pedig a konstruktorának kell azt átadni paraméterül, amelyiket használni szeretnénk. (Ezt a példányosításkor a felhasználói beállítások alapján teszi meg a program.)

Később ha elkészül egy hatékonyabb útvonalkereső algoritmus implementációja is, azt is át lehet majd adni a konstruktornak, hogy onnan kezdve azt használja, ehhez a kettévágó algoritmus kódjában semmit nem kell módosítani (open-close SOLID elv követése).

### Részletek

A strategy mintában egy algoritmus konkrét implementációja cserélhető, mivel az egyes megvalósításoknak egy közös interfésze van (közös ősosztály formájában), így az azt felhasználó osztályoknak nem kell tudniuk, hogy konkrétan melyikkel dolgoznak éppen.

A stratégiákat legtöbbször induláskor választjuk ki (például konfiguráció alapján), de ez sokszor akár futási időben is változhat.

### Példa: foltokat szétválasztó algoritmus kiválasztása

A [SOLSUN](http://www.enlight.co.uk/index.php/solsun) projektben a képfeldolgozás során szükség van egy lépésre, mely a képen látható foltokat szétválasztja. Ez a BlobSplitter, amire több kísérleti implementáció is elkészült. Ezek közül választani a konfigurációs fájlban lehet (amit a singleton ConfigManagertől lehet elkérni). A BlobSplittert használó osztály a konstruktorában vár egy pointert egy konkrét BlobSplitter példányra (a dependency injection koncepciónak megfelelően), amit az alábbi factory method hoz létre:

	BlobSplitterBase *CreateBlobSplitterBase()
	{
	    const char *optionString = ConfigManager::Instance()->getStringValue("BlobSplitter","Strategy");
	    OPENCV_ASSERT(optionString != nullptr, "CreateBlobSplitterBase", "No setting for BlobSplitter/Strategy");
	    string usedOption = string(optionString);
	    if (usedOption == string("BlobSplitter"))
	    {
	        return new BlobSplitter(BlobSplitter::splitType::BLOB);
	    }
	    else if (usedOption == string("BlobSplitter_CC"))
	    {
	        return new BlobSplitter(BlobSplitter::splitType::CC);
	    }
	    else if (usedOption == string("ShapeBasedBlobSplitter"))
	    {
	        return new ShapeBasedBlobSplitter();
	    }
	    LOG(FATAL) << "Unknown setting in BlobSplitter/Strategy";
	    exit(1);
	}

(Minden BlobSplitter implementáció a BlobSplitterBase leszármazottja, a LOG(FATAL) pedig a saját logolási mechanizmus része, ahol a FATAL paraméter a hiba súlyosságát, és így kezelési módját határozza meg.)

### Példa: RobonAUT sebességszabályozás ügyességi és gyorsasági verseny esetére

Hasonlóan lehetne például választani egy RobonAUT robot szabályozói közül annak megfelelően, hogy ügyességi vagy gyorsasági versenyre készülünk. Ha a szabályozó nem csak néhány paraméterben tér el egymástól, akkor érdemes lehet külön osztályokat létrehozni az egyes szabályozóknak. Például merészebb üzemmódban mehet a robot gyorsabban és használhatja a szoftveres ABS-t, vagy egy vonalra lefutás után is visszataláló módszert. (Ez így már kicsit több, mint sebesség szabályozó, inkább teljes vonalkövetési stratégia.) 

### Egyéb megjegyzések

  * A stratégia kiválasztás alapja lehet a konfiguráció mellett a rendszer aktuális állapota (ez már kicsit State pattern is), vagy például jogosultság is.
  * A cserélhető stratégia is lehet többek között validációs, ellenőrzési mechanizmus (eltérő szigorúsággal), vagy egy éppen kiválasztott feldolgozó algoritmus. (A GrainAutLine projektben minden képmanipulációs eszköz egy Processzor, melyeknek egységes a be- és kimenete, így a felhasználó kiválaszt egyet és csak futtatja az aktuális képen, a program oldaláról egységes az összesnek a kezelése.)
  * Előfordul, hogy egy ősosztály előír egy metódust (pl. CarControlMethod ősosztály brake() metódusa), melyet így  minden leszármazottban meg kell írni. Ha sok leszármazott van és ezek között csak 2-3 féle fékezési stratégia van, érdemes lehet azt kód duplázás helyett egy köztes osztályban implementálni, aminek őse a CarControlMethod, leszármazottjai pedig azok a stratégiák, melyek ezt a fékezési módot használják. A Strategy mintán belül néha kettőnél több szintű öröklés is igen hasznos lehet.  

<small>Szerzők, verziók: Csorba Kristóf</small>
