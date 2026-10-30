# irap-imposta-regione

**Domanda guida:** Quanta IRAP si paga in ogni regione, e quanto pesa sulla base imponibile?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** DIRTOT1001 (Base imponibile ed imposta totale — Regione)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; scaricato via `http_file`, letto con `read.skip: 9`
**Copertura:** 2014–2023 (10 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (es. `2024DIRTOT1001` = dichiarazioni 2024). Il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)

## Schema (8 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta (URL anno - 1) |
| `regione` | VARCHAR | Denominazione regione (21: Trentino diviso in P.A. Trento e Bolzano) |
| `cod_regione` | VARCHAR | Codice ISTAT regione |
| `contribuenti` | BIGINT | Contribuenti IRAP della regione |
| `base_imponibile_frequenza` | BIGINT | Dichiarazioni con base imponibile |
| `base_imponibile_eur` | DOUBLE | Base imponibile IRAP (€) |
| `imposta_frequenza` | BIGINT | Dichiarazioni con imposta |
| `imposta_eur` | DOUBLE | Totale imposta IRAP (€) |

## Mart

- `mart_regioni_anno` — regione × anno: base, imposta, **aliquota effettiva** (imposta / base), quota sulla base nazionale, `rank_imposta`
- `mart_imposta_anno` — nazionale per anno (multi-year): base, imposta, aliquota effettiva, delta % sull'anno precedente

## Note metodologiche

- ⚠️ **Break di serie tra 2014 e 2015.** Il primo anno è su un perimetro diverso: a.i. 2014 → base imponibile **605,8 mld €**, imposta 30,03 mld, 4.458.780 contribuenti; a.i. 2015 → base **444,7 mld** (−26,6%), imposta 23,29 mld (−22,4%), contribuenti 4.331.836 (−2,8%). I contribuenti calano poco mentre la base media per contribuente scende del ~24% (135,9 k€ → 102,7 k€): è coerente con un **cambio di definizione/perimetro della base**, non con un crollo dell'attività — la causa non è documentata nella fonte. Lo schema dei due file è identico, quindi non è un artefatto della pipeline. **Per leggere il trend partire dal 2015** (o trattare il 2014 come regime separato).
- ⚠️ **Secondo cambio di perimetro, a.i. 2022 — è una legge, non una crisi.** Dal periodo d'imposta 2022 l'IRAP non è dovuta dalle persone fisiche esercenti attività commerciali e arti/professioni, che sono esonerate anche dalla dichiarazione (L. 234/2021, art. 1 comma 8). La voce **Persone fisiche** sparisce dalle viste MEF: a.i. 2021 valeva **1.249.708 contribuenti, 32,11 mld € di base e 1,31 mld € di imposta**. Effetto apparente 2021→2022: contribuenti **−37,0%**, base **+5,2%**, imposta **+5,6%**. Confronto omogeneo (2021 al netto delle persone fisiche): contribuenti 2.084.244 → 2.101.567 (**+0,8%**), base 470,95 → 529,11 mld (**+12,3%**), imposta 24,92 → 27,70 mld (**+11,2%**). Sono gli stessi valori della nota MEF "Analisi dei dati IRAP" a.i. 2022, che dedica un paragrafo al confronto omogeneo. **Contribuenti e medie per contribuente non sono leggibili a cavallo del 2021/2022.**
- **Aliquota effettiva**: `imposta_eur / base_imponibile_eur`. È il carico reale, al netto di deduzioni e credito d'imposta — non l'aliquota di legge (3,9% + maggiorazioni regionali). Nel 2023 vale ~5,2% a livello nazionale.
- **Totali nazionali**: le mart sommano le **21 regioni dichiarate**. La riga `TOTALE` della fonte è esclusa dal clean (come la riga `Non indicata`), quindi i totali differiscono da essa per la quota "Non indicata" e per l'arrotondamento per regione (~0,0004%).
- **Perimetro P.A.**: questa vista è il **totale** (P.A. incluse). La scomposizione sta in due viste separate — `DIRTOT0401` (escluse le P.A. con attività istituzionale) e `DIRTOT0501` (attività istituzionali delle P.A.) — che **non** sono unite qui: hanno layout diversi (16 vs 22 colonne) e nomi colonna che cambiano anche nell'encoding tra anni (`attività` vs `attivita'`), quindi non entrano nella stessa lettura.
  Verificato sui totali nazionali 2024: base `455.230.923 + 125.194.629 = 580.425.552` (totale vista: `580.425.553`), imposta `19.450.669 + 10.605.821 = 30.056.490` (`30.056.489`). **Le P.A. valgono il 35,3% dell'imposta IRAP.**
- **Anni pre-2015**: disponibili alla fonte (2009–2014) ma con schema v1 (senza colonna `Codice`, encoding latin-1) → esclusi, come per gli altri dataset IRAP.
- **`TOTALE` e riga-nota escluse**: il file ha 21 regioni + riga `TOTALE` + una nota finale ("Ammontare e media in migliaia di euro") con `Codice` vuoto.
- **`anno` = anno d'imposta**: allineato a `iva_*`, `irpef_comunale` e `mef_irpef_regionale` (gli altri dataset IRAP/IRES sono stati allineati in #12).
