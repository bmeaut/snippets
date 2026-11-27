# Összesítő táblák (analyze.py generálta)


## A rész: tokenszám-arány az angolhoz (csomagszintű bootstrap, 95% CI)

| modell | nyelv | ratio | ci_lo | ci_hi | chars_per_token | bytes_per_token |
|---|---|---|---|---|---|---|
| Haiku 5.5 | angol | 1.00 | 1.00 | 1.00 | 3.09 | 3.10 |
| Haiku 5.5 | magyar | 1.55 | 1.53 | 1.58 | 2.09 | 2.30 |
| Haiku 5.5 | német | 1.72 | 1.69 | 1.74 | 2.10 | 2.13 |
| Haiku 5.5 | japán | 1.26 | 1.25 | 1.28 | 1.07 | 3.10 |
| Sonnet 5.5 | angol | 1.00 | 1.00 | 1.00 | 3.09 | 3.10 |
| Sonnet 5.5 | magyar | 1.55 | 1.53 | 1.58 | 2.09 | 2.30 |
| Sonnet 5.5 | német | 1.72 | 1.69 | 1.74 | 2.10 | 2.13 |
| Sonnet 5.5 | japán | 1.26 | 1.25 | 1.28 | 1.07 | 3.10 |
| Opus 5 | angol | 1.00 | 1.00 | 1.00 | 3.09 | 3.10 |
| Opus 5 | magyar | 1.55 | 1.53 | 1.57 | 2.09 | 2.30 |
| Opus 5 | német | 1.72 | 1.69 | 1.74 | 2.10 | 2.13 |
| Opus 5 | japán | 1.26 | 1.25 | 1.28 | 1.07 | 3.10 |
| Sonnet 4.6 | angol | 1.00 | 1.00 | 1.00 | 4.44 | 4.45 |
| Sonnet 4.6 | magyar | 1.75 | 1.72 | 1.78 | 2.67 | 2.94 |
| Sonnet 4.6 | német | 1.74 | 1.71 | 1.76 | 2.98 | 3.03 |
| Sonnet 4.6 | japán | 1.81 | 1.79 | 1.84 | 1.07 | 3.10 |
| Haiku 4.5 | angol | 1.00 | 1.00 | 1.00 | 4.44 | 4.45 |
| Haiku 4.5 | magyar | 1.75 | 1.72 | 1.78 | 2.67 | 2.94 |
| Haiku 4.5 | német | 1.74 | 1.71 | 1.76 | 2.98 | 3.03 |
| Haiku 4.5 | japán | 1.81 | 1.79 | 1.84 | 1.07 | 3.10 |

## B rész: számított költség, arány az `EN_EN`-hez (feladatonkénti bootstrap, 95% CI)

| model_alias | variant | n | ratio | ci_lo | ci_hi |
|---|---|---|---|---|---|
| haiku | HU_HU | 180 | 1.60 | 1.48 | 1.73 |
| haiku | HU_EN | 180 | 2.33 | 2.17 | 2.48 |
| haiku | EN_HU | 180 | 1.30 | 1.23 | 1.38 |
| haiku | DE_DE | 180 | 1.51 | 1.43 | 1.60 |
| haiku | DE_EN | 180 | 1.80 | 1.69 | 1.91 |
| haiku | EN_DE | 180 | 1.29 | 1.24 | 1.35 |
| haiku | JA_JA | 180 | 1.34 | 1.23 | 1.44 |
| haiku | JA_EN | 180 | 1.79 | 1.70 | 1.88 |
| haiku | EN_JA | 180 | 1.20 | 1.14 | 1.27 |
| sonnet | HU_HU | 180 | 1.22 | 1.18 | 1.26 |
| sonnet | HU_EN | 180 | 1.26 | 1.21 | 1.32 |
| sonnet | EN_HU | 180 | 1.28 | 1.24 | 1.32 |
| sonnet | DE_DE | 180 | 1.38 | 1.33 | 1.43 |
| sonnet | DE_EN | 180 | 1.35 | 1.31 | 1.39 |
| sonnet | EN_DE | 180 | 1.47 | 1.40 | 1.54 |
| sonnet | JA_JA | 180 | 1.20 | 1.15 | 1.26 |
| sonnet | JA_EN | 180 | 1.31 | 1.26 | 1.37 |
| sonnet | EN_JA | 180 | 1.16 | 1.12 | 1.20 |
| opus | HU_HU | 60 | 1.13 | 1.08 | 1.19 |
| opus | HU_EN | 60 | 1.35 | 1.28 | 1.42 |
| opus | EN_HU | 60 | 1.36 | 1.27 | 1.45 |
| opus | DE_DE | 60 | 1.22 | 1.16 | 1.29 |
| opus | DE_EN | 60 | 1.34 | 1.29 | 1.40 |
| opus | EN_DE | 60 | 1.59 | 1.49 | 1.70 |
| opus | JA_JA | 60 | 1.19 | 1.12 | 1.26 |
| opus | JA_EN | 60 | 1.41 | 1.33 | 1.49 |
| opus | EN_JA | 60 | 1.33 | 1.25 | 1.42 |

