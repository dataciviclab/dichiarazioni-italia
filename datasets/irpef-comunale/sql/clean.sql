-- IRPEF Comunale — CLEAN
-- Gestisce schema drift: 2019-2022 (50 cols) vs 2023+ (52 cols).
-- Con header:false + normalize_rows_to_columns:true, la prima riga dati
-- è il testo dell'header CSV. Usiamo window function per rilevare lo
-- schema dalla prima riga e propagarlo a tutte le righe.

WITH raw_numbered AS (
    SELECT *, ROW_NUMBER() OVER () AS rn
    FROM raw_input
),
schema_detect AS (
    SELECT *,
        -- Prima riga = header text: column34 contiene il nome colonna
        -- Nuovo schema (2023+): "Reddito complessivo - Frequenza"
        -- Vecchio schema: "Reddito complessivo minore..."
        CASE
            WHEN rn = 1 AND column34 LIKE '%complessivo%'
                 AND column34 NOT LIKE '%minore%' THEN 1
            WHEN rn = 1 THEN 0
        END AS schema_flag
    FROM raw_numbered
),
propagated AS (
    SELECT *,
        MAX(schema_flag) OVER () AS is_new_schema
    FROM schema_detect
)
SELECT
    cast_int(column00) AS anno_di_imposta,
    normalize_string(column01) AS codice_catastale,
    normalize_string(column02) AS codice_istat_comune,
    normalize_string(column03) AS denominazione_comune,
    normalize_string(column04) AS sigla_provincia,
    normalize_string(column05) AS regione,
    normalize_string(column06) AS codice_istat_regione,
    cast_int(column07) AS numero_contribuenti,
    cast_int(column08) AS reddito_da_fabbricati_freq,
    cast_double(column09) AS reddito_da_fabbricati_eur,
    cast_int(column10) AS reddito_da_lavoro_dipendente_e_assimilati_freq,
    cast_double(column11) AS reddito_da_lavoro_dipendente_e_assimilati_eur,
    cast_int(column12) AS reddito_da_pensione_freq,
    cast_double(column13) AS reddito_da_pensione_eur,
    cast_int(column14) AS reddito_da_lavoro_autonomo_comprensivo_valori_nulli_freq,
    cast_double(column15) AS reddito_da_lavoro_autonomo_comprensivo_valori_nulli_eur,
    cast_int(column16) AS reddito_di_spettanza_imprenditore_contabilita_ordinaria_freq,
    cast_double(column17) AS reddito_di_spettanza_imprenditore_contabilita_ordinaria_eur,
    cast_int(column18) AS reddito_di_spettanza_imprenditore_contabilita_semplificata_freq,
    cast_double(column19) AS reddito_di_spettanza_imprenditore_contabilita_semplificata_eur,
    cast_int(column20) AS reddito_da_partecipazione_freq,
    cast_double(column21) AS reddito_da_partecipazione_eur,
    cast_int(column22) AS reddito_imponibile_freq,
    cast_double(column23) AS reddito_imponibile_eur,
    cast_int(column24) AS imposta_netta_freq,
    cast_double(column25) AS imposta_netta_eur,
    cast_int(column26) AS trattamento_spettante_freq,
    cast_double(column27) AS trattamento_spettante_eur,
    cast_int(column28) AS reddito_imponibile_addizionale_freq,
    cast_double(column29) AS reddito_imponibile_addizionale_eur,
    cast_int(column30) AS addizionale_regionale_dovuta_freq,
    cast_double(column31) AS addizionale_regionale_dovuta_eur,
    cast_int(column32) AS addizionale_comunale_dovuta_freq,
    cast_double(column33) AS addizionale_comunale_dovuta_eur,
    -- col34-51: drift schema (skip header text row)
    CASE WHEN rn > 1 AND is_new_schema THEN cast_int(column34) END AS reddito_complessivo_freq,
    CASE WHEN rn > 1 AND is_new_schema THEN cast_double(column35) END AS reddito_complessivo_eur,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_int(column36) ELSE cast_int(column34) END
    END AS reddito_complessivo_minore_o_uguale_a_zero_euro_freq,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_double(column37) ELSE cast_double(column35) END
    END AS reddito_complessivo_minore_o_uguale_a_zero_euro_eur,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_int(column38) ELSE cast_int(column36) END
    END AS reddito_complessivo_da_0_a_10000_euro_freq,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_double(column39) ELSE cast_double(column37) END
    END AS reddito_complessivo_da_0_a_10000_euro_eur,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_int(column40) ELSE cast_int(column38) END
    END AS reddito_complessivo_da_10000_a_15000_euro_freq,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_double(column41) ELSE cast_double(column39) END
    END AS reddito_complessivo_da_10000_a_15000_euro_eur,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_int(column42) ELSE cast_int(column40) END
    END AS reddito_complessivo_da_15000_a_26000_euro_freq,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_double(column43) ELSE cast_double(column41) END
    END AS reddito_complessivo_da_15000_a_26000_euro_eur,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_int(column44) ELSE cast_int(column42) END
    END AS reddito_complessivo_da_26000_a_55000_euro_freq,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_double(column45) ELSE cast_double(column43) END
    END AS reddito_complessivo_da_26000_a_55000_euro_eur,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_int(column46) ELSE cast_int(column44) END
    END AS reddito_complessivo_da_55000_a_75000_euro_freq,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_double(column47) ELSE cast_double(column45) END
    END AS reddito_complessivo_da_55000_a_75000_euro_eur,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_int(column48) ELSE cast_int(column46) END
    END AS reddito_complessivo_da_75000_a_120000_euro_freq,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_double(column49) ELSE cast_double(column47) END
    END AS reddito_complessivo_da_75000_a_120000_euro_eur,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_int(column50) ELSE cast_int(column48) END
    END AS reddito_complessivo_oltre_120000_euro_freq,
    CASE WHEN rn > 1 THEN
        CASE WHEN is_new_schema THEN cast_double(column51) ELSE cast_double(column49) END
    END AS reddito_complessivo_oltre_120000_euro_eur
FROM propagated
WHERE rn > 1  -- esclude riga header text
