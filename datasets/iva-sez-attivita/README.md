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

- **4.146.944 contribuenti** e **4.688,1 mld** di volume d'affari (a.i. 2024); valore aggiunto fiscale 1.027 mld.
- Prime tre sezioni per volume: **manifattura 29,1%**, **commercio 27,9%**, **energia 8,4%**.

## Note metodologiche

- **⚠️ Le colonne non sono additive**: volume d'affari, acquisti e valore aggiunto sono grandezze distinte, non componenti di una somma.
- **Fonte malformata, e come è riparata.** 2-3 nomi di sezione per anno contengono un `;` **non quotato** (`Fornitura di acqua; reti fognarie…`, `Commercio all'ingrosso e al dettaglio; riparazione…`, `Amministrazione pubblica e difesa; assicurazione sociale obbligatoria`): quelle righe hanno **una cella in più** e tutti i valori slittano di uno. La clean riconosce il caso dalla posizione del codice (cella 1 = riga normale, cella 2 = riga spostata) e ricompone nome e valori — stesso pattern di `irap_imposta_settore`.
  **Verifica**: nome, codice e volume di **ogni** sezione confrontati cella per cella con la fonte in tutti gli 11 anni; la somma delle sezioni coincide con la riga `TOTALE` (±0,00%).
  **Fino al 2026-10-29 la riparazione non c'era**: la sezione "Commercio all'ingrosso e al dettaglio" — la seconda d'Italia per volume — valeva ~0 e il totale nazionale perdeva il **26-33% in a.i. 2014-2023** (−1,4% in a.i. 2024, l'unico anno quasi integro).
- **⚠️ Break di tassonomia ad a.i. 2024.** La fonte cambia i nomi delle sezioni: 22 sezioni fino ad a.i. 2023, **23 da a.i. 2024** (`Istruzione` → `Istruzione e formazione`, `Sanita' e assistenza sociale` → `Attivita' per la salute umana e di assistenza sociale`, `Servizi di informazione e comunicazione` → più sezioni, …). Un confronto anno-su-anno a cavallo del 2024 va fatto **per codice**, non per nome.
- **Righe escluse**: header, `TOTALE` (codice `0`), `Non indicata` e la riga-nota finale.
- **Perimetro**: fonte MEF `analisi_stat`; valori raw in migliaia di euro, convertiti in euro (×1000). Le colonne "Media" della fonte sono scartate (si ricalcolano da frequenza e ammontare).
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