## B rész: bemeneti tokenek, arány az `EN_EN`-hez (feladatonkénti bootstrap, 95% CI)

| model_alias | variant | n | ratio | ci_lo | ci_hi |
|---|---|---|---|---|---|
| haiku | HU_HU | 180 | 1.57 | 1.54 | 1.61 |
| haiku | HU_EN | 180 | 1.74 | 1.71 | 1.78 |
| haiku | EN_HU | 180 | 1.15 | 1.15 | 1.16 |
| haiku | DE_DE | 180 | 1.87 | 1.83 | 1.90 |
| haiku | DE_EN | 180 | 2.11 | 2.08 | 2.15 |
| haiku | EN_DE | 180 | 1.10 | 1.09 | 1.10 |
| haiku | JA_JA | 180 | 1.38 | 1.35 | 1.41 |
| haiku | JA_EN | 180 | 1.50 | 1.47 | 1.53 |
| haiku | EN_JA | 180 | 1.14 | 1.13 | 1.14 |
| sonnet | HU_HU | 180 | 1.57 | 1.54 | 1.61 |
| sonnet | HU_EN | 180 | 1.74 | 1.70 | 1.78 |
| sonnet | EN_HU | 180 | 1.15 | 1.15 | 1.16 |
| sonnet | DE_DE | 180 | 1.87 | 1.83 | 1.90 |
| sonnet | DE_EN | 180 | 2.11 | 2.08 | 2.15 |
| sonnet | EN_DE | 180 | 1.10 | 1.09 | 1.10 |
| sonnet | JA_JA | 180 | 1.38 | 1.35 | 1.41 |
| sonnet | JA_EN | 180 | 1.50 | 1.47 | 1.53 |
| sonnet | EN_JA | 180 | 1.14 | 1.13 | 1.14 |
| opus | HU_HU | 60 | 1.58 | 1.52 | 1.65 |
| opus | HU_EN | 60 | 1.75 | 1.68 | 1.82 |
| opus | EN_HU | 60 | 1.15 | 1.15 | 1.16 |
| opus | DE_DE | 60 | 1.90 | 1.85 | 1.96 |
| opus | DE_EN | 60 | 2.15 | 2.09 | 2.22 |
| opus | EN_DE | 60 | 1.10 | 1.09 | 1.10 |
| opus | JA_JA | 60 | 1.42 | 1.37 | 1.47 |
| opus | JA_EN | 60 | 1.55 | 1.50 | 1.60 |
| opus | EN_JA | 60 | 1.14 | 1.13 | 1.15 |

## B rész: kimeneti tokenek, arány az `EN_EN`-hez (feladatonkénti bootstrap, 95% CI)

