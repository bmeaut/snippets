# Kód – 1099_FacebookSentimentMap

A Biatorbágy helyi Facebook-csoportjának szentimentelemzéséhez és problématérképéhez használt szkriptek. A kódot egy AI-ágens írta a munkamenet során, és utólag rendeztük futtatható formába. Kutatási prototípus, nem karbantartott szoftver.

## Mi van benne, és mi nincs

**Benne van:** a teljes feldolgozási lánc kódja, a kulcsszavas problémataxonómia (`issues.py`), a problémák kézzel írt összefoglalói (`issue_texts.py`), a téma-kulcsszavak (`topics.py`) és a dashboard forrása (`web/`).

**Nincs benne, adatvédelmi okból:**

- a nyers Apify-export (`posts.json`): nevek, Facebook-azonosítók és teljes szövegek vannak benne;
- az OSM-export (`export.geojson`): ez nem személyes adat, de újra letölthető (lásd lent);
- a validációs minták (`val_sample.json`, `train2_sample.json`) és a hozzájuk tartozó kézi címkék (`gold.txt`, `gold2.txt`): ezek posztok és kommentek teljes szövegét tartalmazzák;
- a köztes fájlok (`work/`, `out/`) és a tételenként címkézett CSV.

Emiatt a `validate.py` és az `indomain.py` csak a saját, újracímkézett mintával futtatható.

## Előfeltételek

```
pip install -r requirements.txt
npm install d3@7          # csak az offline HTML összeállításához
```

Külső adatok a `ext/` mappába:

```
git clone https://github.com/nytud/HuSST ext/HuSST
git clone https://github.com/dhuszti/SentimentAnalysisHUN ext/SentimentAnalysisHUN
```

A PrecoSenti szentimentszótár a `SentimentAnalysisHUN` repóban található.

Saját adatok a `data_raw/` mappába:

- `posts.json`: a Facebook-csoport Apify-exportja (*Facebook Group Post Scraper*, posztok kommentekkel);
- `export.geojson`: a település utcái, területei és nevezetes helyei Overpass-lekérdezéssel. Az út- és helynevek, valamint a közigazgatási határ kell hozzá.

## Futtatási sorrend

A parancsokat a repó gyökeréből (a `code/` szülőmappájából) kell futtatni. A köztes fájlok a `work/` és `out/` mappába kerülnek.

| # | Szkript | Mit csinál | Kimenet |
|---|---------|-----------|---------|
| 1 | `python code/prep.py data_raw/posts.json` | Posztok és kommentek egységes táblába, validációs minta | `work/units.pkl`, `work/val_sample.json` |
| 2 | `python code/model.py` | Általános magyar modell: TF-IDF + logisztikus regresszió (HuSST, OpinHuBank) és PrecoSenti szótár | `work/model.pkl` |
| 3 | *(kézi lépés)* | A minta címkézése neg/neu/pos szerint, soronként egy címke | `work/gold.txt`, `work/gold2.txt` |
| 4 | `python code/validate.py` | Az általános modell mérése, súlyok hangolása | `work/val_result.json` |
| 5 | `python code/indomain.py` | Doménspecifikus modell a címkézett FB-szövegeken, keresztvalidáció | `work/indomain.pkl`, `work/indomain_eval.json` |
| 6 | `python code/score_all.py` | Minden szöveg pontozása, témacímkék | `work/scored.pkl` |
| 7 | `python code/aggregate.py` | Összesítések, prevalencia-korrekció a konfúziós mátrixszal | `work/summary.json` |
| 8 | `python code/issue_stats.py` | Konkrét problémák kulcsszavas azonosítása, statisztikák | `work/issues_scored.pkl`, `work/issue_table.pkl`, `work/issue_monthly.pkl` |
| 9 | `python code/geo_build.py` | Helynévtár az OSM-ből, helynevek felismerése a szövegekben | `work/geo_scored.pkl`, `work/gazetteer.json`, `work/area_geoms.json` |
| 10 | `python code/geo_agg.py` | Problémák helyszínenként | `out/places.json`, `out/place_issues.json`, `out/unplaced.json` |
| 11 | `python code/basemap.py` | Egyszerűsített alaptérkép (Douglas–Peucker) | `out/basemap.json` |
| 12 | `python code/build_dashboard_data.py` | A publikálható, anonimizált adatfájlok (szövegrészletek nélkül) | `data/*.json` |
| 13 | `python code/build_offline_html.py` | Egyfájlos, offline dashboard | `biatorbagy_szentiment_dashboard.html` |

**Figyelem:** a 7. és 10. lépés köztes kimenetei (`work/szentiment_cimkezett.csv`, `out/places.json`) még tartalmaznak szerzőneveket vagy szövegrészleteket. Ezeket ne tedd közzé. A publikálható változat a 12. lépés kimenete.

## Testreszabás más településre

- `issues.py`: problémák és kulcsszavak. A szótövek prefixként illeszkednek. A `re:` előtagú elemek nyers regexek, a kizárások a téves találatokat szűrik (például *csatorna* mint YouTube-csatorna).
- `issue_texts.py`: a problémák kártyán megjelenő összefoglalói. Ezeket a szálak elolvasása után kell megírni. A szkript nem generálja őket.
- `geo_build.py`: a helynév-felismerés kontextusszabályai, az ok() függvény. Itt kezelhetők az utcanevekkel ütköző köznevek (például *Forrás utca* és *forrás*) és az álnevek.
