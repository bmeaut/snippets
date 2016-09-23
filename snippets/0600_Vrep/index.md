---
layout: default
codename: VRep
title: V-Rep kapcsolat C++ alkalmazásból
tags: alkfejl other
authors: Katona Máté
---

# Kommunikáció V-REP-ben szimulált robottal

A [V-REP](http://www.coppeliarobotics.com/) (**V**irtual **R**obot **E**xperimentation **P**latform)
egy oktatási célra ingyenesen elérhető platformfüggetlen robot szimulációs környezet. Tulajdonképpen
bármilyen robotot össze lehet rakni benne, de elérhető sok előre elkészített
robot/szenzor is, a robot egyes részei külön szkriptekkel vezérelhetők. 
Egy kis ügyeskedéssel elérhető, hogy egy valós robothoz hasonló 
módon a szimulált robottal TCP socketen keresztül lehessen kommunikálni.
Hasznos olyan csapatoknak, akik nem indulnak a RobonAUT-on, mert így is
"valós" robottal tesztelhetik és mutathatják be a házi feladatukat, nem kell még egy 
saját robot leprogramozásával is bajlódni, de akár RobonAUT-os csapatok
is használhatják kísérletezésre.

Készítettünk a snippet tartalmát minimalista stílusban, de egyben bemutató
[**minta projektet**](https://github.com/matekatona/vrep-sample).

## Alapok

A V-REP működését nem részletezzük (mások megtették 
[itt](http://www.coppeliarobotics.com/helpFiles/en/welcome.htm)), 
csak a fontosabb dolgokat emeljük ki.

A V-REP szkriptnyelve a Lua. A szimuláció tulajdonképpen abból áll, 
hogy minden szimulációs lépésben meghívja a 
[main script](http://www.coppeliarobotics.com/helpFiles/en/mainScript.htm)-et, 
ebben történnek a szimulációs számítások és sok egyéb varázslat. 
**Ezt a script-et ne bántsuk**. 

Saját kód futtatására használhatók a 
[child script](http://www.coppeliarobotics.com/helpFiles/en/childScripts.htm)-ek 
(amiket a main script hív meg). Ezek a robot moduljaihoz vannak rendelve,
lehetnek "hagyományos" szkriptek, de külön szálon futó szkriptek is. 
TCP kommunikáció megvalósításához az utóbbi ajánlott.

### Koncepció

A megoldás lépései vázlatosan:

1. robot összekattintgatása V-REP-ben
2. robot moduljait (pl. vonalérzékelő, motorok) vezérlő Lua szkriptek megírása
3. TCP szerver létrehozása (szintén külön szkriptben, külön szálon)
4. kommunikácó a szerver és a robot modulok szkriptjei között
5. TCP kliens létrehozása (C++/Qt oldalon)
6. kommunikáció a TCP szerver és kliens, ezáltal a robot és a diagnosztika program között

## TCP server létrehozása Lua-ban

Ezt Lua-ban is a többi nyelvhez nagyon hasonlóan lehet megtenni. Amennyiben a szimuláció
és a diagnosztika program is ugyanazon a számítógépen fut, érdemes a localhoston keresztül 
kommunikálniuk. Akik merészebbek, azok LAN-on egy másik számítógépen szimulált robothoz 
is csatlakozhatnak (részletes leírás [itt](http://w3.impa.br/~diego/software/luasocket/tcp.html)).

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

## Szálak közötti kommunikáció

Ahhoz, hogy tudjuk a robotot vezérelni, illetve tőle adatot lekérdezni,
szükséges, hogy a TCP kommunikációt kezelő szál tudjon a többi szkripttel
is kommunikálni.

A V-REP child script-jei között ez úgynevezett **signal**-okon keresztül lehetséges.
Alapvetően `int`, `float` és `string` signal-ok állnak rendelkezésre, ezek a nevüknek
megfelelő típusú változó továbbítására alkalmasak. Az összes elérhető függvény 
[itt](http://www.coppeliarobotics.com/helpFiles/en/apiFunctionListCategory.htm#signals) található.
A signal-okat egy string-gel lehet azonosítani, ezt íráskor és olvasáskor
is meg kell adni.

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

Több változó (pl. 10 darab vonalérzékelő) küldésére használható több signal is, 
mi a string-be pakolás, string-ként küldés majd visszaalakítás mellett döntöttünk. Ehhez külön 
[packing függvények](http://www.coppeliarobotics.com/helpFiles/en/apiFunctionListCategory.htm#packing) 
állnak rendelkezésre:

```lua
simSetStringSignal("line_sensor_data", simPackFloats(line_data))
...
line_data = simUnpackFloats(simGetStringSignal("line_sensor_data"))
```

## Threaded child script V-REP-ben

Az egyszerű child script-ek felépítésével itt nem foglalkozunk (arról
[itt](http://www.coppeliarobotics.com/helpFiles/en/childScripts.htm#nonThreaded)), 
csak a külön szálon futókéval. Ezek négy fő szekcióból állnak, melyeket
később részletezünk:

1. külön szálon futó kód egy függvényben
2. inicializáló kód
3. szál indítása
4. clean-up kód

### A script felépítése

A külön száló futó kódot egy külön függvénybe írjuk:

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
Ez ebben az esetben a feljebb tárgyalt socket inicializálása.
A csatlakozást érdemes már a szálként futó függvénybe rakni, így
nem fagy le a program ha mégsem csatlakoznak.

Inicializálás után elindítjuk a feljebb definiált függvényünket külön szálon
az `xpcall()` hívással (így a szálban bekövetkező hiba esetén is rendes
stacktrace-t kapunk hibaüzenetként). Ez csak akkor tér vissza, ha a függvényünk 
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
    client:settimeout(1)
end

threadFunction=function()
    while simGetSimulationState()~=sim_simulation_advancing_abouttostop do
        simAddStatusbarMessage('Waiting for connection...')
        while (not client) and (simGetSimulationState()~=sim_simulation_advancing_abouttostop) do
            simSetThreadIsFree(true)
            client = server:accept()  -- waits until client connects with 1 sec timeout
            simSetThreadIsFree(false)
            simSwitchThread()  -- read on this later
        end
        if(client) then
            simAddStatusbarMessage('Connection established...')
            client:settimeout(0)
            while simGetSimulationState()~=sim_simulation_advancing_abouttostop do
                some_variable = simGetFloatSignal('some_signal_name')
                some_data = string.format("some data: %.2f\n", some_variable)
                client:send(some_data)  -- write a line
            end
        end
    end
end

-- initialization
simSetThreadSwitchTiming(2) -- Default timing for automatic thread switching
openSocket()

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

## Szálak időzítése

Fontos megjegyezni, hogy a külön szálon futó 
child script-ek igazából nem is futnak külön szálon, csak a V-REP futtatja
őket időosztásban. Jól megírt kód esetében azonban ez a felhasználó
számára transzparens, így továbbra is külön szálon futóként hivatkozunk rá.

Minden threaded child script-hez hozzá van rendelve egy futási idő 
(alapértelmezettként 2 ms), minden szimulációs lépésben ennyi ideig fut, 
majd a V-REP átvált egy másik szkriptre. Ezen az időn a 
`simSetThreadSwitchTiming()` függvénnyel állíthatunk, 1-200 ms közötti időt 
megadva. Ez mindig arra a threaded child script-re vonatkozik, amelyikből 
meghívjuk, így minden scriptnél lehet különböző.

A `simSwitchThread()` függvénnyel explicit lemondhatunk a futásról. Ez 
akkor hasznos, ha bizonyos körülmények között nincs rá szükség, hogy az
adott szimulációs lépésben tovább fusson a szál.

Ha a futásidőt 200 ms-ra (max) állítjuk, és a while ciklus végén
meghívjuk a `simSwitchThread()` függvényt, ráadásul egy ciklus lefut 200 ms alatt, 
akkor a szál futása szinkronizálva lesz a szimuláció lépéseivel, és minden 
lépésben egyszer fog lefutni.


Az is külön figyelmet igényel, ha valamelyik szál blokkoló hívást 
tartalmaz, ilyenkor ugyanis a V-REP nem tudja elvenni tőle a 
futási jogot, és az egész program megfagy amíg a blokkoló utasítás
véget nem ér. Ilyen blokkoló utasítás például a `client:receive()`. Annak érdekében,
hogy ilyenkor más szálak is tudjanak futni, a hasonló hívásokat egy non-blocking
section-be kell rakni. Ezt a `simSetThreadIsFree()` fügvénnyel tehetjük meg:

```lua
simSetThreadIsFree(true)  -- start of non-blocking section
server:accept()           -- some blocking code
simSetThreadIsFree(false) -- end of non-blocking section
```

Mivel a csatlakozés másik programból (vagy másik számítógépről) történik
akár több percig is eltarthat, elég kellemetlen ha addig a V-REP nem reagál semmire.
Fontos hogy a non-blocking section-t amint lehet zárjuk le, különben szinkronizációs 
problémáink adóthatnak!

### Példa szimulációval szinkronizált szálra

Erre kézenfekvő példa a robot állapotát a diagnosztika kliensnek küldő szál.
Mivel a robotot leíró változók leggyakrabban szimulációs lépésenként változhatnak,
nem érdemes őket gyakrabban küldeni (főleg nem pár ms alatt többször).

Ekkor a child script fontos elemei:

```lua
...
threadFunction=function()
    while simGetSimulationState()~=sim_simulation_advancing_abouttostop do
        client.send(robot_status)
        simSwitchThread()
    end
end
...
-- init code
simSetThreadSwitchTiming(200)
...
```

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
Ez természetesen kikerülhető a külön portok külön szálon indításával, vagy 
sikertelen csatlakozás esetén a még nem csatlakoztatott portokkal ciklikusan újrapróbálkozni.
- a V-REP bezárása előtt mindenképp állítsuk le a szimulációt, különben nem hívódik meg a 
clean-up kód, nem zárjuk le a portokat. Ez a szimuláció következő indításakor pánikot 
és sok fölösleges debuggolást okozhat.
- Mivel a V-REP az egész [scene](http://www.coppeliarobotics.com/helpFiles/en/scenes.htm)-t
egy bináris file-ban tárolja, a Lua szkripteken eszközölt változások nem
követhetők git-ben. Érdemes azokat pl. egy almappába időnként kimenteni, így
használható a diff.
