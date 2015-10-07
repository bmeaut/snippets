---
layout: default
---

# A Signals and slots koncepció Qt alatt

Az eseményvezérelt rendszerekben gyakran van szükség arra, hogy egy eseményhez hozzákössünk egy eseménykezelőt. Eredetileg C-ben és C++-ban erre valók a függvény pointerek, mivel azokat paraméterként átadva "be tudunk regisztrálni" egy meghívandó függvényt. Ezzel két gond van:

  * Ha egy eseményhez több eseménykezelő függvényt is meg akarunk tudni adni, akkor valami pointer tárolót is létre kell hozni.
  * Ha a kezelő függvény egy objektumban van, akkor annak vagy csak statikus metódusát tudjuk beregisztrálni, vagy meg kell oldanunk, hogy az objektum this pointerét is valahogy regisztráljuk a függvénypointerrel együtt.

A Qt kihasználva a Meta-object compiler előnyeit erre a problémára alakította ki a signals and slots rendszert: az objektumoknak lehetnek signaljai, amiket "ki tudnak bocsátani", valamint slotjai, amikhez pedig ilyen signalokat lehet kötni. Ha egy objektum kiad egy signalt, akkor a hozzá csatlakozó összes slot, mint függvény meghívódik.

## A konkrét példa részei

