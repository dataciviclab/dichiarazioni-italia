# acsp-imprese-regione

**Domanda guida:** Quanto reddito dichiarano le società di persone con reddito d'impresa, e come si determina il loro reddito?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** ACSPIMP0201 (Imprese — Tematica personalizzata — Regione)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; letto per **posizione** (`read.skip: 9`, tutte le colonne `VARCHAR`)
**Copertura:** 2014–2024 (11 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (es. `2025ACSPIMP0201` = dichiarazioni 2025). Il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)

## Schema (48 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta |
| `regione` | VARCHAR | Denominazione regione (21: Trentino diviso in P.A. Trento e Bolzano) |
| `cod_regione` | VARCHAR | Codice ISTAT regione (condiviso da Trento e Bolzano) |
| `numero_imprenditori` | INTEGER | Imprenditori dichiaranti |
| `reddito_impresa_ordinaria_frequenza` | INTEGER | Reddito di impresa in contabilità ordinaria — numero dichiarazioni |
| `reddito_impresa_ordinaria_eur` | DOUBLE | Reddito di impresa in contabilità ordinaria — importo (€) |
| `reddito_impresa_semplificata_frequenza` | INTEGER | Reddito di impresa in contabilità semplificata — numero dichiarazioni |
| `reddito_impresa_semplificata_eur` | DOUBLE | Reddito di impresa in contabilità semplificata — importo (€) |
| `reddito_partecipazione_frequenza` | INTEGER | Reddito di partecipazione — numero dichiarazioni |
| `reddito_partecipazione_eur` | DOUBLE | Reddito di partecipazione — importo (€) |
| `capitali_diversi_frequenza` | INTEGER | Reddito di capitali e diversi — numero dichiarazioni |
| `capitali_diversi_eur` | DOUBLE | Reddito di capitali e diversi — importo (€) |
| `redditi_tassazione_separata_frequenza` | INTEGER | Redditi soggetti a tassazione separata — numero dichiarazioni |
| `redditi_tassazione_separata_eur` | DOUBLE | Redditi soggetti a tassazione separata — importo (€) |
| `totale_reddito_frequenza` | INTEGER | Totale reddito dichiarato — numero dichiarazioni |
| `totale_reddito_eur` | DOUBLE | Totale reddito dichiarato — importo (€) |
| `totale_perdita_frequenza` | INTEGER | Totale perdita dichiarata — numero dichiarazioni |
| `totale_perdita_eur` | DOUBLE | Totale perdita dichiarata — importo (€) |
| `utile_conto_economico_frequenza` | INTEGER | Utile risultante dal conto economico — numero dichiarazioni |
| `utile_conto_economico_eur` | DOUBLE | Utile risultante dal conto economico — importo (€) |
| `perdita_conto_economico_frequenza` | INTEGER | Perdita risultante dal conto economico — numero dichiarazioni |
| `perdita_conto_economico_eur` | DOUBLE | Perdita risultante dal conto economico — importo (€) |
| `variazioni_aumento_frequenza` | INTEGER | Variazioni in aumento — numero dichiarazioni |
| `variazioni_aumento_eur` | DOUBLE | Variazioni in aumento — importo (€) |
| `variazioni_diminuzione_frequenza` | INTEGER | Variazioni in diminuzione — numero dichiarazioni |
| `variazioni_diminuzione_eur` | DOUBLE | Variazioni in diminuzione — importo (€) |
| `erogazioni_liberali_blocco1_frequenza` | INTEGER | Erogazioni liberali (1° blocco — contabilità ordinaria) — numero dichiarazioni |
| `erogazioni_liberali_blocco1_eur` | DOUBLE | Erogazioni liberali (1° blocco — contabilità ordinaria) — importo (€) |
| `reddito_impresa_blocco1_frequenza` | INTEGER | Reddito di impresa (1° blocco — contabilità ordinaria) — numero dichiarazioni |
| `reddito_impresa_blocco1_eur` | DOUBLE | Reddito di impresa (1° blocco — contabilità ordinaria) — importo (€) |
| `perdita_impresa_blocco1_frequenza` | INTEGER | Perdita di impresa (1° blocco — contabilità ordinaria) — numero dichiarazioni |
| `perdita_impresa_blocco1_eur` | DOUBLE | Perdita di impresa (1° blocco — contabilità ordinaria) — importo (€) |
| `ricavi_vendite_frequenza` | INTEGER | Ricavi delle vendite — numero dichiarazioni |
| `ricavi_vendite_eur` | DOUBLE | Ricavi delle vendite — importo (€) |
| `componenti_positivi_frequenza` | INTEGER | Componenti positivi — numero dichiarazioni |
| `componenti_positivi_eur` | DOUBLE | Componenti positivi — importo (€) |
| `componenti_negativi_frequenza` | INTEGER | Componenti negativi — numero dichiarazioni |
| `componenti_negativi_eur` | DOUBLE | Componenti negativi — importo (€) |
| `differenza_frequenza` | INTEGER | Differenza (componenti positivi − negativi) — numero dichiarazioni |
| `differenza_eur` | DOUBLE | Differenza (componenti positivi − negativi) — importo (€) |
| `erogazioni_liberali_blocco2_frequenza` | INTEGER | Erogazioni liberali (2° blocco — contabilità semplificata) — numero dichiarazioni |
| `erogazioni_liberali_blocco2_eur` | DOUBLE | Erogazioni liberali (2° blocco — contabilità semplificata) — importo (€) |
| `reddito_impresa_blocco2_frequenza` | INTEGER | Reddito di impresa (2° blocco — contabilità semplificata) — numero dichiarazioni |
| `reddito_impresa_blocco2_eur` | DOUBLE | Reddito di impresa (2° blocco — contabilità semplificata) — importo (€) |
| `perdita_impresa_blocco2_frequenza` | INTEGER | Perdita di impresa (2° blocco — contabilità semplificata) — numero dichiarazioni |
| `perdita_impresa_blocco2_eur` | DOUBLE | Perdita di impresa (2° blocco — contabilità semplificata) — importo (€) |
| `altri_ricavi_frequenza` | INTEGER | Altri ricavi — numero dichiarazioni |
| `altri_ricavi_eur` | DOUBLE | Altri ricavi — importo (€) |

