# irap_italia_estero

**Domanda guida:** Quanta produzione netta IRAP viene realizzata all'estero, e da quali regioni?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** DIRTOT030001 (IRAP — Produzione realizzata in Italia e all'estero — Regione)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; letto per **posizione** (`skip: 9`, tutte le colonne `VARCHAR`)
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
| `prod_netta_freq` | INTEGER | Produzione netta totale — numero dichiarazioni |
| `prod_netta_eur` | DOUBLE | Produzione netta totale (€) |
| `vp_estero_freq` | INTEGER | Produzione realizzata all'estero — numero dichiarazioni |
| `vp_estero_eur` | DOUBLE | Produzione realizzata all'estero (€) |
| `vp_italia_freq` | INTEGER | Produzione realizzata in Italia — numero dichiarazioni |
| `vp_italia_eur` | DOUBLE | Produzione realizzata in Italia (€) |

## Mart

- `mart_regioni_anno` — regione × anno: contribuenti, produzione netta, produzione realizzata in Italia e all'estero, quota estera, quota nazionale e `rank_produzione`

## Cosa dicono i dati

- A.i. 2023: **2.110.970 contribuenti**, produzione netta **526,4 mld** — di cui **517,2 mld in Italia** e **9,2 mld all'estero** (1,7%).
- La quota estera è molto diversa per regione: **Liguria 16,0%**, **Sicilia 9,4%**, Lombardia 2,0%.

## Note metodologiche

- **Fix #21**: la colonna `vp_estero_freq` (massimo 1.088 migliaia) veniva tipizzata `DOUBLE` in **2 anni su 10** (2016 e 2022) e la macro la corrompeva: **40 celle ×10** (es. Piemonte 2016 `38` → `380`). Negli altri anni la stessa colonna restava `VARCHAR` — l'inferenza dei tipi è per file.
- **Italia + estero ricompongono la produzione netta** (a.i. 2023: 517,2 + 9,2 = 526,4 mld; lo scarto è di arrotondamento, 0,001%).
- **Righe escluse**: header, `TOTALE`, l'eventuale `Non indicata` e la nota finale.
- **Perimetro**: fonte MEF `analisi_stat`; valori raw in migliaia di euro, convertiti in euro (×1000). Le colonne "Media" della fonte sono scartate (si ricalcolano da frequenza e ammontare).
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
