-- clean.sql — irap_imposta_settore
-- IRAP: base imponibile e totale imposta per sezione di attività (DIRTOT1002).
--
-- Lettura per POSIZIONE (header: false + normalize_rows_to_columns) perché la
-- fonte ha un CSV malformato: alcuni nomi di sezione contengono un ';' NON
-- quotato — "Fornitura di acqua; reti fognarie…" (cod. 05), "Commercio
-- all'ingrosso e al dettaglio; riparazione…" (07), "Amministrazione pubblica e
-- difesa; assicurazione sociale obbligatoria" (15) — quindi quelle righe hanno
-- una cella in più e le colonne slittano di uno.
-- La clean riconosce il caso dal fatto che la cella 1 è (o non è) il codice:
-- riga normale → cod in column01; riga spostata → cod in column02 e nome
-- ricomposto da column00 + '; ' + column01.
-- Verificato: con la riparazione la somma delle sezioni coincide con la riga
-- TOTALE della fonte (a.i. 2014: 605,9 vs 605,8 mld di base).
--
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
-- Valori raw in migliaia di euro → ×1000.
-- Righe escluse: la riga di header (column01 = 'Codice'), TOTALE (codice '0')
-- e la riga-nota finale (column01 NULL → codice NULL).

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER) AS anno,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN trim(column00)
             ELSE trim(column00) || '; ' || trim(column01)
        END AS sezione_attivita,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN trim(column01) ELSE trim(column02)
        END AS _codice,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column02 ELSE column03
        END AS _contribuenti,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column03 ELSE column04
        END AS _base_freq,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column04 ELSE column05
        END AS _base_amm,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column06 ELSE column07
        END AS _imposta_freq,
        CASE WHEN regexp_matches(trim(column01), '^[0-9]{1,2}$')
             THEN column07 ELSE column08
        END AS _imposta_amm
    FROM raw_input
    -- la riga di header (letta come dato con skip: 9) ha 'Codice' nella 2ª cella
    WHERE column01 IS DISTINCT FROM 'Codice'
)
SELECT
    anno,
    sezione_attivita,
    LPAD(normalize_string(_codice), 2, '0')        AS codice,
    normalize_italian_integer(_contribuenti)       AS contribuenti,
    normalize_italian_integer(_base_freq)          AS base_imponibile_frequenza,
    ROUND(normalize_italian_number(_base_amm) * 1000, 0)    AS base_imponibile_eur,
    normalize_italian_integer(_imposta_freq)       AS imposta_frequenza,
    ROUND(normalize_italian_number(_imposta_amm) * 1000, 0) AS imposta_eur
FROM raw_parsed
WHERE _codice IS NOT NULL
  AND normalize_string(_codice) NOT IN ('0', '')   -- '0' = TOTALE
  AND normalize_string(sezione_attivita) IS NOT NULL
