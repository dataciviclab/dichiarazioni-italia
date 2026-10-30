# irpef-calcolo-tipologia

**Domanda guida:** Quanto si paga di IRPEF *lordo*, quanto lo Stato restituisce in detrazioni, e quanto resta netto — per tipologia di contribuente e regione?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** famiglia `AETIP*0201` — *"Persone fisiche in base al reddito prevalente / Calcolo dell'Irpef / Regione"*
**Formato:** CSV `;` con 8 righe di metadati + riga vuota → header a riga 10 (`skip: 9`), tutte le colonne `VARCHAR`, lettura **posizionale**
**Copertura:** 2013–2024 (12 anni, anno d'imposta)
**Nota:** il file MEF usa l'anno di presentazione (`{year}AETIPLD0201` = dichiarazioni a.i. `{year} - 1`)
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)

## Le sei viste

Schema identico (18 colonne), popolazioni diverse. La tipologia **non è nel dato**: arriva da `inject_column` in `dataset.yml`.

| vista | tipologia | cod |
|---|---|---|
| `AETIPLD0201` | Lavoratori dipendenti | `LD` |
| `AETIPPE0201` | Pensionati | `PE` |
| `AETPFGA0201` | Imprenditori | `IM` |
| `AETPREA0201` | Lavoratori autonomi abituali con partita IVA | `AU` |
| `AETPRHA0201` | Partecipanti in società di persone ed assimilate | `SP` |
| `AETIPRB0201` | Proprietari di fabbricati | `PF` |

## Schema del clean (16 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta (`{year} - 1`) |
| `regione` | VARCHAR | Regione (21: Trentino diviso in P.A. Trento e Bolzano) |
| `cod_regione` | VARCHAR | Codice ISTAT regione |
| `cod_tipologia` | VARCHAR | Codice della tipologia (da `inject_column`) |
| `tipologia` | VARCHAR | Tipologia di contribuente (reddito prevalente) |
| `contribuenti` | BIGINT | Contribuenti della cella |
| `reddito_complessivo_frequenza` / `reddito_complessivo_eur` | BIGINT / DOUBLE | Dichiarazioni e reddito complessivo al netto della cedolare secca |
| `reddito_imponibile_frequenza` / `reddito_imponibile_eur` | BIGINT / DOUBLE | Dichiarazioni e reddito imponibile |
| `imposta_lorda_frequenza` / `imposta_lorda_eur` | BIGINT / DOUBLE | Dichiarazioni e **imposta lorda** |
| `detrazioni_frequenza` / `detrazioni_eur` | BIGINT / DOUBLE | Dichiarazioni e **totale detrazioni** |
| `imposta_netta_frequenza` / `imposta_netta_eur` | BIGINT / DOUBLE | Dichiarazioni e imposta netta |

## Mart

- `mart_tipologie_anno` — tipologia × anno (multi-anno, 72 righe): contribuenti, reddito complessivo/imponibile, lorda, detrazioni, netta, **aliquota lorda**, **aliquota netta**, **incidenza detrazioni**, quota su contribuenti e imposta delle sei viste, delta % annui, rank.
- `mart_regioni_anno` — regione × anno × tipologia (1.512 righe): le stesse metriche più reddito imponibile medio e imposta netta media per contribuente, con rank per tipologia.

## Cosa dicono i dati

A.i. 2023 (ultimo anno completo):

| Tipologia | Contribuenti | Imposta lorda | Detrazioni | Imposta netta | Detrazioni / lorda |
|---|---:|---:|---:|---:|---:|
| Lavoratori dipendenti | 22.700.231 | 149,80 mld € | 50,68 mld € | 101,19 mld € | **33,8%** |
| Pensionati | 13.526.465 | 78,36 mld € | 22,79 mld € | 57,37 mld € | 29,1% |
| Lavoratori autonomi P.IVA | 354.964 | 11,12 mld € | 0,86 mld € | 10,30 mld € | **7,8%** |
| Partecipanti s.d.p. | 933.376 | 10,47 mld € | 1,25 mld € | 9,39 mld € | 12,0% |
| Imprenditori | 890.472 | 8,03 mld € | 1,27 mld € | 7,01 mld € | 15,8% |
| Proprietari di fabbricati | 1.541.602 | 3,85 mld € | 1,48 mld € | 2,78 mld € | 38,4% |
| **Totale sei viste** | **39.947.110** | **261,64 mld €** | **78,33 mld €** | **188,05 mld €** | **29,9%** |

- **Le detrazioni valgono il 34% della lorda per i dipendenti e l'8% per le partite IVA**: due sistemi fiscali dentro la stessa imposta.
- **Aliquota lorda**: 36,2% per gli autonomi con P.IVA, 27,0% per i dipendenti. Il vantaggio degli autonomi sta nel lordo, non solo nelle detrazioni.
- **I proprietari di fabbricati** hanno l'incidenza detrazioni più alta (38,4%) su un'imposta lorda piccola.

## Note metodologiche

- ⚠️ **Le sei tipologie non sono una partizione dell'IRPEF.** Coprono **39.947.110 contribuenti su 42.570.078 (93,8%)** e **188,05 mld su 189,94 di imposta netta (99,0%)** a.i. 2023. Non sommarle per ottenere il totale nazionale: per quello c'è `irpef_imposta_tipologia`.
- ⚠️ **`AETPFGA0201` contiene due righe `TOTALE`**, la seconda con valori esattamente doppi (890.472 → 1.780.944 contribuenti a.i. 2023). Il clean esclude per **codice `0`**, non per etichetta: filtrando per nome il dataset raddoppierebbe.
- ⚠️ **`Non indicata`** compare in 4 viste su 6 (22 righe non-totale invece di 21): esclusa come negli altri dataset regionali. Per questo i totali delle sei viste sono leggermente inferiori a quelli della riga `TOTALE` della fonte.
- **Lettura posizionale obbligatoria**: l'header è instabile e i numeri sono in formato italiano. Con `source: auto` lo sniffer tipizza `DOUBLE` le colonne ambigue e le macro `normalize_italian_*` le corrompono (×10 / ÷10).
- **`normalize_rows_to_columns` non è utilizzabile**: quel percorso registra un DataFrame e perde `inject_column`, quindi la tipologia non arriverebbe.
- **Anni pre-2013 esclusi**: i file 2012–2013 esistono ma hanno **17 colonne** (manca `Codice`); i file 2010–2011 restituiscono HTTP 200 con 0 byte.
- **`AETPTOT0201` non è questa famiglia**: è "Incrocio redditi / Tipologia di reddito dichiarato". Non usarla come totale.
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
