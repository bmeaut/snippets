---
layout: default
codename: FusionEffectScripting
title: Fusion Effect Scripting
tags: davinci fusion video
authors: Hartmann Ábel
---

# DaVinci Resolve x AI - Saját Fusion Effect fejlesztése

[Letölthető Fusion script (.zip)](scripts/LowShutter.fuse)

## Motiváció 

A DaVinci Resolve videó utómunka szoftver előnyös tulajdonságai közé tartozik, hogy az egyébként is gazdag, beépített effect könyvtárából bármiylen effectet tetszőleges végrehajtási struktúrába szervezhetünk, gráf képében.
A több effectből felépített szerkezeteket csoportokba rendezhetjük, de akár macrot is létrehozhatunk belőlük, ekkor saját képünkre szabhatjuk, hogy milyen beállításokhoz legyen hozzáférésünk a macron keresztül.
Az egyszerű effecteket tartalmazó gyári könyvtárból a legtöbb komplex effect felépíthető, de előfordulhat, hogy ez sem elegendő vagy csak egyszerűen képtelenek vagyunk ezen előre gyártott komponensek segítségével megoldani a feladatot.
A DaVinci Resolve lehetőséget nyújt arra, hogy a Fusion effect könyvtárat saját elemekkel bővítsük, amelyeket lua scriptekkel valósíthatunk meg, hasonlóan ahhoz, ahogyan a szoftver egyéb nézeteiben írhatunk python sripteket több szerkesztési művelet összevonására akár.
Korábban voltak már próbálkozásaim hasonló scriptek írására, de nem igazán jártam sikerrel, és a hagyományos programozási módszerek sokkal több energia befektetést igényeltek volna, mint amennyi idő alatt a beépített komponensek segítségével megoldottam a volna a problémát.
Az AI eszközök segíthetnek ezen a problémám, így itt az ideje újra próbálkozni.


## Konkrét feladat

Példaként egy egyszerű, mégis direkt nem beépített effect megvalósítását tűztem ki célul.
Low shutter speed effect során azt próbáljuk imitálni, mintha túl nagy záridőn rögzítettük volna a felvételt, emiatt a kép olyan, mintha egyszerre nyúlna és elmosódna egy kissé. 
Ezt két beépített effect segítségével tudnánk megvalósítani. Először is a Stop Motion effect többszörözni képes egy adott frame ismételt lejátszását (gyakorlatilag frame rate-et redukál). Második lépésként pedig Motion Blurt kell hozzáadnunk, amit vegy külön effectből tehetünk meg, vagy pedig, ha a Fusion rendszeren belül dolgozunk, az alapértelmezett effect beállításnál a Stop Motion effecthez is állíthatunk be egy bizonyos mértékben.
![Node Graph a beépített effectekkel](image/dvrfuse_1.PNG){width=480}
![Stop Motion effect beállítása](image/dvrfuse_3.PNG){width=320} ![Motion Blur effect beállítása](image/dvrfuse_4.PNG){width=320}
![Példa az effektek hatására](image/dvrfuse_2.PNG){width=640}
Nem bonyolult, de sokkal egyszerűbb és logikusabban vezérelhető volna azonban, ha lenne egy erre dedikált effectünk, így szeretnénk ezt megvalósítani.


## Script fejlesztés AI eszköz segítségével

### *Nehézségek*

Maga a kódolási feladat, technikailag egyszerű, egy összetettnek tekinthető alkalmazás se okoz túlságosan komplex kódot, hiszen a DaVinci Resolve saját függvénykönyvtárával kell csak dolgozni. Ennek ellenére akad néhány nehézség, amely hátráltatja a jó eredmény létrejöttét.
A fejlesztői dokumentációk közül, a nem elavult, hiteles verziók legegyszerűbben a DaVinci Resolve telepítésével együtt érhetők el. A gond az, hogy a szoftvert folyamatosan fejlesztik, nem ritkán olyan mértékben, hogy a kódjaink elveszítik a kompatibilitásukat, és megfigyeléseim alapján, a korábban próbált AI modellek gyakran elavult információkkal voltak etetve.

### *Eszközválasztás, előkészítés*

A tökéletes, működő megoldás önmagában nem elegendő szempont. A DaVinci Resolve mellett eleve szól a nagy képességű ingyenes verziója, a kompakt, jól rendezhető layoutja és a workflowja maga. Ahhoz, hogy értelme legyen scripteket készíteni hozzá, azoknak valóban gyorsítaniuk kell a munkát, és nem igényelhet bonyolult promtokat és speciális tudást, gyorsan és egyszerűen kell tudnunk generálni őket, lehetőleg ingyen.
A fentebb részletezett problémák alapján az világos, hogy olyan AI eszközre van szükség, amelyet a hiteles Fusion scripting dokumentáció irányába tudunk kényszeríteni. Egyszerű, speciális tudást nem igénylő, bárki számára ingyen elérhető szolgáltatás gyanánt a Google Gemini Notebook (Notebook LM) alkalmazását választottam, a példa fejlesztés ennek segítségével kerül bemutatásra.

