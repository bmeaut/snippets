---
layout: default
codename: OpencodeChatbot
title: Ügyfélszolgálati chatbot Kubernetesbe deployolt Opencode pod-okkal
tags: snippets mieset opencode kubernetes claude-code chatbot
authors: Barkóczi Alexandra
---

# MI esettanulmány – Ügyfélszolgálati chatbot Kubernetesbe deployolt Opencode pod-okkal

## Cél

A feladat egy olyan ügyfélszolgálati chatbot kialakítása volt, amely nem egy klasszikus alkalmazásba beágyazva fut, hanem önálló, Kubernetesben futó szolgáltatásként, amelyet tetszőleges kliens API hívásokkal kérdezhet. Az ötlet az volt, hogy az **Opencode**-ot (egy nyílt forráskódú AI kódoló ágenst, amely server módban HTTP API-n keresztül is elérhető) magát futtatom egy podban, és ehhez a podhoz intézek kérdéseket, mintha egy ügyfélszolgálati végpont lenne. A fejlesztéshez (a Kubernetes manifesztek, Dockerfile-ok és a deploy folyamat megírásához) a **Claude Code**-ot használtam.

A munka két lépésben zajlott:

1. Először egy "csupasz" Opencode pod deployolása volt a cél Kubernetesbe, amit API hívásokkal, kérdésekkel lehet hívogatni, és a pod (a mögé kötött LLM-en keresztül) válaszol.
2. Ezután a podot egy konkrét projekt dokumentációjára "betanítottam" (valójában a dokumentációt a pod kontextusába/tudásbázisába injektáltam), hogy az valóban egy adott termék ügyfélszolgálataként tudjon viselkedni, konkrét, dokumentált válaszokkal.

## Technológia

* Kubernetes klaszter (helyi, kind/minikube alapú teszt-klaszter)
* Opencode, server módban futtatva egy konténeren belül, HTTP API-t kitéve
* Docker image az Opencode-hoz, saját Dockerfile-lal
* Kubernetes `Deployment` + `Service` (később `Ingress`) a pod eléréséhez
* Fejlesztői eszköz: Claude Code, terminálban, agent módban, a manifesztek és a Dockerfile megírásához, valamint a hibák diagnosztizálásához
* Második fázisban: a projekt dokumentációja (Markdown fájlok) `ConfigMap`/`PersistentVolume` formájában mountolva a podba, amit az Opencode kontextusként tud használni válaszadáskor

## Tanulságok

* A Claude Code jól kezelte a Kubernetes YAML-ok írását, de az első próbálkozásnál olyan `resources` limiteket állított be a pod-nak, amivel az folyamatosan `OOMKilled` állapotba került – ezt csak a `kubectl describe pod` kimenete alapján sikerült felismerni és a memórialimitet megemelni.
* A pod service módban indított Opencode-jának hitelesítését (API kulcs, amivel a külső hívó azonosítja magát) kezdetben elfelejtette bekötni, így a pod nyíltan, hitelesítés nélkül volt elérhető a klaszteren belül – ezt külön kellett kérnem, hogy javítsa.
* A health check (`livenessProbe`/`readinessProbe`) beállítása elsőre túl szigorú időzítéssel készült, ami miatt a pod folyamatosan újraindult, mielőtt az Opencode szerver egyáltalán elindult volna – ez is csak a pod eseménynaplója (`kubectl describe pod` / `kubectl logs --previous`) alapján derült ki.
* A dokumentációval való "betanítás" valójában nem finomhangolás, hanem kontextusba/tudásbázisba töltés volt – ezt a fogalmi különbséget érdemes volt tisztázni már a tervezés elején, mert az első promptomban még "fine-tune"-ról beszéltem, és a Claude Code emiatt egy jóval bonyolultabb, felesleges irányba indult volna el.
* Miután a dokumentáció be volt kötve, a pod válaszai érdemben pontosabbak és a konkrét projektre szabottak lettek, viszont a dokumentáció frissítésekor a podot újra kellett indítani (vagy a ConfigMapet újratölteni), ez a szinkronizáció nem volt automatikus.

## A munkafolyamat tanulságos részletei

### Az első, csupasz Opencode pod

Az első promptban egy egyszerű, kérdezhető Opencode szolgáltatást kértem Kubernetesbe:

```
Szeretnék egy Opencode-ot futtatni server módban egy Kubernetes podban, amit utána API hívásokkal
tudok kérdezni (kérdés be, válasz ki, mint egy chat végpont). Készíts hozzá Dockerfile-t, Deployment
és Service YAML-t, és mutasd meg, hogyan tudom localhoston keresztül elérni port-forward-dal.
```

A Claude Code elkészítette a Dockerfile-t (Opencode telepítéssel és a server mód indításával), egy alap `Deployment` és `Service` manifesztet, valamint egy `kubectl port-forward` alapú tesztelési útmutatót. Az első futtatásnál viszont a pod folyamatosan újraindult:

```
A pod folyamatosan CrashLoopBackOff állapotba kerül. A kubectl describe pod szerint az OOMKilled
üzenet jelenik meg, a memory limit 128Mi-ra van állítva.
```

