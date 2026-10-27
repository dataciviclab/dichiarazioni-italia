-- mart_imposta_anno.sql — irap_imposta_settore (multi-year)
-- Trend nazionale: base imponibile, imposta, aliquota effettiva e delta
-- sull'anno precedente. Confrontabile con irap_imposta_regione (stessa misura
-- per regione): i due totali coincidono.
--
-- ⚠️ Il 2014 è il primo anno disponibile ma ha un perimetro diverso
-- (cambio di definizione della base: −31% sull'anno successivo): i delta
-- 2014→2015 vanno letti con cautela, il trend parte dal 2015.

WITH per_anno AS (
    SELECT
        anno,
        SUM(contribuenti)              AS contribuenti,
        SUM(base_imponibile_frequenza) AS base_imponibile_frequenza,
        SUM(base_imponibile_eur)       AS base_imponibile_eur,
        SUM(imposta_frequenza)         AS imposta_frequenza,
        SUM(imposta_eur)               AS imposta_eur
    FROM clean_input
    WHERE anno IS NOT NULL
    GROUP BY anno
),
con_lag AS (
    SELECT
        *,
        LAG(base_imponibile_eur) OVER (ORDER BY anno) AS base_anno_precedente,
        LAG(imposta_eur) OVER (ORDER BY anno)         AS imposta_anno_precedente
    FROM per_anno
)
SELECT
    anno,
    contribuenti,
    base_imponibile_frequenza,
    base_imponibile_eur,
    imposta_frequenza,
    imposta_eur,
    ROUND(100.0 * imposta_eur / NULLIF(base_imponibile_eur, 0), 2) AS aliquota_effettiva_pct,
    ROUND(
        100.0 * (base_imponibile_eur - base_anno_precedente) / NULLIF(base_anno_precedente, 0),
        1
    ) AS delta_base_pct,
    ROUND(
        100.0 * (imposta_eur - imposta_anno_precedente) / NULLIF(imposta_anno_precedente, 0),
        1
    ) AS delta_imposta_pct
FROM con_lag
ORDER BY anno
