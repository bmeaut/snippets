---
layout: default
---

# V-REP

V-REP robot vezérlése TCP socketen keresztül. 

## Alapok

lua, main script, child script, threading, blocking

## TCP socket V-REP-ben

socket nyitása:
```lua
socket = require("socket")
server = socket.tcp()
server:bind('127.0.0.1', 25455)
server:listen(1)
client = command_server:accept()
client:settimeout(0)
```
socket olvasása/írása:
```lua
command = client:receive('*l')  -- read a line
if(command == "GET") then   
    data = string.format("%f %f\n", lineData[1], lineData[2])
    client:send(data)  -- write the line
end
```
## Threading V-REP-ben
<http://www.coppeliarobotics.com/helpFiles/en/childScripts.htm#threaded>

```lua
threadFunction=function()
    while simGetSimulationState()~=sim_simulation_advancing_abouttostop do
        -- NO INIT CODE
        -- communication between threads
        -- communication over TCP socket
        simSwitchThread()  -- wait for next sim step
        -- NO CLEANUP CODE
    end
end

-- initialization code
simSetThreadSwitchTiming(200) -- suggested timing for sim sync thread exec
simAddStatusbarMessage('Waiting for connection...')
simSetThreadIsFree(true)  -- non blocking start
customSocket()  -- socket stuff
simSetThreadIsFree(false)  -- non blocking end
simAddStatusbarMessage('Connection established...')

-- start thread
res,err = xpcall(threadFunction, function(err) return debug.traceback(err) end)
if not res then
    simAddStatusbarMessage('Lua runtime error: '..err)
end

-- clean-up code
client:shutdown('both')
server:close()
simAddStatusbarMessage('Connections closed...')
```
szálak közötti kommunikáció - írás:
```
simSetStringSignal("myLineData",simPackFloats(lineData))
```
szálak közötti kommunikáció - olvasás:
```
linePack=simGetStringSignal("myLineData")
``` 

## TCP kapcsolat CPP oldalon

ez lehet nem is kell mer tananyag

## Hibakezelés

csatlakozási sorrend
disconnect, stop sim, etc.

