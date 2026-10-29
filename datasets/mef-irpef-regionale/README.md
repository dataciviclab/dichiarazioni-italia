# mef-irpef-regionale

**Domanda guida:** Come si distribuiscono i contribuenti IRPEF per classe di reddito, regione per regione?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** `REG_tipo_reddito` (IRPEF regionale per tipo di reddito e classe)
**Formato:** CSV con 1 riga di metadati → letto **per posizione** (`read.skip: 1`, tutte le colonne `VARCHAR`, `normalize_rows_to_columns`)
**Copertura:** 2016–2024 (9 anni, anno d'imposta)
**Nota:** il file MEF usa l'anno di presentazione (`REG_tipo_reddito_2025.csv` = dichiarazioni a.i. 2024); il clean espone `anno` = `{year} - 1`.
**Licenza:** CC BY (MEF)
**Valori:** in **euro**

## Perché è letto per posizione

La fonte è un CSV senza header di colonna utile: la prima riga è di metadati e le
colonne sono 42 posizioni fisse (`column00` … `column41`), con la prima colonna =
classe di reddito e la seconda = regione. La clean legge per posizione e mappa
esplicitamente ogni cella (nessuno sniffing di tipo: i numeri sono in formato
italiano).

## Schema del clean (42 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta (`{year} - 1`) |
| `classe_reddito` | VARCHAR | Classe di reddito complessivo (34 classi) |
| `regione` | VARCHAR | Regione (21) |
| `numero_contribuenti` | DOUBLE | Contribuenti della cella |
| `reddito_*_freq` / `reddito_*_eur` | DOUBLE | Frequenza e importo per tipo di reddito: dominicale, agrario, allevamento, fabbricati, lavoro dipendente, pensione, altri assimilati, lavoro autonomo, perdite, provvigioni, impresa ordinaria/semplificata, partecipazione, plusvalenze, capitale, diversi, start-up, tassazione separata |

## Mart

- `irpef_regione_classe` — regione × anno (21 righe per anno): contribuenti totali, contribuenti nelle **due code** della distribuzione e le relative quote:
  - `contribuenti_fascia_inferiore` / `pct_fascia_inferiore` — reddito **≤ 0** (3 classi)
  - `contribuenti_fascia_superiore` / `pct_fascia_superiore` — reddito **≥ 10.000 €** (20 classi)
  - `num_classi_presente` — classi distinte (34)
  - `classi_non_mappate` — guardia: classi non coperte dalla mappatura (deve restare **0**)

Le 11 classi intermedie (da 0 a 10.000 €) non entrano in nessuna delle due fasce,
quindi le due quote non sommano a 100.

## Cosa dicono i dati

- **42.832.641 contribuenti** ad a.i. 2024, di cui **1.148.500 (2,68%)** con reddito **≤ 0** e **32.037.568 (74,80%)** con reddito **≥ 10.000 €**.
- La quota di contribuenti con reddito ≤ 0 è più alta in **Campania (3,30%)**, **Lazio (3,20%)** e **Abruzzo (3,03%)**.

## Note metodologiche

- **⚠️ `anno` è l'anno d'imposta, non l'anno del file.** Verificato confrontando i contribuenti totali del file con quelli di `irpef_imposta_tipologia`: file 2025 → 42.832.641 vs a.i. 2024 = 42.837.963; file 2024 → 42.564.337 vs a.i. 2023 = 42.570.078. La differenza (~5-6 mila) è il perimetro "Non indicata". **Fino al 2026-10-29 la colonna riportava l'anno di presentazione** (`anno_di_imposta` = 2017…2025): l'intera serie era avanti di un anno.
- **⚠️ La mappatura delle classi è esplicita, una riga per classe.** Fino al 2026-10-29 il mart elencava etichette che **non esistono** nella fonte (`da 10.000 a 15.000`, `da 20.000 a 25.000`, `maggiore di 30.000`, …) e chiudeva con `ELSE 99` sotto la soglia `>= 17`: **21 delle 34 classi** finivano nella fascia alta, che misurava di fatto «reddito > 6.000 €» invece di «≥ 10.000 €» (verificato su Campania, Abruzzo e Lombardia: la colonna coincideva con `totale − classi mappate ≤ 6.000`).
- **Guardie**: `num_classi_presente = 34` e `classi_non_mappate = 0` sono regole `ranges` in `dataset.yml`. Se la fonte cambiasse le etichette, la validazione fallisce invece di produrre numeri sbagliati.
- **Il mart è un riassunto**: il dettaglio per classe e per tipo di reddito è nel clean (714 righe per anno = 21 regioni × 34 classi).
- **Classi identiche in tutti gli anni**: le 34 etichette sono le stesse nei 9 file coperti (verificato file per file), quindi la mappatura statica è sicura.
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
