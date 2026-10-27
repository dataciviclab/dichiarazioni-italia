# irap-imposta-pa-regione

**Domanda guida:** Quanta IRAP pagano le pubbliche amministrazioni, e quanto pesa sul totale?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** DIRTOT0501 (Base imponibile ed imposta relativa alle attività istituzionali esercitate dalle P.A. — Regione)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; scaricato via `http_file`, letto con `read.skip: 9`
**Copertura:** 2014–2023 (10 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (es. `2024DIRTOT0501` = dichiarazioni 2024). Il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)

## Schema (9 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta (URL anno - 1) |
| `regione` | VARCHAR | Denominazione regione (21: Trentino diviso in P.A. Trento e Bolzano) |
| `cod_regione` | VARCHAR | Codice ISTAT regione |
| `base_imponibile_frequenza` | BIGINT | Enti P.A. con base imponibile |
| `base_imponibile_eur` | DOUBLE | Base imponibile IRAP delle P.A. (€) |
| `imposta_netta_frequenza` | BIGINT | Enti P.A. con imposta netta |
| `imposta_netta_eur` | DOUBLE | Imposta netta IRAP delle P.A. (€) |
| `imposta_debito_eur` | DOUBLE | Saldo a debito dopo gli acconti (€) |
| `imposta_credito_eur` | DOUBLE | Saldo a credito dopo gli acconti (€) |

## Mart

- `mart_regioni_anno` — regione × anno: base, imposta netta, **saldo** a debito/credito, aliquota effettiva, quota sulla base nazionale, `rank_imposta`
- `mart_imposta_anno` — nazionale per anno (multi-year): base, imposta, aliquota effettiva, delta % sull'anno precedente

## Note metodologiche

- **Complemento di `irap_imposta_regione`** (vista totale, P.A. incluse): la differenza fra i due è il **settore privato**. Verificato sui totali 2024: totale 30,06 mld di imposta, di cui P.A. **10,61 mld (35,3%)**; base 580,4 mld di cui P.A. 125,2 mld.
- **`imposta_debito_eur` / `imposta_credito_eur` sono il saldo** d'imposta *dopo gli acconti* (chi deve ancora versare / chi ha un credito da riportare o compensare), non una scomposizione di `imposta_netta_eur`: nel 2024 la netta è 10,6 mld contro 0,40 mld di debito e 0,24 mld di credito.
- **Le P.A. pagano un'aliquota effettiva più alta**: 8,47% nel 2023 contro 5,18% del totale — coerente con un perimetro di deduzioni più stretto.
- **`Numero contribuenti` non è esposto**: nella fonte è il totale IRAP della regione (identico a `irap_imposta_regione`), non il numero di enti P.A. Il conteggio delle P.A. è `base_imponibile_frequenza`.
- **Nessun break 2014→2015**: a differenza della vista totale, il perimetro P.A. è stabile (base +0,4% tra a.i. 2014 e 2015) — il salto della serie IRAP è tutto nel settore privato.
- **Totali nazionali**: somma delle 21 regioni dichiarate; la riga `TOTALE` della fonte è esclusa dal clean. Nel file 2015 (a.i. 2014) la riga `TOTALE` della fonte è mascherata (`***`), quindi i totali nazionali si possono ricavare solo dalle regioni — è quello che fa il clean.
- **`anno` = anno d'imposta**, coerente con gli altri dataset del repo.
