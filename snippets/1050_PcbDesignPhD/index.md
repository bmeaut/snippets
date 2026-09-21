---
layout: default
codename: PcbDesignPhD
title: USB-C töltőáramkör (MCP73831 + AP2112K) bekötése MI segítségével (PhD, mikroelektronika)
tags: snippets mieset pcb mikroelektronika toltoaramkor
authors: Barkóczi Alexandra
---

# MI esettanulmány – USB-C töltőáramkör bekötése mikroelektronikai PhD kutatáshoz

## Cél

A PhD kutatásom egyik önálló mérőegysége akkumulátorról üzemel, és USB-C-n keresztül tölthető. A tápáramkör egy MCP73831 lítium-ion töltő IC-ből (ami a cellát tölti a VBUS-ról), egy AP2112K LDO feszültségszabályozóból (ami a cella feszültségéből stabil, alacsony zajú tápot állít elő a mérőelektronikának) és a hozzájuk tartozó csatlakozókból áll. Korábban elsősorban rendszerszintű méréstechnikával foglalkoztam, a töltő IC-k és LDO-k konkrét lábkiosztása és a köréjük épülő minimális kapcsolás (PROG ellenállás, bypass kondenzátorok, EN láb kezelése) sok tekintetben új volt számomra. Az AI-t (elsősorban ChatGPT-t és Claude-ot) ezúttal nem kódgenerálásra, hanem az adatlapok lábkiosztásának értelmezésére, a bekötés összeállítására és egy szemléltető bekötési ábra elkészítésére használtam.

## Kontextus

Az áramkör a következő fő elemekből áll:
* USB-C konnektor (J1), amiről a VBUS táplálja a töltő áramkört
* MCP73831 lítium-ion töltő IC, egy PROG ellenállással a töltőáram beállítására
* akkumulátor csatlakozó (J2), a Li-ion cellához
* AP2112K LDO feszültségszabályozó, ami a cella feszültségéből állítja elő a mérőelektronika tápját

## Tanulságok

* Az AI kiválóan alkalmas volt arra, hogy egy-egy lábfunkciót (pl. mire való a MCP73831 PROG lába, vagy miért van szükség az AP2112K EN lábára) emberi nyelven, egyszerű analógiákkal elmagyarázzon, ez nagyságrendekkel gyorsabb volt, mint az adatlapok application diagramjait önállóan visszafejteni.
* A PROG ellenállás értékének kiszámításánál a modell elsőre a megfelelő képletet alkalmazta, de a mértékegység-átváltásnál (µA vs. mA) hibázott, ami tízszeres eltérést okozott volna a tervezett töltőáramban – ezt csak a kézi visszaszámolás lepleztette le.
* Amikor megkértem, hogy a szöveges lábkiosztás mellé készítsen egy szemléltető bekötési ábrát is, a modell egy egyszerű, ASCII-alapú blokkrajzot generált, ami jól mutatta a fő jelutakat (VBUS, VBAT, GND), viszont az EN láb és a PROG ellenállás pontos kapcsolódását csak egy külön rákérdezésre pontosította.
* Az AP2112K EN lábának bekötésénél a modell első válasza megengedte volna, hogy a láb lebegjen (floating), ami az adatlap szerint nem javasolt – ezt csak explicit rákérdezésre javította ki egy VIN-re húzott bekötésre.
* Rendkívül hasznos volt "adversarial review" jelleggel használni: a kész bekötési ábrát visszaadva megkérdezni, hogy talál-e benne hibát vagy hiányosságot – ez rávilágított egy hiányzó bemeneti és kimeneti bypass kondenzátorra is.

## A munkafolyamat tanulságos részletei

### Alapfogalmak megértése – miért kell külön töltő IC és LDO

```
Egy USB-C-n tölthető, Li-ion cellás mérőeszközt tervezek. Miért nem elég a cellát közvetlenül a
VBUS-ra kötni töltéshez, és miért kell külön LDO a mérőelektronika táplálásához, ha a cella
feszültsége amúgy is elég közel van ahhoz, amire a mérőáramkörnek szüksége van?
```

A válasz jól elmagyarázta, hogy egy Li-ion cella közvetlen VBUS-ról töltése szabályozatlan, veszélyes töltőáramot és túltöltést eredményezhet, ezért kell egy dedikált töltő IC (jelen esetben MCP73831), ami a töltési fázisokat (előtöltés, konstans áram, konstans feszültség) felügyeli. Az LDO-ra pedig azért van szükség, mert a cella feszültsége töltés közben és lemerülés közben is változik (kb. 3,0–4,2 V között), a mérőelektronikának viszont stabil, alacsony zajú tápra van szüksége – ezt egy lineáris szabályozó (AP2112K) biztosítja.

### A PROG ellenállás értékének meghatározása – hibás mértékegység-átváltás

```
A MCP73831 töltő IC-hez szeretnék 250 mA-es töltőáramot beállítani. Az adatlap szerint a PROG
ellenállás értéke az I_reg = 1000V/R_prog képlettel számolható. Milyen ellenállásértéket válasszak?
```

A modell a képletet helyesen alkalmazta, de a végeredményt milliamperben adta meg úgy, mintha az képlet egysége is milliamper lenne, holott az adatlapban szereplő állandó ohm és mikroamper (illetve volt/amper) kombinációjából adódik – emiatt a javasolt ellenállásérték a ténylegesen kívánt 250 mA helyett kb. 2,5 A-es töltőáramot eredményezett volna. Ezt visszajeleztem:

```
Leellenőriztem: a javasolt ellenállásértékkel visszaszámolva kb. 2,5 A töltőáram jönne ki, nem
250 mA. Nézd át újra a mértékegységeket a képletben, és mutasd meg lépésről lépésre a számítást.
```

