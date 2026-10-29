# irpef-imposta-tipologia

**Domanda guida:** Chi paga l'IRPEF in Italia, e quanto paga ciascuna tipologia di contribuente?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** AETPTOT0401 (Persone fisiche totali — Confronto tra imposte nette)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; letto per **posizione** (`read.skip: 9`, tutte le colonne `VARCHAR`, `encoding: cp1252`)
**Copertura:** 2012–2024 (13 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (es. `2025AETPTOT0401` = dichiarazioni 2025). Il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)

## Schema (5 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta |
| `tipologia` | VARCHAR | Tipologia di soggetto in base al reddito prevalente (canonica, vedi note) |
| `numero_contribuenti` | INTEGER | Contribuenti della tipologia |
| `imposta_netta_frequenza` | INTEGER | Contribuenti con imposta netta positiva |
| `imposta_netta_eur` | DOUBLE | Imposta netta (€) |

## Mart

- `mart_tipologie_anno` — tipologia × anno: contribuenti, imposta netta, **imposta media per contribuente**, quota sull'imposta nazionale, `rank_imposta`
- `mart_anno` — nazionale per anno (multi-year): contribuenti, imposta netta, imposta media per contribuente, variazione % sull'anno precedente

## Cosa dicono i dati

**L'84,8% dell'IRPEF italiana viene da dipendenti e pensionati.**

| tipologia (a.i. 2024) | contribuenti | imposta netta | quota | media per contribuente |
|---|---|---|---|---|
| Lavoratore dipendente | 23.072.978 | **106,4 mld** | 53,9% | 4.612 € |
| Pensionato | 13.534.816 | **61,0 mld** | 30,9% | 4.503 € |
| Lavoratore autonomo abituale con partita IVA | 343.618 | **10,1 mld** | 5,1% | 29.344 € |
| Partecipante in società di persone | 892.638 | **8,7 mld** | 4,4% | 9.711 € |
| Imprenditore | 861.423 | **6,9 mld** | 3,5% | 8.001 € |
| Proprietario di fabbricati | 1.524.560 | **2,8 mld** | 1,4% | 1.860 € |
| **totale** | **42.837.963** | **197,4 mld** | 100% | 4.608 € |

- **Trend**: l'imposta netta passa da **152,3 mld** (a.i. 2012) a **197,4 mld** (a.i. 2024), **+29,6%**, con i contribuenti quasi stabili. La media per contribuente sale da 3.677 € a 4.608 €.
- **Imposta media più alta**: plusvalenze di natura finanziaria (42.331 €), redditi da capitale (32.377 €), autonomi con partita IVA (29.344 €) — contro 4.612 € dei dipendenti e 1.860 € dei proprietari di fabbricati.
- **Il 2020** è l'unico anno di calo dell'imposta (159,3 mld): l'effetto del blocco pandemico.

## Note metodologiche

- **✅ Le tipologie sono additive**: la somma delle righe coincide con la riga `TOTALE` della fonte (verificato: differenza 0 sui contribuenti e ±1.000 € sull'imposta, arrotondamento). Si possono sommare e calcolare quote senza doppio conteggio.
- **⚠️ `encoding: cp1252` è obbligatorio.** I file fino al 2019 (e il 2021) contengono un byte `0xC3` isolato al posto della "a" accentata di "società". Con `encoding: utf-8` DuckDB **scarta la riga in silenzio** (verificato: file 2019 → 18 righe con utf-8, **19** con cp1252) e la somma delle tipologie non coinciderebbe più con il `TOTALE`.
- **⚠️ `tipologia` è canonica, derivata dal codice della fonte.** Le etichette di origine variano tra anni (accento rotto, `societa'` vs `società`, `Autonomo/Provv/Diversi da 770` vs `da Mod.CU`) e **i codici 14–16 cambiano significato dal file 2019** (a.i. 2018): la fonte inserisce "Regime fiscale agevolato" come 14 e fa slittare 14→15 e 15→16. Il dataset espone quindi **solo la `tipologia` canonica** (serie continua) e **non il codice**, che non è una chiave stabile tra anni.
- **Copertura dal 2012** (file 2013): il file 2012 non ha la colonna `Codice` (6 celle invece di 7) e non è coperto dalla lettura posizionale.
- **Righe escluse**: la riga di header (letta come dato, codice `Codice`), `TOTALE` (codice `0`) e la nota finale.
- **Denominatore della media**: `imposta_media_contribuente_eur` divide l'imposta netta per **tutti** i contribuenti della tipologia, non solo per quelli con imposta positiva (`imposta_netta_frequenza`: 19.754.053 dei 23.072.978 dipendenti).
- **`***` = dato oscurato dalla fonte**: in questa vista non ne compaiono.
