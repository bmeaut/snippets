---
layout: post
title: Okos Pénztárgép (Shop) fejlesztése TDD módszerrel
tags: tdd programming
author: Szakszon Ádám
---

# Pénztárgép Esettanulmány

## Áttekintés
Ez a projekt egy fokozatosan bővített, tesztvezérelt (TDD) pénztárgép-motor megvalósítása C# nyelven. A cél nem csak egy helyes árkalkulátor volt, hanem egy olyan, folyamatosan fejleszthető domain motor létrehozása, amelyben az új üzleti követelmények (CRD-k) kis lépésekben, regresszió nélkül bevezethetők.

A fejlesztés alapelve:
1. Először piros tesztet írni.
2. Ai megkérése, hogy implamentáljon pontosan annyit, hogy zöld legyen a teszt.
3. Folyamatosan futtatni a teljes tesztkészletet.

Az eredmény egy olyan Shop motor lett, amely már nem csak árat számol, hanem eseményvezérelt pénztári folyamatokat, hardver-integrációkat, készletkezelést, napi riportot, valamint jogi/üzleti kontrollokat (pl. kiskorú tiltás) is támogat.

## Használt technológiák
1. .NET 9
2. xUnit
3. FluentAssertions
4. NSubstitute
5. WinForms (külön GUI kliens a kipróbáláshoz)

## Architektúra röviden

### Projektek
1. `TddShop.Core`: üzleti logika (Shop, interfészek, domain műveletek)
2. `TddShop.Tests`: automata tesztek (unit + viselkedési tesztek)
3. `TddShop.Gui`: grafikus kipróbáló felület

### Integrációs interfészek
A core réteg több külső függőséget interfészeken keresztül kezel:

```csharp
public interface IInventory
{
	void Update(char product, int delta);
}

public interface IScale
{
	double GetCurrentWeight();
}

public interface IPosTerminal
{
	void StartPayment(double amount);
}

public interface IPaymentNotifier
{
	void NotifySuccessfulPayment(double amount);
}

public interface IMinorCustomerNotifier
{
	void NotifyMinorCustomer();
}

public interface IIllegalPurchaseNotifier
{
	void NotifyIllegalPurchase(char product);
}
```

Ez a megoldás lehetővé teszi, hogy a program működését a valódi gépek nélkül is ellenőrizni tudjuk. Így a tesztelés gyorsabb és biztosabb, mert nem kell hozzá az igazi hardver, elég csak szimulálni azt.

## Funkcionális fejlődési út

### 1. Alap árkalkuláció
Kezdetben a rendszer egyszerű kosár-stringből számolt végösszeget, pl. `GetPrice("ACEE")`.

### 2. Kedvezményrendszer
Bevezetésre kerültek:
1. Mennyiségi kedvezmény (`RegisterAmountDiscount`)
2. Darabos kedvezmény (`RegisterCountDiscount`)
3. Kombó kedvezmény (`RegisterComboDiscount`)

A logika nem triviális, mert különböző kedvezmények versenyeznek egymással. A megoldás minimálár-alapú döntésekkel és kontrollált kombinációs szabályokkal működik.

### 3. Tagság, azonosítók, kupon
A kosár-parsing képes meta-információkat értelmezni:
1. tagság (`t`)
2. user id (`v` + számjegyek)
3. pontgyűjtés (`p` + számjegyek)
4. kupon (`k` + kód)

Kiemelt követelmény volt, hogy ezek ne borítsák fel a termékszámlálást.

### 4. Speciális mennyiségkezelés
1. Darabos rövid jelölés: pl. `A3B3C`
2. Tömeges termékek: pl. `A300`, ahol a gram-egység alapján darabra konvertálódik

### 5. Eseményvezérelt pénztár üzemmód
Az egyszeri stringes `GetPrice` mellé megjelent a pénztárgép-jellegű esemény API:
1. `Scan(char)`
2. `Checkout()`

Ez közelebb viszi a motort egy valós kasszafolyamathoz.

### 6. Készlet és visszáru
1. Vásárlás utáni készletfrissítés (`IInventory`)
2. Visszáru kezelés (`ReturnProducts`)
3. Vásárlási kontextus tárolása (mennyi volt vásárolva, milyen áron)

### 7. Fizetési folyamatok
1. Készpénzes fizetés (`ProcessCashPayment`)
2. POS indítás (`ProcessPosPayment`)
3. POS visszajelzés kezelése (`OnPaymentResult`)
4. Stornó (`Storno`)

### 8. Nap végi riport
A rendszer képes termékszintű napi összesítést adni:
1. eladott mennyiség
2. realizált bevétel

Kiemelt üzleti döntés: kombó bevétel felosztása listaárarányosan történik a termékek között.

### 9. CRD X02 - Kiskorúak kezelése
Bevezetett szabályok:
1. A vásárló állapotát explicit lehet kiskorúra állítani.
2. Termékenként regisztrálható, hogy kiskorúnak tiltott-e.
3. Tiltott termék vásárlási kísérletnél külön illegális vásárlás esemény megy ki.
4. Kiskorú állapotváltás külön eseményen jelezhető.

## TDD működés közben

### Miért volt fontos a TDD ebben a projektben?
1. A követelmények folyamatosan változtak.
2. Sok, egymást keresztező üzleti szabály jelent meg.
3. Regresszióveszély magas volt (egy új CRD könnyen törhetett régi működést).

### Minta ciklus
1. Új követelményhez bukó teszt.
2. Minimális implementáció.
3. Teljes tesztfuttatás.
4. Szükség esetén refaktor.

Ez tette lehetővé, hogy a rendszer 50+ tesztesetre bővülve is stabil maradjon.

## Fontosabb üzleti döntések (nem-specifikált pontoknál)
1. A stornó hard cancel-ként kezeli az aktuális kosárfolyamatot.
2. A napi riport lekérdezése read-only művelet, nem nulláz adatot.
3. Sikertelen POS fizetés nem könyvelődik bevételbe.
4. A sikeres fizetés a könyvelés trigger pontja (készlet, riport, események konzisztenciája).

## Minőség és tesztelhetőség

### Erősségek
1. Interfész-alapú függőségek miatt jó mockolhatóság.
2. Eseményvezérelt működés jól tesztelhető állapotgépre bontható.
3. A kritikus pénzügyi logika több szinten fedett (egyszerű, kombinált, edge case).

## Grafikus kipróbálás
Készült egy külön WinForms kliens, amiben a fő funkciók kézzel kipróbálhatók:
1. termékregisztráció
2. szkennelés
3. fizetés és stornó
4. napi összesítés
5. kiskorú / illegális vásárlás események

Indítás:

```bash
dotnet run --project TddShop.Gui/TddShop.Gui.csproj
```

## Összegzés
Ez a projekt jól mutatja, hogy a TDD nem csak tesztelési technika, hanem tervezési eszköz is. A Shop motor egy kezdetben egyszerű árkalkulátorból fokozatosan egy valós üzleti szabályokat és külső integrációkat kezelő, stabilan fejleszthető rendszerré nőtt.

A legfontosabb tanulság: Amikor vibe codeolni szeretnénk, akkor egy TDD/test-first módszer nagyon jó arra, hogy átlássuk mi történik a kódunkban. Az AI fejlődése mellett pedig már a teszteket is érdemesebb vele íratni, hiszen kevesebb hibát vét és gyorsabb mint a fejlesztők.