| model_alias | variant | n | ratio | ci_lo | ci_hi |
|---|---|---|---|---|---|
| haiku | HU_HU | 180 | 1.61 | 1.45 | 1.78 |
| haiku | HU_EN | 180 | 2.50 | 2.29 | 2.71 |
| haiku | EN_HU | 180 | 1.35 | 1.26 | 1.45 |
| haiku | DE_DE | 180 | 1.41 | 1.31 | 1.51 |
| haiku | DE_EN | 180 | 1.71 | 1.58 | 1.84 |
| haiku | EN_DE | 180 | 1.35 | 1.28 | 1.42 |
| haiku | JA_JA | 180 | 1.33 | 1.19 | 1.46 |
| haiku | JA_EN | 180 | 1.87 | 1.75 | 2.00 |
| haiku | EN_JA | 180 | 1.22 | 1.14 | 1.31 |
| sonnet | HU_HU | 180 | 1.11 | 1.07 | 1.16 |
| sonnet | HU_EN | 180 | 1.13 | 1.07 | 1.19 |
| sonnet | EN_HU | 180 | 1.32 | 1.27 | 1.38 |
| sonnet | DE_DE | 180 | 1.24 | 1.19 | 1.29 |
| sonnet | DE_EN | 180 | 1.13 | 1.09 | 1.18 |
| sonnet | EN_DE | 180 | 1.57 | 1.49 | 1.66 |
| sonnet | JA_JA | 180 | 1.15 | 1.08 | 1.22 |
| sonnet | JA_EN | 180 | 1.25 | 1.19 | 1.32 |
| sonnet | EN_JA | 180 | 1.17 | 1.11 | 1.22 |
| opus | HU_HU | 60 | 1.01 | 0.96 | 1.08 |
| opus | HU_EN | 60 | 1.24 | 1.16 | 1.33 |
| opus | EN_HU | 60 | 1.41 | 1.30 | 1.54 |
| opus | DE_DE | 60 | 1.04 | 0.96 | 1.13 |
| opus | DE_EN | 60 | 1.12 | 1.07 | 1.18 |
| opus | EN_DE | 60 | 1.73 | 1.60 | 1.88 |
| opus | JA_JA | 60 | 1.13 | 1.05 | 1.23 |
| opus | JA_EN | 60 | 1.37 | 1.28 | 1.48 |
| opus | EN_JA | 60 | 1.39 | 1.29 | 1.50 |

## B rész: kimeneti tokenek a nyitott (3 mondatos) feladatoknál

| model_alias | variant | n | ratio | ci_lo | ci_hi |
|---|---|---|---|---|---|
| haiku | HU_HU | 20 | 1.50 | 1.37 | 1.66 |
| haiku | HU_EN | 20 | 1.18 | 1.03 | 1.34 |
| haiku | EN_HU | 20 | 1.42 | 1.26 | 1.60 |
| haiku | DE_DE | 20 | 1.61 | 1.50 | 1.75 |
| haiku | DE_EN | 20 | 1.08 | 0.96 | 1.23 |
| haiku | EN_DE | 20 | 1.59 | 1.49 | 1.72 |
| haiku | JA_JA | 20 | 1.13 | 1.06 | 1.20 |
| haiku | JA_EN | 20 | 1.00 | 0.89 | 1.14 |
| haiku | EN_JA | 20 | 1.10 | 1.01 | 1.20 |
| sonnet | HU_HU | 20 | 1.52 | 1.40 | 1.63 |
| sonnet | HU_EN | 20 | 0.92 | 0.89 | 0.96 |
| sonnet | EN_HU | 20 | 1.45 | 1.26 | 1.64 |
| sonnet | DE_DE | 20 | 1.54 | 1.40 | 1.69 |
| sonnet | DE_EN | 20 | 0.96 | 0.88 | 1.04 |
| sonnet | EN_DE | 20 | 1.46 | 1.32 | 1.59 |
| sonnet | JA_JA | 20 | 1.08 | 0.94 | 1.23 |
| sonnet | JA_EN | 20 | 0.95 | 0.88 | 1.02 |
| sonnet | EN_JA | 20 | 1.10 | 1.02 | 1.17 |

## B rész: látható és a látható szövegen felüli kimeneti tokenek (20%-os részminta, becslés)

