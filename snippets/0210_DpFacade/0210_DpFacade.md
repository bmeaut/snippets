---
layout: default
---

## Facade (FONTOS)

### Bevezető példa

Tegyük fel, hogy Bluetooth kommunikációt implementálunk egy Bluetooth modul segítségével (pl. Bluegiga WT12). A Bluetooth modult UART-on kereszül tudjuk vezérelni szöveges parancsok segítségével. Péládul a párosításhoz szükséges PIN-t a "SET BT AUTH * 123456" paranccsal tudjuk beállítani.

Objektum orientált alkalmazásunkban egyrészt kényelmes lenne egy objektumon kereszül elérni a szükséges API funkciókat, másrészt egy csomó funkcióra nincs is szükségünk, így számunkra elég lenne egy sokkal egyszerűbb API is, ami egy csomó mindent magától, automatikusan beállít egy default értékre.

A Facade design pattern célja egy olyan interfész kialakítása, mely a mögötte lévő funkciókat az adott alkalmazás számára kényelmesebb formában teszi elérhetővé. Jelen esetben a szükséges funkciókat lefedi a metódusaival, de a feleslegesen bonyolult részleteket elfedi a fejleszők elől.

    class BluetoothCommunication
    {
    public:
        virtual void SetPin(string pin) = 0;
        virtual std::ostream GetOutputStream() = 0;
        virtual std::istream GetInputStream() = 0;
    };

    class Wt12Communication : public BluetoothCommunication
    {
    public:
        virtual void SetPin(string pin) override
        {
            GetOutputStream() << "SET BT AUTH * " << pin << endl;
        }
    };

A *GetOutputStream()* és *GetInputStream()* metódusokat most nem tárgyajuk. Légyegük, hogy olyan streameket adnak vissza, amikkel már könnyedén tudunk küldeni/fogadni a bluetooth kapcsolaton kereszül.

A fenti példában később a Wt12Communication osztály segítségével már nagyon könnyen tudunk péládul PIN-t módosítani:

    Wt12Communication wt12comm;
    wt12comm.SetPin("123456");

Mind a kommunikáció, mind az esetleges visszajelzések és hibaellenőrzések részleteit be tudjuk burkolni a BluetoothCommunication osztály mögé.

**Erre pont van osztály Qt alatt, csak Windows alatt nem mindig megy. (?)**

### Részletek

Aggregál egy összetettebb rendszert, interfészeket.
Wrapperként egy sokkal egyszerűbb interfészt ad. Pl. API elé. Vagy egy bonyolult rendszert egyszerűen akarunk elérni, sok éppen felesleges részlet nélkül.

Kiegészítési lehetőségek:

* Adapter: más interfészeket kell támogatni
* Decorator: futási időben változtatható viselkedés

### Példa:

### Példa:

### További példák

* C# környezetben a Windows Forms osztálykönyvtár feladata, hogy a háttérben meghúzódó WIN32 API használatát megkönnyítse, és hogy egy objektum orientált interfészt biztosítson felé.
