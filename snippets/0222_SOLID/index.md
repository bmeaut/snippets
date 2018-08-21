---
layout: default
codename: SOLID
title: SOLID elvek
tags: designpatterns alkfejl
authors: Csorba Kristóf
---

# SOLID elvek

A SOLID elvek irányelvek, hogy OK, hogy objektum orientáltan programozunk, de azt is lehet jól is és rosszul is. Hogyan érdemes ezt csinálni úgy, hogy elkerüljük a kód rothadást (code rot) és a programunk karbantartható legyen.

A SOLID itt egy betűszó:

  * Single Responsibility Principle (SRP)
  * Open-Close Principle (OCP)
  * Liskov Substitution Principle (LSP)
  * Interface Segregation Principle (ISP)
  * Dependency Inversion Principle (DIP)

## Single Responsibility Principle (SRP)

Az SRP lényege, hogy egy valaminek (tipikusan osztály, metódus) egy felelőssége legyen és ne több. Ha több dolgot csinál valami, akkor azt már érdemes kettévágni. Ennek nem csak az átláthatóság az oka, hanem az is, hogy ha több dolgot csinál, akkor azok a dolgok egymástól független fejlődnek, változnak, és ezek összeakadhatnak: felesleges egymásra hatások jelennek meg, nem lehet őket függetlenül használni, tesztelni.

Amikor egy osztály megsérti az SRP-t, akkor általában vagy két azonos szinten lévő feladatot tartalmaz (pl. kommunikál egy távolságérzékelővel és egy kamerável), vagy egy kiszervezhető részfeladatot is magába foglal, ami miatt már túl nagy (pl. ha egy webáruház rendszerben a `Person` osztály tartalazza a hitelkártya számának ellenőrzését is). Mindkét esetben érdemes darabolni, amint a darabok mérete már nem triviálisan kicsi. (Nyilván nem fogunk 3 sor kódot minden esetben kiszervezni egy külön osztályba.)

## Open-Close Principle (OCP)

AZ OCP keretében arra törekszünk, hogy amikor új funkciót kell hozzátenni a rendszerhez (új fejlesztés), akkor lehetőleg ne kelljen már meglévő forráskódot módosítani, hanem csak újat hozzátenni. A lényeg, hogy ne kelljen mások régi kódjába beletúrni csak azért, hogy berakjunk egy új funkciót. Az ok nagyon egyszerű: egyrészt jó eséllyel sértenénk a Single Responsibility Principlet, valamint amin nem módosítunk, azt kisebb eséllyel rontjuk el. Vagyis lényegesen kisebb a regressziós hibák bevitelének esélye. (Regresszió az, amikor valami korábban már működött, de most elromlott.)

A gyakorlatban ezt az elvet teljesen tisztán nemigen tudjuk követni, mert például ha mindent egy új osztályba készítünk el, akkor is azt valahol az eddigi kódban kell példányosítani. De egy új eseménykezelő, egy új művelet regisztrálása csak pár sor, ott kicsi eséllyel viszünk be hibát.

Például ha van egy beágyazott rendszerünk, ami szenzorokat használ, akkor érdemes kialakítani egy szenzor ősosztályt, hogy aztán amikor egy újat kell támogatni, akkor csak ennek egy új leszármazottját kelljen elkészíteni és beregisztrálni (felvenni egy listába). Az eddigi kódrészletek ezután már a többi szenzorhoz hasonlóan ezt is fogják inicializálni, pollozni, miközben nem is tudnak róla, hogy egy új eszközről van szó. (A programunk egy pontján ha valamiről nem tudunk, akkor jó eséllyel annak a változása sem befolyásol minket.)

## Liskov Substitution Principle (LSP)

Az LSP az osztályok származtatásánál jelenik meg fontos szempontként: ha egy osztályból több másik származik le, akkor elvileg az ősosztályt interfészként használva mindegy kell, hogy legyen, melyik konkrét leszármazott példányával is dolgozunk. Első hangzásra ez triviálisnak tűnhet, hiszen erről szól a származtatás, a gyakorlatban viszont egész könnyű beleszaladni olyan hibákba, amikor az egyik leszármazott nem teljesen úgy működik, mint a társai, és ez oda vezet, hogy mégsem lehet teljesen észrevétlenül kicserélni őket. (Ha pedig egy metódus azt vizsgálja if-ek sorában, hogy a kapott objektum tényleges típusa mi, akkor valószínűleg már baj van... ezt az esetet hívják type casingnek.)

Egy hosszabb példa található erre a [../0221_LiskovModemPelda/index.html](Modemes példa a Liskov Substitution Principlere) snippetben.

## Interface Segregation Principle (ISP)

Az ISP az interfészek kialakításánál játszik szerepet. Lényege, hogy amikor egy interfészt (vagy absztrakt ősosztályt) készítünk, akkor az egy feladatkörre vonatkozzon. Vagyis ha egy osztályt 3 féle környezetből használhatnak és ezek kicsit más metódusokat hívnának, akkor ne mindent egy interfészbe rakjunk bele, hanem daraboljuk fel és a konkrét osztályunk majd származik mindháromból.

Például ha van egy csomó szenzorunk és lehet őket pollozni és diagnosztizálni is (önteszt futtatása), akkor erre érdemes egy közös ISensor interfész helyett készíteni egy IPollable és IDiagnosable interfészt is. Egyrészt áttekinthetőbb (single responsibility principle), másrészt így nem kényszerítjük rá minden szenzorra, hogy diagnosztizálható is legyen. (Ha megtesszük, egy idő után tuti lesz egy csomó szenzorunk, amiben a diagnosztika egy `return true` lesz...)

## Dependency Inversion Principle (DIP)

A DIP lényege, hogy magas szintű kód ne függjön az alacsony szintű megvalósítástól. Vagyis például a menüvezérlő ne tudja, hogy ő most pontosan milyen grafikus LCD-re vagy monitorra rajzol. Objektum orientált környezetben ez azt jelenti, hogy a menüvezérlő csak egy interfészt lásson a kijelzőből, azt ne tudja, hogy pontosan milyen osztállyal kommunikál ezen keresztül.

Egy UML osztály diagrammon ez nagyon jól látszik: az öröklés nyila mindig az ősosztály felé mutat, mivel az ősosztály ismerete kell az örökléshez. A hivatkozás sima nyila arra az osztályra mutat, aminek meg akarjuk hívni a metódusait, így tehát annak az ismerete is kell a programrészlet lefordításához. A nyíl mindig arra mutat, amitől függünk. A fenti menüvezérlőből mutatna egy nyíl pl. egy IDisplay interfészre vagy ősosztályra, de annak leszármazottjaiból (pl. grafikus LCD, HDMI, VGA port stb.) megint csak az IDisplay felé mutatnának nyilak. Vagyis a függőség iránya itt megforul és a menüvezérlő nem függ a tényleges, alacsonyabb szintű megvalósítástól.

A DIP gyakran olyan irányelvként jelenik meg, hogy programozzunk interfészekre: az osztályainkat rejtsük interfészek mögé, mert akkor a hívó fél számára teljesen transzparensen lecserélhetjük az osztályunkat egy másikra, a hívó fél oldalán semmilyen módosításra nem lesz szükség.
