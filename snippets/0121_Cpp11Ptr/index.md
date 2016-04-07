---
layout: default
title: C++11 smart pointerek, a new/delete kerülése
authors: Csorba Kristóf
tags: alkfejl
---

# C++11 smart pointerek, a new/delete kerülése

A C++11 megjelenése óta a new, és főleg a delete operátor igen ritka lett a forráskódokban. Leginkább csak akkor találkozunk velük, ha valami keretrendszert, újrafelhasználható komponenst készítünk. Ennek oka az okos mutatók, smart pointerek megjelenése. Ezek lényege, hogy számon tudják tartani, egy adott objektumra hány pointer mutat. És ha már egy sem, akkor az utolsó megszünteti, vagyis hív rajta egy delete-et. Ennek hatalmas előnye, hogy egyrészt nem lehet elfelejteni a delete operátorokat, ami a memory leakek egyik fő forrása volt, másrészt általában nem kell törődni az objektumok felszabadításával, mert magától megy.

Ez hasonló a felügyelt nyelvek (C#, Java) esetében megismert garbage collection koncepcióval, viszont azzal ellentétben a C++-os verzió determinisztikus: pontosan tudjuk, mikor fog felszabadulni az objektum, ellentétben a háttérben néha lefutó garbage collection alapvetően nem determinisztikus jellegével.

Minden ilyen automatikus felszabadítási koncepcióban a legfontosabb kérdés a birtoklás, az ownership kérdése: minek a megszűnésekor kell felszabadítani egy másik objektumot is? Például egy nyomógomb tipikusan akkor szűnik meg, amikor az őt tartalmazó ablak megszűnik.

A smart pointerek, mint objektumok általában két helyen fordulnak elő: (1) egy metóduson belüli (stacken létrehozott) változóként, vagy (2) egy osztályon belüli attribútumként. Az első esetben a smart pointer a metódus végén szűnik meg, a második esetben az osztály példányának megszűnésekor. A kérdés az, hogy ez után a pillanat után lesz-e még szükség arra az objektumra, amire a smart pointer mutatott.

A C++11 3 okos mutatót hozott be:

  * unique\_ptr: a unique pointer esetében minden objektumra pontosan egy unique\_ptr pointer mutat és amikor az megszűnik, megszűnik a mutatott objektum is. A unique\_ptr objektumról ezért nem lehet simán másolatot készíteni, mivel akkor már ketten hivatkoznának az objektumra, vagyis nem igaz az, hogy a unique_ptr megszűnésekor egyből hívhat delete-et. Helyette ha egy unique\_ptr-t "lemásolunk", akkor az új másolat megkapja az ownershipet, az előző pedig elveszíti és nullptr lesz.
  * shared\_ptr: amennyiben egy objektumra többen hivatkoznak és akkor szabad csak megszüntetni, ha már senki nem hivatkozik rá, akkor a shared\_ptr a megoldás. A C# és Java világ referenciáinak a működését a shared\_ptr-ekkel érhetjük el.
  * weak\_ptr: mivel előfordul, hogy egy shared\_ptr által "életben tartott" objektumra több helyen is szükség van, a weak\_ptr-be le lehet másolni egy shared\_ptr értékét, a weak\_ptr azonban nem "birtokol". Cserébe lehet, hogy az általa mutatott objektum időközben megszűnt, így le lehet mindig kérdezni, hogy még érvényes-e.

A fentiek mellett természetesen a hagyományos pointereket is lehet használni, a smart pointerek get() metódusával bármikor elkérhetjük a beburkolt pointert. Ez gyors és hatékony, csak arra kell figyelni, hogy olyan esetekben használjuk, amikor menet közben nem szűnhet meg a mutatott objektum. Például ha egy függvénynek át kell adni egy objektumot, amit egy unique\_ptr birtokol, akkor nyugodtan át lehet adni pointerrel vagy referenciával, ha nem áll fenn a veszélye, hogy a függvényhívás alatt egy másik szálon a unique\_ptr megsemmisül, mert akkor a pointer érvénytelen területre fog mutatni.

Ami a lényeg: bár a következőkben elsőre úgy tűnhet, hogy ezek a smart pointerek veszedelmesen komlikáltak, érdemes átgondolni, hogy amire most figyelni kell, arra régen is figyelni kellett, csak nehezebb volt: ha pointerrel hivatkoztunk valamire, amire esetleg máshol már valaki hívott egy delete-et, akkor igen nehezen debuggolható hibákat kaptunk. Most nyugodtan dolgozhatunk referenciákkal vagy sima pointerekkel, de ha az ownership a kérdés, akkor a new és delete megoldásokat sokkal biztonságosabb lecserélni a smart pointerekre.

Shared\_ptr és unique\_ptr objektumokat legelegánsabban a make\_shared és make\_unique függvényekkel tudunk készíteni. (Ez utóbbi a C++14-ben jelent meg, a C++11-ben még csak make\_shared volt.)

Az alábbi példák az [alkalmazásfejelsztés tárgy Git repositoryjában](https://github.com/csorbakristof/alkalmazasfejlesztes) érhetőek el a Cpp11Pointers és Cpp11UniqueAndLambda könyvtárakban.

## A Cpp11Pointers példa: shared\_ptr vektor és weak\_ptr hivatkozás

```cpp
#include <iostream>
#include <vector>
#include <memory>

using namespace std;

class Blob
{
public:
    Blob(int x, int y)
        : x(x), y(y)
    {
    }

public:
    int x,y;
};
```

A main()-ben shared\_ptr-ekkel tárolunk blobokat, melyekre ha mindenhol shared\_ptr-ekkel hivatkozunk, akkor azzal nem is lesz gond, viszont a referencia számlálás miatt kicsi többletköltséggel jár. Ha nem kell shared\_ptr, hivatkozhatunk rájuk weak\_ptr-ekkel is, mint például itt a megjelenítésnél. Viszont ha weak\_ptr-rel hivatkozunk, akkor biztosítani kell, hogy futás közben egy másik szálon nem szűnik meg a hivatkozott objektum. Ezért ha biztosra akarunk menni, akkor a weak\_ptr-eket lehet lockolni. Ilyenkor ha már nem létezik a hivatkozott objektum, akkor nullptr-t kapunk vissza, ellenkező esetben pedig egy shared\_ptr-t, ami addig biztosan "életben tartja" az objektumot, amíg dolgozunk vele:

    void show(std::weak_ptr<Blob>& blob)
    {
        std::shared_ptr<Blob> lockedBlob = blob.lock();

        if (lockedBlob)
        {
            cout << "Blob(" << lockedBlob->x << "," << lockedBlob->y << ")" << endl;
        }
        else
        {
            cout << "A Blob már nem létezik." << endl;
        }
    }

    int main()
    {
        // Kelleni fog 2 tároló
        std::vector<std::shared_ptr<Blob>> container0;
        std::vector<std::shared_ptr<Blob>> container1;
        // Egy blobot mindkettőhöz hozzáadunk.
        std::shared_ptr<Blob> newBlob = std::make_shared<Blob>(12,34);
        container0.push_back(newBlob);
        container1.push_back(newBlob);
        // Egy másik blobot csak az egyikhez.
        newBlob = std::make_shared<Blob>(56,78);
        container0.push_back(newBlob);

        // Létrehozunk egy weak pointert arra a blobra, mely mindkét tárolóban benne van.
        std::weak_ptr<Blob> selectedBlob = (std::shared_ptr<Blob>)container1[0];

        // Sorban töröljük a konténereket és közben figyeljuk a selectedBlob-ot.
        show(selectedBlob); // Megmutatja Blob(12,34)-t
        container1.clear();
        show(selectedBlob); // Megmutatja Blob(12,34)-t
        container0.clear();
        show(selectedBlob); // Blob(12,34) már nem létezik

        cout << "Kész." << endl;
    }

Az utolsó show() híváskor bár a weak\_ptr még hivatkozik a blobra, az mindkét containerből eltűnt, így nincs több shared\_ptr, ami hivatkozik rá, vagyis megszűnt.

## A Cpp11UniqueAndLambda példa: tárolás unique\_ptr-ekkel, lambda kifejezés, valamint egy kis "for each"

Az alábbi példa szintén Blobokat tárol, de egy konténer osztályban, ami birtokolja is a tárolt objektumokat. Vagyis minden Blob addig létezik, amíg a konténerben van (és az nem szűnt meg), utána magától megszűnik.

    #include <iostream>
    #include <vector>
    #include <memory>
    #include <functional>
    #include <algorithm>

    using namespace std;

    class Blob
    {
    public:
        Blob(int x, int y)
            : x(x), y(y)
        {
        }

    public:
        int x,y;
    };

Itt következik a tároló osztály

    class BlobContainer
    {
    public:
        void add(std::unique_ptr<Blob>& newBlob)
        {

Mivel a (referenciával) paraméterül kapott unique\_ptr-től el kell venni az ownershipet, nem lehet lemásolni. Helyette mozgatni kell. A move semantic szintén a C++11-ben jelent meg és azt fejezi ki, hogy a newBlob ez után a művelet után meg fog szűnni, vagyis nyugodtan újra lehet belőle bármit hasznosítani.

            blobs.push_back(std::move(newBlob));
        }

A konténer minden elemén egy műveletet végrehajtani kétféle módon is tudunk. Ez egyik lehetőség az alábbi ForEach metódus, mely egy paraméterül kapott lambda kifejezést lefuttat minden elemre.

        void ForEach(std::function<void(const Blob&)> lambda ) const
        {

Érdemes megfigyelni a C++11-es for ciklust, mely végigmegy a blobs minden elemén. Ez minden olyan tárolóra működik, aminek van iterátora. Mivel tudjuk, hogy a blob-ot csak olvasni fogjuk, jobb ki is írni, hogy bármi is legyen a típusa (auto kulcsszó), const is legyen.

            for(const auto& blob : blobs)
            {

A blob jelen esetben egy unique\_ptr, így a tényleges objektumot a * operátorral tudjuk elérni, a lambda kifejezés paramétere ugyanis _const Blob&_ típusú.

                lambda(*blob);
            }
        }

Azért, hogy a fenti ForEach mellett az std::for\_each függvénye is működjön a konténerünkön, ennek is kell, hogy legyen begin() és end() metódusa, ami a blobs vector megfelelő iterátorait adják vissza.

        auto begin()
        {
            return blobs.begin();
        }

        auto end()
        {
            return blobs.end();
        }

    private:
        // Itt tároljuk a blobokat
        std::vector<std::unique_ptr<Blob>> blobs;

    };

Hogy kényelmesebb legyen a megjelenítés, a Blob-okra is definiáljuk a << operátort.

    std::ostream& operator<<(std::ostream& stream, const Blob& blob)
    {
        stream << "Blob(" << blob.x << "," << blob.y << ")";
        return stream;
    }

    int main()
    {
        // A blob tároló létrehozása
        BlobContainer blobs;

        // Hozzáadunk 2 Blobot
        std::unique_ptr<Blob> newBlob = std::make_unique<Blob>(12,34);
        blobs.add(newBlob);
        newBlob = std::make_unique<Blob>(56,78);
        blobs.add(newBlob);

        // Az add() után a newBlob pointer nullptr, mivel a konténer
        // átvette tőle az ownershipet.
        cout << ( newBlob ? "newBlob érvényes" : "newBlob érvénytelen" ) << endl;

Minden blob megjelenítése úgy, hogy minden blobra lefuttatunk egy olyan lambda kifejezést, ami a paraméterül kapott blobot kiírja.

        cout << "Tartalom:" << endl;
        blobs.ForEach( [](const Blob& blob){ cout << blob << endl; } );

        cout << "Ugyanez iterátorokkal és std::for_each függvénnyel" << endl;
        std::for_each(
            blobs.begin(),
            blobs.end(),
            [](std::unique_ptr<Blob>& blob)
                { cout << *blob << endl; });
    }

## További megjegyzések

A lambda kifejezés gyakorlatilag egy olyan függvény, aminek nincsen neve. Három részből áll:

  * a [] zárójelek között azt adjuk meg, hogy mely, a létrehozáskor látható változókat akarjuk majd ott is elérni, ahol fut a kifejezés (vagyis melyeket "vigye magával").
  * a () zárójelek között a paraméter listája van
  * a {} zárójelek között pedig a törzse

Sokszor a létrehozás helyén látható változókból semmit nem kell magunkkal vinni, de ha mégis, változókat referencia vagy érték szerint is magával tud vinni a lambda kifejezés. A C++11-ben a [&] az összes változót elérhetővé teszi (referencia szerint).

A move szemantika, amit a unique\_ptr-nél használtunk, szintén C++11 újdonság. Jelentése ezen a leíráson túlmutat, de lényege, hogy van olyan (move) konstruktor, ami hasonló a copy konstruktorhoz, de tudja, hogy amit lemásol, meg fog semmisülni. Ezért például egy vector esetében valójában nem lemásolja az értékeket, hanem arra a memóriaterületre fog mutatni, amire a másolandó vektor is mutat, mivel annak már úgyse lesz rá szüksége. Ezzel az újrahaszosítási módszerrel rengeteg időt lehet nyerni és a legtöbb esetben a fordító megától megoldja, így nekünk nem is kell rá figyelni. A unique\_ptr esetében ugyan kicsit más a helyet, viszont a move szemantikával pont el tudjuk érni az ownership átadást is. (Az std::move függvény azért kell, mert alapból másolat jönne létre, ami meg van tiltva, az std::move egy trükkös függvény és kb. csak annyit tesz, hogy mozgatássá alakítja a másolást.)

<small>Szerzők, verziók: Csorba Kristóf</small>
