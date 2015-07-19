---
layout: default
---

## Proxy (FONTOS)

### Bevezető példa

Tegyük fel, hogy egy távvezérelhető robot minden funkcióját egy objektum metódushívásaival akarjuk elérni. Azt szeretnénk, hogy azon az objektumon kívül a kommunikáció részleteivel már egyáltalán ne kelljen foglalkozni.

A megoldás a Proxy design pattern: az alkalmazásunkban egy Proxy objektum fogja képviselni a robotunkat, minden kérés hozzá fut majd be, amiket ő a megfelelő módon továbbít.

class RobotProxy
{
public:
   virtual void Forward(int distance) = 0;
   virtual void Turn(int degrees) = 0;
   virtual int ReadFrontDistanceSensor() = 0 const;
};

class DefaultRobotProxy : public RobotProxy
{
public:
   virtual void Forward(int distance) override;
   virtual void Turn(int degrees) override;
   virtual int ReadFrontDistanceSensor() const override;
};


Ennek az osztálynak a használata egyrészt nagyon egyszerű és kényelmes, másrészt van még egy nagy előnye: könnyen le lehet cserélni. Tesztelési célokra készíthetünk egy olyan leszármazottat is, ami valójában egy szimulátorhoz csatlakozik. Vagy egy olyat, ami csak a felhasználó felület tesztelésére szolgál és csak kiírja, hogy "most előre küldjük a robotot 3 méterrel".

(Amennyiben a szimulátor és az igazi robot eléggé hasonló protokollal kommunikál, akkor lehet, hogy felesleges két Proxy kialakítása. Elég, ha a Proxy konstruktora paraméterként megkap egy kommunikációs objektumot, amit használ majd. Ennek lecserésésével a Proxy nem is tudja majd, hogy valójában az igazi robottal beszél, vagy a szimulátorral.) **Ref dependency injection**

### Részletek

Placeholder for another object to control access to it.

Lehet kombinálni a flyweighttel.



### Példa:

### Példa:

### További példák

* Jogosultság ellenőrzés
* Egyszerűbb interfész (ez az alkalmazás nagyon közel van a Facade design patternhez.)
* Távoli erőforrások eléréséhez interfész (pl. webservice, REST API hívások)
* Távoli, nagy erőforrás igényű műveletek koordinálása. Péládul a tényleges kérés előtt már elkezdi a végrehajtást.
* Ha egy osztály funkciói eredetileg nem thread-safek és nem tuduk rajta módosítani, egy Proxy eltakarhatja és megoldhatja a szükséges szinkronizációkat.
* A std::shared_ptr<> smart pointer is egyfajta proxy, mivel elérhetővé teszti a pointer értékét, valamint számolja a hivatkozásokat, és ha ez a számláló eléri a nullát, megszünteti a pointer által hivatkozott objektumot.
