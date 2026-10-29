# Note tecniche — mef-irpef-regionale

## Fonte

MEF Dipartimento Finanze — Open Data IRPEF:
- Primary: `REG_tipo_reddito_{year}.csv`
- Secondary: `REG_calcolo_irpef_{year}.csv`, `REG_bonus_irpef_{year}.csv`

URL base: `https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/`

## Copertura temporale

**a.i. 2016–2024** (9 anni d'imposta). I file MEF usano l'anno di *presentazione*:
`REG_tipo_reddito_2017.csv` … `_2025.csv` → il clean espone `anno = {year} - 1`.
I file pre-2017 restituiscono 404.

## Struttura raw

CSV con `;` delimiter, encoding `utf-8`.
- Header riga 1 (da skip)
- Dati: 714 righe per anno = 21 regioni × 34 classi di reddito
- Colonna 1: "Classi di reddito complessivo in euro"
- Colonna 2: "Regione"
- Colonne 3–43: coppie frequenza/ammontare per ogni tipologia di reddito (max 43 colonne dopo normalizzazione, 2017)

## Schema clean

Il raw MEF ha formato "report rigato" — ogni regione ha 34 righe impilate, una per classe di reddito.
`normalize_rows_to_columns: true` converte ciascuna regione in una riga tabellare.
42 colonne dopo normalizzazione: 4 non-pair (`anno`, `classe_reddito`, `regione`, `numero_contribuenti`) + **19 coppie** frequenza/ammontare.

## Caveat

- **34 classi, tutte mappate**: il dataset MEF REG ha 34 classi di reddito (non 21 come
  nell'issue #253). Il `mart.sql` le mappa **tutte e 34**, una riga per classe, con
  `LEFT JOIN` senza `ELSE`: fascia inferiore = reddito ≤ 0 (3 classi), fascia superiore =
  reddito ≥ 10.000 € (20 classi). Le guardie `num_classi_presente = 34` e
  `classi_non_mappate = 0` fanno **fallire la validazione** se la fonte cambia le etichette.
  *(Fino al 2026-10-29 il mart elencava etichette inesistenti e chiudeva con `ELSE 99` sotto
  la soglia `>= 17`: 21 classi su 34 finivano nella fascia alta, che misurava di fatto
  «reddito > 6.000 €».)*
- **Contributi nulli**: le celle vuote indicano valori nulli (NON zero reale). Gestiti con NULLIF + regexp_replace per separatori italiani.
- **Dimensione sesso assente**: l'issue #253 menzionava "per classe e sesso". I file REG_tipo_reddito non hanno breakdown per sesso — la dimensione sesso è disponibile solo nei file `sesso_*` del portale MEF (stesso source_id `mef_irpef`). Per ora la v1 è solo regione × classe × anno. L'analisi di genere richiede un candidate separato.

## Note di ingest / clean

- Il toolkit supporta `{year}` nella clean.sql — il template renderer lo sostituisce prima dell'esecuzione. L'anno d'imposta si ottiene con `({year} - 1)::INTEGER AS anno`, **mai** `{year}::INTEGER`: il file MEF usa l'anno di presentazione e la colonna resterebbe avanti di uno.
- 34 classi di reddito nel MEF REG (vs 21 dichiarate nell'issue) — il `mart.sql` le mappa tutte e 34; vedi il caveat sopra.
- Filtro `Mancante/errata` gia nel WHERE della clean.sql.

## Status

Pipeline OK su tutti i 9 anni (a.i. 2016-2024). Multi-anno confermato. Mergiata con #35.