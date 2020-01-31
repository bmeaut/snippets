---
layout: default
codename: StopwatchVsDateTime
title: Stopwatch és DateTime használata időmérésre
tags: time, snippet
authors: Faragó Timea
---

# Stopwatch és DateTime használata időmérésre

Hasznos tud lenni ha már valamilyen meglévő kódot tesztelgetünk, elemezgetünk például  gyorsaság szempontból. Vannak helyzetek, amikor a helyes működés nem elegendő és szeretnénk megtudni, hogy mi lassít az alkalmazásunkon és szükségünk van egy pontos időmérésre alkalmas eszközre. Most két ilyen lehetőségről lesz só, melyek közül az egyik...

## DateTime.Now

Ez egy C# property, ami éppen az aktuális dátumot adja vissza jó pontossággal. Egy mérendő művelet kezdete előttre írunk egy ``var start = DateTime.Now;``változót a programba, majd a mérendő rész után egy ``var stop = DateTime.Now;`` változót és megnézzük, hogy mennyi idő telt el a kettő között.
Szerencsére a különbséget egy egyszerű kivonással meg tudjuk oldani a két DateTime típusú változó között és az eredményt TimeSpan típusú értékként kapjuk meg, amely képes az eredményt milliszekundum pontossággal kiírni.

## Stopwatch

A másik lehetőség a Stopwatch használata. Létrehozunk egy új ``Stopwatch stopwatch = new Stopwatch();`` változót, elindítjuk a ``stopwatch.Start();`` hívással, majd megállítjuk a ``stopwatch.Stop();``-al. Az eltelt időt milliszekundumban megkaphatjuk a ``stopwatch.ElapsedMilliseconds`` property segítségével.

## Pontosság

Noha mindkét lehetőség tud időtmérni a pontosságuk nem ugyanolyan jó. Nézzünk egy rövid ideig tartó műveletet, ezt szemléltesse most a ``await Task.Delay(100);`` hívás, ami hatására a végrehajtásunk várakozik 100 milliszekundumot.
Egy kis statisztika miatt futtassuk le ezt a műveletet és nézzük meg milyen értékeket mér a DateTime és a Stopwatch! Nézzük meg, hogy átlagosan mennyi ideig tartottak a műveletek lemérve!

### Próbáljuk ki!

```csharp
static async Task Main(string[] args)
        {
            List<double> DateTimeValues = new List<double>();
            for (int i = 0; i < 10; i++)
            {
                var start = DateTime.Now;
                await Task.Delay(100);
                var stop = DateTime.Now;
                Console.WriteLine("DateTime waited:\t{0}",(stop-start).TotalMilliseconds);
                DateTimeValues.Add((stop - start).TotalMilliseconds);
            }
            double DateTimeAverage=DateTimeValues.Average();
            Console.WriteLine("Average value with DateTime:\t{0}",DateTimeAverage);
            Console.WriteLine();
            List<long> StopwatchValues = new List<long>();
            for (int i = 0; i < 10; i++)
            {
                Stopwatch stopwatch = new Stopwatch();
                stopwatch.Start();
                await Task.Delay(100);
                stopwatch.Stop();
                Console.WriteLine("Stopwatch waited:\t{0}", stopwatch.ElapsedMilliseconds);
                StopwatchValues.Add(stopwatch.ElapsedMilliseconds);
            }
            double StopwatchAverage = StopwatchValues.Average();
            Console.WriteLine("Average value with Stopwatch:\t{0}", StopwatchAverage);
            Console.WriteLine("Done");
            Console.ReadKey();
        }
```
Valamilyen hasonló értékeket kell kapnunk, mint ez:
```
DateTime waited:        146,5008
DateTime waited:        100,97200000000001
DateTime waited:        116,9658
DateTime waited:        109,26830000000001
DateTime waited:        109,1342
DateTime waited:        113,5616
DateTime waited:        104,60430000000001
DateTime waited:        109,1606
DateTime waited:        109,50080000000001
DateTime waited:        108,73140000000001
Average value with DateTime:    112,83998000000001

Stopwatch waited:       113
Stopwatch waited:       103
Stopwatch waited:       109
Stopwatch waited:       109
Stopwatch waited:       109
Stopwatch waited:       109
Stopwatch waited:       109
Stopwatch waited:       109
Stopwatch waited:       109
Stopwatch waited:       108
Average value with Stopwatch:    108,7
Done
```
Most nézzünk egy rövidebb, 20 ms várakozást:
```
DateTime waited:        114,64760000000001
DateTime waited:        20,6021
DateTime waited:        30,8688
DateTime waited:        36,4865
DateTime waited:        25,7516
DateTime waited:        31,064400000000003
DateTime waited:        31,0289
DateTime waited:        31,0696
DateTime waited:        31,2073
DateTime waited:        36,426100000000005
Average value with DateTime:    38,91529

Stopwatch waited:       24
Stopwatch waited:       30
Stopwatch waited:       31
Stopwatch waited:       31
Stopwatch waited:       31
Stopwatch waited:       31
Stopwatch waited:       31
Stopwatch waited:       31
Stopwatch waited:       31
Stopwatch waited:       31
Average value with Stopwatch:    30,2
Done
```
Végül egy 10 ms-osat:
```
DateTime waited:        97,7485
DateTime waited:        21,1372
DateTime waited:        15,399600000000001
DateTime waited:        15,354700000000001
DateTime waited:        15,3938
DateTime waited:        15,4311
DateTime waited:        20,1487
DateTime waited:        10,7728
DateTime waited:        15,4769
DateTime waited:        15,455
Average value with DateTime:    24,23183

Stopwatch waited:       14
Stopwatch waited:       15
Stopwatch waited:       15
Stopwatch waited:       20
Stopwatch waited:       10
Stopwatch waited:       15
Stopwatch waited:       15
Stopwatch waited:       15
Stopwatch waited:       15
Stopwatch waited:       15
Average value with Stopwatch:    14,9
Done
```
Ahogy láthatjuk, minnél rövidebb ideig tart egy művelet a DateTime annál pontatlanabb lesz a Stopwatch-hoz képest. Tanulság: használjunk időmérésre Stopwatch-ot!

## További információk az osztályokról

Hivatalos dokumentáció Stopwatch-ról [itt](https://docs.microsoft.com/en-us/dotnet/api/system.diagnostics.stopwatch?view=netcore-3.0).
Hivatalos dokumentáció DateTime-ről [itt](https://docs.microsoft.com/en-us/dotnet/api/system.datetime?view=netcore-3.0).