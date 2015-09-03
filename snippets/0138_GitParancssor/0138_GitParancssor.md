---
layout: default
---

# A Git konzolos használata során gyakran előkerülő parancsok

Változó, hogy ki mennyire szereti a konzolos megoldásokat. Sokak szerint sokkal gyorsabb, mint kattintgatni. Mivel a Git alapvetően egy parancssoros alkalmazás és a háttérben a grafikus felületei is konzolos parancsokat adnak ki, érdemes összeszedni, mik a leggyakrabban használat parancsok.

## Első lépések

  * git init
  * git clone <url>
  * git status
  * git add *
  * git commit -m "Üzenet"

## Branch, checkout, reset

  * git checkout -b UjBranchnev [commit]
  * git reset --hard [commit]
  * git checkout master

## Push, pull, fetch

  * git push
  * git pull
  * git fetch

## Merge, rebase, cherry-picking

  * git merge MasikBranch
  * git rebase MasikBranch
  * git rebase --continue
  * git cherry-pick 0f543fe

##

## További információk a szintaxisról

  * [Git dokumentáció](http://git-scm.com/docs/)
  * A legtöbb git parancs a --help opció hatására megmutatja a saját dokumentációját. (Pl. ``git status --help``)
  * Számos "Git Cheat Sheet" található a weben, melyek tömören összefoglalják a legfontosabb parancsokat. [GitHub Training Cheat Sheet](https://training.github.com/kit/)

<small>Szerzők, verziók: Csorba Kristóf</small>
