-- clean.sql — irap_imposta_pa_regione
-- IRAP delle P.A.: base imponibile e imposta netta delle *attività
-- istituzionali* esercitate dalle pubbliche amministrazioni (DIRTOT0501).
--
-- Complemento di irap_imposta_regione (vista totale): la differenza fra i due
-- dà il settore privato. Verificato sui totali 2024: totale 30,06 mld di
-- imposta, di cui P.A. 10,61 mld (35,3%).
--
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
-- Valori raw in migliaia di euro → ×1000.
--
-- NON esposto: "Numero contribuenti" della fonte è il totale IRAP della
-- regione (identico a irap_imposta_regione), non il numero di enti P.A.:
-- il conteggio delle P.A. è la frequenza della base imponibile.
-- Riga finale del file = nota ("Ammontare e media in migliaia di euro") con
-- Codice vuoto: esclusa dal filtro su Codice.

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER)                              AS anno,
        normalize_string("Regione")                              AS regione,
        LPAD(normalize_string("Codice"), 2, '0')                 AS cod_regione,
        normalize_italian_integer("Base imponibile - Frequenza")  AS base_imponibile_frequenza,
        normalize_italian_number("Base imponibile - Ammontare")   AS _base,
        normalize_italian_integer("Imposta netta - Frequenza")    AS imposta_netta_frequenza,
        normalize_italian_number("Imposta netta - Ammontare")     AS _imposta,
        normalize_italian_number("Imposta a debito - Ammontare")  AS _debito,
        normalize_italian_number("Imposta a credito - Ammontare") AS _credito
    FROM raw_input
    WHERE "Regione" IS NOT NULL AND "Codice" IS NOT NULL
      AND normalize_string("Regione") NOT IN ('TOTALE', 'Non indicata')
      AND normalize_string("Codice") != ''
)
SELECT
    anno,
    regione,
    cod_regione,
    base_imponibile_frequenza,
    ROUND(_base * 1000, 0)    AS base_imponibile_eur,
    imposta_netta_frequenza,
    ROUND(_imposta * 1000, 0) AS imposta_netta_eur,
    ROUND(_debito * 1000, 0)  AS imposta_debito_eur,
    ROUND(_credito * 1000, 0) AS imposta_credito_eur
FROM raw_parsed
