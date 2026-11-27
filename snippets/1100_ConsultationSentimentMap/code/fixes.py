"""Az átirat visszatérő félrehallásainak javítása (helynevek, nevek, szakszavak).

A Whisper a helyi hely- és személyneveket rendszeresen félrehallja, és
ugyanazt a nevet mindig hasonlóan rontja el. Ezeket egy reguláris
kifejezésekből álló listával cseréljük. A listát az átirat olvasása közben kell
bővíteni.

Óvatosan kell vele bánni: egy rosszul megírt szabály új hibát okoz. A munkamenet
során például egy szakszó félrehallott alakját a lista tévesen tulajdonnévvé
alakította, és ez csak az átirat olvasásakor derült ki.

Az alábbi bejegyzések kitalált példák; a valódi listát mindig a saját
felvételhez kell összeállítani.
"""
import re

REPLACE = {
    # településnév: kis- és nagybetűs, b/v és a/o tévesztések
    r"\b[pP][ée]ld[aá][vb][aá]ros": "Példaváros",
    # városrész kötőjellel
    r"Malom hegy": "Malom-hegy", r"Malomhegy": "Malom-hegy",
    # szakszó, amelyet a modell más szóként hall
    r"\bszenyvíz": "szennyvíz", r"\bkarstos": "karsztos",
    # intézménynév rövidítése
    r"\bB[ée]-?[eE]m-?[eE]\b": "BME",
}


def fix(text):
    for pattern, repl in REPLACE.items():
        text = re.sub(pattern, repl, text)
    return text
