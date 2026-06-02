import random
from logic import tipp_kiszamolasa

# Elérhető színek
SZINEK = ["szurke", "piros", "narancs", "sarga", "zold", "pink", "lila", "kek", "fekete", "feher"]
MAX_KOROK = 12

def welcome():
    """Üdvözlő üzenet és játékszabályok"""
    print("=" * 60)
    print(" " * 20 + "MASTERMIND JÁTÉK")
    print("=" * 60)
    print("\nÜdvözöllek a Mastermind játékban!")
    print(f"\nElérhető színek ({len(SZINEK)} db):")
    for i, szin in enumerate(SZINEK, 1):
        print(f"  {i}. {szin}", end="    " if i % 3 != 0 else "\n")
    print("\n\nCélod: Találd ki a 4 színből álló titkos kombinációt!")
    print(f"Neked {MAX_KOROK} körödön van tippelni.\n")
    print("Válaszban kapod:")
    print("  - FEKETE tüskék: hány szín van jó helyen")
    print("  - FEHÉR tüskék: hány szín van rossz helyen\n")
    print("Adj meg 4 színt szóközzel elválasztva!")
    print("Például: piros kek zold sarga\n")
    print("=" * 60 + "\n")

def generalt_felallas():
    """Véletlenszerű felállás generálása"""
    return [random.choice(SZINEK) for _ in range(4)]

def beker_tippet(kor):
    """Tipp bekérése a felhasználótól"""
    while True:
        try:
            print(f"[{kor}. kör] Add meg a tipped: ", end="")
            tipp_str = input().strip().lower()
            
            if not tipp_str:
                print("❌ Üres tipp! Próbáld újra.")
                continue
            
            tipp = tipp_str.split()
            
            if len(tipp) != 4:
                print(f"❌ Pontosan 4 színt kell megadnod! Te {len(tipp)} színt adtál meg.")
                continue
            
            # Ellenőrizzük, hogy minden szín érvényes-e
            hibas_szinek = [szin for szin in tipp if szin not in SZINEK]
            if hibas_szinek:
                print(f"❌ Érvénytelen szín(ek): {', '.join(hibas_szinek)}")
                print(f"   Elérhető színek: {', '.join(SZINEK)}")
                continue
            
            return tipp
        except KeyboardInterrupt:
            print("\n\n👋 Játék megszakítva. Viszlát!")
            exit(0)
        except Exception as e:
            print(f"❌ Hiba: {e}")
            continue

def eredmeny_kiiras(fekete, feher):
    """Eredmény szép megjelenítése"""
    print(f"   Eredmény: ", end="")
    
    # Fekete tüskék
    if fekete > 0:
        print(f"🔴 {fekete} fekete", end="")
    
    # Fehér tüskék
    if feher > 0:
        if fekete > 0:
            print(", ", end="")
        print(f"⚪ {feher} fehér", end="")
    
    # Ha egyik sincs
    if fekete == 0 and feher == 0:
        print("❌ Nincs találat", end="")
    
    print()

def jatek():
    """Fő játék logika"""
    welcome()
    
    # Titkos felállás generálása
    felallas = generalt_felallas()
    # print(f"[DEBUG] Titkos kód: {' '.join(felallas)}")  # Debug célra
    
    # Játék ciklus
    for kor in range(1, MAX_KOROK + 1):
        tipp = beker_tippet(kor)
        
        try:
            fekete, feher = tipp_kiszamolasa(felallas, tipp, SZINEK)
            eredmeny_kiiras(fekete, feher)
            
            # Győzelem ellenőrzése
            if fekete == 4:
                print("\n" + "=" * 60)
                print(f"🎉 GRATULÁLOK! Kitaláltad {kor} körből!")
                print(f"A titkos kód: {' '.join(felallas).upper()}")
                print("=" * 60)
                return True
            
            print()  # Üres sor a következő kör előtt
            
        except ValueError as e:
            print(f"❌ Hiba: {e}")
            continue
    
    # Ha elfogytak a körök
    print("\n" + "=" * 60)
    print("😞 Sajnos elfogytak a köreid!")
    print(f"A titkos kód: {' '.join(felallas).upper()}")
    print("=" * 60)
    return False

def main():
    """Főprogram - újrajátszás kezelése"""
    while True:
        jatek()
        
        print("\nSzeretnél újra játszani? (i/n): ", end="")
        try:
            valasz = input().strip().lower()
            if valasz not in ['i', 'igen', 'y', 'yes']:
                print("\n👋 Köszönöm a játékot! Viszlát!")
                break
            print("\n" + "=" * 60 + "\n")
        except KeyboardInterrupt:
            print("\n\n👋 Viszlát!")
            break

if __name__ == "__main__":
    main()
