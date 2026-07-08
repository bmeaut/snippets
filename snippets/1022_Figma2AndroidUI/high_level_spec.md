# kcalc alkalmazás magasszintű specifikáció

## Főbb funkciók

Az alkalmazás az egyéni étrend és az azáltal bevitt tápanyagok követésére hivatott nyújtani egyszerű és megbízható megoldást.

**Ételek kezelése**

A felhasználónak egy külön felületen lehetősége van ételek felvételére. Az ételek felvételekor, annak tápértékeinek (fehérje, rostok, zsír, szénhidrát, kalória) meghatározására van szükség 100g-ra visszafejtve. A felvett ételek egy listában érhetőek el egy külön felületen, és ezek szerkeszthetőek és törölhetőek.

A tápértékek felvétele során lehetőség van az értékek becslésére, amelyhez internet használat szükséges. A felhasználónak ehhez csupán az étel nevét kell kitöltenie és az alkalmazás egy külső szerver segítségével becsli meg az értékeket csupán az étel nevéből kiindulva.

A felhasználónak lehetősége van a felvitt ételek kombinációjára is. Ebben az esetben egy új étel keletkezik, amely az ahhoz felvettek tápértékeinek összegéből tevődik össze skálázva azok tömegeivel. Ilyenkor az egyes összetevőkhöz szükséges azok tömegeiknek definiálása is. Az alkalmazás ezt általános ételkhez hasonló megjelenítés mellett mutatja, hogy milyen továbbiakból tevődik össze. Egy példa a kombinációra: `Vajaskenyér` esetén `vaj`* 2g + `kenyér`* 50g.

**Napi bevitelek kezelése**

Az adott napra a felhasználó tudja követni a főmenüből, hogy milyen ételeket vitt be. Itt tud további táplálék bevitelt felvenni vagy aznapi korábbit törölni az étel kiválasztásával (amelyeket a korábban már felvett), illetve annak tömegének kiválasztásával.
A főmenüben továbbá az aznap elfogyasztott fő tápérték célokat is megfigyelheti mutatók formájában.

**Napi bevitelek nyomonkövetése**

Egy külön panel-en a felhasználó vissza tudja nézni, hogy adott múltbéli napon milyen ételeket vitt be és milyen tápérték értékeket ért el. A múltbéli adatok módosítására nincs lehetőség, mindig csak az aznapi adatokra.

**Mérleg hibák kezelése**

Az alkalmazás lehetőséget biztosít a mérleg hibáinak korrigálására is, annak mért értékekhez tartozó hibáinak megadásával. Ezt tömegek megadásakor teheti meg a felhasználó egy checkbox formájában. Ilyenkor a fix pontok közötti interpolációval korrigálja az alkalmazás a bevitt tömeget. Pl.: 100g -> 102g, 500g -> 504g értékek esetén 300g esetén 3g lesz a hiba. Az alkalmazás egy időben egy mérleg korrigációjával képes dolgozni. A mérleghibák felvételére egy külön képernyő szolgál.

Az alkalmazás az adatokat csupán lokálisan tárolja és alapvető működése nem igényel internethez való kapcsolódást, leszámítva a tápértékek becslését.

**Tápérték cél meghatározása**

A felhasználó meg tud határozni egy tápérték célt, amely esetén az alkalmazás, ahhoz viszonyítva mutatja a bevitt értékeket. Ezt a célt később a felhasználónak lehetősége nyílik módosítani.