Az eszköz kifejezetten jegyzet feldolgozásra optimalizált, így bármely, az adott sessionbe feltöltött dokumentum erős prioritást élvez a megoldások keresésében. 
Két, a telepített szoftver 'Developer' mappájában talált dokumentációt töltöttem fel forrásként:
* A vezérlő scriptekhez való függvénykönyvtár dokumentációjaként szolgáló README fájlt
* Az ún. Fusion Fuse SDK pdf dokumentációját
Azért mindkettőt, hogy kellően tág kontextusból nyerhessek információt a pontos üzembe helyezésre, habár elvileg a Fusion Fuse SDK dokumentáció is elég kellene legyen.

### *Low Shutter Speed effect fejlesztése*

#### Prompt

USER:
```
Craete a simple low shutter speed effect for the Fusion part of DaVinci Resolve Studio 20 that can be used as an effect node in node graph too, and provide a description about installation of the effect.
The effect must have tunable user parameters like frame rate of low shutter, or frame rate multiplier, and optional motion blur effect with all of its common settings.
```

MI:
Eredményül adott egy LowShutter.fuse scriptet és néhány fontos információt a beállítható paraméterek és az üzembe helyezés kapcsán:
```
[...]

Features & Parameter Breakdown
1. Low Shutter Modes (Mode)
    * Frame Hold (Step Count): Holds each sampled frame for a fixed number of frames (e.g., setting 2 on a 24 fps timeline gives a 12 fps stop-motion look)
    * Target Frame Rate (FPS): Automatically calculates the step ratio based on your composition's timeline frame rate (e.g., target 12.0 FPS or 8.0 FPS).
    * FPS Multiplier: Scale the original frame rate by a fractional multiplier (e.g., 0.5x or 0.25x).
2. Frame Phase Offset: Allows you to shift which frame in a cycle gets held
3. Optional Temporal Motion Blur
    * Enable Motion Blur: Checkbox toggle that reveals motion blur parameters dynamically
    * Quality / Samples: Controls how many sub-frame temporal samples are averaged per frame (e.g., 5 to 32 samples)
    * Shutter Angle: Set standard camera shutter angles (e.g., 180.0°, 360.0°)
    * Shutter Phase / Bias: Adjusts shutter opening alignment (-1.0 = backward/opening, 0.0 = centered, 1.0 = forward/closing)

[...]

How to Install the Fuse in DaVinci Resolve Studio 20
Copy the LowShutter.fuse file into DaVinci Resolve's user Fuses folder for your operating system

Installation Directories
macOS: ~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Support/Fusion/Fuses
Windows: C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Fusion\Fuses
Linux: ~/.local/share/DaVinciResolve/Fusion/Fuses

Activation & Usage in Node Graph
1. Restart DaVinci Resolve Studio 20 (required when adding a new .fuse file for the first time)
2. Open your project and switch to the Fusion Page.
3. In the Node Graph, press Shift + Space to open the Tool Select dialog and search for Low Shutter (or locate it in the Effects Library > Tools > Fuses > Effects)
4. Insert the Low Shutter node between your MediaIn and MediaOut nodes.
5. Select the node and adjust parameters in the Inspector tab
6. To reload script edits on the fly, click the Reload button at the top of the Inspector

[...]
```

#### Teszt
A telepítési ajánlásokat követve, a saját script megjelent a DaVinci Resolveon belül, és Ctrl+Space billentyűkombinációval is elő tudtam hívni, ugyanazzal a módszerrel, ahogyan a beépített effecteket is.
Ahogyan az AI is ismertette, a frame rate redukciós részhez háromféle megközelítést is biztosított, a hagyományos frame tartást, a direkt frame rate beállítást és a timelinehoz képesti szorzót.
Ezen kívül kaptunk egy featuret, hogy a tartási periódus alatti framek közül is választhassunk, fázistolás szerűen.
Motion blur paraméterek gyanánt pedig megkaptuk a jól ismert lehetőségeket, az átlagolási ablakot és a rekeszmozgás beállításokat.

![Node Graph a beépített effectekkel](image/dvrfuse_5.PNG){width=480}
![Stop Motion effect beállítása](image/dvrfuse_6.PNG){width=480}
![Példa az effektek hatására](image/dvrfuse_7.PNG){width=640}

Az ábrákból megfigyelhető, hogy hasonló beállításokkal éltem, mint a beépített effectekből való építkezés esetén. Maga az eredmény hozza az elvárt szellemképes megjelenést.


## Tanulságok

- A generált script nagyjából azzal a tudással rendelkezik, mint a beépített effektekből összerakott lánc. Ugyanezt az egy nodeos működést azokból is megvalósíthattuk volna, macroként egységbe zárva, azonban a scriptelt esetben sokkal nagyobb szabadságot kaptunk a feature bővítésre, ha a frame rate redukció megközelítését nézzük.
- Kevés utasítással, szinte hiba nélkül sikerült a scriptet megvalósítani, egyetlen helytelen információ a telepítési mappa pontos helye volt, de ott is csak minimális eltérést tapasztaltam. Ez sokkal jobb eredmény, mint amit az ehhez hasonló, a szoftver Edit tabjának munkafolyamataira írt macro scriptek esetén tapasztaltam, ott több fejlesztési iterációra volt szükség.