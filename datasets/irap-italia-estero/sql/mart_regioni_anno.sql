-- mart_regioni_anno.sql — irap_italia_estero
-- Quota % produzione estera e Italia sul totale regionale.

WITH totals AS (
    SELECT anno, SUM(prod_netta_eur) AS totale_nazionale
    FROM clean_input
    GROUP BY anno
)
SELECT
    c.anno, c.regione, c.cod_regione, c.contribuenti,
    c.prod_netta_freq, c.prod_netta_eur,
    c.vp_estero_freq, c.vp_estero_eur,
    c.vp_italia_freq, c.vp_italia_eur,
    ROUND(c.vp_estero_eur * 100.0 / c.prod_netta_eur, 2) AS quota_estero_pct,
    ROUND(c.prod_netta_eur * 100.0 / t.totale_nazionale, 2) AS quota_nazionale_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.prod_netta_eur DESC) AS rank_produzione
FROM clean_input c
JOIN totals t USING (anno)
