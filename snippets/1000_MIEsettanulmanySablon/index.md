---
layout: default
codename: MIEsettanulmanySablon
title: MI Esettanulmány Sablon
tags: snippets mieset
authors: Csorba Kristóf
---

# Ez egy snippet sablon az MI Esettanulmányok számára

Ide jön a snippet teljes szövege, GitHub Markdown formátumban.

Ezek a snippetek egy konkrét MI esettanulmányról tartalmaznak egy leírást, ami később mások számára összefoglalja a tapasztalatokat és a tanulságokat. Egyetlen markdown fájl a hozzá kapcsolódó egyéb fájlokkal, amikre hivatkozik (képek, screenshotok, mellékelt forráskód vagy scriptek, esetleg ha például a konkrét használathoz tartozik egy Excel fájl is, azt is lehet mellékelni.)

A dokumentum formájához használd ennek a sablonnak a második felében lévő mintát.

## Új snippet létrehozása

Mivel a snippeteknek egyedi sorszáma és kódneve van, a munka elkezdésekor egyeztetni kell a snippet gyűjtemény karbantartójával (jelenleg Csorba Kristóf). Küldd el neki a témakört egy mondatban és ha van javaslat a kódnévre, akkor azt. Ő ad neked egy sorszámot. Ezzel hozz létre egy alkönyvtárat a többi snippet mellé (pl. ennek 1000_MIEsettanulmanySablon), másold oda ezt a sablont és egy külön branchen kezdj el dolgozni rajta.

Ha készen vagy, pull requestként adhatod be az eredményt, reviewerként rendeld hozzá Kristófot (csorbakristof) és a biztonság kedvéért írj neki emailt vagy Teams üzenetet.

## Felsorolások, forráskód

A snippetekben forráskód az alábbi három módon jelenhet meg:

* Közvetlenül a szövegbe ágyazva, mint lentebb.
* Magában a snippet könyvtárában szerepelhet minta forráskód, külön fájlban.
* Hivatkozhatunk például egy github repositoryra is, mint ez itt: [ennek a snippetnek a forrása a github.com-on](https://github.com/bmeaut/snippets/blob/gh-pages/snippets/1000_MIEsettanulmanySablon/index.md)


A forráskód lehet inline, mint a `` printf() ``, vagy lehet kódblokk, melynek minden sora legalább 4 szóközzel kezdődik:

```cpp
void main()
{
  printf("Mizu?\n");
}
```

## Képek beágyazása

Képek beágyazása az image alkönyvtárból, relatív címzéssel így történik:

![AUT Logó](image/AUT_logo.png "AUT Logó")

## További információk a szintaxisról

Például itt: [Markdown szintaxis összefoglaló](http://daringfireball.net/projects/markdown/syntax)

# Egy konkrét MI esettanulmány (ide jön a címe)

Ide jön a témakör rövid leírása: mi volt a feladat, ehhez miben használtad fel az MI-t, valamint hogy konkértan milyen MI eszközt (pl. N8N, Github Copilot és Clude Sonnet 99 stb.) használtál.

## Tanulságok

A fő tanulságokat a snippet elején foglald össze felsorolás jelleggel, hogy a legfontosabb dolgok az oldal elején legyenek, a részletek pedig utána.

- Office makró generálás VBA scriptként jól ment, de a hibakezelést érdemes megtiltani neki, hogy debuggolhatóbb maradjon a script.
- A specifikáció megírása után kérd meg, hogy tegyen fel pontosító kérdéseket azzal kapcsolatban!

## Az eredmény használata

Ha olyan a snippet, hogy ki is lehet próbálni (pl. rövid python script, amit mellékeltél), akkor itt foglald össze röviden, hogy hogyan kell használni. Ha ennél hosszabb a használati útmutató, mert bonyolultabb az eset, azt rakd egy másik markdown fájlba e mellé és itt csak hivatkozz rá.

## A munkafolyamat tanulságos részletei

Ide jöhetnek fontos promptok és az arra kapott válaszok (szükség esetén rövidítve). Minden, ami a tanulságokban csak röviden felsorolt dolgok megértéséhez, reprodukálásához, magyarázatához hasznos lehet.

### Script környezet kiválasztása

```
What language would you recommend to implement a script which creates zip files from all subdirectories in Windows environment?
```

MI:
```
[...]
Recommendation: Use PowerShell for the simplest Windows-native solution, or Python for a cross-platform, scriptable solution with more control.
[...]
```

### Specifikáció pontosítása

Előre megírtam a teljes specifikációt egy spec.md fájlba.

```
Have a look at the specification in #spec.md and ask me clarification questions!
```

MI: hosszú válaszban számos hasznos kérdést tett fel.

Válaszoltam a kérdésekre a spec.md kiegészítésével.

```
I have extended #spec.md, now start the implementation in a new file called zipper.py !
```
