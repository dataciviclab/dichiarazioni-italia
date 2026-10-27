-- clean.sql — irap_italia_estero
-- Produzione netta IRAP realizzata in Italia vs estero.
-- Le colonne "Media" vengono scartate.
-- Valori raw in migliaia di euro, convertiti in euro (×1000) per coerenza.
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
--
-- Lettura POSIZIONALE, tutte le colonne VARCHAR (vedi dataset.yml): i numeri
-- sono in formato italiano e vanno normalizzati dalle macro, che lavorano su
-- stringhe. Con `source: auto` lo sniffer tipizza DOUBLE le colonne i cui
-- valori hanno un solo punto (qui `vp_estero_freq`, max 1.088) e la macro le
-- corrompe: in 2 anni su 10 la colonna risultava DOUBLE → 40 celle ×10.
--
-- Esclusi: la riga di header (letta come dato con skip: 9), `TOTALE` e
-- l'eventuale `Non indicata`; la nota finale ha `codice` vuoto.

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER)                        AS anno,
        normalize_string(regione)                          AS regione,
        LPAD(normalize_string(codice), 2, '0')             AS cod_regione,
        normalize_italian_integer(contribuenti)            AS contribuenti,
        -- Produzione netta totale
        normalize_italian_integer(prod_netta_frequenza)    AS prod_netta_freq,
        normalize_italian_number(prod_netta_ammontare)     AS prod_netta_eur,
        -- Produzione realizzata all'estero
        normalize_italian_integer(vp_estero_frequenza)     AS vp_estero_freq,
        normalize_italian_number(vp_estero_ammontare)      AS vp_estero_eur,
        -- Produzione realizzata in Italia
        normalize_italian_integer(vp_italia_frequenza)     AS vp_italia_freq,
        normalize_italian_number(vp_italia_ammontare)      AS vp_italia_eur
    FROM raw_input
    WHERE normalize_string(codice) IS NOT NULL
      AND normalize_string(codice) NOT IN ('Codice', '0')
      AND normalize_string(regione) NOT IN ('Regione', 'TOTALE', 'Non indicata')
)
SELECT
    anno, regione, cod_regione, contribuenti,
    prod_netta_freq, ROUND(prod_netta_eur * 1000, 0) AS prod_netta_eur,
    vp_estero_freq, ROUND(vp_estero_eur * 1000, 0)   AS vp_estero_eur,
    vp_italia_freq, ROUND(vp_italia_eur * 1000, 0)   AS vp_italia_eur
FROM raw_parsed
