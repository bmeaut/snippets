---
layout: default
codename: DpVisitorObserver
title: A Visitor és az observer tervezési minta
tags: designpatterns
authors: Csorba Kristóf
---

# Visitor és Observer minta

Az alábbi példa egy konkrét implementációja a visitor és observer tervezési mintáknak, melyek egyéb részleteit másik snippetek tartalmazzák.

[A példa forráskódja itt érhető el.](https://github.com/csorbakristof/alkalmazasfejlesztes/tree/master/VisitorObserverPelda)

Ez a példaprogram a Visitor és Observer design patternek működését mutatja be.
Egy tároló objektumban (ElementContainer) elemeket (ElementBase leszármazottjai, ElementInt és ElementString) tárolunk.

Az observer (Observer osztály, az ObserverBase leszármazottja) minden egyes Elementhez be van regisztrálva, hogy ha változik annak belső állapota (value attribútuma), akkor erről szóljon az observernek.

Egy visitor (Visitor, ami a VisitorBase-ből származik) a tárolóban lévő összes elemet módosítja. Tud kezelni ElementInt és ElementString objektumokat is.

A következőkben bemutatom a forráskód részleteit, nem feltétlenül a forráskódban szereplő sorrendben.

## Ősosztályok

A VisitorBase ősosztály a visitorok számára, melyek ElementInt és ElementString objektumokat tudnak fogadni. A visitor minta lényege, hogy minden ElementInt és ElementString meg fogja hívni a visitor megfelelő metódusát önmagára, így a visitor minden elemen végre tudja hajtani az általa képviselt műveletet.

	class VisitorBase
	{
	public:
	    virtual void Visit(ElementInt& element) = 0;
	    virtual void Visit(ElementString& element) = 0;
	};

Az ObserverBase az observerek ősosztálya. Minden ElementBase leszármazottnak be lehet ilyen objektumokat regisztrálni, hogy neki is szóljanak, ha változik az értékük.

	class ObserverBase
	{
	public:
	    virtual void ValueChanged(int oldValue, int newValue) = 0;
	    virtual void ValueChanged(string oldValue, string newValue) = 0;
	};

Az ElementBase a tároló elemeinek ősosztálya. Minden elem meg tudja magát jeleníteni, tud kezelni visitort, valamint observereket is be lehet regisztrálni mindegyiknek, amiket értesít, ha az értéke megváltozik.

Itt tároljuk a pointereket a regisztrált observerekre.

	class ElementBase
	{
	protected:
	    vector<ObserverBase*> observers;
	public:
	    virtual void Show() = 0;
	    virtual void Accept(VisitorBase& visitor) = 0;
	
	    void RegisterObserver(ObserverBase *observer)
	    {
	        observers.push_back(observer);
	    }
	};

## A tárolt elemek osztályai

Két osztály származik le az ElementBase-ből, az egyik egy int, a másik egy string típusú változót tartalmaz.

A visitor szempontjából a lényegi pont az Accept metódus, mely visszahívja a kapott visitort. Ennek előnye, hogy a visitornak automatikusan a hívó Element objektum osztályának megfelelő (Visit nevű) metódusa hívódik meg. Ha esetleg a visitor nem támogat egy adott elemtípust, akkor pedig már itt, fordítási időben kiderül a hiba.

Ezen kívül az observer szempontjából a setter metódus (SetValue) a fontos, mely változás esetén értesíti az összes regisztrált observert. (A tömörség miatt itt nem készítettem fel a programot arra, ha egy observer idő előtt megszűnik. Ha erre van esély, akkor itt figyelni kell rá, hogy a sima pointer helyett például egy weak_ptr-t használjunk, hogy ellenőrizni tudjuk, hogy még érvényes-e.)  

	class ElementInt : public ElementBase
	{
	    int value;
	public:
	    int GetValue() { return value; }
	    void SetValue(int newValue)
	    {
	        int oldValue = value;
	        value = newValue;
	        // Minden observer értesítése.
	        for(auto observer : observers)
	        {
	            observer->ValueChanged(oldValue, newValue);
	        }
	    }
	
	    ElementInt(const int value = 0)
	        : value(value)
	    {
	    }
	
	    virtual void Show() override
	    {
	        cout << "ElementInt: " << value << endl;
	    }
	
	    virtual void Accept(VisitorBase& visitor) override
	    {
	        visitor.Visit(*this);
	    }
	};

	class ElementString : public ElementBase
	{
	    string value;
	public:
	    string GetValue() { return value; }
	    void SetValue(string newValue)
	    {
	        string oldValue = value;
	        value = newValue;
	        for(auto observer : observers)
	        {
	            observer->ValueChanged(oldValue, newValue);
	        }
	    }
	
	    ElementString(const string value)
	        : value(value)
	    {
	    }
	
	    virtual void Show() override
	    {
	        cout << "ElementString: " << value << endl;
	    }
	
	    virtual void Accept(VisitorBase& visitor) override
	    {
	        visitor.Visit(*this);
	    }
	};

## A konkrét visitor

Ez a konkrét visitor osztály. Int típus esetén hozzáad 100-at az értékhez, string esetén pedig utána írja, hogy "+100".

Ezt a műveletet fogjuk végrehajtani az összes tárolt elemen. (Az ilyen műveletek hatására az Element értesíteni fogja az összes observerét a változásról.)

Így a visitor gyakorlatilag egy új műveletet definiál az Element-ek felett, melyhez azonban nem kell módosítani az Element-ek osztályait.

Az elemek Accept metódusa a visitor megfelelő metódusát fogja mindig visszahívni.

	class Visitor : public VisitorBase
	{
	public:
	    virtual void Visit(ElementInt& element) override
	    {
	        element.SetValue(element.GetValue() + 100);
	    }
	
	    virtual void Visit(ElementString& element) override
	    {
	        element.SetValue(element.GetValue() + "+100");
	    }
	};

## A konkrét observer

Ez pedig egy konkrét observer implementáció, mely a konzolra kiírja az értékváltozásokat.

	class Observer : public ObserverBase
	{
	public:
	    virtual void ValueChanged(int oldValue, int newValue) override
	    {
	        cout << "Int value changed from " << oldValue << " to " << newValue << endl;
	    }
	
	    virtual void ValueChanged(string oldValue, string newValue) override
	    {
	        cout << "String value changed from " << oldValue << " to " << newValue << endl;
	    }
	};

## Az elemeket tároló osztály

Ez a tároló osztály az ElementBase leszármazottjait tudja eltárolni. Az elemeknek ő az ownere, a tároló a megszűnésekor a tárolt elemeit is megszünteti. Ezt úgy oldja meg, hogy unique_ptr smart pointerrel tárolja őket.

Az AddAndTakeOwnership metódus unique\_ptr-t kap paraméterként, amit viszont nem lehet másolni, csak mozgatni (move semantics), ezért a vektorba mentésnél az std::move függvény segítségével mozgatjuk az értéket. Ez azért fontos, mert így nem lehet véletlenül sem lemásolni egy unique\_ptr-t, aminek hatására végül mégiscsak több smart pointer birtokolná az objektumot. Mozgatáskor a forrás tudja, hogy elvesztette az ownershipet és nullptr-re állítja magát.

(Szintén a unique\_ptr másolhatatlansága miatt kell a Show() metódusban referencia szerint végigmenni az elemeken, mivel ideiglenes másolatot itt sem készíthetünk, vagyis egy sima "auto element : elements" nem fordulna le.)

Ahhoz, hogy a visitorokat könnyen át tudjuk adni minden elemnek, a tároló Accept metódusa továbbítja azt minden elemének.

	class ElementContainer
	{
	    vector<std::unique_ptr<ElementBase>> elements;
	public:
	    void AddAndTakeOwnership(std::unique_ptr<ElementBase>& element)
	    {
	        elements.push_back(std::move(element));
	    }
	
	    void Show()
	    {
	        for(auto& element : elements)
	        {
	            element->Show();
	        }
	    }
	
	    void Accept(VisitorBase& visitor)
	    {
	        for(auto& element : elements)
	        {
	            element->Accept(visitor);
	        }
	    }
	};

## A főprogram

A főprogramban 4 elemet hozunk létre. Mindbe regisztráljuk az observert, majd berakjuk a tárolóba.

(Érdekesség, hogy a move semantika miatt a unique\_ptr-t minden elemnél újra lehet hasznosítani.)

Az egyes fázisok után a kimenetet kommentárba beleírtam a forráskódba.


	int main()
	{
	    ElementContainer container;
	    Observer observer;
	
	    unique_ptr<ElementBase> newElement = std::make_unique<ElementInt>(1);
	    newElement->RegisterObserver(&observer);
	    container.AddAndTakeOwnership(newElement);
	
	    newElement = std::make_unique<ElementString>("1");
	    newElement->RegisterObserver(&observer);
	    container.AddAndTakeOwnership(newElement);
	
	    newElement = std::make_unique<ElementInt>(2);
	    newElement->RegisterObserver(&observer);
	    container.AddAndTakeOwnership(newElement);
	
	    newElement = std::make_unique<ElementString>("2");
	    newElement->RegisterObserver(&observer);
	    container.AddAndTakeOwnership(newElement);
	
	    cout << "--- Before visit:" << endl;
	    container.Show();
	
		/*
		--- Before visit:
		ElementInt: 1
		ElementString: 1
		ElementInt: 2
		ElementString: 2
		*/
	
	    cout << "--- During visit:" << endl;
	    Visitor visitor;
	    container.Accept(visitor);
	
	    /*
	    --- During visit:
	    Int value changed from 1 to 101
	    String value changed from 1 to 1+100
	    Int value changed from 2 to 102
	    String value changed from 2 to 2+100
	    */
	
	    cout << "--- After visit:" << endl;
	    container.Show();
	
	    /*
	    --- After visit:
	    ElementInt: 101
	    ElementString: 1+100
	    ElementInt: 102
	    ElementString: 2+100
	    */
	}

<small>Szerzők, verziók: Csorba Kristóf</small>