Az alábbi példa (mely [itt](https://github.com/csorbakristof/alkalmazasfejlesztes) érhető el a SignalsAndSlots könyvtárban) három objektumot használ:

  * Application: ez képviseli az alkalmazást, ami létrehoz egy időzítőt (QTimer) és egy szimulátort (Simulator), ami egy járművet szimulál.
  * Simulator: pozíció és sebesség alapján szimulál egy járművet. Akkor lép az idő, amikor meghívódik a tick() slotja. Ezt fogjuk majd a QTimer-hez kötni, hogy másodpercenként meghívódjon.
  * QTimer: ő adja az ütemet a szimulátornak a timeout signalja segítségével.

## A Simulator osztály

Kezdjük a szimulátor osztállyal:

### Simulator.h

    #pragma once
    #ifndef SIMULATOR_H
    #define SIMULATOR_H
    #include <QObject>

Ahhoz, hogy a signals and slots rendszer működjön, a QObject-ből kell leszármazni.

    class Simulator : public QObject
    {

A Q_OBJECT makrót minden olyan objektumnak tartalmaznia kell, ami a QObject-ből származik. Akkor is, ha tranzitívan származik csak a QObjectből, vagyis az ősein keresztül.

        Q_OBJECT

    public:
        Simulator(int velocity);
        ~Simulator() = default;

    signals:

Az arrived signal fogja jelezni, hogy megérkeztünk egy szép helyre (bármit is jelentsen a szép hely :) ).

        void arrived(int where);

    public slots:

Az idő haladását pedig a QTimer a tick() slotnak a hívásával fogja jelezni.

        void tick();

    private:
        int x;  // pozíció
        int v;  // sebesség
    };

    #endif // SIMULATOR_H

### Simulator.cpp

A Simulator.cpp inicializálja a QObject őst, a pozíciót és a sebességet, valamint a tick() hívás esetén lefuttat egy szimulációs lépést.

    #include <QDebug>
    #include "Simulator.h"

A konstruktorban fontos, hogy a QObject ősosztály konstruktorát is meghívjuk. Paramétere egy szölő osztály, de most ezt nullptr-re állítjuk. (A C++11 előtti időkre a Qt-nak lett egy saját objektum megszüntető rendszere, ez a szülő pointer ahhoz kellett.)

    Simulator::Simulator(int velocity)
        : QObject(nullptr), x(0), v(velocity)
    {
    }

    void Simulator::tick()
    {
        x += v;
        qDebug() << "Szimulátor: x =" << x
                 << "és v =" << v;
        if (x % 10 == 0)
        {

Kiadjuk ("emittáljuk") a jelet, hogy szép helyre érkeztünk. Vagyis ekkor egymás után meghívódók minden feliratkozott objektum erre a signalra csatlakoztatott slotja.

            emit arrived(x);
        }
    }

## Az Application osztály

Az Application a konstruktorában létrehozza az alkalmazás többi objektumát és összekapcsolja őket. A konstruktor végén gyakorlatilag készen el is indul minden.

### Application.h

    #pragma once
    #ifndef APPLICATION_H
    #define APPLICATION_H
    #include <QCoreApplication>
    #include <QObject>
    #include <QTimer>
    #include "Simulator.h"

    class Application : public QCoreApplication
    {
        Q_OBJECT

    public:
        Application(int argc, char* argv[]);
        ~Application() = default;

    private:
        Simulator simulator;
        QTimer timer;

    private slots:
        void simulatorArrivedToNicePlace(int where);
    };

    #endif // APPLICATION_H

Érdemes megfigyelni, hogy a simulatorArrivedToNicePlace metódus paraméterlistája igazodika Simulator::arrived signalhoz.

### Application.cpp

    #include <QCoreApplication>
    #include <QDebug>
    #include "Application.h"
    #include "Simulator.h"

    Application::Application(int argc, char* argv[])
        : QCoreApplication(argc, argv),
          simulator(2),
          timer()
    {

Most kapcsoljuk össze a signalokat és slotokat. Sok hibának az az oka, hogy

  * valamelyik objektum nem publikusan származik a QObject-ből
  * az objektum nem tartalmazza a Q_OBJECT makrót
  * valamelyik & jel lemarad

A szintaktika egyszerű: forrás objektum, signal, cél objektum, slot.

        connect(&timer, &QTimer::timeout, &simulator, &Simulator::tick);
        connect(&simulator, &Simulator::arrived,
                this, &Application::simulatorArrivedToNicePlace);

A timert pedig elindítjuk 1000ms periódus idővel.

        timer.start(1000);
    }

    void Application::simulatorArrivedToNicePlace(int where)
    {
        qDebug() << "A szimulátor szép helyre ért: " << where;
        exit(0);
    }

## main.cpp

A teljesség kedvéért itt a main.cpp is, mely csak létrehozza az Application objektumot.

    #include "Application.h"

    int main(int argc, char* argv[])
    {
        Application a(argc, argv);
        return a.exec();
    }

Az a.exec() hívás a Qt-s ablakok eseménykezelőit tartalmazná, de most ilyenünk sincs, így az csak egy várakozó ciklus addig, amíg a Application::simulatorArrivedToNicePlace metódus meg nem hívja az exit()-et.

### A program kimenete:

    Szimulátor: x = 2 és v = 2
    Szimulátor: x = 4 és v = 2
    Szimulátor: x = 6 és v = 2
    Szimulátor: x = 8 és v = 2
    Szimulátor: x = 10 és v = 2
    A szimulátor szép helyre ért:  10

## Mire fordul le a signal és a slot?

A Qt Meta-object rendszerének nagy trükkje, hogy minden szabványos C++-ra fordul le, így bármly fordítóval használható. Na de mire fordulnak le ezek a kulcsszavak, mint slots, emit, meg maguk a signalok és slotok?

A válasz meglepően egyszerű: a signal egy sima függvény lesz, amit megír helyettünk a MOC (Meta-Object Compiler). Így az emit kulcsszó igazából csak neki szól, valójában semmire nem fordul le: az "emit arrived(x);"-ból a tényleges C++ fordító már csak "arrived(x);"-et lát.

A slot szintén csak egy sima metódus. Valójában az emit, slots és signals preprocesszor makrók. Qt Creatorban rajtuk F2-t nyomva az alábbit látjuk a qobjectdefs.h-ban:

    # define emit

Hasonló a helyzet a többi kulcsszóval is:

    #     define slots
    #     define signals public

A varázslás a MOC által generált C++ forrásfájlban van, mint amilyen a moc_Simulator.cpp (ezt a fordítás eredményeit tartalmazó build könyvtárban találjuk meg a fordítás után):

    // SIGNAL 0
    void Simulator::arrived(int _t1)
    {
        void *_a[] = { Q_NULLPTR, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
        QMetaObject::activate(this, &staticMetaObject, 0, _a);
    }

Valójában a signalhoz generált függvény továbbhív a QMetaObject ősosztály activate metódusába.  Ahhoz, hogy megértsük, ott mi történik, ugyanebben a fájlban még nézzünk meg egy másik metódust:

    void Simulator::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
    {
        if (_c == QMetaObject::InvokeMetaMethod) {
            Simulator *_t = static_cast<Simulator *>(_o);
            switch (_id) {
            case 0: _t->arrived((*reinterpret_cast< int(*)>(_a[1]))); break;
            case 1: _t->tick(); break;
            default: ;
            }
        } else if (_c == QMetaObject::IndexOfMethod) {
            int *result = reinterpret_cast<int *>(_a[0]);
            void **func = reinterpret_cast<void **>(_a[1]);
            {
                typedef void (Simulator::*_t)(int );
                if (*reinterpret_cast<_t *>(func) == static_cast<_t>(&Simulator::arrived)) {
                    *result = 0;
                }
            }
        }
    }

Ez a statikus metódus gyakorlatilag arra jó, hogy átadva neki egy Simulator objektumra mutató pointert és egy metódus sorszámot, meg tudjuk hívni azt a metódust. És ez a lényege a mata-object rendszernek: egy metódust nem csak pointerrel lehet meghívni, de sorszámmal is. A connect metódus a pointerek alapján megkeresi a metódusok sorszámát és egy nagy tárolóba csak azt menti le, hogy melyik forrás objektum melyik sorszámú metódusa (a signal) melyik cél objektumok mely sorszámú metódusaihoz (a slot) csatlakozik. És a fenti activate() metódus ezeket szépen végighivogatja.

## Záró megjegyzések

  * Befejezésül még annyit hozzáteszek, hogy a connect-nek nyilván van egy disconnect megfelelője is, ami megszünteti a kapcsolatokat.
  * Természetesen ez a funkcionalitás más környezetekben is szükségessé vált. C# alatt például a delegate egy konténer és egy függvény pointer kombinációja, amivel ugyanezt lehet elérni.
  * Mivel valójában a signal és slot is metódus lesz, ezért nincs akadálya annak, hogy egy signalhoz egy másik signal meghívását kapcsoljuk, vagy hogy egy slotot metódusként meghívjunk. Sőt, a C++11 óta signalhoz a connect segítségével lamda kifejezést is hozzá lehet kapcsolni.
  * További információk itt: [http://woboq.com/blog/how-qt-signals-slots-work-part2-qt5.html](http://woboq.com/blog/how-qt-signals-slots-work-part2-qt5.html)