| model_alias | variant | n | visible | extra | extra_share |
|---|---|---|---|---|---|
| haiku | DE_DE | 35 | 58.89 | 6.34 | 0.10 |
| haiku | DE_EN | 42 | 49.98 | 28.00 | 0.36 |
| haiku | EN_DE | 47 | 67.62 | 2.89 | 0.04 |
| haiku | EN_EN | 37 | 49.92 | 4.05 | 0.08 |
| haiku | EN_HU | 36 | 57.83 | 10.03 | 0.15 |
| haiku | EN_JA | 38 | 55.18 | 2.05 | 0.04 |
| haiku | HU_EN | 29 | 51.21 | 64.41 | 0.56 |
| haiku | HU_HU | 40 | 54.67 | 25.40 | 0.32 |
| haiku | JA_EN | 33 | 57.21 | 36.67 | 0.39 |
| haiku | JA_JA | 42 | 48.95 | 18.52 | 0.27 |
| opus | DE_DE | 6 | 53.17 | 15.67 | 0.23 |
| opus | DE_EN | 15 | 48.13 | 15.20 | 0.24 |
| opus | EN_DE | 12 | 79.00 | 18.33 | 0.19 |
| opus | EN_EN | 14 | 39.07 | 14.50 | 0.27 |
| opus | EN_HU | 14 | 56.64 | 18.29 | 0.24 |
| opus | EN_JA | 11 | 49.73 | 13.18 | 0.21 |
| opus | HU_EN | 13 | 47.69 | 12.08 | 0.20 |
| opus | HU_HU | 12 | 39.42 | 11.75 | 0.23 |
| opus | JA_EN | 12 | 61.33 | 17.67 | 0.22 |
| opus | JA_JA | 18 | 43.72 | 14.56 | 0.25 |
| sonnet | DE_DE | 38 | 58.89 | 1.00 | 0.02 |
| sonnet | DE_EN | 46 | 54.89 | 1.00 | 0.02 |
| sonnet | EN_DE | 38 | 81.05 | 1.00 | 0.01 |
| sonnet | EN_EN | 27 | 46.85 | 1.00 | 0.02 |
| sonnet | EN_HU | 27 | 68.81 | 1.00 | 0.01 |
| sonnet | EN_JA | 34 | 58.09 | 1.00 | 0.02 |
| sonnet | HU_EN | 22 | 58.32 | 1.00 | 0.02 |
| sonnet | HU_HU | 36 | 59.28 | 1.00 | 0.02 |
| sonnet | JA_EN | 31 | 60.68 | 1.00 | 0.02 |
| sonnet | JA_JA | 34 | 62.24 | 1.00 | 0.02 |

## B rész: pontosság és a kért nyelv betartása

| model_alias | variant | n | correct | rate | ci_lo | ci_hi | format_ok_rate | lang_ok_rate |
|---|---|---|---|---|---|---|---|---|
| haiku | DE_DE | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.99 |
| haiku | DE_EN | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.87 |
| haiku | EN_DE | 180 | 180 | 1.00 | 0.98 | 1.00 | 0.99 | 0.92 |
| haiku | EN_EN | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.66 |
| haiku | EN_HU | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.86 |
| haiku | EN_JA | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.54 |
| haiku | HU_EN | 180 | 179 | 0.99 | 0.97 | 1.00 | 0.99 | 0.94 |
| haiku | HU_HU | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.92 |
| haiku | JA_EN | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.92 |
| haiku | JA_JA | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.92 |
| opus | DE_DE | 60 | 60 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 |
| opus | DE_EN | 60 | 60 | 1.00 | 0.94 | 1.00 | 1.00 | 0.76 |
| opus | EN_DE | 60 | 60 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 |
| opus | EN_EN | 60 | 60 | 1.00 | 0.94 | 1.00 | 1.00 | 0.68 |
| opus | EN_HU | 60 | 60 | 1.00 | 0.94 | 1.00 | 1.00 | 0.96 |
| opus | EN_JA | 60 | 60 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 |
| opus | HU_EN | 60 | 60 | 1.00 | 0.94 | 1.00 | 1.00 | 0.85 |
| opus | HU_HU | 60 | 60 | 1.00 | 0.94 | 1.00 | 1.00 | 0.90 |
| opus | JA_EN | 60 | 60 | 1.00 | 0.94 | 1.00 | 1.00 | 0.85 |
| opus | JA_JA | 60 | 60 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 |
| sonnet | DE_DE | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.99 |
| sonnet | DE_EN | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.87 |
| sonnet | EN_DE | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.98 |
| sonnet | EN_EN | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.75 |
| sonnet | EN_HU | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 |
| sonnet | EN_JA | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 |
| sonnet | HU_EN | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.89 |
| sonnet | HU_HU | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 |
| sonnet | JA_EN | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 0.90 |
| sonnet | JA_JA | 180 | 180 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 |
