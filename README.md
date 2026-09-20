# dichiarazioni-italia

[![CI](https://github.com/dataciviclab/dichiarazioni-italia/actions/workflows/ci.yml/badge.svg)](https://github.com/dataciviclab/dichiarazioni-italia/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Perché questi dati

Le dichiarazioni fiscali italiane sono lo specchio più fedele dell'economia reale: ogni impresa e ogni lavoratore dichiarano redditi, volumi d'affari e imposte. Questi dati permettono di misurare la ricchezza territoriale, confrontare il carico fiscale tra regioni e settori, e monitorare l'evoluzione del tessuto economico italiano.

## Cosa contengono

| Dataset | Righe/anno | Periodo | Copertura |
|---|---|---|---|
| `irpef_comunale` | ~7.900 comuni | 2015–2024 | IRPEF per comune: redditi, imposta, fasce di reddito |
| `iva_regionale` | 21 regioni | 2014–2024 | Volume d'affari IVA, valore aggiunto, imposta |
| `iva_sez_attivita` | 22 settori ATECO | 2014–2024 | Volume d'affari IVA per settore economico |
| `mef_irpef_regionale` | 21 × 34 classi | 2017–2025 | IRPEF per regione e classe di reddito |
| `ires_redditi_regione` | 21 regioni | 2015–2024 | Reddito/perdita d'impresa societaria |
| `irap_vp_regime` | 21 regioni | 2015–2024 | Valore produzione IRAP per regime contabile |
| `irap_italia_estero` | 21 regioni | 2015–2024 | Produzione netta realizzata in Italia vs estero |

**Fonte**: MEF — Dipartimento delle Finanze, portale [analisi_stat](https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php?opendata=yes)
**Licenza**: CC BY (MEF)

## Esempi di domande

- Quali regioni producono più valore aggiunto IVA? Come è cambiata la distribuzione dal 2015?
- Quanto reddito d'impresa dichiarano le società di capitali in ciascuna regione?
- Quali settori ATECO hanno la maggiore crescita del volume d'affari IVA?
- Come si distribuisce la produzione IRAP tra regime ordinario, forfetario e agricolo?
- Quanta produzione netta viene realizzata all'estero vs in Italia, per regione?

## Come accedere

**DuckDB** (consigliato per analisi SQL):
```sql
SELECT anno, regione, volume_affari_eur
FROM read_parquet('out/data/clean/iva_regionale/*/*_clean.parquet')
WHERE anno = 2023
ORDER BY volume_affari_eur DESC;
```

**Parquet files**: i dati puliti sono in `out/data/clean/<dataset>/<year>/`

**Riproduci la pipeline**:
```bash
make check        # valida tutti i dataset.yml
make run-all      # esegui tutte le pipeline
```

## Approfondimenti

- [Discussions](https://github.com/dataciviclab/dichiarazioni-italia/discussions) — domande, idee, proposte
- [Issues](https://github.com/dataciviclab/dichiarazioni-italia/issues) — bug, dataset mancanti, miglioramenti

## Partecipa

Hai trovato un errore o vuoi aggiungere un dataset? Apri un'[Issue](https://github.com/dataciviclab/dichiarazioni-italia/issues) o una [Discussion](https://github.com/dataciviclab/dichiarazioni-italia/discussions).

## Licenza

MIT — vedi [LICENSE](LICENSE) per dettagli.
