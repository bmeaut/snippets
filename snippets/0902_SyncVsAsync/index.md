---
layout: default
codename: SyncVsAsync
title: Szinkron és aszinkron műveletvégzés összehasonlítása
tags: threading, snippet
authors: Faragó Timea
---

# Szinkron és aszinkron műveletvégzés összehasonlítása

"Szinkron" és "aszinkron" szavak több kontextusban is előkerülhetnek az órákon. Az egyik nagyon gyakori példa, amit minden kliens technológiát bemutató tárgynál a "ne blokkold a UI-t sokáig tartó szinkron műveletekkel!"
Most nem erről lesz szó. Most csak egy egyszerű példát nézünk arra, hogy ha tudunk egyszerre több műveletet is végezni, akkor milyen időbeli javulást érhetünk el az alkalmazásainknál.

## Sync

Először is nézzük az ismert esetet. Minden szinkron megy, végrehajtódnak a dolgok egymás után. Van egy fő tevékenységünk, aminek vannak kisebb altevékenységei. Ezek futnak, csinálnak dolgokat, amit most csak egy egyszerű várakozással fogunk szemléltetni. Időméréshez használjunk Stopwatch-ot!

### Próbáljuk ki!

```csharp
public static void DoStuffSync()
        {
            Stopwatch stopwatch = new Stopwatch();
            stopwatch.Start();
            DoStuff1();
            DoStuff2();
            DoStuff3();
            DoStuff4();
            stopwatch.Stop();
            Console.WriteLine("Sync running time: {0}", stopwatch.Elapsed);
        }
        public static void DoStuff1()
        {
            Task.Delay(2000).Wait();
            Console.WriteLine("Stuff1 done");
        }
        public static void DoStuff2()
        {
            Task.Delay(5000).Wait();
            Console.WriteLine("Stuff2 done");
        }
        public static void DoStuff3()
        {
            Task.Delay(3000).Wait();
            Console.WriteLine("Stuff3 done");
        }
        public static void DoStuff4()
        {
            Task.Delay(2000).Wait();
            Console.WriteLine("Stuff4 done");
        }
```
Ahogy gondoltuk, először az első tevékenység fejeződik be (ami 2 másodpercet vett igénybe), aztán a második (5 sec), harmadik (3 sec) és végül a negyedik (2 sec). Azt várjuk, hogy ez kb 2+5+3+2=12 másodpercig tartott.

## Async

Mi lenne ez a futási idő ha a tevékenységek egymástól függetlenül végrehajthatóak lennének (ezalatt értsd: pl a 4. tevékenység nem használja fel az "előtte lévő" 3 másik eredményeit) és erőforrásfoglalási, lock-olási probléma se állna fenn? Ekkor ezek a tevékenységek végrehajthatóak lennének egyszerre is és nem tartana az egész folyamat 12 másodpercig.

### Próbáljuk ki!

```csharp
        public static void DoStuffAsync()
        {
            Stopwatch stopwatch = new Stopwatch();
            stopwatch.Start();
            Task.WaitAll(DoStuff1Async(), DoStuff2Async(), DoStuff3Async(), DoStuff4Async());
            stopwatch.Stop();
            Console.WriteLine("Async running time: {0}", stopwatch.Elapsed);
        }
        public static async Task DoStuff1Async()
        {
            await Task.Delay(2000);
            Console.WriteLine("Stuff1 done");
        }
        public static async Task DoStuff2Async()
        {
            await Task.Delay(5000);
            Console.WriteLine("Stuff2 done");
        }
        public static async Task DoStuff3Async()
        {
            await Task.Delay(3000);
            Console.WriteLine("Stuff3 done");
        }
        public static async Task DoStuff4Async()
        {
            await Task.Delay(2000);
            Console.WriteLine("Stuff4 done");
        }
```
Mit tippelünk mennyi ideig fog tartani a műveletek elvégzése? Ha 5 másodpercet (azaz a legtöbb időt igénylő tevékenység idejét) tippeltük, akkor jól gondoljuk.
És milyen sorrendben hajtódtak végre a tevékenységek? Értelem szerűen, az 5 másodperces a legutolsó, 3 másodperces előtte, de mi van a két ugyanannyi ideig tartó tevékenységgel? Mindkettő 2 másodperces művelet, emiatt változó eredményeket kaphatunk, ha többször is lefuttatjuk a kódot.

## ... amiről nem lesz most szó

Az előző résznél kiemelésre került, hogy "ha tevékenységek egymástól függetlenül végrehajthatóak lennének"  és "erőforrásfoglalási, lock-olási probléma se állna fenn". Ha async-ot használunk figyeljünk arra, hogy konkurens hozzáférést megfelelően kezeljük. Nem várt kivételeket kaphatunk például, ha adatbázis ugyanahhoz az adatbázis kontextushoz több helyről szeretnénk egyszerre hozzáférni! Illetve számoljunk azzal, hogy a szálkezelésnek megvan a maga nehezen debug-olható természete.

## További kedvcsináló az aszinkron programozáshoz

Egy másik példa async használatra [itt](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/async/).