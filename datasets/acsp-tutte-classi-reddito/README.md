# acsp-tutte-classi-reddito

**Domanda guida:** Come si distribuiscono le società di persone tra le classi di reddito dichiarato?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** ACSPGEN0202 (Tutte le tipologie di contribuenti — Classi di reddito dichiarato in euro)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; letto per **posizione** (`read.skip: 9`, tutte le colonne `VARCHAR`)
**Copertura:** 2013–2024 (12 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (es. `2025ACSPGEN0202` = dichiarazioni 2025). Il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)

## Schema (28 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta |
| `classe_reddito` | VARCHAR | Denominazione classe di reddito |
| `codice` | VARCHAR | Codice della fonte |
| `numero_societa` | INTEGER | Società di persone dichiaranti |
| `totale_reddito_frequenza` | INTEGER | Totale reddito dichiarato — numero dichiarazioni |
| `totale_reddito_eur` | DOUBLE | Totale reddito dichiarato — importo (€) |
| `totale_perdita_frequenza` | INTEGER | Totale perdita dichiarata — numero dichiarazioni |
| `totale_perdita_eur` | DOUBLE | Totale perdita dichiarata — importo (€) |
| `reddito_continuita_frequenza` | INTEGER | Reddito dichiarato in continuità d'esercizio — numero dichiarazioni |
| `reddito_continuita_eur` | DOUBLE | Reddito dichiarato in continuità d'esercizio — importo (€) |
| `perdita_continuita_frequenza` | INTEGER | Perdita dichiarata in continuità d'esercizio — numero dichiarazioni |
| `perdita_continuita_eur` | DOUBLE | Perdita dichiarata in continuità d'esercizio — importo (€) |
| `reddito_impresa_ordinaria_frequenza` | INTEGER | Reddito di impresa in contabilità ordinaria — numero dichiarazioni |
| `reddito_impresa_ordinaria_eur` | DOUBLE | Reddito di impresa in contabilità ordinaria — importo (€) |
| `reddito_impresa_semplificata_frequenza` | INTEGER | Reddito di impresa in contabilità semplificata — numero dichiarazioni |
| `reddito_impresa_semplificata_eur` | DOUBLE | Reddito di impresa in contabilità semplificata — importo (€) |
| `reddito_lavoro_autonomo_frequenza` | INTEGER | Reddito da lavoro autonomo — numero dichiarazioni |
| `reddito_lavoro_autonomo_eur` | DOUBLE | Reddito da lavoro autonomo — importo (€) |
| `terreni_imponibile_frequenza` | INTEGER | Reddito dei terreni imponibile — numero dichiarazioni |
| `terreni_imponibile_eur` | DOUBLE | Reddito dei terreni imponibile — importo (€) |
| `terreni_non_imponibile_frequenza` | INTEGER | Reddito dei terreni non imponibile — numero dichiarazioni |
| `terreni_non_imponibile_eur` | DOUBLE | Reddito dei terreni non imponibile — importo (€) |
| `fabbricati_imponibile_frequenza` | INTEGER | Reddito dei fabbricati imponibile — numero dichiarazioni |
| `fabbricati_imponibile_eur` | DOUBLE | Reddito dei fabbricati imponibile — importo (€) |
| `fabbricati_non_imponibile_frequenza` | INTEGER | Reddito dei fabbricati non imponibile — numero dichiarazioni |
| `fabbricati_non_imponibile_eur` | DOUBLE | Reddito dei fabbricati non imponibile — importo (€) |
| `capitali_diversi_frequenza` | INTEGER | Reddito da capitali e diversi — numero dichiarazioni |
| `capitali_diversi_eur` | DOUBLE | Reddito da capitali e diversi — importo (€) |

## Mart

- `mart_classe_reddito_anno` — classe di reddito × anno: numero società, totale reddito dichiarato, reddito medio per società, quota sul totale nazionale, `rank_reddito`
- `mart_anno` — nazionale per anno (multi-year): numero società, reddito totale, reddito medio per società, variazione % sull'anno precedente

## Note metodologiche

- **⚠️ Le colonne NON sono additive.** Ogni colonna è una grandezza dichiarata su una **riga diversa** del modello, non una voce di un'unica somma. Ad a.i. 2023 il `totale_reddito_eur` nazionale è 34,14 mld, ma la somma delle voci di dettaglio (impresa ordinaria/semplificata, lavoro autonomo, terreni, fabbricati, capitali) è 32,25 mld: **−5,5%**. Sommare colonne produce numeri sbagliati.
- **⚠️ `reddito_continuita` è un sottoinsieme, non un'alternativa.** Ad a.i. 2023 `totale_reddito_eur` è 34,14 mld e `reddito_continuita_eur` 33,78 mld (**99%**): la variante "in continuità d'esercizio" è quasi tutto il totale. Sommare `totale_reddito` + `reddito_continuita` conta due volte lo stesso reddito.
- **Perimetro**: società di persone (modello ACSP) — Tutte le tipologie di contribuenti. Le società di capitali (modello UNICO SC) non sono incluse.
- **Anno d'imposta**: `anno` è l'anno d'imposta (l'URL MEF usa l'anno di presentazione, `{year}` = anno d'imposta + 1).
- **Valori in migliaia di euro**: gli `*_eur` sono convertiti in euro (×1000). Le colonne "Media" della fonte sono scartate.
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
- **`TOTALE` e riga-nota escluse**: la fonte ha le righe di dettaglio + una riga `TOTALE` + una nota finale ("Ammontare e media in migliaia di euro"). Il clean tiene solo le righe di dettaglio, quindi i totali nazionali differiscono dalla riga `TOTALE` solo per l'arrotondamento per riga.
- **Lettura per posizione**: la vista è letta con `read.skip: 9` e tutte le colonne `VARCHAR` (`source: config_only`). Con `source: auto` lo sniffing di DuckDB tipizzerebbe `DOUBLE` le colonne i cui valori hanno un solo punto (es. `"121.330"`) e le macro `normalize_italian_*` le corromperebbero (×10/÷10); l'inferenza è per file, quindi un campione di anni non basta a escluderlo.
- **⚠️ Anomalia della fonte ad a.i. 2017.** Il reddito di impresa in contabilità semplificata crolla a **4,11 mld** (da 10,12 ad a.i. 2016, risale a 9,62 ad a.i. 2018) e le perdite dichiarate saltano a **6,30 mld** (da 2,20 e 1,84 negli anni adiacenti), mentre il numero di dichiarazioni cala regolarmente. Il reddito medio per dichiarazione si dimezza per un solo anno. **L'anomalia è nella riga `TOTALE` della fonte** (verificata sui file grezzi), non è un artefatto della pipeline: il dato va trattato come sospetto e non letto come trend. Il resto è verificato cella per cella contro la fonte in tutti gli anni.
- **33 classi** di reddito dichiarato, da "minore di -1.000" a "oltre 200.000" euro (le soglie delle classi sono in **euro**, non in migliaia). Le soglie sono stabili dal 2014.
- `codice` è il codice di classe della fonte (`01`–`33`).
- **Concentrazione** (a.i. 2023): il 4,9% delle società (classe "oltre 200.000") dichiara il **38,9%** del reddito; il top 11% ne dichiara il 50%. 30.580 società dichiarano reddito zero.
- **Celle oscurate**: circa il 5% delle righe ha almeno una cella `NULL` (la fonte maschera le combinazioni con poche osservazioni).
