# acsp-professionisti-regione

**Domanda guida:** Quanto reddito e quanti compensi dichiarano le società di persone professionali in ogni regione?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** ACSPPROF0201 (Professionisti — Regione)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; letto per **posizione** (`read.skip: 9`, tutte le colonne `VARCHAR`)
**Copertura:** 2018–2024 (7 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (es. `2025ACSPPROF0201` = dichiarazioni 2025). Il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)

## Schema (30 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta |
| `regione` | VARCHAR | Denominazione regione |
| `cod_regione` | VARCHAR | Codice della fonte (ISTAT regione; condiviso da Trento e Bolzano) |
| `numero_societa` | INTEGER | Società di persone dichiaranti |
| `reddito_lavoro_autonomo_frequenza` | INTEGER | Reddito da lavoro autonomo — numero dichiarazioni |
| `reddito_lavoro_autonomo_eur` | DOUBLE | Reddito da lavoro autonomo — importo (€) |
| `perdita_lavoro_autonomo_frequenza` | INTEGER | Perdita da lavoro autonomo — numero dichiarazioni |
| `perdita_lavoro_autonomo_eur` | DOUBLE | Perdita da lavoro autonomo — importo (€) |
| `reddito_partecipazione_associazione_frequenza` | INTEGER | Reddito di partecipazione di associazioni tra artisti e professionisti — numero dichiarazioni |
| `reddito_partecipazione_associazione_eur` | DOUBLE | Reddito di partecipazione di associazioni tra artisti e professionisti — importo (€) |
| `capitali_diversi_frequenza` | INTEGER | Reddito da capitali e diversi — numero dichiarazioni |
| `capitali_diversi_eur` | DOUBLE | Reddito da capitali e diversi — importo (€) |
| `totale_reddito_frequenza` | INTEGER | Totale reddito dichiarato — numero dichiarazioni |
| `totale_reddito_eur` | DOUBLE | Totale reddito dichiarato — importo (€) |
| `totale_perdita_frequenza` | INTEGER | Totale perdita dichiarata — numero dichiarazioni |
| `totale_perdita_eur` | DOUBLE | Totale perdita dichiarata — importo (€) |
| `compensi_non_annotati_isa_frequenza` | INTEGER | Compensi non annotati rilevati con ISA — numero dichiarazioni |
| `compensi_non_annotati_isa_eur` | DOUBLE | Compensi non annotati rilevati con ISA — importo (€) |
| `compensi_non_annotati_frequenza` | INTEGER | Compensi non annotati nelle scritture contabili — numero dichiarazioni |
| `compensi_non_annotati_eur` | DOUBLE | Compensi non annotati nelle scritture contabili — importo (€) |
| `compensi_frequenza` | INTEGER | Compensi — numero dichiarazioni |
| `compensi_eur` | DOUBLE | Compensi — importo (€) |
| `spese_immobili_frequenza` | INTEGER | Spese relative agli immobili — numero dichiarazioni |
| `spese_immobili_eur` | DOUBLE | Spese relative agli immobili — importo (€) |
| `spese_lavoro_dipendente_frequenza` | INTEGER | Spese per prestazioni di lavoro dipendente — numero dichiarazioni |
| `spese_lavoro_dipendente_eur` | DOUBLE | Spese per prestazioni di lavoro dipendente — importo (€) |
| `compensi_terzi_frequenza` | INTEGER | Compensi corrisposti a terzi — numero dichiarazioni |
| `compensi_terzi_eur` | DOUBLE | Compensi corrisposti a terzi — importo (€) |
| `totale_spese_frequenza` | INTEGER | Totale spese — numero dichiarazioni |
| `totale_spese_eur` | DOUBLE | Totale spese — importo (€) |

## Mart

- `mart_regione_anno` — regione × anno: numero società, totale reddito dichiarato, reddito medio per società, quota sul totale nazionale, `rank_reddito`
- `mart_anno` — nazionale per anno (multi-year): numero società, reddito totale, reddito medio per società, variazione % sull'anno precedente

## Note metodologiche

- **⚠️ Le colonne NON sono additive.** `compensi` (14,98 mld ad a.i. 2023) e `totale_spese` (7,56 mld) sono flussi **lordi**; `totale_reddito` (7,44 mld) è il **netto**. Sommarli non ha senso. Anche le voci di spesa (`spese_immobili`, `spese_lavoro_dipendente`, `compensi_terzi`) sono un sottoinsieme di `totale_spese`.
- **Perimetro**: società di persone (modello ACSP) — Professionisti. Le società di capitali (modello UNICO SC) non sono incluse.
- **Anno d'imposta**: `anno` è l'anno d'imposta (l'URL MEF usa l'anno di presentazione, `{year}` = anno d'imposta + 1).
- **Valori in migliaia di euro**: gli `*_eur` sono convertiti in euro (×1000). Le colonne "Media" della fonte sono scartate.
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
- **`TOTALE` e riga-nota escluse**: la fonte ha le righe di dettaglio + una riga `TOTALE` + una nota finale ("Ammontare e media in migliaia di euro"). Il clean tiene solo le righe di dettaglio, quindi i totali nazionali differiscono dalla riga `TOTALE` solo per l'arrotondamento per riga.
- **Lettura per posizione**: la vista è letta con `read.skip: 9` e tutte le colonne `VARCHAR` (`source: config_only`). Con `source: auto` lo sniffing di DuckDB tipizzerebbe `DOUBLE` le colonne i cui valori hanno un solo punto (es. `"121.330"`) e le macro `normalize_italian_*` le corromperebbero (×10/÷10); l'inferenza è per file, quindi un campione di anni non basta a escluderlo.
- **Copertura 2018–2024** (7 anni): prima del file 2019 (a.i. 2018) la fonte usa nomi e definizioni diversi per le voci sui compensi non annotati (`corrispettivi non annotati` con adeguamento **studi di settore** → `compensi non annotati` con **ISA**). Le posizioni delle colonne restano le stesse, ma la definizione cambia: per non pubblicare un salto non documentato il dataset parte dal 2019.
- **Blocco di misure unico**: `compensi`, `spese_*` e `totale_spese` non esistono negli altri dataset del repo. A.i. 2023: 14,98 mld di compensi, 7,56 mld di spese (**50%** dei compensi), 7,43 mld di reddito da lavoro autonomo.
- **`reddito_partecipazione_associazione` è inutilizzabile**: `NULL` nel **41%** delle righe (mascheramento della fonte). `capitali_diversi` è `NULL` nel 26%.