## Mart

- `mart_regione_anno` — regione × anno: numero imprenditori, totale reddito e perdita, reddito medio per imprenditore, quota sul totale nazionale, `rank_reddito`
- `mart_anno` — nazionale per anno (multi-year): numero imprenditori, reddito e perdita, **determinazione del reddito d'impresa** (contabilità ordinaria/semplificata, `*_blocco1`/`*_blocco2`, ricavi, componenti, differenza), reddito medio per imprenditore, variazione % sull'anno precedente

## Ruolo nella famiglia ACSP

La famiglia ACSP (società di persone) è una **gerarchia** (verificata, somme esatte):

```
tutte                    672.150 soggetti   34,14 mld
├─ titolari P.IVA        641.742            33,70
│  ├─ agricoltori         55.880             0,51
│  ├─ imprese            552.905            25,75   ← questo dataset
│  └─ professionisti      32.957             7,44
└─ non titolari           30.408             0,43
```

**Imprese è il pezzo dominante**: 82,3% dei soggetti e 75,4% del reddito delle società di persone (a.i. 2023). Con `agricoltori`, `professionisti` e `non titolari` la scomposizione per tipologia è completa (e `titolari P.IVA` si ricava per somma dei tre sotto-gruppi).

## Note metodologiche

- **⚠️ Le colonne NON sono additive.** Ogni voce è dichiarata su una riga diversa del modello: `totale_reddito` (25,75 mld ad a.i. 2023) non è la somma delle voci di dettaglio.
- **⚠️ Anomalia della fonte ad a.i. 2017.** Il reddito di impresa in contabilità semplificata crolla a **4,11 mld** (da 10,12 ad a.i. 2016, risale a 9,62) e le perdite dichiarate saltano a **6,27 mld** (da 2,18 e 1,82 negli anni adiacenti), mentre le dichiarazioni calano regolarmente. **L'anomalia è nella riga `TOTALE` della fonte**, non è un artefatto della pipeline (vedi issue #25). Il resto è verificato cella per cella.
- **⚠️ Due blocchi di colonne con lo stesso nome.** La fonte ha `Erogazioni liberali`, `Reddito di impresa` e `Perdita di impresa` **due volte** (posizioni 36-44 e 57-65). Qui sono disambiguati come `*_blocco1` / `*_blocco2`. L'aritmetica identifica il blocco centrale (`ricavi_vendite`, `componenti_positivi`, `componenti_negativi`, `differenza`) come la determinazione in **contabilità semplificata** (`differenza = componenti_positivi − componenti_negativi`, verificato), quindi `_blocco1` corrisponde alla contabilità ordinaria e `_blocco2` alla semplificata — **la fonte non etichetta i blocchi**: la corrispondenza è un'inferenza documentata, non una dichiarazione della fonte. L'inferenza è **protetta da una guardia**: `mart_anno.rapporto_blocco1_ordinaria` vale 1,07–1,19 su tutti gli anni (se la fonte riordinasse i blocchi darebbe ~0,84–0,94) e ha una range rule `[0.97, 1.5]` in `dataset.yml` → la pipeline fallisce invece di scambiare le etichette in silenzio.
- **Copertura dal 2014** (file 2015): il file 2014 ha un layout diverso (73 celle, 3 colonne `Ricavi di cui art. 85 a) e b)` in più e 3 posizioni spostate) → non coperto dalla lettura posizionale. Dal 2015 al 2025 l'ordine delle colonne è identico.
- **Perimetro**: società di persone (modello ACSP) — Imprese. Le società di capitali (modello UNICO SC) non sono incluse.
- **Anno d'imposta**: `anno` è l'anno d'imposta (l'URL MEF usa l'anno di presentazione, `{year}` = anno d'imposta + 1).
- **Valori in migliaia di euro**: gli `*_eur` sono convertiti in euro (×1000). Le colonne "Media" della fonte sono scartate.
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
- **`TOTALE` e riga-nota escluse**: il clean tiene solo le righe di dettaglio.
- **Lettura per posizione**: `read.skip: 9` e tutte le colonne `VARCHAR` (`source: config_only`). Con `source: auto` lo sniffing di DuckDB tipizzerebbe `DOUBLE` le colonne i cui valori hanno un solo punto (es. `"121.330"`) e le macro `normalize_italian_*` le corromperebbero (×10/÷10).
- **Trentino-Alto Adige**: le due province autonome hanno entrambe `cod_regione = '04'`: la chiave è `[anno, regione]`.
