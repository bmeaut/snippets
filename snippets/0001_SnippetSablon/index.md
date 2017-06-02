---
layout: default
codename: SnippetSablon
title: Snippet sablon
tags: snippets
authors: Csorba Kristóf
---

# Ez egy snippet sablon

Ide jön a snippet teljes szövege.

## Felsorolások, forráskód

A snippetekben forráskód az alábbi három módon jelenhet meg:

* Közvetlenül a szövegbe ágyazva, mint lentebb.
* Magában a snippet könyvtárában szerepelhet minta forráskód, külön fájlban.
* Hivatkozhatunk például egy github repositoryra is, mint ez itt: [ennek a snippetnek a forrása a github.com-on](https://github.com/bmeaut/snippets/blob/gh-pages/snippets/0001_SnippetSablon/index.md)


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
