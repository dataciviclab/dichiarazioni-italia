-- clean.sql — irap_imposta_pa_regione
-- IRAP delle P.A.: base imponibile e imposta netta delle *attività
-- istituzionali* esercitate dalle pubbliche amministrazioni (DIRTOT0501).
--
-- Complemento di irap_imposta_regione (vista totale): la differenza fra i due
-- dà il settore privato. Verificato sui totali 2024: totale 30,06 mld di
-- imposta, di cui P.A. 10,61 mld (35,3%).
--
-- Lettura POSIZIONALE, tutte le colonne VARCHAR (vedi dataset.yml): i numeri
-- sono in formato italiano e vanno normalizzati dalle macro, che lavorano su
-- stringhe. Con `source: auto` lo sniffer tipizza DOUBLE le colonne con valori
-- piccoli ("132", "3.440") e `normalize_italian_*` le corrompe (×10 / ÷10).
--
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
-- Valori raw in migliaia di euro → ×1000.
--
-- NON esposto: "Numero contribuenti" della fonte è il totale IRAP della
-- regione (identico a irap_imposta_regione), non il numero di enti P.A.:
-- il conteggio delle P.A. è la frequenza della base imponibile.
-- Esclusi: la riga di header (letta come dato, `codice` = 'Codice'), la riga
-- `TOTALE`, l'eventuale `Non indicata` e la nota finale (codice vuoto).

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER)                    AS anno,
        normalize_string(regione)                      AS regione,
        LPAD(normalize_string(codice), 2, '0')         AS cod_regione,
        normalize_italian_integer(base_imponibile_frequenza) AS base_imponibile_frequenza,
        normalize_italian_number(base_imponibile_ammontare)  AS _base,
        normalize_italian_integer(imposta_netta_frequenza)   AS imposta_netta_frequenza,
        normalize_italian_number(imposta_netta_ammontare)    AS _imposta,
        normalize_italian_number(imposta_debito_ammontare)   AS _debito,
        normalize_italian_number(imposta_credito_ammontare)  AS _credito
    FROM raw_input
    WHERE normalize_string(codice) IS NOT NULL
      AND normalize_string(codice) NOT IN ('Codice', '0')
      AND normalize_string(regione) NOT IN ('TOTALE', 'Non indicata', 'Regione')
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
