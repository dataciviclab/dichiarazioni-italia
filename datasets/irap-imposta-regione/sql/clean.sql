-- clean.sql — irap_imposta_regione
-- IRAP: base imponibile e totale imposta per regione (vista "Base imponibile
-- ed imposta totale", DIRTOT1001: P.A. incluse).
--
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
-- Valori raw in migliaia di euro → ×1000.
-- `Numero contribuenti` è il totale dei contribuenti IRAP della regione.
-- La riga finale del file è una nota ("Ammontare e media in migliaia di euro")
-- con Codice vuoto: esclusa dal filtro su Codice.
--
-- Perimetro: questa vista è il totale. La scomposizione privati / P.A. sta in
-- DIRTOT0401 (escluse le P.A.) e DIRTOT0501 (attività istituzionali delle P.A.):
-- verificato su 2024 che base imponibile e imposta delle due sommano al totale
-- di questa vista. Non sono unite qui perché le due viste hanno layout diversi
-- (16 vs 22 colonne) e nomi colonna che cambiano anche nell'encoding tra anni.

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER)                                 AS anno,
        normalize_string("Regione")                                 AS regione,
        LPAD(normalize_string("Codice"), 2, '0')                    AS cod_regione,
        normalize_italian_integer("Numero contribuenti")            AS contribuenti,
        normalize_italian_integer("Base imponibile - Frequenza")    AS base_imponibile_frequenza,
        normalize_italian_number("Base imponibile - Ammontare")     AS _base,
        normalize_italian_integer("Totale imposta - Frequenza")     AS imposta_frequenza,
        normalize_italian_number("Totale imposta - Ammontare")      AS _imposta
    FROM raw_input
    WHERE "Regione" IS NOT NULL AND "Codice" IS NOT NULL
      AND normalize_string("Regione") NOT IN ('TOTALE', 'Non indicata')
      AND normalize_string("Codice") != ''
)
SELECT
    anno,
    regione,
    cod_regione,
    contribuenti,
    base_imponibile_frequenza,
    ROUND(_base * 1000, 0)    AS base_imponibile_eur,
    imposta_frequenza,
    ROUND(_imposta * 1000, 0) AS imposta_eur
FROM raw_parsed
