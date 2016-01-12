---
layout: default
---

# QTest, vagyis unit tesztelés Qt környezetben

A unit tesztek célja, hogy az alkalmazásunk bizonyos funkcióit automatizáltan tudjuk ellenőrizni. Így elkerülhetők például a regressziós hibák, vagyis amikor valami már elkészült és működött, de aztán valami miatt megint elromlott. Ha a kód elég nagy részét lefedik a unit tesztek és mind zöld, akkor biztosak lehetünk benne, hogy a módosításaink olyan nagyon nagy bajt nem okozhattak. (Például a Team Foundation Server alatt be lehet állítani a gated checkint, vagyis hogy csak akkor lehessen módosításokat becheckolni a repositoryba, ha minden unit teszt lefutott.) A unit tesztek nagyon előtérbe helyező módszertan a Test Driven Development, amikor kódot csak azért írnak, mert egy teszt nem futott le. Vagyis először készülnek el a tesztek, és utána az ezeknek megfelelő funkciók. Így biztos, hogy minden elkészült funkcióhoz lesz unit teszt.

A unit tesztek Qt alatt egy külön alkalmazást jelentenek, melynek main() függvénye teszteket futtat egymás után, az eredményeket pedig kiírja a konzolra. (A konzolos kimenetet pl. a Jenkins szerver fel tudja dolgozni, így nem feltétlenül csak szöveges eredményeket kell nézni.)

Qt Creatorban unit teszt projektet létrehozva kapunk egyből egy kis keretprogramot is, ami elég jól megmutatja, hogyan is kell tesztet készíteni. A unit tesztelés általában azt jelenti, hogy a tesztelendő osztályokat példányosítjuk és mindenféle bemenetekkel bombázzuk, hogy utána ellenőrizzük a reakcióikat. A tesztelendő osztályok általában másik projektből származnak: általában több projektünk van, amiből az egyik a unit tesztek helye, és természetesen látják a többi projekt (pl. library és futtatható alkalmazás külön projektben) osztályait.

A példa unit tesztünk egyetlen fájlból áll.

```C++
#include <QString>
#include <QtTest>

// A tömörség kedvéért most itt definiáljuk
//  a tesztelendő osztályt.
class Calculator
{
public:
    int add(int a, int b)
    {
        return a+b;
    }
};

// Ez itt a unit test osztályunk, ami a teszteket tartalmazza.
// A keretprogramot a Qt Creator autmatikusan generálja.
// A teszt egy sima osztály. Annyi extra van benne, hogy bizonyos
//  metódusait a unit teszt keretrendszer lefuttatja.
class QTestDemoTest : public QObject
{
    Q_OBJECT

public:
    QTestDemoTest();

// Most jönnek azok a metódusok, amik a teszteket képviselik.
private Q_SLOTS:
    void testCase1();
    void testCase2();

private:
    // Felveszünk egy példányt, amit tesztelni fogunk.
    Calculator calculator;
};

QTestDemoTest::QTestDemoTest()
    : calculator()
{
}

void QTestDemoTest::testCase1()
{
    // A QVERIFY2 jelzi az esetleges hibákat a teszt rendszernek,
    //  így ennek segítségével ellenőrizzük a funkciókról,
    //  hogy helyesen működnek-e.
    QVERIFY2(calculator.add(1,2) == 3, "Az 1+2 még nem megy. :(");
}

void QTestDemoTest::testCase2()
{
    // Ezt most direkt nem fog sikerülni.
    QVERIFY2(calculator.add(1,1) == 3, "A hibas unit teszt nem sikerult. :)");
}

// Itt most nem készítünk main() függvényt, azt ez a makró
//  legenerálja nekünk. Lefuttatja majd a tesztet és az eredményt
//  kiírja a konzolra.
QTEST_APPLESS_MAIN(QTestDemoTest)

#include "tst_qtestdemotest.moc"
```

Lefuttatva az alkalmazást az alábbi kimenetet kapjuk:

```
********* Start testing of QTestDemoTest *********
Config: Using QtTest library 5.4.0, Qt 5.4.0 (i386-little_endian-ilp32 shared (dynamic) debug build; by GCC 4.9.1)
PASS   : QTestDemoTest::initTestCase()
PASS   : QTestDemoTest::testCase1()
FAIL!  : QTestDemoTest::testCase2() 'calculator.add(1,1) == 3' returned FALSE. (A hibas unit teszt nem sikerult. :))
..\QTestDemo\tst_qtestdemotest.cpp(52) : failure location
PASS   : QTestDemoTest::cleanupTestCase()
Totals: 3 passed, 1 failed, 0 skipped, 0 blacklisted
********* Finished testing of QTestDemoTest *********
```

Természetesen a unit tesztek ennél bonyolultabban szoktak lenni, de az alapvető koncepció nem változik.

<small>Szerzők, verziók: Csorba Kristóf</small>
