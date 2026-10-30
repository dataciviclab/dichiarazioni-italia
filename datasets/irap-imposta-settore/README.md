# irap-imposta-settore

**Domanda guida:** Come si distribuisce l'IRAP tra i settori economici, e chi paga l'aliquota effettiva più alta?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** DIRTOT1002 (Base imponibile ed imposta totale — Sezione di attività)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; letto **per posizione** (`read.skip: 9`, `header: false`, `normalize_rows_to_columns`)
**Copertura:** 2014–2023 (10 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (es. `2024DIRTOT1002` = dichiarazioni 2024). Il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)

## Schema (8 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta (URL anno - 1) |
| `sezione_attivita` | VARCHAR | Sezione di attività (22 righe: 21 sezioni ATECO + "Attività non classificabile") |
| `codice` | VARCHAR | Codice della sezione (01-22) |
| `contribuenti` | BIGINT | Contribuenti IRAP della sezione |
| `base_imponibile_frequenza` | BIGINT | Dichiarazioni con base imponibile |
| `base_imponibile_eur` | DOUBLE | Base imponibile IRAP (€) |
| `imposta_frequenza` | BIGINT | Dichiarazioni con imposta |
| `imposta_eur` | DOUBLE | Totale imposta IRAP (€) |

## Mart

- `mart_settori_anno` — sezione × anno: base, imposta, **aliquota effettiva**, quota sulla base nazionale, `rank_imposta`
- `mart_imposta_anno` — nazionale per anno (multi-year): base, imposta, aliquota effettiva, delta % sull'anno precedente

## Note metodologiche

- ⚠️ **La fonte è malformata e va riparata.** Tre nomi di sezione contengono un `;` **non quotato** — "Fornitura di acqua; reti fognarie…" (05), "Commercio all'ingrosso e al dettaglio; riparazione…" (07), "Amministrazione pubblica e difesa; assicurazione sociale obbligatoria" (15) — quindi quelle righe hanno una cella in più e le colonne slittano di uno. Il clean le riconosce (il codice sta in `column02` invece che `column01`) e ricompone nome e valori. **Verifica**: con la riparazione la somma delle sezioni coincide con la riga `TOTALE` della fonte (a.i. 2014: 605,9 vs 605,8 mld di base); senza riparazione si perdono ~169 mld, quasi tutti nella riga P.A.
- ⚠️ **Break di serie tra 2014 e 2015.** La base imponibile passa da **605,8 a 444,7 mld** (−26,6%) e l'imposta da **30,03 a 23,29 mld** (−22,4%): è il cambio di definizione della base già documentato in `irap_imposta_regione` (i due totali coincidono, come da verifica sopra). **Leggere il trend dal 2015.**
- ⚠️ **Il crollo dei contribuenti a.i. 2022 non è una crisi settoriale: è l'esonero delle persone fisiche** (L. 234/2021, art. 1 comma 8). In aggregato i contribuenti calano del 37%, ma la caduta si concentra dove operano le persone fisiche: **agricoltura −56,4%**, **sanità −52,3%**, **commercio −49,1%**, **trasporto −45,6%**, **attività professionali −43,3%**; restano stabili P.A. (**+1,7%**) e attività immobiliari (**−4,6%**). Base e imposta non calano: la voce "Persone fisiche" valeva 32,11 mld di base e 1,31 mld di imposta. Confronto omogeneo e dettaglio in `irap_imposta_regione`.
- **Il totale coincide con `irap_imposta_regione`**: 2023 → base 580,4 mld, imposta 30,06 mld, aliquota effettiva 5,18% (stessa vista per regione). Le due viste sono due tagli dello stesso universo.
- **Aliquota effettiva per settore** (2023): la più alta è l'**Amministrazione pubblica (8,47%)**, poi **Sanità (6,32%)**, **Istruzione (5,84%)**, Attività finanziarie (5,60%), Commercio (4,16%), Manifattura (4,04%).
- **La riga P.A. non coincide col dataset `irap_imposta_pa_regione`**: qui la sezione ATECO O vale 8,99 mld di imposta, mentre le *attività istituzionali di tutte le P.A.* valgono 10,61 mld. Sono perimetri diversi (classificazione settoriale vs natura dell'attività); l'aliquota effettiva invece coincide (8,47%).
- **`Attivita' non classificabile`** (codice 22) è una categoria della fonte, non una sezione ATECO.
- **Totali nazionali**: somma delle 22 righe; la riga `TOTALE` della fonte è esclusa dal clean.
- **`anno` = anno d'imposta**, coerente con gli altri dataset del repo.
