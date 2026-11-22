# Kód – 1100_ConsultationSentimentMap

Szkriptek egy élőszóban zajló konzultáció hangfelvételének átiratához és a kézi címkékből készülő szentiment- és problémaösszesítéshez. A kódot egy AI-ágens írta a munkamenet során, és utólag rendeztük futtatható formába. Kutatási prototípus, nem karbantartott szoftver.

## Mi van benne, és mi nincs

**Benne van:**

- az átirat és az egységképzés szkriptjei;
- a félrehallások javítólistájának formátuma kitalált példákkal (`fixes.py`);
- a dashboard-adatok összesítése (`build_dashboard_data.py`);
- egy kitalált kódkönyv (`codebook_example.py`) és egy hatsoros, kitalált címkefájl a `../example/` mappában, hogy a lánc kipróbálható legyen.

**Nincs benne, titoktartási és adatvédelmi okból:** a hangfelvételek, az átiratok, a valódi kódkönyvek, a címkék, az összesített eredmények és a dashboardok.

## Előfeltételek

```
pip install -r code/requirements.txt
```

Kell még az `ffmpeg` és egy faster-whisper (CTranslate2) formátumú Whisper-modell, például a `large-v3-turbo`.

## Futtatási sorrend

A parancsokat a snippet gyökeréből (a `code/` szülőmappájából) kell futtatni.

| # | Parancs | Mit csinál | Kimenet |
|---|---------|-----------|---------|
| 1 | `ffmpeg -i felvetel.mp3 -ar 16000 -ac 1 -f segment -segment_time 600 work/chunks/c%02d.wav` | 10 perces, 16 kHz-es mono WAV-darabok | `work/chunks/` |
| 2 | `python code/transcribe.py <modell> work/chunks work/tsv` | Gépi átirat darabonként, folytatható | `work/tsv/*.tsv` |
| 3 | `python code/format_transcript.py work/tsv > atirat.md` | Olvasható átirat percenkénti időbélyegekkel | `atirat.md` |
| 4 | `python code/make_units.py work/tsv work` | 20–25 másodperces elemzési egységek | `work/units.json`, `work/units.txt` |
| 5 | *(kézi lépés)* | Egységenként: hangulat, szerep, problémák, helyek; a kódkönyv megírása | `labels.txt`, `code/codebook_<név>.py` |
| 6 | `python code/build_dashboard_data.py codebook_<név> work/units.json labels.txt out` | A dashboard összesített adatai | `out/*.json` |

Kipróbálás a kitalált példával:

```
python code/build_dashboard_data.py codebook_example example/units_example.json example/labels_example.txt out
```

A 6. lépés kimenetében (`units_labeled.json`) benne vannak az egységek időpontjai, de a szövegük nem. Ezért ezzel a fájllal a nyers átirat nélkül is újraszámolható minden összesítés.

## A címkefájl formátuma

Soronként egy egység, szóközzel elválasztva: `azonosító hangulat szerep problémák helyek`.

- hangulat: `n` (negatív), `0` (semleges), `p` (pozitív);
- szerep: `m` (moderátor és szervező csapat), `p` (résztvevő), `x` (vegyes);
- problémák és helyek: a kódkönyv kulcsai vesszővel elválasztva, vagy `-`.

Példa: `3 n x dugo,fout fout`.

## A kimeneti fájlok

| Fájl | Tartalom |
|------|----------|
| `overall.json` | Hangulat és beszédidő szerepenként |
| `timeline.json` | Hangulati arányok tízperces szakaszonként (mindenki, résztvevők, moderátor) |
| `issues.json` | Problémánként: egységszám, negatív és pozitív arány, résztvevői arány, első említés, csúcsszakasz, összefoglaló |
| `issue_time.json` | Problémánként az említések tízperces szakaszonként |
| `issue_groups.json` | Hangulati arányok témakörönként |
| `places.json`, `place_issues.json` | Helyenként az említések, a negatív arány és a fő problémák |
| `sections.json` | Húszperces szakaszok összesítése |
| `units_labeled.json` | Egységenkénti címkék szöveg nélkül |
