-- clean.sql — irap_italia_estero
-- Produzione netta IRAP realizzata in Italia vs estero.
-- Le colonne "Media" vengono scartate.

WITH raw_parsed AS (
    SELECT
        CAST({year} AS INTEGER)                                              AS anno,
        normalize_string("Regione")                                          AS regione,
        LPAD(normalize_string("Codice"), 2, '0')                             AS cod_regione,
        normalize_italian_integer("Numero contribuenti")                     AS contribuenti,
        -- Produzione netta totale
        normalize_italian_integer("Totale produzione netta - Frequenza")     AS prod_netta_freq,
        normalize_italian_number("Totale produzione netta - Ammontare")      AS prod_netta_eur,
        -- Produzione realizzata all'estero
        normalize_italian_integer("Valore della produzione netta realizzata all'estero - Frequenza") AS vp_estero_freq,
        normalize_italian_number("Valore della produzione netta realizzata all'estero - Ammontare")    AS vp_estero_eur,
        -- Produzione realizzata in Italia
        normalize_italian_integer("Valore della produzione netta realizzata in Italia - Frequenza") AS vp_italia_freq,
        normalize_italian_number("Valore della produzione netta realizzata in Italia - Ammontare")    AS vp_italia_eur
    FROM raw_input
    WHERE "Regione" IS NOT NULL AND "Codice" IS NOT NULL
      AND normalize_string("Regione") NOT IN ('TOTALE', 'Non indicata')
      AND normalize_string("Codice") != ''
)
SELECT
    anno, regione, cod_regione, contribuenti,
    prod_netta_freq, ROUND(prod_netta_eur, 0) AS prod_netta_eur,
    vp_estero_freq, ROUND(vp_estero_eur, 0)   AS vp_estero_eur,
    vp_italia_freq, ROUND(vp_italia_eur, 0)   AS vp_italia_eur
FROM raw_parsed
