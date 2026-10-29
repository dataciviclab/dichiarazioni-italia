-- clean.sql — iva_sez_attivita
-- Volume d'affari IVA per sezione di attività (ATECO). Fonte: CIVATOT0202.
--
-- Lettura per POSIZIONE (header: false + normalize_rows_to_columns) perché la
-- fonte ha un CSV malformato: 2-3 nomi di sezione contengono un ';' NON
-- quotato — "Fornitura di acqua; reti fognarie…" (05), "Commercio all'ingrosso
-- e al dettaglio; riparazione…" (07), "Amministrazione pubblica e difesa;
-- assicurazione sociale obbligatoria" (15) — quindi quelle righe hanno una
-- cella in più e TUTTI i valori slittano di uno.
--
-- La clean riconosce il caso dal fatto che la cella 1 è (o non è) il codice:
-- riga normale → codice in column01; riga spostata → codice in column02 e nome
-- ricomposto da column00 + '; ' + column01.
--
-- ⚠️ Senza questa riparazione la sezione "Commercio all'ingrosso e al
-- dettaglio" — la prima d'Italia per volume — finiva a ~0 e il totale
-- nazionale perdeva il 26-33% in a.i. 2014-2023 (verificato contro la riga
-- TOTALE della fonte). Lo stesso pattern è in irap_imposta_settore, dove la
-- fonte ha la stessa malformazione.
--
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
-- Valori raw in migliaia di euro → ×1000.
-- Righe escluse: header (column01 = 'Codice'), TOTALE (codice '0'),
-- "Non indicata" e la riga-nota finale.

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER) AS anno,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN trim(column00)
             ELSE trim(column00) || '; ' || trim(column01)
        END AS sezione_attivita,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column01 ELSE column02
        END AS _codice,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column02 ELSE column03
        END AS _contribuenti,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column03 ELSE column04
        END AS _volume_frequenza,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column04 ELSE column05
        END AS _volume_ammontare,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column06 ELSE column07
        END AS _acquisti_frequenza,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column07 ELSE column08
        END AS _acquisti_ammontare,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column09 ELSE column10
        END AS _va_frequenza,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column10 ELSE column11
        END AS _va_ammontare,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column12 ELSE column13
        END AS _imposta_dovuta_frequenza,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column13 ELSE column14
        END AS _imposta_dovuta_ammontare,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column15 ELSE column16
        END AS _imposta_credito_frequenza,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column16 ELSE column17
        END AS _imposta_credito_ammontare
    FROM raw_input
    -- la riga di header (letta come dato con skip: 9) ha 'Codice' nella 2ª cella
    WHERE column01 IS DISTINCT FROM 'Codice'
)
SELECT
    anno,
    sezione_attivita,
    LPAD(normalize_string(_codice), 2, '0')                        AS codice,
    normalize_italian_integer(_contribuenti)                       AS contribuenti,
    normalize_italian_integer(_volume_frequenza)                   AS volume_frequenza,
    ROUND(normalize_italian_number(_volume_ammontare) * 1000, 0)   AS volume_affari_eur,
    normalize_italian_integer(_acquisti_frequenza)                 AS acquisti_frequenza,
    ROUND(normalize_italian_number(_acquisti_ammontare) * 1000, 0) AS acquisti_eur,
    normalize_italian_integer(_va_frequenza)                       AS va_frequenza,
    ROUND(normalize_italian_number(_va_ammontare) * 1000, 0)       AS va_fiscale_eur,
    normalize_italian_integer(_imposta_dovuta_frequenza)           AS imposta_dovuta_frequenza,
    ROUND(normalize_italian_number(_imposta_dovuta_ammontare) * 1000, 0)  AS imposta_dovuta_eur,
    normalize_italian_integer(_imposta_credito_frequenza)          AS imposta_credito_frequenza,
    ROUND(normalize_italian_number(_imposta_credito_ammontare) * 1000, 0) AS imposta_credito_eur
FROM raw_parsed
WHERE normalize_string(_codice) IS NOT NULL
  AND normalize_string(_codice) NOT IN ('0', '')          -- '0' = TOTALE
  AND normalize_string(sezione_attivita) IS NOT NULL
  AND normalize_string(sezione_attivita) NOT IN ('TOTALE', 'Non indicata', 'Sezione di attivita''')
