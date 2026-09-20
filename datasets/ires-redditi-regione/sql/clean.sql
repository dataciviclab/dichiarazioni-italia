-- clean.sql — ires_redditi_regione
-- Reddito/perdita d'impresa IRES per regione (Societa' di Capitali).
-- Le colonne "Media" vengono scartate.

WITH raw_parsed AS (
    SELECT
        CAST({year} AS INTEGER)                                              AS anno,
        normalize_string("Regione")                                          AS regione,
        normalize_italian_integer("Numero dichiarazioni")                    AS n_dichiarazioni,
        -- Reddito d'impresa in continuita'
        normalize_italian_integer("Reddito d'impresa in continuita' di esercizio - Frequenza") AS reddito_continuita_freq,
        normalize_italian_number("Reddito d'impresa in continuita' di esercizio - Ammontare")    AS reddito_continuita_eur,
        -- Perdita d'impresa in continuita'
        normalize_italian_integer("Perdita d'impresa in continuita' di esercizio - Frequenza") AS perdita_continuita_freq,
        normalize_italian_number("Perdita d'impresa in continuita' di esercizio - Ammontare")    AS perdita_continuita_eur,
        -- Reddito d'impresa totale
        normalize_italian_integer("Reddito d'impresa - Frequenza") AS reddito_totale_freq,
        normalize_italian_number("Reddito d'impresa - Ammontare")    AS reddito_totale_eur,
        -- Perdita d'impresa totale
        normalize_italian_integer("Perdita d'impresa - Frequenza") AS perdita_totale_freq,
        normalize_italian_number("Perdita d'impresa - Ammontare")    AS perdita_totale_eur
    FROM raw_input
    WHERE "Regione" IS NOT NULL
      AND normalize_string("Regione") NOT IN ('TOTALE', 'Non indicata')
      AND "Numero dichiarazioni" IS NOT NULL
)
SELECT
    anno, regione, n_dichiarazioni,
    reddito_continuita_freq, ROUND(reddito_continuita_eur, 0) AS reddito_continuita_eur,
    perdita_continuita_freq, ROUND(perdita_continuita_eur, 0) AS perdita_continuita_eur,
    reddito_totale_freq, ROUND(reddito_totale_eur, 0) AS reddito_totale_eur,
    perdita_totale_freq, ROUND(perdita_totale_eur, 0) AS perdita_totale_eur
FROM raw_parsed
