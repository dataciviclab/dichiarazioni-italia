# dichiarazioni-italia

[![CI](https://github.com/dataciviclab/dichiarazioni-italia/actions/workflows/ci.yml/badge.svg)](https://github.com/dataciviclab/dichiarazioni-italia/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Perché questi dati

Le dichiarazioni fiscali sono lo specchio più fedele dell'economia reale: ogni impresa e ogni lavoratore dichiarano redditi, volumi d'affari e imposte. Qui si misura la ricchezza territoriale, si confronta il carico fiscale tra regioni e settori, e si segue l'evoluzione del tessuto produttivo italiano — dalle società di capitali alle partite IVA.

## Cosa contengono

17 dataset dalla stessa fonte (MEF `analisi_stat`), raggruppati per imposta e forma giuridica. Ogni nome linka il README del dataset (schema e limiti).

**IRPEF · persone fisiche**

| Dataset | Righe/anno | Periodo | Copertura |
|---|---|---|---|
| [`irpef_imposta_tipologia`](datasets/irpef-imposta-tipologia/README.md) | 16 tipologie | 2012–2024 | **Imposta netta** per tipologia di contribuente |
| [`irpef_comunale`](datasets/irpef-comunale/README.md) | ~7.900 comuni | 2015–2024 | Redditi, imposta e fasce di reddito per comune |
| [`mef_irpef_regionale`](datasets/mef-irpef-regionale/README.md) | 21 × 34 classi | 2016–2024 | Contribuenti per regione e classe di reddito |

**IRPEF · titolari di partita IVA**

| Dataset | Righe/anno | Periodo | Copertura |
|---|---|---|---|
| [`abpf_titolari_piva_regione`](datasets/abpf-titolari-piva-regione/README.md) | 21 regioni | 2015–2024 | 3,8 M soggetti: redditi, imposta, regimi agevolati |

**IRPEF · società di persone** — gerarchia: l'aggregato più imprese (75% del reddito) e professionisti (22%) coprono il 97%.

| Dataset | Righe/anno | Periodo | Copertura |
|---|---|---|---|
| [`acsp_tutte_regione`](datasets/acsp-tutte-regione/README.md) | 21 regioni | 2013–2024 | Aggregato: redditi dichiarati per regione |
| [`acsp_imprese_regione`](datasets/acsp-imprese-regione/README.md) | 21 regioni | 2014–2024 | Imprese: redditi e determinazione |
| [`acsp_professionisti_regione`](datasets/acsp-professionisti-regione/README.md) | 21 regioni | 2018–2024 | Professionisti: compensi e spese |
| [`acsp_tutte_classi_reddito`](datasets/acsp-tutte-classi-reddito/README.md) | 33 classi | 2013–2024 | Distribuzione per classe di reddito |
| [`acsp_tutte_classi_volume`](datasets/acsp-tutte-classi-volume/README.md) | 38 classi | 2013–2024 | Distribuzione per classe di volume d'affari |

**IRES · società di capitali**

| Dataset | Righe/anno | Periodo | Copertura |
|---|---|---|---|
| [`ires_redditi_regione`](datasets/ires-redditi-regione/README.md) | 21 regioni | 2014–2023 | Reddito e perdita d'impresa societaria |

**IVA**

| Dataset | Righe/anno | Periodo | Copertura |
|---|---|---|---|
| [`iva_regionale`](datasets/iva-regionale/README.md) | 21 regioni | 2014–2024 | Volume d'affari, valore aggiunto, imposta |
| [`iva_sez_attivita`](datasets/iva-sez-attivita/README.md) | 22–23 sezioni ATECO | 2014–2024 | Volume d'affari per settore |

**IRAP**

| Dataset | Righe/anno | Periodo | Copertura |
|---|---|---|---|
| [`irap_imposta_regione`](datasets/irap-imposta-regione/README.md) | 21 regioni | 2014–2023 | Base imponibile e imposta |
| [`irap_imposta_pa_regione`](datasets/irap-imposta-pa-regione/README.md) | 21 regioni | 2014–2023 | P.A.: base e imposta (35% del gettito) |
| [`irap_imposta_settore`](datasets/irap-imposta-settore/README.md) | 22 sezioni ATECO | 2014–2023 | Base e imposta per settore |
| [`irap_vp_regime`](datasets/irap-vp-regime/README.md) | 21 regioni | 2014–2023 | Valore della produzione per regime contabile |
| [`irap_italia_estero`](datasets/irap-italia-estero/README.md) | 21 regioni | 2014–2023 | Produzione realizzata in Italia vs all'estero |

### ⚠️ Prima di leggere i dati

- **IRAP** — la base imponibile cambia definizione tra a.i. 2014 e 2015 (−27%): i trend si leggono **dal 2015**.
- **Società di persone (ACSP)** — le colonne **non sono additive**: ogni voce è dichiarata su una riga diversa del modello. La fonte ha inoltre un'anomalia ad a.i. 2017 (reddito d'impresa in contabilità semplificata −59%) — issue [#25](https://github.com/dataciviclab/dichiarazioni-italia/issues/25).
- **IVA e IRPEF comunale** — perimetri e anni parziali: vedi il README del dataset.

**Fonte**: MEF — Dipartimento delle Finanze, portale [analisi_stat](https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php?opendata=yes) · **Licenza**: CC BY (MEF)

## Esempi di domande

- Chi paga l'IRPEF in Italia, e quanto pesa ciascuna tipologia di contribuente?
- Quanto reddito dichiarano le società di persone, e come si distribuisce tra le regioni?
- Quanto pesa il regime forfetario sui redditi delle partite IVA, e come è cambiato dal 2015?
- Quali regioni e settori ATECO trainano il volume d'affari IVA, e quanta IRAP si paga?

## Come accedere

**DuckDB** (consigliato per analisi SQL):
```sql
SELECT anno, regione, volume_affari_eur
FROM read_parquet('out/data/clean/iva_regionale/*/*_clean.parquet')
WHERE anno = 2023 ORDER BY volume_affari_eur DESC;
```

**Parquet**: clean in `out/data/clean/<dataset>/<year>/`, mart in `out/data/mart/<dataset>/`.
**MCP**: i dataset pubblicati sono interrogabili via `find` / `gcs_query`.
**Riproduci**: `make check` (valida i config) · `make run-all` (esegue tutto).

## Approfondimenti

- [Discussions](https://github.com/dataciviclab/dichiarazioni-italia/discussions) — domande, idee, proposte
- [Issues](https://github.com/dataciviclab/dichiarazioni-italia/issues) — bug, dataset mancanti, miglioramenti

## Partecipa

Hai trovato un errore o vuoi aggiungere un dataset? Apri una [Discussion](https://github.com/dataciviclab/dichiarazioni-italia/discussions) o una [Issue](https://github.com/dataciviclab/dichiarazioni-italia/issues).

## Licenza

MIT — vedi [LICENSE](LICENSE) per dettagli.
