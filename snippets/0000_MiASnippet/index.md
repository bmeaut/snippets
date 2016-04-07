---
layout: default
codename: MiASnippet
title: Mi a snippet?
tags: snippets
authors: Csorba Kristóf
---

# Mi az a Snippet?

A Snippet egy rövid, lehetőleg egy konkrét példa köré felépített leírás valamiről. Lehet ez például technológia, algoritmus, érdekes jelenség, nagy tanulság.

A Snippet gyűjtemény hosszú távú célja az, hogy az oktatás és kutatás során összegyűjtött ismereteket könnyen elérhető, újrahasznosítható formában tárolja.

## Hol készülnek új snippetek?

Az első snippetek a BME AUT Alkalmazásfejlesztés tantárgyához jöttek létre. A fenti hosszú távú cél érdekében többek között az alábbi snippet forrásokra számítunk:

* Új tantárgyak jegyzete snippetek formájában is készülhet. Ekkor az egyes előadások közvetlenül hivatkozhatnak snippetekre, mint jegyzetre. Ráadásul a tantárgyak könnyen hivatkozhatnak másik tantárgyak anyagaira is.
* Ha bármi olyan felvetődik az oktatás vagy kutatás során, amit tipikusan sokszor el kell valakinek magyarázni, akkor érdemes belőle készíteni egy snippetet és utána már csak hivatkozni kell rá.
* Az önálló labor témák végén szükség van dokumentációra is. Ha a konzulens hasznosnak ítéli, megkérheti a hallgatót, hogy a hagyományos dokumentáció helyett készítsen 1-2 ilyen snippetet arról, amivel foglalkozott a félév során. Ezáltal minden félévben nagyon sok érdekes témában tudunk snippeteket gyártani és mindenki jól jár vele.

## Publikálás módja

A tárba egy új snippet az alábbi módokon kerülhet be (preferencia sorrendben):

  * Ha van hozzáférésed a repositoryhoz, szabad a pálya. Saját branchen dolgozz és szólj Kristófnak, hogy mergelje, ha készen vagy.
  * Ha forkolod a git repositoryt a githubon, a kiegészítés után küljd pull requestet Kristófnak és mergelni fogja a snippetedet vagy a javításaidat.
  * Egy zip-ben elküldheted Kristófnak.

## Technikailag hogy készül egy snippet?

A snippet tár egy GIT repository a github.com-on. Minden snippet viszonylag független egymástól és külön könyvtárakban vannak. Minden snippet egy index.md (Markdown formátumú) fájlban található, valamint lehetnek mellette képek, például egy image könyvtárban. A Markdown egy nagyon egyszerű, szöveges formátum, melyből a háttérben lévő Jekyll engine egész designos oldalakat tud létrehozni.

Mivel a repository mindenki számára olvasható, bármely snippet kódját meg tudod nézni és újra tudod hasznosítani.

## Ha megakadok, kihez forduljak?

Jelenleg a BME AUT-on Csorba Kristóf a snippet rendszer koordinálója, mivel az ő agyából pattant ki az ötlet... :)

<small>Szerzők, verziók: Csorba Kristóf</small>
