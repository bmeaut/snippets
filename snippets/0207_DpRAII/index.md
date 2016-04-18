---
layout: default
codename: DpRAII
title: RAII tervezési minta
tags: designpatterns alkfejl
authors: Csorba Kristóf
---

## Resource acquisition is initialization (RAII)

A RAII tervezési minta célja egy objektum garantált, szabályos felszabadítása úgy, hogy ezt egy másik objektum életciklusához kötjük.

### Bevezető példa

Ha egy fájlba írunk és közben előfordulhat, hogy egy kivétel miatt megszakad az írási folyamat, gondoskodnunk kell a fájl megfelelő lezárásáról. Amennyiben a fájl objektumunkat a kiíró függvény elején, a stacken hozzuk létre (nem a heap-en, new-val), akkor amikor kilép a végrehajtás a függvényből (vagy normális működéssel, vagy kivétel miatt, ez most mindegy), a stacken létrehozott objektum destruktora garantáltan meg fog hívódni. Ha a fájlt itt szabályosan lezárjuk, ezzel nyelvi szintű garanciánk van arra, hogy a fájl mindig lezáródik, akárhogy lépünk ki a függvényből.

### Részletek

A RAII mintát Bjarne Stroustrup és Andrew Koenig alkották meg a kivétel-biztos erőforrás kezeléshez. Ezért nincsen a kivételek kezelésénél C++-ban finally blokk, mint a Java nyelvben. Java alatt objektumot nem tudunk a stacken létrehozni, így a fenti mechanizmus nem működne. C#-ban hasonló céllal jött létre a "using" blokk.

### Példa:

  * Mutex objektumok garantált felszabadítása
  * Fájlok lezárása
  * Dinamikus objektum lefoglalása és felszabadítása: ha nem simán new-val hozzuk létre, hanem egy a stacken létrehozott unique_ptr smart pointerrel, akkor annak megszűnésekor a smart pointer destruktora a dinamikusan (heapen) létrehozott objektumot is felszabadítja.

<small>Szerzők, verziók: Csorba Kristóf</small>
