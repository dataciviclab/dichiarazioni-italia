-- clean.sql — acsp_tutte_classi_reddito
-- Società di persone (modello ACSP): Redditi dichiarati dalle società di persone (tutte le tipologie) per classe di reddito.
-- Vista MEF analisi_stat ACSPGEN0202 — "Tutte le tipologie di contribuenti" — "Classi di reddito dichiarato in euro".
--
-- Lettura POSIZIONALE con tutte le colonne VARCHAR (vedi dataset.yml): i numeri
-- sono in formato italiano e vanno normalizzati dalle macro, che lavorano su
-- stringhe. Con `source: auto` lo sniffing di DuckDB tipizza DOUBLE le colonne i
-- cui valori hanno un solo punto (es. "121.330" è un float valido) e la macro le
-- corrompe (×10 / ÷10); l'inferenza è PER FILE, quindi un campione di anni non
-- basta a escluderlo. Qui l'ordine delle colonne è verificato identico in tutti
-- gli anni, quindi la lettura posizionale è sicura.
--
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
-- Ammontari in migliaia di euro → ×1000. Colonne "Media" scartate.
-- `***` = dato oscurato dalla fonte (privacy) → NULL via TRY_CAST.
-- Righe escluse: la riga di header (letta come dato con skip: 9, codice='Codice'),
-- `TOTALE` (codice='0') e la riga-nota finale (codice NULL).

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER)                     AS anno,
        normalize_string(classe_reddito)                       AS classe_reddito,
        LPAD(normalize_string(codice), 2, '0')          AS codice,
        normalize_italian_integer(numero_societa)       AS numero_societa,
        normalize_italian_integer(totale_reddito_frequenza)      AS totale_reddito_frequenza,
        normalize_italian_number(totale_reddito_ammontare)       AS _totale_reddito_eur,
        normalize_italian_integer(totale_perdita_frequenza)      AS totale_perdita_frequenza,
        normalize_italian_number(totale_perdita_ammontare)       AS _totale_perdita_eur,
        normalize_italian_integer(reddito_continuita_frequenza)      AS reddito_continuita_frequenza,
        normalize_italian_number(reddito_continuita_ammontare)       AS _reddito_continuita_eur,
        normalize_italian_integer(perdita_continuita_frequenza)      AS perdita_continuita_frequenza,
        normalize_italian_number(perdita_continuita_ammontare)       AS _perdita_continuita_eur,
        normalize_italian_integer(reddito_impresa_ordinaria_frequenza)      AS reddito_impresa_ordinaria_frequenza,
        normalize_italian_number(reddito_impresa_ordinaria_ammontare)       AS _reddito_impresa_ordinaria_eur,
        normalize_italian_integer(reddito_impresa_semplificata_frequenza)      AS reddito_impresa_semplificata_frequenza,
        normalize_italian_number(reddito_impresa_semplificata_ammontare)       AS _reddito_impresa_semplificata_eur,
        normalize_italian_integer(reddito_lavoro_autonomo_frequenza)      AS reddito_lavoro_autonomo_frequenza,
        normalize_italian_number(reddito_lavoro_autonomo_ammontare)       AS _reddito_lavoro_autonomo_eur,
        normalize_italian_integer(terreni_imponibile_frequenza)      AS terreni_imponibile_frequenza,
        normalize_italian_number(terreni_imponibile_ammontare)       AS _terreni_imponibile_eur,
        normalize_italian_integer(terreni_non_imponibile_frequenza)      AS terreni_non_imponibile_frequenza,
        normalize_italian_number(terreni_non_imponibile_ammontare)       AS _terreni_non_imponibile_eur,
        normalize_italian_integer(fabbricati_imponibile_frequenza)      AS fabbricati_imponibile_frequenza,
        normalize_italian_number(fabbricati_imponibile_ammontare)       AS _fabbricati_imponibile_eur,
        normalize_italian_integer(fabbricati_non_imponibile_frequenza)      AS fabbricati_non_imponibile_frequenza,
        normalize_italian_number(fabbricati_non_imponibile_ammontare)       AS _fabbricati_non_imponibile_eur,
        normalize_italian_integer(capitali_diversi_frequenza)      AS capitali_diversi_frequenza,
        normalize_italian_number(capitali_diversi_ammontare)       AS _capitali_diversi_eur
    FROM raw_input
    WHERE normalize_string(codice) IS NOT NULL
      AND normalize_string(codice) NOT IN ('Codice', '0')
)
SELECT
    anno,
    classe_reddito,
    codice,
    numero_societa,
    totale_reddito_frequenza, ROUND(_totale_reddito_eur * 1000, 0) AS totale_reddito_eur,
    totale_perdita_frequenza, ROUND(_totale_perdita_eur * 1000, 0) AS totale_perdita_eur,
    reddito_continuita_frequenza, ROUND(_reddito_continuita_eur * 1000, 0) AS reddito_continuita_eur,
    perdita_continuita_frequenza, ROUND(_perdita_continuita_eur * 1000, 0) AS perdita_continuita_eur,
    reddito_impresa_ordinaria_frequenza, ROUND(_reddito_impresa_ordinaria_eur * 1000, 0) AS reddito_impresa_ordinaria_eur,
    reddito_impresa_semplificata_frequenza, ROUND(_reddito_impresa_semplificata_eur * 1000, 0) AS reddito_impresa_semplificata_eur,
    reddito_lavoro_autonomo_frequenza, ROUND(_reddito_lavoro_autonomo_eur * 1000, 0) AS reddito_lavoro_autonomo_eur,
    terreni_imponibile_frequenza, ROUND(_terreni_imponibile_eur * 1000, 0) AS terreni_imponibile_eur,
    terreni_non_imponibile_frequenza, ROUND(_terreni_non_imponibile_eur * 1000, 0) AS terreni_non_imponibile_eur,
    fabbricati_imponibile_frequenza, ROUND(_fabbricati_imponibile_eur * 1000, 0) AS fabbricati_imponibile_eur,
    fabbricati_non_imponibile_frequenza, ROUND(_fabbricati_non_imponibile_eur * 1000, 0) AS fabbricati_non_imponibile_eur,
    capitali_diversi_frequenza, ROUND(_capitali_diversi_eur * 1000, 0) AS capitali_diversi_eur
FROM raw_parsed
