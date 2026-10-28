# irap_vp_regime

**Domanda guida:** Come si compone il valore della produzione IRAP tra i regimi contabili, e quanto pesano le deduzioni?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** DIRTOT020001 (IRAP — Valore della produzione per regime — Regione)
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
| `cod_regione` | VARCHAR | Codice ISTAT regione (condiviso da Trento e Bolzano) |
| `contribuenti` | INTEGER | Contribuenti IRAP della regione |
| `vp_ord_freq` | INTEGER | Valore produzione, contabilità ordinaria e semplificata — numero dichiarazioni |
| `vp_ord_eur` | DOUBLE | Valore produzione, contabilità ordinaria e semplificata — importo (€) |
| `vp_forf_freq` | INTEGER | Valore produzione, regime forfetario — numero dichiarazioni |
| `vp_forf_eur` | DOUBLE | Valore produzione, regime forfetario — importo (€) |
| `vp_agr_freq` | INTEGER | Valore produzione, produttori agricoli — numero dichiarazioni |
| `vp_agr_eur` | DOUBLE | Valore produzione, produttori agricoli — importo (€) |
| `vp_arti_freq` | INTEGER | Valore produzione, arti e professioni — numero dichiarazioni |
| `vp_arti_eur` | DOUBLE | Valore produzione, arti e professioni — importo (€) |
| `vp_noncomm_freq` | INTEGER | Valore produzione, enti non commerciali — numero dichiarazioni |
| `vp_noncomm_eur` | DOUBLE | Valore produzione, enti non commerciali — importo (€) |
| `deduzioni_freq` | INTEGER | Deduzioni — numero dichiarazioni |
| `deduzioni_eur` | DOUBLE | Deduzioni — importo (€) |
| `prod_netta_freq` | INTEGER | Produzione netta — numero dichiarazioni |
| `prod_netta_eur` | DOUBLE | Produzione netta (€) |

## Mart

- `mart_regioni_anno` — regione × anno: valore della produzione per regime (ordinaria, forfetario, agricolo, arti e professioni, non commerciali), deduzioni, produzione netta, quota nazionale e `rank_produzione`

## Cosa dicono i dati

- A.i. 2023: valore della produzione **874,1 mld** in contabilità ordinaria/semplificata, **132,1 mld** per gli enti non commerciali, **9,1 mld** per arti e professioni; **deduzioni 489,6 mld** → **produzione netta 526,4 mld**.
- **Produzione netta = somma dei regimi − deduzioni** (verificato: 1.016,1 − 489,6 = 526,4 mld a.i. 2023). Le deduzioni valgono il **48,2%** del valore della produzione: è la ragione per cui la base IRAP è molto più piccola del valore prodotto.

## Note metodologiche

- **⚠️ I regimi sono un perimetro, non componenti da sommare alla produzione netta**: la somma dei cinque regimi **è** il valore della produzione; la netta si ottiene sottraendo le deduzioni.
- **Lettura posizionale**: l'header è corrotto in alcuni anni (nomi colonna che cambiano anche nell'encoding), quindi si legge per posizione con nomi propri.
- **Righe escluse**: header, `TOTALE` e nota finale. Il break di definizione IRAP a.i. 2014→2015 vale anche qui: i trend si leggono dal 2015.
- **Perimetro**: fonte MEF `analisi_stat`; valori raw in migliaia di euro, convertiti in euro (×1000). Le colonne "Media" della fonte sono scartate (si ricalcolano da frequenza e ammontare).
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
