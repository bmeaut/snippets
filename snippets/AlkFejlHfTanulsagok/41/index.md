---
layout: default
codename: Mesterharmas
title: Mesterhármas tapasztalatok, WebSocket
tags: alkfejl git
authors: Törcsvári Zsombor, Antal Márton, Kondákor András
---

# Bevezetés

Első körben szeretnénk ismertetni, hogy házifeladatunk megoldásához milyen technológiákat használtunk, amik nagy mértékben megkönnyítették a programjaink megírását. Ezek a következők voltak: Websocket, JSON, és JavaScript használta a szimulátorhoz.

# Websocket

Kommunikációra magasabb nyelven írt applikációkban érdemes lehet a websocket használta. Használata nagyon egyszerű, valós idejű alkalmazásoknál nagyon gyakran használják.

## Mi is a Websocket

Egy kétirányú kommunikációs csatorna ami duplex kommunikációt valósít meg, TCP-re épül. A kiépítéséhez egy HTTP kommunikációra van szükség, ahol a két fél megegyezik arról, hogy „felfejlesztik” a kommunikációt innentől WebSocketre. Innentől már csak TCP fölött kommunikának, amit nagyon kis overheaddel tud a szerver és a kliens megvalósítani. Nagy előnye a HTTP-vel szemben, hogy a két félnek nem kell folyton pollingolnia egymást, hanem ha van adat azt egyből tudják küldeni a másik fél részére. Mivel HTTP-n indul a kommunikáció, így egy HTTP-s webszerveren könnyedén megvalósítható ez a módszer. A kis overhead, és a pusholt adatok miatt valós idejű komminkációk megvalósításához nagyon elterjedt technológia.

#JSON (JavaScript Object Notation):

Adatok átviteléhez érdemes az üzeneteket valamilyen struktúrába becsomagolni. Erre az egyik legegyszerűbb lehetőség a JSON használta. 

Ember által is olvasható, kisméretű szabvány, ami összesen 6 féle adattípust használ: szám, szöveg, boolean, null, objektum és tömb. Ezekkel általában mindent le lehet írni, akár több szintű struktúrákat is. Napjainkban nagyon elterjedt, szinte mindenhol ezt használnak adatcserére, ahol nem szükséges bináris adatátvitel, vagy nem probléma a szerializálás számításigényessége.

Az XML-hez képest sokkal kisebb a mérete, sokkal kevesebb memóriát igényel és egyszerűbb a szerializálása, egyetlen hátránya, hogy nem lehet benne kommentet használni.


# JavaScript

Alapból a QML is használ JavaScriptet ezért a megismerése ebből a szempontból is előnyös a félév során. Ugyan interpreteres és gyengén típusos nyelv, de ezzel körülbelül minden negatívumát elmondtuk. Természetesen a sebessége sem egyezik meg egy hasonló C++-os kódéval, de nem is olyan helyeken kell használni, ahol arra kell kiélezni az alkalmazást.
A megismerését megkönnyíti, hogy szintakszisa nagyon hasonló a C++-hoz.

Könnyen lehet vele egyszerű programokat összerakni. Ilyen volt a mi esetünkben is a szimulátor, ami csak tárol pár állapotot, és a kapott üzenetekre megváltoztatja azokat, és visszakommunikál.

Sok programkönyvtár található hozzá, például a korábban ismertetett Websocket, és a gyakran használatos műveletek JSON-ökkel már implementálva vannak benne. Ezen felül HTTP szervert, TCP klienst és szervert is könnyen lehet vele megvalósítani.

# Websocket használata QT-ben, QML-ben és JavaScriptben JSON adatcsomagokra:

QML-ben is van implementációja (import QtWebSockets 1.0) mind a Websocket szervernek, mind a kliensnek.

