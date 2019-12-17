---
layout: default
codename: RandomSzam
title: Random szám generálásról
tags: random, snippet
authors: Faragó Timea
---

# Random szám generálás

Esetenként jól jöhet a kódunkban, ha nem mindig determinisztikusan ugyanazzal a számmal, értékkel dolgozunk, hanem viszünk egy kis véletlenszerűséget a számolásokban. Gondoljunk például egy játékra, ahol van n% esélyünk arra, hogy a fényesen csillogó ládikából valamilyen nagyon epik új felszerelést kapunk, de ez persze csak n% esély és nem biztos, nem is kizárt.

## Ténylegesen random

De mégis hogyan lehet C# kódban random számot generáltatni?
 * Ehhez először is szükségünk lesz egy ``Random rnd = new Random();`` változóra. Oké, mi a következő?
 * Ebből hogyan kapunk véletlenszerű számot? ``rnd.Next();`` függvényhívással.
 * Vannak helyzetek, amikor meg szeretnénk adni, hogy maximum mekkora legyen az a random érték. Gondoljunk bele, érdemes lenne azt az előbb említett n%-ot valahol 100% alatt tartani (legjobb esetben is). Ehhez a ``rnd.Next(max);`` verzióját használhatjuk a randomnak.
 * Van tovább is. Megadhatjuk, hogy mely két érték közötti számot szeretnénk kapni: ``rnd.Next(min,max);``

## ... vagy kevésbé random

Előfordulhatnak olyan esetek, amikor viszont szeretnénk, hogy ugyanazokat a random számokat kapjuk több random számot generáló változótól is. Vagy a program többszöri futására ugyanazokat a véletlen értékeket kapjuk, mert reprodukálni szeretnénk valamilyen viselkedést.
* Továbbra is szükség lesz egy ``Random rnd;`` változóra.
* Viszont most ennek adunk egy úgynevezett "seed" értéket, ami alapján számokat fog generálni: ``rnd = new Random(seed);``

### Próbáljuk ki!

Futtassuk az alábbi kódot egymás után többször! A 2. sorban mindig ugyanaz a szám lesz.
```csharp
        static void Main(string[] args)
        {
            Random r1 = new Random();
            Console.WriteLine(r1.Next());
            Random r2 = new Random(42);
            Console.WriteLine(r2.Next());

            Console.ReadKey();
        }
```

## Tesztelés?

Tesztelés fontos. De ha az alábbi módrészlettel próbálnánk tesztelni a random szám generálását kevés esélyünk van sikeres tesztet kapni.
```csharp
            Random r = new Random();
            //Ez így nem jó!
            Assert.Equal(new Random().Next(), r.Next());
```
Ha valamilyen algoritmus implementálásban random számmal dolgozunk akkor érdemes valamilyen módon biztosítani, hogy ugyanazzal a seed-del tudjunk létrehozni egy algoritmust elvégző objektumot és az assert elvárt érték helyén álló felhasznált véletlen is ugyanazzal a seed-del történjen.
```csharp
            //Algo implementálása a VeryRandomNumber osztályban
            VeryRandomNumber r = new VeryRandomNumber(42);
            Random rnd = new Random(42);

            int expected = rnd.Next() * 2 + 42;

            Assert.Equal(expected, r.GetMagicRandom());
```

## További információk a C# Random osztályáról

Hivatalos dokumentáció [itt](https://docs.microsoft.com/en-us/dotnet/api/system.random?view=netcore-3.0).