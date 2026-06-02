---
layout: post
title: Okos Pénztárgép (Shop) fejlesztése TDD módszerrel
tags: tdd programming vibe-coding
author: Szakszon Ádám Dániel
---

# Pénztárgép Esettanulmány: Vibe kódolás kontrolláltan

Ez az esettanulmány egy okos pénztárgép, vagyis Shop motor fejlesztését mutatja be C# nyelven. A fő cél nem csak egy helyes árkalkulátor megírása volt, hanem egy olyan domain motor létrehozása, amelyet a TDD módszerrel folyamatosan, biztonságosan lehetett bővíteni a változó üzleti igények mentén.

> **Megjegyzés az olvasónak:** a történet megértéséhez hasznos a projekt gyökerében lévő feladatkiírás és a CRD-k, vagyis a Change Request Documentek ismerete is. Az alábbiakban a funkciók mellett hivatkozom a megfelelő CRD azonosítókra is, hogy az összefüggések egyértelműek legyenek.

## Az alapfeladat

A kiindulási követelmény nagyon egyszerű volt: létre kell hozni egy `Shop` osztályt, aminek megadhatók a termékek és az áraik. Egy terméket egyetlen nagybetű jelölt, az ár pedig egész szám volt. Ha a rendszer kapott egy kosarat stringként, például `"ABC"`, akkor vissza kellett adnia az összesített fizetendő árat.

```csharp
Shop.RegisterProduct('A', 10);
Shop.RegisterProduct('C', 20);

var price = Shop.GetPrice("AAC"); // 40
```

## A mozgó célpont

A kihívás ott kezdődött, hogy a megrendelői követelmények folyamatosan bővültek úgynevezett CRD-k formájában. Ezek új üzleti szabályokat hoztak be, és úgy kellett őket beépíteni, hogy a korábbi működés ne törjön el.

Korai példa volt a CRD P01, amely mennyiségi kedvezményt vezetett be: ha egy termékből legalább öt darabot veszünk, akkor 10% kedvezmény jár az adott termékre. Ezt követték a "3-at fizet, 4-et vihet" típusú akciók, a komplex kombó kedvezmények, a klubtagságok és a kuponkódok.

## Áttekintés és fejlesztési alapelvek

A cél egy olyan, folyamatosan fejleszthető domain motor létrehozása volt, amelyben az új üzleti követelmények kis lépésekben, regresszió nélkül vezethetők be.

A fejlesztés alapelve:

1. Először piros tesztet írni az új CRD alapján.
2. AI asszisztenssel pontosan annyi implementációt készíttetni, hogy a teszt zöld legyen.
3. Folyamatosan futtatni a teljes tesztkészletet.

Az eredmény egy olyan Shop motor lett, amely már nem csak árat számol, hanem eseményvezérelt pénztári folyamatokat, hardver-integrációkat, készletkezelést, napi riportot, valamint jogi és üzleti kontrollokat is támogat.

## Használt technológiák

* .NET 9
* xUnit
* FluentAssertions
* NSubstitute
* WinForms, külön GUI kliens a kipróbáláshoz

## Architektúra röviden

### Projektek

* `TddShop.Core`: üzleti logika, a `Shop` és a domain műveletek
* `TddShop.Tests`: automata tesztek, unit és viselkedési tesztek
* `TddShop.Gui`: grafikus kipróbáló felület

### Integrációs interfészek

A core réteg több külső függőséget interfészeken keresztül kezel.

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

Ez a megoldás lehetővé teszi, hogy a program működését a valódi gépek nélkül is ellenőrizni lehessen. Így a tesztelés gyorsabb és biztosabb, mert elég a hardvereket szimulálni.

## Funkcionális fejlődési út

### 1. Kedvezményrendszer

A rendszer egy rendkívül egyszerű árkalkulátorként indult, a kihívások pedig a kedvezményrendszerek bevezetésével kezdődtek. Első lépésként a mennyiségi kedvezményeket (CRD P01), majd a "3-at fizet, 4-et vihet" típusú darabos akciókat (CRD P02), végül az összetett kombó kedvezményeket (CRD P03) kellett implementálni. A nehézséget itt az adta, hogy ezek a kedvezmények sokszor versenyeztek egymással (CRD P07), amit egy minimálár-alapú döntési logikával és szigorú kombinációs szabályokkal oldottam meg.

