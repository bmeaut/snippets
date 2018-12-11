---
layout: default
codename: AlkFejlHf33
title: Határozott határozatlanság csapat tanulságai
tags: alkfejl afhf skipfromindex
authors: Zolnai László, Schöberl Krisztián, Baumgartner Ádám
---

# Határozott határozatlanság csapat összefoglalója

## 1) Nem jelennek meg a változások?
Ha nem akarnak megjelenni a változások újrabuildelés során, megéri kitörölni a build könyvtárat.

## 2) QML debugolása
QML debugoláshoz hasznos a QDebug << “” parancs, amivel a konzolban tudunk megjeleníteni üzeneteket.

## 3) Qt saját típusai
Néha váratlanul meg tudnak viccelni a Qt saját típusai, amiket ráadásul sok esetben nehéz debugolni. Pl. volt olyan függvény, ami hibátlanul működött ```QList<double>```-lel és ```QList<int>```-tel, de ```QList<float>```-tal nem. 

## 4) Objektumok forgatása
Körülményes nem szimmetrikus objektumokat forgatni, ezért célszerű szimmetrikusokat választani.

## 5) Esztétikai tanácsok
### 5.1)
A legtöbb QT-ben fejlesztett alkalmazásnak nincs ikonja, ami nem kölcsönöz túl jó megjelenést. Az ikon hozzáadásához szükségünk van egy .ico fájlra a projektkönyvtárban, valamint az alábbi sort kell hozzáadni a projektfájlunkhoz: 

```RC_ICONS = robo.ico```

Ez után csak egy qmake választ el a profibb megjelenéstől minket.

### 5.2)
Érdemes pontosan vágni Photoshopban a képeket, különben ugrálni fog ha köztük váltunk.

## 6) Dokumentáció
Érdemes kódolás közben kommentezni a kódot, rögtön a Doxygennek megfelelő formátumúra. Ellenkező esetben a hajrában 1-2 órányi elfoglaltságot rá kell számolni, és fennáll a veszélye, hogy valami kimarad.

## 7) Snippetek olvasása
Ha valamilyen probléma merül fel, érdemes keresgélni a snippetek közt. Jó eséllyel más is találkozott korábban a problémával és leírta a megoldást rá.

