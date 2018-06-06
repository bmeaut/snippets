---
layout: default
codename: QDataStream
title: QBuffer és QDataStream
tags: alkfejl qt
authors: Csorba Kristóf
---

# A QBuffer és QDataStream használata

Az alábbi példaprogram az [alkalmazásfejlesztés repository](https://github.com/csorbakristof/alkalmazasfejlesztes) InMemoryStream példája. Bemutatja röviden a QBuffer, mint általános adattároló buffer, és a QDataStream, mint tárolók fölött működő stream osztály használatát.

A példában létrehozunk egy buffert a memóriában, amire létrehozunk egy folyamot, ami pont ebbe a bufferbe tud írni. Utána létrehozunk ugyanarra a bufferre egy másik folyamot is, ami olvasni fog belőle. És megnézzük, hogy a bufferbe pontosan mi kerül bele.

    #include <QCoreApplication>
    #include <QString>
    #include <QBuffer>
    #include <QDataStream>
    #include <QDebug>

    int main(int argc, char* argv[])
    {
        Q_UNUSED(argc);
        Q_UNUSED(argv);

A buffer tárolja az adatokat

        QByteArray buffer;

A stream fog írni ("WriteOnly" nincsen). A stream tudja követni, hogy hol tart, tud írni... de tárolója nincsen, azt kívülről biztosítjuk neki.

        QDataStream stream(&buffer, QIODevice::ReadWrite);

Most direkt olyan szöveget fogunk beírni a bufferbe, hogy hexában is könnyen felismerjük, hogy mi van ott.

        QString text1("ABCD");
        QString text2("EFG");

Most írunk a streambe. A QString osztály ki tudja magát írni és vissza is tudja magát olvasni.

        stream << text1;
        stream << text2;

Létrehozunk egy streamet, ami olvasni tud a bufferből. A két stream tetszőlegesen tud írni, olvasni és ugrálni a bufferen, egymást nem zavarják.

        QDataStream readStream(&buffer, QIODevice::ReadOnly);
        QString readText1;
        QString readText2;

Fontos, hogy a két QString tudja, hogy milyen hosszú, így nem kell megkeresni a határukat. Ez nagyon kényelmessé teszi az összetettebb adatstruktúrák sorosítását, mivel csak egymás után ki kell írni az adatokat.

        readStream >> readText1;
        readStream >> readText2;

Megnézzük, mit sikerült visszaolvasni.

        qDebug() << "Text1: " << readText1;
        qDebug() << "Text2: " << readText2;

És megnézzük a buffer tartalmát is, mert tanulságos:

        qDebug() << "A buffer: " << buffer.toHex();
    }

A kapott kimenet az alábbi:

    Text1:  "ABCD"
    Text2:  "EFG"
    A buffer:  "00000008004100420043004400000006004500460047"

A QString először elmenti a saját hosszát bájtban, 32 biten (00000008), utána az egyes karaktereket UTF-16 kódolással: A (0041), B (0042), C (0043), D (0044). Utána pedig jön a második QString.

<small>Szerzők, verziók: Csorba Kristóf</small>
