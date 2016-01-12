---
layout: default
---

# GIT és authentikáció

A GIT SSH kulcs alapú authentikációt használ. Amikor egy titkosított SSH kapcsolat felépül, a két oldal az RSA algoritmus segítségével, nyilvános kulcsú titkosítással azonosítja egymást. Az esetek nagy részében ezt a lépést csak arra használják, hogy a kliens oldal meggyőződjön a szerver oldal identitásáról (tanúsítványok ellenőrzése). Viszont ha a szerver oldal valahonnan tudja, hogy a kliensnek (felhasználónak) mi az SSH nyilvános kulcsa, akkor ezt fel lehet használni authentikációra is: ha az üzeneteidet vissza tudom fejteni a te nyilvános kulcsoddal, akkor az azt jelenti, hogy a te titkos kulcsoddal titkosították őket.

Ezért a GIT bár olykor képes felhasználói név és jelszó alapú authentikációra is (pl. TFS szerver esetén), de a szokásos módszer az SSH kulcs alapú. Ilyenkor az admin a GIT szervernek megadja a felhasználók SSH nyilvános kulcsait (ezeket tipikusa a felhasználók generálják le). Ha pedig a felhasználó szeretne csatlakozni, akkor csak megmondja a GIT kliensnek, hogy ezt a kulcspárt használja, és amint elkezdődik a kapcsolat felépítése, a szerver már tudni is fogja, hogy kivel beszél.

Ez a fajta authentikáció általában nagyon kényelmes, mivel csak egyszer kell megadni a kliensnek az SSH titkos kulcsot tartalmazó fájl helyét, utána teljesen transzparens az authentikáció.

Ilyenkor a kliens gépen az SSH titkos kulcsot természetesen védeni kell, mivel az a fájl szó szerint a belépés kulcsa. Éppen ezért a legtöbb rendszerben lehetőség van az SSH titkos kulcs jelszavas védelmére. Ez azt jelenti, hogy a titkos kulcs fájl egy jelszóval titkosított, annak megadása nélkül a benne lévő titkos kulcshoz nem fér hozzá a GIT kliens program sem.

## SSH kulcs generálása

Az SSH kulcspár generálása egy pár perces folyamat, lépéseiről a github.com-on van egy nagyon jó és tömör leírás:
[https://help.github.com/articles/generating-ssh-keys/](https://help.github.com/articles/generating-ssh-keys/)

## Putty és formátumok

Aki a GitExtensions kliens programot használja, találkozhat a [putty](http://www.putty.org/) kulcskezelő szolgáltatásával (Pageant) is. Ez egy windows alatt a háttérben futó szolgáltatás, mely az SSH kulcsunkat kezeli.

Mivel a putty is tud SSH kulcsot generálni (PuTTYgen), előfordulhat, hogy a GIT-es és a puttyos formátum között konvertálnunk kell. A GIT-es (OpenSSH) fájl eleje "ssh-rsa", a puttyosé "PuTTY".

Konvertálás OpenSSH -> Putty irányba: a PuTTYgen felhasználói felületén betöltve a másik formátumban lévő kulcsot, majd elmentve.

Konvertálás Putty -> OpenSSH irányba: a GIT által telepített ssh-keygen programmal az alábbiak szerint.

```Shell
ssh-keygen -i -f regi_nyilvanos_kulcs.pub > uj_nyilvanos_kulcs.pub
```

## SSH kulcs regisztrálása GitHub-on

A [www.github.com](www.github.com) esetében a felhasználói névvel és jelszóval belépve fel lehet tölteni SSH nyilvános kulcsokat, amiket onnan kezdve a szerver fel fog ismerni. Mivel a kulcsokat nem szokás több helyen használni (eltérő gépeknek eltérő kulcsa van), ezért két felhasználó nem adhatja meg ugyanazt a nyilvános kulcsot. (Ez amúgy is azt eredményezné, hogy nem egyértelmű, ki akar csatlakozni.)

## Egyéb authentikációs módszerek

Péládul a TFS (Microsoft Team Foundation Server) és a bitbucket.org felhasználói névvel authentikál. Ilyenkor a GIT push és pull műveleteknél ezeket kell megadni.

<small>Szerzők, verziók: Csorba Kristóf</small>
