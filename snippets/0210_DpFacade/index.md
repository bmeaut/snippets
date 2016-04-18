---
layout: default
codename: DpFacade
title: Facade tervezési minta
tags: designpatterns alkfejl
authors: Csorba Kristóf
---

## Facade

A facade egy egyszerűbben használható (vagy egyéb szempontból más) interfészt biztosít egy elfedett osztály, osztály halmaz vagy függvények felé.

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

A *GetOutputStream()* és *GetInputStream()* metódusokat most nem tárgyajuk. Légyegük, hogy olyan streameket adnak vissza, amikkel már könnyedén tudunk küldeni/fogadni a bluetooth kapcsolaton keresztül.

A fenti példában később a Wt12Communication osztály segítségével már nagyon könnyen tudunk péládul PIN-t módosítani:

    Wt12Communication wt12comm;
    wt12comm.SetPin("123456");

Mind a kommunikáció, mind az esetleges visszajelzések és hibaellenőrzések részleteit be tudjuk burkolni a BluetoothCommunication osztály mögé.

### Egyéb részletek

A facade tehát belül aggregál egy másik, összetettebb rendszert, vagy interfészt. A facade osztály metódusai ehhez férnek hozzá, hogy megoldják a feladatot, de kifelé egy sokkal egyszerűbb interfészt biztosítanak.

Gyakori alkalmazása, amikor egy viszonylag összetett API-t kell elérni, de a funkciók nagy részére nincsen szükségünk és meg is akarjuk kímélni a fejlesztő csapat többi tagját a felesleges részletektől. Ilyenkor készítünk egy facade osztályt, mely kifelé pont annyit tud, amit kell, a többit meg megoldja belül.


### Példa: DLL betöltésének elrejtése

Egyik hallgatómnak szüksége volt egy osztálykönyvtárra, mely C++ alatt lineáris programozási feladatokat tud megoldani. Talált is egy alkalmasat, mely azonban DLL-ben állt rendelkezésre, így a program indulása után a DLL betöltést is meg kellett oldani.

Ilyen esetekben hosszabb távon igen kényelmes, ha ezeket a kiegészítő teendőket elfedjük: készítünk egy facade osztályt, melynek látszólag csak meg kell adni a lineáris programozási feladatot és visszakapjuk az eredményt. A háttérben persze ő betölti a DLL-t, megfelelően inicializálja az osztálykönyvtárat, átaja neki a feladatot, megoldatja, visszaolvassa és esetleg kényelmesebben kezelhető alakra hozza az eredményt, majd visszaadja azt. De ezt kívülről már nem lehet látni és ami még fontosabb, nem is kell tudni róla.

### További példák

  * C# környezetben a Windows Forms osztálykönyvtár feladata, hogy a háttérben meghúzódó WIN32 API használatát megkönnyítse, és hogy egy objektum orientált interfészt biztosítson felé. (Az utóbbi időben helyette már Windows Presentation Foundationt használunk, melynek hasonló a feladata, de a Windows Formshoz képest már nagyon eltávolodott az alacsony szintektől.)
  * Szintén hasznos ez a tervezési minta akkor, ha az eltakart API használata során valamire külön kellene figyelni, vagyis a használó kódrészletektől nagyon függ. Például ha egy funkció meghívásakor nagyon fontos, hogy egy máshol lévő paraméter helyesen be legyen állítva, akkor erről egy facade nagyon szépen gondoskodhat.
  * Előfordul, hogy egy API nagyon kiforratlan vagy kényelmetlen, elavult. Ilyenkor a rossz API elé készíthetünk egy "jó" API-t, amit már kényelmesen lehet használni.

<small>Szerzők, verziók: Csorba Kristóf</small>
