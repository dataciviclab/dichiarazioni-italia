-- mart_imposta_anno.sql — irap_imposta_pa_regione (multi-year)
-- Trend nazionale delle P.A.: base imponibile, imposta netta, aliquota
-- effettiva e delta sull'anno precedente. Confrontabile con
-- irap_imposta_regione (totale): la differenza è il settore privato.

WITH per_anno AS (
    SELECT
        anno,
        SUM(base_imponibile_frequenza)  AS base_imponibile_frequenza,
        SUM(base_imponibile_eur)        AS base_imponibile_eur,
        SUM(imposta_netta_frequenza)    AS imposta_netta_frequenza,
        SUM(imposta_netta_eur)          AS imposta_netta_eur,
        SUM(imposta_debito_eur)         AS imposta_debito_eur,
        SUM(imposta_credito_eur)        AS imposta_credito_eur
    FROM clean_input
    WHERE anno IS NOT NULL
    GROUP BY anno
),
con_lag AS (
    SELECT
        *,
        LAG(base_imponibile_eur) OVER (ORDER BY anno) AS base_anno_precedente,
        LAG(imposta_netta_eur) OVER (ORDER BY anno)   AS imposta_anno_precedente
    FROM per_anno
)
SELECT
    anno,
    base_imponibile_frequenza,
    base_imponibile_eur,
    imposta_netta_frequenza,
    imposta_netta_eur,
    imposta_debito_eur,
    imposta_credito_eur,
    ROUND(100.0 * imposta_netta_eur / NULLIF(base_imponibile_eur, 0), 2) AS aliquota_effettiva_pct,
    ROUND(
        100.0 * (base_imponibile_eur - base_anno_precedente) / NULLIF(base_anno_precedente, 0),
        1
    ) AS delta_base_pct,
    ROUND(
        100.0 * (imposta_netta_eur - imposta_anno_precedente) / NULLIF(imposta_anno_precedente, 0),
        1
    ) AS delta_imposta_pct
FROM con_lag
ORDER BY anno
