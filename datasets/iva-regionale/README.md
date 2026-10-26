# iva-regionale

**Domanda guida:** Come si distribuisce il volume d'affari IVA tra le regioni italiane?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** CIVATOT0201 (Regione)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; scaricato via `http_file`, letto con `read.skip: 9`
**Copertura:** 2014–2024 (11 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (es. `2024CIVATOT0201` = dichiarazioni 2024). Il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)

## Schema (14 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta (URL anno - 1) |
| `regione` | VARCHAR | Denominazione regione |
| `cod_regione` | VARCHAR | Codice ISTAT regione |
| `contribuenti` | BIGINT | Numero contribuenti IVA |
| `volume_frequenza` | BIGINT | Partite IVA che dichiarano volume d'affari |
| `volume_affari_eur` | DOUBLE | Volume d'affari (€) |
| `acquisti_frequenza` | BIGINT | Partite IVA che dichiarano acquisti |
| `acquisti_eur` | DOUBLE | Acquisti e importazioni (€) |
| `va_frequenza` | BIGINT | Partite IVA con valore aggiunto fiscale |
| `va_fiscale_eur` | DOUBLE | Valore aggiunto fiscale (€) |
| `imposta_dovuta_frequenza` | BIGINT | Partite IVA con imposta a debito |
| `imposta_dovuta_eur` | DOUBLE | Imposta IVA dovuta (€) |
| `imposta_credito_frequenza` | BIGINT | Partite IVA con imposta a credito |
| `imposta_credito_eur` | DOUBLE | IVA a credito (€) |

Le **frequenze** (numero di partite IVA che dichiarano ciascuna voce) sono
fondamentali per calcoli pro-capite corretti e per l'analisi contribuenti a
credito vs a debito. Le medie MEF non sono esposte: si ricalcolano come
Ammontare / Frequenza.

## Esecuzione

```bash
# dal root del repo
toolkit run -c datasets/iva-regionale/dataset.yml
make run        # tutti i dataset del repo
```

Fonte scaricata via `http_file` (URL MEF con `{year}` nel path);
`read.skip: 9` salta le 8 righe di metadati e la riga vuota (header sempre
alla riga 10).

## Issue di riferimento

- Intake: [#551](https://github.com/dataciviclab/dataset-incubator/issues/551)

## Note metodologiche

- **"Non indicata" esclusa**: il clean scarta la riga `TOTALE` e la riga
  `Non indicata` (contribuenti con regione indeterminata). I totali nazionali
  delle mart sono la somma delle **21 regioni dichiarate** (~4.649 mld nel
  2023), non il totale MEF ufficiale (~4.737 mld, che include ~88 mld di
  "Non indicata" = ~1,9%). Citare come "totale regioni dichiarate".
- **Denominatori pro-capite**: usano la frequenza della voce, non i
  contribuenti totali (es. `va_per_dichiarante = va_fiscale_eur /
  va_frequenza`). Usare i contribuenti totali distorce il valore.
- **Data masking**: `***` nel sorgente MEF (meno di 3 contribuenti) → NULL.
