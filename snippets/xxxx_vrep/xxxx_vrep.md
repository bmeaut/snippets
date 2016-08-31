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
---
layout: default
---

# Kommunikáció V-REP-ben szimulált robottal

A [V-REP](http://www.coppeliarobotics.com/) (**V**irtual **R**obot **E**xperimentation **P**latform)
egy oktatási célra ingyenesen elérhető robot szimulációs környezet. Tulajdonképpen
bármilyen robotot össze lehet rakni benne, a robot egyes részei külön szkriptekkel
vezérelhetők. Hasznos olyan csapatoknak, akik nem indulnak a RobonAUT-on, mert így is
"valós" robottal tesztelhetik és mutathatják be a házi feladatukat, nem kell még egy 
saját robot leprogramozásával is bajlódni.  

## Alapok

A V-REP működését nem részletezzük (mások megtették 
[itt](http://www.coppeliarobotics.com/helpFiles/en/welcome.htm)), 
csak a fontosabb dolgokat emeljük ki.

A V-REP szkriptnyelve a Lua. A szimuláció tulajdonképpen abból áll, 
hogy minden szimulációs lépésben meghívja a 
[main script](http://www.coppeliarobotics.com/helpFiles/en/mainScript.htm)-et, 
ebben történnek a szimulációs számítások. Ezt a script-et ne bántsuk. 

Saját kód futtatására használhatók a 
[child script](http://www.coppeliarobotics.com/helpFiles/en/childScripts.htm)-ek 
(amiket a main script hív meg). Ezek a robot moduljaihoz vannak rendelve,
lehetnek "hagyományos" szkriptek, de külön szálon futó szkriptek is. 
TCP kommunikáció megvalósításához az utóbbi ajánlott.

### Koncepció

A megoldás lépései vázlatosan:
1. robot összekattintgatása V-REP-ben
2. robot moduljait (pl vonalérzékelő, motorok) vezérlő Lua szkriptek megírása
3. TCP server létrehozása (szintén külön szkriptben)
4. kommunikácó a server és a modulok szkriptjei között
5. TCP client létrehozása (C++/Qt oldalon)
6. kommunikáció a TCP client és server, ezáltal a diagnosztika program és a robot között

## TCP server létrehozása Lua-ban

Ezt Lua-ban is a többi nyelvhez nagyon hasonlóan lehet megtenni. Amennyiben a szimuláció
és a diagnosztika program is ugyanazon a számítógépen fut, érdemes a localhoston keresztül 
kommunikálniuk. Akik merészebbek, azok LAN-on egy másik számítógépen szimulált robothoz 
is csatlakozhatnak.

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

## Threaded child script V-REP-ben

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
Ez ebben az esetben a feljebb tárgyalt socket létrehozása és 
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
    client = server:accept()  -- waits until client connects
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
openSocket()
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

A V-REP child script-jei között ez úgynevezett **signal**-okon keresztül lehetséges.
Alapvetően `int`, `float` és `string` signal-ok állnak rendelkezésre, ezek a nevüknek
megfelelő típusú változó továbbítására alkalmasak. Az összes elérhető függvény 
[itt](http://www.coppeliarobotics.com/helpFiles/en/apiFunctionListCategory.htm#signals) található.

### Példa:

A TCP szerver a klienstől megkapja a robot új sebesség alapjelét, ezt beírja a megfelelő
signal-ba:
```
simSetFloatSignal("robot_speed_setpoint", speed_from_client)
```
A robot sebességszabályzója egy másik szálon kiolvassa az új értéket:
```
new_speed = simGetFloatSignal("robot_speed_setpoint")
``` 
Ha íráskor a hivatkozott signal még nem létezik, akkor létrehozza. Olvasásnál
a `simWaitForSignal("signal_name")` fügvénnyel lehet addig várni, amíg a megadott signal
létre nem jön.

Több változó (pl. 10 darab vonalérzékeló) küldésére használható több signal is, 
mi a string-be pakolás, string-ként küldés majd visszaalakítás mellett döntöttünk. Ehhez külön 
[packing függvények](http://www.coppeliarobotics.com/helpFiles/en/apiFunctionListCategory.htm#packing) 
állnak rendelkezésre:
```lua
simSetStringSignal("line_sensor_data", simPackFloats(line_data))
...
line_data = simUnpackFloats(simGetStringSignal("line_sensor_data"))
```

## Szálak időzítése

Alapértelmezettként a szálak szimulációs lépésenként 2 ms futásidőt kapnak, 
utána a scheduler átadja a futási jogot egy másik szálnak. Ezen az időn a 
`simSetThreadSwitchTiming()` függvénnyel állíthatunk, 0-200 ms közötti időt 
megadva. Ez mindig arra a threaded child script-re vonatkozik, amelyikből 
meghívjuk, így minden scriptnél lehet különböző.

A `simSwitchThread()` függvénnyel explicit lemondhatunk a futásról. Amennyiben ezt 
200 ms-os futási idővel kombináljuk (maximális beállítható szimulációs mintavételi idő), 
úgy a szálunk szinkronizálva lesz a szimulációs lépésekkel.

BIZTOS??

Fontos megjegyezni, hogy a külön szálon futó child script-ek igazából
nem is futnak külön szálon. Ez kívülről azonban csak akkor látszik, amikor
valamelyik szál blokkoló hívást tartalmaz, ilyenkor ugyanis a V-REP nem tudja
elvenni tőle a futási jogot, és az egész program megfagy amíg a blokkoló utasítás
véget nem ér. Ilyen blokkoló utasítás például a `client:receive()`. Annak érdekében,
hogy ilyenkor más szálak is tudjanak futni, a hasonló hívásokat egy non-blocking
section-be kell rakni. Ezt a `simSetThreadIsFree()` fügvénnyel tehetjük meg:
```lua
simSetThreadIsFree(true)  -- start of non-blocking section
server:accept()           -- some blocking code
simSetThreadIsFree(false) -- end of non-blocking section
```
Erre láthattunk példát a TCP child script inicializáló részénél, ahol szintén a client csatlakozása 
volt a blokkoló hívás. Mivel ez másik programból (vagy másik számítógépről) történik
akár több percig is eltarthat, elég kellemetlen ha addig a V-REP nem reagál semmire.
Fontos hogy a non-blocking section-t amint lehet zárjuk le, különben szinkronizációs 
problémáink adóthatnak!

### Példák

kell egy példa sima szálra

kell egy példa 200ms+switchThread-re

## TCP kapcsolat C++ oldalon

Miután elindítottuk a V-REP szimulációt (ahol a kommunikációs szál 
ekkor a `server:accept()` hívásnál várakozik) 
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

## Lessons learned

- Mi a robot különböző egységeinek külön portokon külön kapcsolatokat nyitottunk, mégpedig
egy szkriptben. Így fontos volt, hogy C++-ban ugyanolyan sorrendben csatlakozzunk hozzájuk, 
mint ahogy Lua-ban megnyitottuk őket. Ellenkező esetben a Lua szkript az egyik csatlakozásnál
marad örökre, a C++ program pedig egy másik portra nem tud csatlakozni, mert az még nincs nyitva.
Ez természetesen kikerülhető a külön portok külön szálon indításával, vagy C++ oldalon
sikertelen csatlakozás esetén a még nem csatlakoztatott portokkal ciklikusan újrapróbálkozni.
- a V-REP bezárása előtt mindenképp állítsuk le a szimulációt, különben nem hívódik meg a 
clean-up kód, nem zárjuk le a portokat. Ez a szimuláció következő indításakor pánikot 
és sok fölösleges debuggolást okozhat.
- mi volt még?

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