### 2. Meta-információk a kosárban

Ezt követően a motor képessé vált a meta-információk kezelésére is anélkül, hogy a termékszámlálás felborult volna. Így került be a kosár-parsingba a klubtagság (CRD P04), a vásárlói azonosító és az ahhoz kötött pontgyűjtés (CRD P06, P08), valamint a kuponkódok beváltásának lehetősége (CRD P11). Szintén ehhez a szakaszhoz tartozott a vonalkód-beolvasás finomítása is: a rendszer megtanulta értelmezni a rövidített, darabszámos (CRD P12), illetve a tömegalapú (CRD P13) bemeneteket is.

### 3. Eseményvezérelt pénztár üzemmód

A legnagyobb architekturális ugrást az eseményvezérelt pénztár üzemmódra való átállás jelentette (CRD C01). Az egyszeri, stringes kiértékelést felváltotta egy valós kasszafolyamatot szimuláló API a Scan és Checkout metódusokkal. Ez az új struktúra tette lehetővé a külső hardverek, például a mérleg integrációját (CRD C02), a készlet valós idejű frissítését egy IInventory interfészen keresztül (CRD D01), és a fizetett összeget pontosan visszatérítő visszáru szakszerű kezelését (CRD D02).

### 4. Fizetési folyamatok és üzleti kontrollok

A projekt utolsó fázisában a fizetési folyamatok és az üzleti kontrollok kerültek fókuszba. Dedikált interfészeken keresztül valósult meg a készpénzes és a POS terminálos fizetés (CRD C03-C04), illetve bekerült a stornó funkció (CRD C05), amely a kosárfolyamat fizetés előtti, készletmozgás nélküli teljes megszakításáért felel. Végül a motor kibővült a nap végi riportok generálásával (CRD X01), valamint egy komoly jogi védelemmel: a kiskorúak vásárlásának állapotfüggő ellenőrzésével és a tiltott tranzakciók eseményalapú blokkolásával (CRD X02).

## TDD működés közben

### Miért volt fontos a TDD?

1. A követelmények folyamatosan változtak.
2. Sok, egymást keresztező üzleti szabály jelent meg.
3. Magas volt a regresszióveszély, mert egy új CRD könnyen törhette volna a régi működést.

### Minta ciklus

1. Új követelményhez bukó teszt.
2. Minimális implementáció.
3. Teljes tesztfuttatás.
4. Szükség esetén refaktor.

Ez tette lehetővé, hogy a rendszer 50+ tesztesetre bővülve is stabil maradjon.

## Minőség és tesztelhetőség

### Erősségek

1. Interfész-alapú függőségek miatt jól mockolható.
2. Az eseményvezérelt működés jól tesztelhető állapotgépre bontható.
3. A kritikus pénzügyi logika több szinten fedett, az egyszerű, kombinált és edge case helyzetekre is.

## Grafikus kipróbálás

Készült egy külön WinForms kliens, amiben a fő funkciók kézzel kipróbálhatók:

1. termékregisztráció
2. szkennelés
3. fizetés és stornó
4. napi összesítés
5. kiskorú és illegális vásárlás események

Indítás:

```bash
dotnet run --project TddShop.Gui/TddShop.Gui.csproj
```

## Összegzés

Ez a projekt jól mutatja, hogy a TDD nem csak tesztelési technika, hanem tervezési eszköz is. A Shop motor egy kezdetben egyszerű árkalkulátorból fokozatosan egy valós üzleti szabályokat és külső integrációkat kezelő, stabilan fejleszthető rendszerré nőtt.

A legfontosabb tanulság az, hogy amikor vibe codeolni szeretnénk, akkor a TDD vagy test-first módszer nagyon jó arra, hogy átlássuk, mi történik a kódunkban. Az AI fejlődésével már a teszteket is érdemes vele íratni, mert kevesebb hibát vét és gyorsabb, mint a manuális írás. Nekünk pedig mérnökként a pontos specifikációra, az architektúrára és a kimenet validálására kell fókuszálnunk.