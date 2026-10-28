# iva_sez_attivita

**Domanda guida:** Quali settori economici generano volume d'affari IVA, e come sono cambiati?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** CIVATOT0202 (IVA — Totale — Sezione di attività — Regione)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; letto per **posizione** (`read.skip: 9`, tutte le colonne `VARCHAR`)
**Copertura:** 2014–2024 (11 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (file 2015–2025); il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)


## Schema

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta |
| `sezione_attivita` | VARCHAR | Sezione di attività (ATECO) |
| `codice` | VARCHAR | Codice sezione ATECO |
| `contribuenti` | INTEGER | Contribuenti IVA della sezione |
| `volume_frequenza` | INTEGER | Dichiarazioni con volume d'affari |
| `volume_affari_eur` | DOUBLE | Volume d'affari (€) |
| `acquisti_frequenza` | INTEGER | Dichiarazioni con acquisti |
| `acquisti_eur` | DOUBLE | Acquisti (€) |
| `va_frequenza` | INTEGER | Dichiarazioni con valore aggiunto |
| `va_fiscale_eur` | DOUBLE | Valore aggiunto fiscale (€) |
| `imposta_dovuta_frequenza` | INTEGER | Dichiarazioni con imposta dovuta |
| `imposta_dovuta_eur` | DOUBLE | Imposta IVA dovuta (€) |
| `imposta_credito_frequenza` | INTEGER | Dichiarazioni con imposta a credito |
| `imposta_credito_eur` | DOUBLE | Imposta IVA a credito (€) |

## Mart

- `mart_settori_anno` — sezione × anno: contribuenti, volume d'affari, acquisti, valore aggiunto, imposta dovuta e a credito, quota sul volume nazionale, `rank_volume`

## Cosa dicono i dati

- **4.127.519 contribuenti** e **4.622 mld** di volume d'affari (a.i. 2024); valore aggiunto fiscale 1.032 mld.
- Prime tre sezioni per volume: **manifattura 29,5%**, **commercio 28,3%**, **energia 8,5%**.

## Note metodologiche

- **⚠️ Le colonne non sono additive**: volume d'affari, acquisti e valore aggiunto sono grandezze distinte, non componenti di una somma.
- **Fonte malformata**: alcuni nomi di sezione contengono un `;` **non quotato** (es. `Fornitura di acqua; reti fognarie…`) → la riga ha una cella in più e le colonne slittano. La clean riconosce il caso dal codice in seconda cella e ricompone il nome; verificato che la somma delle sezioni coincide con la riga `TOTALE` della fonte.
- **Righe escluse**: header, `TOTALE` e nota finale.
- **Perimetro**: fonte MEF `analisi_stat`; valori raw in migliaia di euro, convertiti in euro (×1000). Le colonne "Media" della fonte sono scartate (si ricalcolano da frequenza e ammontare).
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
