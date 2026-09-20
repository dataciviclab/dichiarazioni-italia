-- clean.sql — iva_sez_attivita
-- Volume d'affari IVA per sezione di attivita' (ATECO).
-- usa header:false + normalize_rows_to_columns:true per gestire il BOM.
-- La prima riga dati e' l'header text (Sezione di attivita';Codice;...).

WITH raw_numbered AS (
    SELECT *, ROW_NUMBER() OVER () AS rn
    FROM raw_input
)
SELECT
    CAST({year} - 1 AS INTEGER)                   AS anno,
    normalize_string(column00)                    AS sezione_attivita,
    LPAD(normalize_string(column01), 2, '0')     AS codice,
    normalize_italian_integer(column02)           AS contribuenti,
    normalize_italian_integer(column03)           AS volume_frequenza,
    ROUND(normalize_italian_number(column04) * 1000, 0) AS volume_affari_eur,
    normalize_italian_integer(column06)           AS acquisti_frequenza,
    ROUND(normalize_italian_number(column07) * 1000, 0) AS acquisti_eur,
    normalize_italian_integer(column09)           AS va_frequenza,
    ROUND(normalize_italian_number(column10) * 1000, 0) AS va_fiscale_eur,
    normalize_italian_integer(column12)           AS imposta_dovuta_frequenza,
    ROUND(normalize_italian_number(column13) * 1000, 0) AS imposta_dovuta_eur,
    normalize_italian_integer(column15)           AS imposta_credito_frequenza,
    ROUND(normalize_italian_number(column16) * 1000, 0) AS imposta_credito_eur
FROM raw_numbered
WHERE rn > 1  -- salta riga header text
  AND normalize_string(column00) IS NOT NULL
  AND normalize_string(column01) IS NOT NULL
  AND normalize_string(column00) NOT IN ('TOTALE', 'Non indicata', 'Sezione di attivita''')
  AND normalize_string(column01) != 'Codice'
