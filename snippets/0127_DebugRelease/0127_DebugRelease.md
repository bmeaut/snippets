---
layout: default
---

# Debug és release módú fordítás

Ha egy program futásának sebességét akarjuk megmérni, mindig fontos, hogy release módban fordítsuk le a programot és ne debug módban. A következőkben megmutatom, miért.

Visual Studio alatt egy program lefordított verzióját könnyen meg lehet nézni: le kell rakni egy töréspontot, majd amikor ott megáll a debuggolás közben, akkor a Debug/Windows/Disassembly (Alt + 8) menüpontot választva megnézhetjük minden egyes C++ forráskód sorhoz, hogy mire fordult le.
   
## Az első próbálkozás

Először az alábbi programmal próbálkoztam, mondván, hogy ez már tartalmaz annyi műveletet, hogy lássunk is valamit.

```C++
#include <iostream>

using namespace std;

int main()
{
    int sum = 0;
    for (int i = 0; i<10; i++)
    {
        sum += i;
    }
    cout << "sum: " << sum << endl;
    return 0;
}
```

No ez nem jött be. Release módban a fordító az egész for ciklus eredményét (45, vagyis 0x2D) kiszámolta előre és az eredményt beleírta a lefordított kódba:

```C++
int sum = 0;
for (int i = 0; i<10; i++)
{
    sum += i;
}
cout << "sum: " << sum << endl;
```

```Cpp-ObjDump
001412A0  mov         ecx,dword ptr ds:[143054h]  
001412A6  push        141980h  
001412AB  push        2Dh  
001412AD  call        std::operator<<<std::char_traits<char> > (0141760h)  
001412B2  mov         ecx,eax  
001412B4  call        dword ptr ds:[143034h]  
001412BA  mov         ecx,eax  
001412BC  call        dword ptr ds:[14305Ch]  
    return 0;
001412C2  xor         eax,eax  
}
001412C4  ret
```

Ennél szemmel láthatóan bonyolultabb dolgot kell számoltatni. (De emellett azért vegyük észre, hogy ez nem kis eredmény a fordítótól, még ha manapság ezt már el is várjuk.)

## A magic

No akkor tegyünk bele egy magic függvényt, amit nem tud ilyen könnyen kiszámolni. Szinusz táblája már csak nincsen:

```C++
#include <iostream>

using namespace std;

int magic(int x)
{
    return 10.0F * sin(x);
}

int main()
{
    int sum = 0;
    for (int i = 0; i<10; i++)
    {
        sum += magic(i);
    }
    cout << "sum: " << sum << endl;
    return 0;
}
```

Kezdjük a debug fordítással. Ennek eredménye a következő:

```Cpp-ObjDump
int main()
{
00DE5640  push        ebp  
00DE5641  mov         ebp,esp  
00DE5643  sub         esp,0D8h  
00DE5649  push        ebx  
00DE564A  push        esi  
00DE564B  push        edi  
00DE564C  lea         edi,[ebp-0D8h]  
00DE5652  mov         ecx,36h  
00DE5657  mov         eax,0CCCCCCCCh  
00DE565C  rep stos    dword ptr es:[edi]  
    int sum = 0;
00DE565E  mov         dword ptr [sum],0  
    for (int i = 0; i<10; i++)
00DE5665  mov         dword ptr [ebp-14h],0  
00DE566C  jmp         main+37h (0DE5677h)  
00DE566E  mov         eax,dword ptr [ebp-14h]  
00DE5671  add         eax,1  
00DE5674  mov         dword ptr [ebp-14h],eax  
00DE5677  cmp         dword ptr [ebp-14h],0Ah  
00DE567B  jge         main+51h (0DE5691h)  
    {
        sum += magic(i);
00DE567D  mov         eax,dword ptr [ebp-14h]  
00DE5680  push        eax  
00DE5681  call        magic (0DE14A6h)  
00DE5686  add         esp,4  
00DE5689  add         eax,dword ptr [sum]  
00DE568C  mov         dword ptr [sum],eax  
    }
00DE568F  jmp         main+2Eh (0DE566Eh)  
    cout << "sum: " << sum << endl;
...
```

A cout utáni részeket már levágtam, mert nem az a lényeg. Ezután pedig a release fordítás eredménye:

