---
layout: default
---

# Kommunikáció V-REP-ben szimulált robottal

Rizsa a V-REP-ről.  

## Alapok

A V-REP működését nem részletezzük (mások megtették 
[itt](http://www.coppeliarobotics.com/helpFiles/en/welcome.htm)), 
csak a fontosabb dolgokat emeljük ki.

A V-REP szkriptnyelve a Lua. A szimuláció tulajdonképpen abból áll, 
hogy minden szimulációs lépésben meghívja a 
[main script](http://www.coppeliarobotics.com/helpFiles/en/mainScript.htm)-et, 
ebben történnek a szimulációs számítások. Ezt a script-et ne bántsuk. Saját kód 
futtatására használhatók a 
[child script](http://www.coppeliarobotics.com/helpFiles/en/childScripts.htm)-ek 
(amiket a main script hív meg). Ezek lehetnek "hagyományos" szkriptek, 
de külön szálon futó szkriptek is. 
TCP kommunikáció megvalósításához az utóbbi ajánlott.

## TCP server létrehozása Lua-ban

Valami bevezető szöveg ide.
írj a localhost-ról is.

Server socket nyitása, csatlakozás:
```lua
socket = require("socket")
server = socket.tcp()
localhost_ip = '127.0.0.1'
random_port_number = 25455  
server:bind(localhost_ip, random_port_number)
number_of_clients = 1
server:listen(number_of_clients)
client = server:accept()  -- waits until client connects
client:settimeout(0)
```
A socket-en adat küldése/fogasása
 a `send()`/`receive()` metódusokkal lehetséges:
```lua
command = client:receive('*l')  -- read a line
if(command == "GET") then
    data = string.format("some text with data: %f\n", some_float_data)
    client:send(data)  -- write a line
end
```
a `receive()` lehetséges paraméterei:
- `'*a'`: addig olvas amíg tud
- `'*l'`: egy sort olvas (az első `\n` karakterig)
- szám: adott számú byte-ot olvas
  
Az általunk használt kommunikációs protokoll szöveg alapú volt 
(kevésbé hatékony, de debuggoláskor nagyon hasznos), 
így minden parancsot és választ egy `'\n'` karakter zárt, 
emiatt sorokat írtunk/olvastunk. 

## Threading V-REP-ben

Az egyszerű child script-ek felépítésével itt nem foglalkozunk, csak a 
külön szálon futókéval. A külön száló futó kódot egy külön függvénybe írjuk:
```lua
threadFunction=function()
    while simGetSimulationState()~=sim_simulation_advancing_abouttostop do
        -- code that runs on separate thread
    end
end
```
A függvény addig pörög a while ciklusban, amíg a szimuláció 
nem szeretne megállni.


A függvény definíció után következik az inicializáló kód. 
Ez a mi esetünkben a  feljebb tárgyalt socket létrehozása és 
a csatlakozás.

Inicializálás után elindítjuk a feljebb definiált függvényünket külön szálon
az `xpcall()` hívással. Ez csak akkor tér vissza, ha a függvényünk 
visszatért, amiről az előbb megtudtuk, hogy a szimuláció leállításakor 
következik be. 
```lua
res, err = xpcall(threadFunction, function(err) return debug.traceback(err) end)
```

Utána jöhet a takarítás: a kapcsolat lezárása.
```lua
client:shutdown('both')
server:close()
```

Az összes eddigi tudást összerakva (egyéb extrákkal, azokról később) 
az egész child script egyben:

```lua
openSocket=function()
    socket = require("socket")
    server = socket.tcp()
    localhost_ip = '127.0.0.1'
    random_port_number = 25455  
    server:bind(localhost_ip, random_port_number)
    number_of_clients = 1
    server:listen(number_of_clients)
    client = command_server:accept()  -- waits until client connects
    client:settimeout(0)
end

threadFunction=function()
    while simGetSimulationState()~=sim_simulation_advancing_abouttostop do
        command = client:receive('*l')  -- read a line
        if(command == "GET") then
            data = string.format("some text with data: %f\n", num_data)
            client:send(data)  -- write a line
        end
    end
end

-- initialization
simSetThreadSwitchTiming(2) -- Default timing for automatic thread switching
simAddStatusbarMessage('Waiting for connection...')
simSetThreadIsFree(true)
customSocket()
simSetThreadIsFree(false)
simAddStatusbarMessage('Connection established...')

-- start thread
res, err = xpcall(threadFunction, function(err) return debug.traceback(err) end)
if not res then
    simAddStatusbarMessage('Lua runtime error: '..err)
end

-- clean-up
client:shutdown('both')
server:close()
simAddStatusbarMessage('Connections closed...')
```


## Szálak közötti kommunikáció

Ahhoz, hogy tudjuk a robotot vezérelni, illetve tőle adatot lekérdezni,
szükséges, hogy a TCP kommunikációt kezelő szál tudjon a többi szállal
is kommunikálni.

Lua elméleti háttér ide.

írás
```
simSetStringSignal("myLineData",simPackFloats(lineData))
```
olvasás
```
linePack=simGetStringSignal("myLineData")
``` 

### Szálak időzítése

ide kell majd a blocking dolog meg a simSwitchThread() meg hasonlók.

## TCP kapcsolat C++ oldalon

Miután elindítottuk a V-REP szimulációt (ahol a kommunikációs szál 
ekkor a `server.accept()` hívásnál várakozik) 
csatlakozhatunk a szerverhez. Ez Qt-ban a következőképp
néz ki:

```cpp
#include <QTcpSocket>  // requires QT += network in .pro file!!!

socket = QTcpSocket();
socket.connectToHost("127.0.0.1", 25455);
int timeout_ms = 100;
socket.waitForConnected(timeout_ms);
```

Ezután a socket írása olvasása már gyerekjáték:
```cpp
// write something
if(socket.state() == QAbstractSocket::ConnectedState)
{
    socket.write("GET\n");
}

// read the answer
if(socket.state() == QAbstractSocket::ConnectedState)
{
    QByteArray raw_data = socket.readLine(300);
    raw_string = QString(raw_data);
}
```

## Hibakezelés

csatlakozási sorrend
disconnect, stop sim, etc.