A második válaszban a modell felismerte, hogy a képlet állandóját helytelenül kezelte mértékegység szempontjából, és a javított, lépésenkénti levezetés már a helyes, kb. tízszer nagyobb ellenállásértéket adta a 250 mA-es célhoz. Ez megerősítette a korábbi tapasztalatot: numerikus tervezési eredményt (különösen, ha alkatrészt véd) mindig érdemes függetlenül, kézzel is visszaszámolni.

### Bekötési ábra generálása

A szöveges lábkiosztást nehéz volt fejben tartani, ezért megkértem az AI-t, hogy a véglegesített bekötésről készítsen egy szemléltető, szöveges (ASCII) blokkrajzot is:

```
A fentebb egyeztetett bekötéshez (USB-C VBUS a MCP73831 VDD lábára, VBAT a cellára és az LDO
VIN lábára, PROG ellenállás a PROG lábon, közös GND) készíts egy egyszerű ASCII blokkrajzot,
ami blokkokkal és feliratozott vonalakkal mutatja a fő jelutakat.
```

Az AI a következő ábrát generálta:

```
 [ USB-C J1 ]               [ MCP73831 ]              [ AP2112K ]
 VBUS (A4) ───────┬─────────► 4:VDD    3:VBAT ───┬──────► 1:VIN (és 3:EN)
                  │                              │
                --- 4.7uF                      ┌─┴────────────────┐
                ---                            │ J2 (Akku Csatl.) │
                  │                            │ Pin 1 (+)        │
 GND ─────────────┴─────────► 2:VSS            │ Pin 2 (-) ──┐    │
                              5:PROG           └─────────────┼────┘
                                │                            │
                              [2kΩ]                          │
                                │                            │
 GND ───────────────────────────┴────────────────────────────┴───── GND
```

Ez az ábra jó gyors, vizuális ellenőrzési pontnak bizonyult, mielőtt a tényleges KiCad kapcsolási rajzot megrajzoltam volna – könnyebb volt ránézésre észrevenni a fő jelutakat, mint a hosszú szöveges leírásból. Az ábrán viszont feltűnt, hogy az AP2112K `3:EN` lába közvetlenül a `1:VIN` lábbal van összekötve feliratozva, ami ugyan működőképes (a bemenetről húzza fel a lábat), de erről a modell korábban nem beszélt explicit módon, ezért rákérdeztem:

```
Az ábrán az EN lábat a VIN-re kötötted. Ez azt jelenti, hogy az EN mindig aktív állapotban lesz,
amint van bemeneti feszültség? Van-e ennek hátránya, vagy javasolnál inkább egy felhúzó
ellenállást a VIN és az EN közé, lebegő láb helyett?
```

A válasz megerősítette, hogy az EN közvetlen VIN-re kötése a legegyszerűbb, állandóan bekapcsolt megoldás, de javasolt egy kis (pl. 100 kΩ) felhúzó ellenállást is, ha később szoftveresen (egy mikrokontroller lábbal) szeretném az LDO-t ki-be kapcsolni – ezt egy jövőbeli, alacsony fogyasztású üzemmódhoz érdemesnek találtam megjegyezni, bár a jelenlegi verzióban nem volt rá szükség.

### Bekötés felülvizsgálata "adversarial" módban

A véglegesített ábrát és lábkiosztást visszaadva kritikus visszajelzést kértem:

```
Ez a végleges bekötés (lásd a mellékelt ábrát): USB-C VBUS – MCP73831 VDD, VBAT – akkumulátor és
AP2112K VIN/EN, PROG – 2 kΩ ellenállás GND-re, közös föld mindenhol. Van ebben a bekötésben olyan
hiba vagy hiányosság, amit érdemes lenne még a panel megrendelése előtt kijavítani?
```

A válasz két hiányosságot azonosított: az ábrán és a leírásban sem szerepelt bemeneti bypass kondenzátor a VBUS és GND között (csak a VDD láb mellett volt egy 4,7 µF-os kondenzátor feltüntetve, ami helyes, de emellett egy kisebb, nagyfrekvenciás 100 nF-os kerámia kondenzátort is javasolt közvetlenül a VBUS mellé), másrészt az AP2112K kimenetén (VOUT) sem szerepelt semmilyen kimeneti kondenzátor, pedig az adatlap szerint az LDO stabil működéséhez ez elengedhetetlen. Mindkét észrevétel helytálló volt, és a kapcsolási rajzon még a gyártás előtt pótoltam őket – ez volt talán a legértékesebb felhasználási mód: nem a bekötés elkészítése, hanem egy második, gyorsan elérhető "véleményező" szerepe, ami a végső ellenőrzésnél talált hibákat.

## Összefoglalás

Az USB-C töltőáramkör bekötésének kialakításában az AI elsősorban a lábfunkciók fogalmi megértésében, egy gyors szemléltető ábra elkészítésében és egy megbízható "review partner" szerepében volt hasznos. Ugyanakkor a konkrét számértékeket (a PROG ellenállás esetén a mértékegység-átváltást) és a lábkiosztás minden részletét (pl. az EN láb bekötésének következményeit) függetlenül kellett ellenőriznem és pontosítanom, mert ezekben a modell első válasza vagy számszakilag hibás, vagy hallgatólagos feltételezéseket tartalmazott. A generált ASCII bekötési ábra kifejezetten hasznos gyors áttekintést adott a fő jelutakról, de a részletes, alkatrészszintű ellenőrzést (bypass kondenzátorok, pontos lábszámok) nem helyettesítette – ehhez mindig az adatlapra és a kézi visszaszámolásra volt szükség.
