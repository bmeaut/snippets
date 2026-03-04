import pytest
from logic import tipp_kiszamolasa

szinek = ["szurke", "piros", "narancs", "sarga", "zold", "pink", "lila", "kek", "fekete", "feher" ]

def test_ervenytelen_szin():
    with pytest.raises(ValueError):
        tipp =  ["sotetkek", "kek", "kek", "kek"]
        felalas = ["piros", "kek", "zold", "sarga"]
        tipp_kiszamolasa(felalas, tipp, szinek)

def test_tulsok_szin():
    with pytest.raises(ValueError):
        tipp =  ["zold", "kek", "kek", "kek", "piros"]
        felalas = ["piros", "kek", "zold", "sarga"]
        tipp_kiszamolasa(felalas, tipp, szinek)


def test_tulkeves_szin():
    with pytest.raises(ValueError):
        tipp =  ["zold", "kek", "kek",]
        felalas = ["piros", "kek", "zold", "sarga"]
        tipp_kiszamolasa(felalas, tipp, szinek)



def test_nincs_talalat():
    tipp = ["szurke", "piros", "narancs", "sarga"]
    felalas = ["lila", "kek", "fekete", "feher"]
    assert tipp_kiszamolasa(felalas, tipp, szinek) == (0,0)

def test_johely():
    tipp = ["zold", "kek", "szurke", "piros"]
    felalas = ["lila", "kek", "fekete", "feher"]
    assert tipp_kiszamolasa(felalas, tipp, szinek) == (1,0)

def test_benne():
    tipp = ["zold", "szurke", "piros", "kek"]
    felalas = ["lila", "kek", "fekete", "feher"]
    assert tipp_kiszamolasa(felalas, tipp, szinek) == (0,1)

def test_benne_johely():
    tipp = ["zold", "szurke", "piros", "kek"]
    felalas = ["szurke", "lila", "piros", "kek"]
    assert tipp_kiszamolasa(felalas, tipp, szinek) == (2,1)

def test_duplikaltszin_johely():
    tipp = ["kek", "kek", "szurke", "piros"]
    felalas = ["lila", "kek", "fekete", "feher"]
    assert tipp_kiszamolasa(felalas, tipp, szinek) == (1,0)

def test_duplikaltszin_benne():
    tipp = ["kek", "szurke", "piros", "kek"]
    felalas = ["lila", "kek", "fekete", "feher"]
    assert tipp_kiszamolasa(felalas, tipp, szinek) == (0,1)

def test_duplikaltszin_benne_tobb():
    tipp = ["kek", "szurke", "kek", "kek"]
    felalas = ["lila", "kek", "kek", "feher"]
    assert tipp_kiszamolasa(felalas, tipp, szinek) == (0,2)

def test_duplikaltszin_johely_tobb():
    tipp = ["kek", "kek", "szurke", "piros"]
    felalas = ["kek", "kek", "fekete", "piros"]
    assert tipp_kiszamolasa(felalas, tipp, szinek) == (3,0)

def test_duplikaltszin_vegyes():
    tipp = ["kek", "kek", "szurke", "piros"]
    felalas = ["kek", "kek", "piros", "piros"]
    assert tipp_kiszamolasa(felalas, tipp, szinek) == (2,1)
    
def test_siker():
    tipp = ["zold", "szurke", "piros", "kek"]
    felalas = ["zold", "szurke", "piros", "kek"]
    assert tipp_kiszamolasa(felalas, tipp, szinek) == (4,0)