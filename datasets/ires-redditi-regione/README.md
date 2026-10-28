# ires_redditi_regione

**Domanda guida:** Quanto reddito d'impresa dichiarano le società di capitali, e dove?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** BASCTOT020101 (Società di capitali — Redditi d'impresa — Regione)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; letto per **posizione** (`read.skip: 9`, tutte le colonne `VARCHAR`)
**Copertura:** 2014–2023 (10 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (file 2015–2024); il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)


## Schema

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta |
| `regione` | VARCHAR | Denominazione regione (21: Trentino diviso in P.A. Trento e Bolzano) |
| `n_dichiarazioni` | INTEGER | Dichiarazioni IRES presentate |
| `reddito_continuita_freq` | INTEGER | Reddito d'impresa in continuità — numero dichiarazioni |
| `reddito_continuita_eur` | DOUBLE | Reddito d'impresa in continuità — importo (€) |
| `perdita_continuita_freq` | INTEGER | Perdita d'impresa in continuità — numero dichiarazioni |
| `perdita_continuita_eur` | DOUBLE | Perdita d'impresa in continuità — importo (€) |
| `reddito_totale_freq` | INTEGER | Reddito d'impresa totale — numero dichiarazioni |
| `reddito_totale_eur` | DOUBLE | Reddito d'impresa totale — importo (€) |
| `perdita_totale_freq` | INTEGER | Perdita d'impresa totale — numero dichiarazioni |
| `perdita_totale_eur` | DOUBLE | Perdita d'impresa totale — importo (€) |

## Mart

- `mart_regioni_anno` — regione × anno: dichiarazioni, reddito e perdita (totale e in continuità), reddito medio per dichiarazione, quota e `rank_reddito`

## Cosa dicono i dati

- **1.383.554 dichiarazioni** (a.i. 2023), **287,8 mld** di reddito d'impresa e **74,3 mld** di perdite dichiarate.
- È il lato **società di capitali** del sistema: si confronta con le società di persone (`acsp_*`) e con le partite IVA (`abpf_*`).

## Note metodologiche

- **⚠️ Reddito e perdita non si sommano**: sono due esiti alternativi della stessa dichiarazione (un'impresa dichiara reddito *o* perdita). Il saldo si legge come `reddito − perdita`.
- **Fix #21**: prima della correzione la lettura con `source: auto` tipizzava `DOUBLE` le frequenze e le macro le corrompevano — **112 celle sbagliate** su 10 anni (es. Molise `3.220` → `322`).
- **Righe escluse**: header (letto come dato), `TOTALE` e nota finale.
- **Perimetro**: fonte MEF `analisi_stat`; valori raw in migliaia di euro, convertiti in euro (×1000). Le colonne "Media" della fonte sono scartate (si ricalcolano da frequenza e ammontare).
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
