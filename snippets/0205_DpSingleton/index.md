---
layout: default
codename: DpSingleton
title: Singleton tervezési minta
tags: designpatterns
authors: Csorba Kristóf
---

## Singleton

a singleton egy olyan osztály, melyből csak egyetlen egy példány létezik a rendszerben. Azt az egyet viszont tipikusan bárhonnan, könnyen el lehet érni.

### Bevezető példa

Tegyük fel, hogy egy ConfigManager osztályt készítünk, mely egy konfigurációs fájlból olvas be beállításokat. A programunkban nagyon sok helyen szükségünk van ezeknek a beállításoknak az olvasására, de az is biztos, hogy egynél több példányra nem lesz szükség a ConfigManager osztályból.

Ekkor a ConfigManager egy singleton lesz, például az alábbiak szerint:

    class ConfigManager
    {
    public:
        static ConfigManager GetInstance()
        {
            if (instance == null)
            {
                instance = new ConfigManager();
            }
            return instance;
        }

        int GetIntSetting(const char *section, const char *key);

    private:
        ConfigManager();

        static ConfigManager* instance;
    }

    ConfigManager* ConfigManager::instance = null;

Mivel a konstruktor private, new operátorral kívülről a ConfigManager nem példányosítható. Az egyetlen lehetőség a statikus GetInstance hívása, ami ha még nincsen egyetlen példány sem (elmentve az instance attribútumban), akkor létrehoz egyet, majd visszaadja azt. És mivel a statikus GetInstance mindenhonnan látható, így a kódban bárhol használhatjuk:

    int defaultTargetSpeed = ConfigManager::GetInstance()->GetIntSetting("Movement","DefaultTargetSpeed");

(Itt most feltételezzük, hogy a beállításokat tartalmazó fájl section-ökre van osztva, azon belül pedig kulcs-érték párokat lehet megadni.)

### Részletek

A singleton implementációra számos lehetőség van. Az egyik legegyszerűbb a fenti példában is bemutatott változat. Amennyiben többszálú alkalmazást fejlesztünk, a fenti megoldás például nem szálbiztos, mert ha két szál egyszerre hívja meg a GetInstance metódust (első alkalommal), akkor előfordulhat, hogy kétszer is lefut a new operátor. De ha ilyen eset nem fordulhat elő, akkor a fenti megoldás is tökéletes.

Gyakori alkalmazások: az abstract factory, builder, prototype, facade, state minták objektumai gyakran singletonok, mivel csak egyetlen példány kell belőlük.

A singletonokat sokszor jobban szeretjük, mint a globális változókat, mivel (1) nem hoznak létre statikus változókat a globális névtérben (csak a saját osztályukon belül van egy statikus instance), valamint (2) lehetővé teszik a lazy initializationt és nem a program indulásakor jön létre az összes, mint a globális változók esetében.

További lehetséges implementáció:

    static Singleton& instance()
    {
        static Singleton s;
        return s;
    }

Hátránya:

  * Nehezíti a unit tesztelést, mert globális állapotot vezet be a rendszerbe, ezért a teszeléshez a program egy kis részének nehezebb teljesen izoláltan egy olyan kis környezetet szimulálni, melyben a tesztet végre kell hajtani.
  * Túlzott használata (singletonism) anti-patternnek minősül. Sokan hajlamosak mindent singletonná tenni. Viszont ha esetleg kiderül, hogy mégis lehet belőle még egy példány, akkor az nagyon nagy átalakítást igényel a programban. (Egyik projektünkben ilyen eset volt egy partnernyilvántartó rendszerben, amikor szerencsére az adatbázis kapcsolat nem volt singleton, mert fél év múlva kiderült, hogy néha nyitnunk kell egy az állandóan használttól független adatbázis kapcsolatot, amin egyébként ugyanazokat a viszonylag bonyolult műveleteket kell tudni elvégezni, mint a szokásos funkciók esetén. Ha singleton lett volna, nem tudtunk volna könnyedén példányosítani még egyet.)

### További példák

  * Log műveletek
  * Beágyazott rendszerekben csak egy példányban jelen lévő perifériák objektumai (esetleg Facade burkolói).
  * abstract factory singleton: a Java Abstract Window Toolkit (AWT) getDefaultToolkit() által visszaadott objektuma, mely nagyon sok helyről használt, általános funkciókat tartalmaz, mint amilyen például képek betöltése fájlból.

### Multiton, mint általánosítás

A singleton általánosításra az egyetlen példány helyett (1) előre adott számú példány esetére, vagy (2) bizonyos kategóriánként pontosan egy példányra.

Hívják még registry of singletonsnak is, ahol kulcsonként csak egyetlen példány lehet. Erre konkrét példa a Lazy Initialization minta leírásában olvasható Lazy Factory.

Konkrét példa lehet beágyazott rendszerben az olyan perifériák burkoló objektumai, amikből több is lehet. Például nyomógombok.

    Buttons::GetInstance(OkButton)->Enable();

<small>Szerzők, verziók: Csorba Kristóf</small>
