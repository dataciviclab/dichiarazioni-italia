-- mart_regioni_anno.sql — irap_vp_regime
-- Produzione netta per regime, quota % sul totale nazionale.

WITH totals AS (
    SELECT anno, SUM(prod_netta_eur) AS totale_nazionale
    FROM clean_input
    GROUP BY anno
)
SELECT
    c.anno, c.regione, c.cod_regione, c.contribuenti,
    c.vp_ord_freq, c.vp_ord_eur,
    c.vp_forf_freq, c.vp_forf_eur,
    c.vp_agr_freq, c.vp_agr_eur,
    c.vp_arti_freq, c.vp_arti_eur,
    c.vp_noncomm_freq, c.vp_noncomm_eur,
    c.deduzioni_freq, c.deduzioni_eur,
    c.prod_netta_freq, c.prod_netta_eur,
    ROUND(c.prod_netta_eur * 100.0 / t.totale_nazionale, 2) AS quota_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.prod_netta_eur DESC) AS rank_produzione
FROM clean_input c
JOIN totals t USING (anno)