## QML:

    WebSocket {
            id: socket
            url: "ws://localhost:8080"
            onTextMessageReceived: {
                console.log("Recieved message: " + message)
                var jsonmsg = JSON.parse(message) 
            }
            onStatusChanged: if (socket.status == WebSocket.Error) {
                                 console.log("Error: " + socket.errorString)
                             } else if (socket.status == WebSocket.Open) {
                                 console.log("opened")
                             } else if (socket.status == WebSocket.Closed) {
                                 messageBox.text += "\nSocket closed"
                             }
            active: true
        }

Az 1. Sorban létrehozzuk a Websocket klienst, a 3. sorban megadjuk, hogy hova csatlakozzon fel. A 4. sorban feliratkozunk arra az eseményre ha üzenet érkezik. Az üzenetet a ’message’ változóban találjuk szöveg formátumban, amit egyből ki is írathatunk a konzolra.
Ha JSON üzeneteket használunk, akkor a var jsonmsg = JSON.parse(message) -el már szét is parseolhatjuk, és ki lehet olvasni belőle a változók értékeit.

Az onStatusChanged arra szolgál, hogy lekezeljük hogy a kommunikációs csatornánkkal mi történik.

## QT-ban ugyanez a kód:

Ahhoz hogy használni tudjuk be kell importálni a QtWebSockets/QWebSocket -et.
Létre kell hozni egy példányt belőle: 

    QWebSocket m_webSocket;

majd:

    connect(&m_webSocket, &QWebSocket::connected, this, &WebSocketClient::onConnected);
    connect(&m_webSocket, &QWebSocket::textMessageReceived,
    this, &WebSocketClient::onTextMessageReceived);

Az első sorral lehet beállítani, hogy a Websocket csatlakozásakor melyik függvény fusson le, a másodikkal, hogy amikor üzenet jön, akkor melyik.

    m_webSocket.open(QUrl(url));

Így lehet felcsatalkozni egy url-re.

    void WebSocketClient::onTextMessageReceived(QString message)
    {
        if (m_debug)
            qDebug() << "Message received:" << message;
    
        QJsonObject obj;
        QJsonDocument doc = QJsonDocument::fromJson(message.toUtf8());
    }

Ez pedig az onTextMessageReceived függvény fogadása, ami szintén kiíratja a kapott üzenetet és parseolja a JSON-t. Innen már az üzenetnek megfelelően lehet az alkalmazásunkat elágaztatni.

Üzenet kültésére használható függvény:

    m_webSocket.sendTextMessage(„Hello”);

## JavaScriptben egy Websocket szerver készítése:

    var WebSocketServer = require('websocket').server;
    var http = require('http');
    
    var server = http.createServer(function(request, response) {
        console.log((new Date()) + ' Received request for ' + request.url);
        response.writeHead(404);
        response.end();
    });
    server.listen(8080, function() {
        console.log((new Date()) + ' Server is listening on port 8080');
    });
    
    wsServer = new WebSocketServer({
        httpServer: server,
        autoAcceptConnections: true
    });
    
        console.log((new Date()) + ' Connection accepted.');
    
    connection.on('message', function(message) {
        if (message.type === 'utf8') {
            console.log('Received Message: ' + message.utf8Data);
            try {
                var jsonMessage = JSON.parse(message.utf8Data);
                connection.send(JSON.stringify({message: jsonMessage["message"]}));
            }
            catch (e) {
                console.error(e);
            }
        }
    }


Ez a kód létrehoz egy http szervert, ami a Websocket szerver alapja. Utána erre létrehozza a Websocket szervert, ami annyit csinál, hogy egy JSON objektumban kapott „message” kulccsal tárolt szöveget belerak egy JSON objektumnak szintén a „message” tagjába, és visszaküldi.


## További információk

  * [QML WebSocket](https://doc.qt.io/qt-5/qml-qtwebsockets-websocket.html)
  * [QT QWebSocket](https://doc.qt.io/qt-5/qwebsocket.html)
  * [NodeJS Websocket tutorial](https://medium.com/@martin.sikora/node-js-websocket-simple-chat-tutorial-2def3a841b61)
