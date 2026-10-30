-- mart_tipologie_anno.sql — irpef_calcolo_tipologia
-- Tipologia × anno: il passaggio lorda → detrazioni → netta, con le aliquote
-- effettive e la quota sul totale delle sei tipologie.
--
-- ⚠️ Le sei tipologie NON sono una partizione dei contribuenti IRPEF: coprono
-- ~94% dei contribuenti e ~99% del gettito (a.i. 2023). Le quote qui sotto
-- sono quote sulle sei viste, non sull'IRPEF totale del Paese.

WITH per_tipologia AS (
    SELECT
        anno,
        cod_tipologia,
        tipologia,
        SUM(contribuenti)            AS contribuenti,
        SUM(reddito_complessivo_eur) AS reddito_complessivo_eur,
        SUM(reddito_imponibile_eur)  AS reddito_imponibile_eur,
        SUM(imposta_lorda_eur)       AS imposta_lorda_eur,
        SUM(detrazioni_eur)          AS detrazioni_eur,
        SUM(imposta_netta_eur)       AS imposta_netta_eur
    FROM clean_input
    WHERE anno IS NOT NULL
    GROUP BY anno, cod_tipologia, tipologia
),
totali AS (
    SELECT
        anno,
        SUM(contribuenti)      AS contribuenti_tot,
        SUM(imposta_netta_eur) AS netta_tot
    FROM per_tipologia
    GROUP BY anno
),
con_lag AS (
    SELECT
        p.*,
        t.contribuenti_tot,
        t.netta_tot,
        LAG(p.imposta_netta_eur) OVER (PARTITION BY p.cod_tipologia ORDER BY p.anno) AS netta_prec,
        LAG(p.contribuenti)      OVER (PARTITION BY p.cod_tipologia ORDER BY p.anno) AS contribuenti_prec
    FROM per_tipologia p
    JOIN totali t USING (anno)
)
SELECT
    anno,
    cod_tipologia,
    tipologia,
    contribuenti,
    reddito_complessivo_eur,
    reddito_imponibile_eur,
    imposta_lorda_eur,
    detrazioni_eur,
    imposta_netta_eur,
    ROUND(100.0 * imposta_lorda_eur / NULLIF(reddito_imponibile_eur, 0), 2) AS aliquota_lorda_pct,
    ROUND(100.0 * imposta_netta_eur / NULLIF(reddito_imponibile_eur, 0), 2) AS aliquota_netta_pct,
    ROUND(100.0 * detrazioni_eur / NULLIF(imposta_lorda_eur, 0), 2)         AS incidenza_detrazioni_pct,
    ROUND(100.0 * contribuenti / NULLIF(contribuenti_tot, 0), 1)            AS quota_contribuenti_pct,
    ROUND(100.0 * imposta_netta_eur / NULLIF(netta_tot, 0), 1)              AS quota_imposta_pct,
    ROUND(
        100.0 * (contribuenti - contribuenti_prec) / NULLIF(contribuenti_prec, 0),
        1
    ) AS delta_contribuenti_pct,
    ROUND(
        100.0 * (imposta_netta_eur - netta_prec) / NULLIF(netta_prec, 0),
        1
    ) AS delta_imposta_pct,
    RANK() OVER (PARTITION BY anno ORDER BY imposta_netta_eur DESC) AS rank_imposta
FROM con_lag
ORDER BY anno, rank_imposta