```Cpp-ObjDump
int main()
{
003712A0  push        esi  
003712A1  push        edi  
    int sum = 0;
003712A2  xor         edi,edi  
    for (int i = 0; i<10; i++)
003712A4  xor         esi,esi  
003712A6  jmp         main+10h (03712B0h)  
003712A8  lea         esp,[esp]  
003712AF  nop  
003712B0  movd        xmm0,esi  
    {
        sum += magic(i);
003712B4  cvtdq2pd    xmm0,xmm0  
003712B8  call        __libm_sse2_sin_precise (0372346h)  
003712BD  mulsd       xmm0,mmword ptr ds:[373260h]  
    for (int i = 0; i<10; i++)
003712C5  inc         esi  
    {
        sum += magic(i);
003712C6  cvttsd2si   eax,xmm0  
003712CA  add         edi,eax  
003712CC  cmp         esi,0Ah  
003712CF  jl          main+10h (03712B0h)  
    }
    cout << "sum: " << sum << endl;
...
```

Láthatjuk, hogy a debug fordítás sokkal több pakolgatást, másolgatást tartalmaz. Például a ciklusmagban minden iterációban a memóriából betölti i értékét (ő a "dword ptr [ebp-14h]"), leraja a stackre, mint a magic függvény paramétere, utána meghívja a függvényt és még a sum értékét is kiírja a memóriába. Ennek az az oka, hogy debuggolás közben minden részeredmény a memóriában legyen és minden soron meg tudjuk állni. Release módban egy csomó forráskód sorhoz nincs is natív kód, így ha ott próbálunk meg soronként ugrálni (vagyis a debuggert megkérni, hogy a következő sornak megfelelő gépi kódú parancsig fusson), akkor kisse össze-vissza fog ugrálni.

## Hibaellenőrző kódrészek

Befejezésül még kíváncsiságból megnéztem, milyen a magic függvény. Ez a memóriában egy kicsit előrébb helyezkedik el, cseles módon a "call magic (0DE14A6h)" által hivatkozott címen csak egy ugrás van a függvény tényleges helyére.

```Cpp-ObjDump
int magic(int x)
{
00DE42F0  push        ebp  
00DE42F1  mov         ebp,esp  
00DE42F3  sub         esp,0C8h  
00DE42F9  push        ebx  
00DE42FA  push        esi  
00DE42FB  push        edi  
00DE42FC  lea         edi,[ebp-0C8h]  
00DE4302  mov         ecx,32h  
00DE4307  mov         eax,0CCCCCCCCh  
00DE430C  rep stos    dword ptr es:[edi]  
    return 10.0F * sin(x);
00DE430E  mov         eax,dword ptr [x]  
00DE4311  push        eax  
00DE4312  call        sin<int> (0DE14A1h)  
00DE4317  add         esp,4  
00DE431A  fstp        qword ptr [ebp-0C8h]  
00DE4320  movsd       xmm0,mmword ptr [ebp-0C8h]  
00DE4328  mulsd       xmm0,mmword ptr ds:[0DEC9B8h]  
00DE4330  cvttsd2si   eax,xmm0  
}
00DE4334  pop         edi  
00DE4335  pop         esi  
00DE4336  pop         ebx  
00DE4337  add         esp,0C8h  
00DE433D  cmp         ebp,esp  
00DE433F  call        __RTC_CheckEsp (0DE132Fh)  
00DE4344  mov         esp,ebp  
00DE4346  pop         ebp  
00DE4347  ret
```

A release mód nem is használ függvényhívást, csak a szinusz kiszámításához. Ehhez képest itt meg egy csomó push-pop páros van, a szokásos memória másolások, valamint egy érdekes ellenőrzés:

```Cpp-ObjDump
00DE42F0  push        ebp  
00DE42F1  mov         ebp,esp  
...
00DE433D  cmp         ebp,esp  
00DE433F  call        __RTC_CheckEsp (0DE132Fh)  
00DE4344  mov         esp,ebp  
00DE4346  pop         ebp  
```

A függvény elején elmenti a bázispointerbe (EBP) a stack pointert (ESP) (amihez a legelején az EBP értékét a stackre elmenti, a levégén meg visszaolvassa), a függvény befejezése előtt pedig van egy ellenőrzés, hogy a stack pointer tényleg oda állt-e vissza, ahol a függvény elején volt. Ha nem, akkor meghívja az RTC_CheckEsp függvényt, ami valószínűleg a hiba jelzésére szolgál.

A konklúzió tehát az, hogy debug módban azért nem mérünk futási időt, mert rengeteg olyan műveletet tartalmaz, ami az éles futáshoz egyáltalán nem kell. Ráadásul debug módban a fordító összes optimalizáló funkciója is ki van kapcsolva.

Végezetül megjegyzem, hogy egyszer a Point Cloud Library használata során tapasztaltuk, hogy a debug és release módú fordítás és futtatás között szó szerint 1000-szeres sebességkülönbség volt! Mivel a program 17 millió (lézerszkennerrel felvett) pontot elemezgetett, nyilván nagyon nem volt mindegy, hogy a ciklusokban mennyi többletfeladat van.

<small>Szerzők, verziók: Csorba Kristóf</small>