A Claude Code erre helyesen ismerte fel, hogy az Opencode szervernek ennél jóval több memória kell, és a limitet megemelte, illetve javasolt egy `requests`/`limits` párost is, hogy a pod ütemezése is reálisabb legyen.

### Hitelesítés hiánya

Amikor sikerült elérni a podot port-forwarddal, észrevettem, hogy bármilyen hívó, hitelesítés nélkül tud kérdéseket feltenni neki:

```
A Service jelenleg bárkinek elérhető a klaszteren belül, hitelesítés nélkül tud kérdéseket küldeni
neki bárki, aki eléri a namespace-t. Szeretnék egy egyszerű API kulcs alapú hitelesítést bevezetni,
amit a hívónak egy header-ben kell elküldenie.
```

A Claude Code egy Kubernetes `Secret`-be helyezte az API kulcsot, majd a konténer indító scriptjét kiegészítette úgy, hogy az Opencode server elé egy vékony proxy réteget tett, ami a header alapján engedi vagy tiltja a kérést. Ez működött, viszont ez is jó példa volt arra, hogy egy alapból nem biztonságos konfigurációt (nyitott, hitelesítés nélküli API végpont) csak explicit kérésre javított ki, magától nem jelezte kockázatként a kezdeti válaszban.

### Kérdezgetés API hívásokkal

A pod felállása után egyszerű `curl` és egy kis Python kliens scripttel teszteltem, hogy a végpont valóban értelmes válaszokat ad-e általános kérdésekre:

```bash
curl -X POST http://localhost:8080/api/ask \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hogyan tudom visszaküldeni a terméket, ha nem tetszik?"}'
```

Ebben a fázisban a pod válaszai még általánosak és a mögöttes LLM "saját tudásából" származtak, semmilyen projektspecifikus információ nem volt bennük – ez volt az alap, amire a második fázisban ráépítettem a dokumentáció-alapú kontextust.

### A pod "betanítása" a projekt dokumentációjára

A második fázisban a cél az volt, hogy a pod egy konkrét projekt dokumentációja alapján tudjon válaszolni, valódi ügyfélszolgálatként:

```
Szeretném, hogy a podban futó Opencode a válaszaihoz a mellékelt projekt dokumentációt (markdown
fájlok egy mappában) használja forrásként, ne csak az általános tudását. Ez nem finomhangolás,
hanem azt szeretném, hogy a dokumentáció tartalma mindig elérhető legyen a válaszadáskor kontextusként.
Hogyan tudom ezt a legegyszerűbben megoldani a jelenlegi Kubernetes felépítésben?
```

A Claude Code tisztázta a fogalmi különbséget (finomhangolás vs. kontextusba töltés/RAG), és egy egyszerűbb megoldást javasolt első lépésként: a dokumentációt egy `ConfigMap`-be (később, a dokumentáció méretének növekedésével egy `PersistentVolume`-ba) töltve mountolta a podba, és az Opencode indító konfigurációját kiegészítette úgy, hogy a mountolt mappát tudásforrásként adja meg a válaszgeneráláshoz.

Ezt követően a korábbi teszt-kérdésre adott válasz már konkrét, a dokumentációból származó adatokat tartalmazott (pl. a tényleges visszaküldési határidőt és a visszaküldési űrlap elérési útját), nem csak egy általános, kitalált választ.

### Dokumentáció frissítésének szinkronizációja

```
Ha frissítem a dokumentációs mappa tartalmát, a podban futó Opencode nem veszi észre a változást,
amíg újra nem indul. Meg tudod oldani, hogy a dokumentáció frissítésekor automatikusan újratöltse
a tudásforrást, pod-újraindítás nélkül?
```

Erre a Claude Code egy egyszerű fájlrendszer-figyelő (watcher) megoldást épített be az induló scriptbe, ami a mountolt mappa változásait figyelve újratölti a kontextust. Ez működött teszt közben, viszont production-szerű használatra (pl. sok egyidejű kérés mellett történő újratöltés esetére) alaposabb tesztelést igényelt volna, amire ebben a fázisban már nem volt szükség.

## Összefoglalás

A legnagyobb tanulság az volt, hogy Kubernetesbe deployolt AI-szolgáltatás esetén a klasszikus üzemeltetési problémák (memórialimit, health check időzítés, hitelesítés) ugyanúgy jelentkeznek, mint bármely más konténerizált szolgáltatásnál, és ezekre a Claude Code csak a tényleges hibaüzenetek (pod leírás, logok) alapján tudott érdemben reagálni – önmagában a kezdeti kérésből nem jósolta meg ezeket a problémákat. A második fázis rávilágított arra is, hogy a "betanítás" fogalmát érdemes pontosan definiálni a modell felé: amint tisztáztam, hogy nem finomhangolásra, hanem kontextusba töltött dokumentációra gondolok, sokkal egyszerűbb és gyorsabban működő megoldást kaptam, mintha hagytam volna, hogy a modell egy bonyolultabb, felesleges irányba induljon el.
