-- clean.sql — ires_redditi_regione
-- Reddito/perdita d'impresa IRES per regione (Societa' di Capitali).
-- Le colonne "Media" vengono scartate (si ricalcolano da Freq/Ammontare).
-- Valori raw in migliaia di euro, convertiti in euro (×1000) per coerenza.
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
--
-- Lettura POSIZIONALE, tutte le colonne VARCHAR (vedi dataset.yml): i numeri
-- sono in formato italiano e vanno normalizzati dalle macro, che lavorano su
-- stringhe. Con `source: auto` lo sniffer tipizza DOUBLE le colonne i cui
-- valori hanno un solo punto ("121.330") e la macro le corrompe
-- ("121.330" → 121.33 → "12133", ÷10). Prima di questo fix 112 celle erano
-- sbagliate su 10 anni (tutte frequenze: es. Molise 3.220 → 322).
--
-- Esclusi: la riga di header (letta come dato, `regione` = 'Regione'), la riga
-- `TOTALE` e la nota finale (regione vuota).

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER)                       AS anno,
        normalize_string(regione)                         AS regione,
        normalize_italian_integer(n_dichiarazioni)         AS n_dichiarazioni,
        -- Reddito d'impresa in continuita'
        normalize_italian_integer(reddito_continuita_frequenza) AS reddito_continuita_freq,
        normalize_italian_number(reddito_continuita_ammontare)  AS reddito_continuita_eur,
        -- Perdita d'impresa in continuita'
        normalize_italian_integer(perdita_continuita_frequenza) AS perdita_continuita_freq,
        normalize_italian_number(perdita_continuita_ammontare)  AS perdita_continuita_eur,
        -- Reddito d'impresa totale
        normalize_italian_integer(reddito_totale_frequenza)     AS reddito_totale_freq,
        normalize_italian_number(reddito_totale_ammontare)      AS reddito_totale_eur,
        -- Perdita d'impresa totale
        normalize_italian_integer(perdita_totale_frequenza)     AS perdita_totale_freq,
        normalize_italian_number(perdita_totale_ammontare)      AS perdita_totale_eur
    FROM raw_input
    WHERE normalize_string(regione) IS NOT NULL
      AND normalize_string(regione) NOT IN ('Regione', 'TOTALE', 'Non indicata')
      -- la nota finale ("Ammontare e media in migliaia di euro") ha la regione
      -- valorizzata ma nessun dato. Attenzione: con normalize_rows_to_columns
      -- le celle mancanti sono '' (non NULL) → serve normalize_string, che
      -- converte le stringhe vuote in NULL
      AND normalize_string(n_dichiarazioni) IS NOT NULL
)
SELECT
    anno, regione, n_dichiarazioni,
    reddito_continuita_freq, ROUND(reddito_continuita_eur * 1000, 0) AS reddito_continuita_eur,
    perdita_continuita_freq, ROUND(perdita_continuita_eur * 1000, 0) AS perdita_continuita_eur,
    reddito_totale_freq, ROUND(reddito_totale_eur * 1000, 0) AS reddito_totale_eur,
    perdita_totale_freq, ROUND(perdita_totale_eur * 1000, 0) AS perdita_totale_eur
FROM raw_parsed
