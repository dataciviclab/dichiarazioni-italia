-- clean.sql — irap_vp_regime
-- Valore della produzione netta IRAP per regime applicato.
-- Colonne per posizione (header corrotto in alcuni anni).
-- Le colonne "Media" vengono scartate (si ricalcolano da Freq/Ammontare).

WITH raw_parsed AS (
    SELECT
        CAST({year} AS INTEGER)            AS anno,
        normalize_string(column00)         AS regione,
        LPAD(normalize_string(column01), 2, '0') AS cod_regione,
        normalize_italian_integer(column02) AS contribuenti,
        -- Contabilità ordinaria e semplificata
        normalize_italian_integer(column03) AS vp_ord_freq,
        normalize_italian_number(column04)  AS vp_ord_eur,
        -- column05 = media (scartata)
        -- Regime forfetario
        normalize_italian_integer(column06) AS vp_forf_freq,
        normalize_italian_number(column07)  AS vp_forf_eur,
        -- column08 = media (scartata)
        -- Produttori agricoli
        normalize_italian_integer(column09) AS vp_agr_freq,
        normalize_italian_number(column10)  AS vp_agr_eur,
        -- column11 = media (scartata)
        -- Arti e professioni
        normalize_italian_integer(column12) AS vp_arti_freq,
        normalize_italian_number(column13)  AS vp_arti_eur,
        -- column14 = media (scartata)
        -- Attività non commerciali e istituzionali
        normalize_italian_integer(column15) AS vp_noncomm_freq,
        normalize_italian_number(column16)  AS vp_noncomm_eur,
        -- column17 = media (scartata)
        -- Deduzioni
        normalize_italian_integer(column18) AS deduzioni_freq,
        normalize_italian_number(column19)  AS deduzioni_eur,
        -- column20 = media (scartata)
        -- Produzione netta totale
        normalize_italian_integer(column21) AS prod_netta_freq,
        normalize_italian_number(column22)  AS prod_netta_eur
        -- column23 = media (scartata)
    FROM raw_input
    WHERE normalize_string(column00) IS NOT NULL
      AND normalize_string(column01) IS NOT NULL
      AND normalize_string(column00) NOT IN ('TOTALE', 'Non indicata')
      AND normalize_string(column00) != 'Regione'
      AND normalize_string(column01) != 'Codice'
)
SELECT
    anno, regione, cod_regione, contribuenti,
    vp_ord_freq, ROUND(vp_ord_eur, 0)    AS vp_ord_eur,
    vp_forf_freq, ROUND(vp_forf_eur, 0)  AS vp_forf_eur,
    vp_agr_freq, ROUND(vp_agr_eur, 0)    AS vp_agr_eur,
    vp_arti_freq, ROUND(vp_arti_eur, 0)   AS vp_arti_eur,
    vp_noncomm_freq, ROUND(vp_noncomm_eur, 0) AS vp_noncomm_eur,
    deduzioni_freq, ROUND(deduzioni_eur, 0) AS deduzioni_eur,
    prod_netta_freq, ROUND(prod_netta_eur, 0) AS prod_netta_eur
FROM raw_parsed
