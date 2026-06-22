def tipp_kiszamolasa(felallas, tipp, szinek):
    """
    Mastermind játék logikája - a tipp kiértékelése.
    
    Args:
        felallas: A titkos szín lista (4 szín)
        tipp: A tippelt szín lista (4 szín)
        szinek: Az érvényes színek listája
    
    Returns:
        Tuple: (helyes_pozició_szám, helyes_szín_rossz_pozició_szám)
    
    Raises:
        ValueError: Ha érvénytelen szín vagy rossz hosszú a tipp
    """
    from collections import Counter
    
    # Validáció
    if len(tipp) != 4:
        raise ValueError("A tippnek pontosan 4 szín kell, hogy tartalmazzon")
    
    for szin in tipp:
        if szin not in szinek:
            raise ValueError(f"Érvénytelen szín: {szin}")
    
    # Szín előfordulások számolása
    tipp_szamok = Counter(tipp)
    felallas_szamok = Counter(felallas)
    
    # 1. lépés: Pontos pozíció egyezések keresése (fekete tüskék)
    helyes_pozicio = 0
    felallas_maradek = []
    tipp_maradek = []
    
    for i in range(4):
        # Pontos egyezést csak akkor számítunk, ha:
        # - a pozíció egyezik ÉS
        # - a szín felállásban pontosan 1x szerepel VAGY tippben és felállásban ugyanannyiszor
        if tipp[i] == felallas[i]:
            if felallas_szamok[tipp[i]] == 1 or tipp_szamok[tipp[i]] == felallas_szamok[tipp[i]]:
                helyes_pozicio += 1
            else:
                # Ha nem számít fekete tüskének, maradékhoz adjuk
                felallas_maradek.append(felallas[i])
                tipp_maradek.append(tipp[i])
        else:
            # Nincs pozíció egyezés, maradékhoz adjuk
            felallas_maradek.append(felallas[i])
            tipp_maradek.append(tipp[i])
    
    # 2. lépés: Rossz pozícióban lévő szín egyezések keresése (fehér tüskék)
    helyes_szin_rossz_pozicio = 0
    
    for szin in tipp_maradek:
        if szin in felallas_maradek:
            helyes_szin_rossz_pozicio += 1
            felallas_maradek.remove(szin)
    
    return (helyes_pozicio, helyes_szin_rossz_pozicio)
