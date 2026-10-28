-- mart_regione_anno.sql — acsp_imprese_regione
-- Regione × anno: numero imprenditori, totale reddito e perdita dichiarati,
-- reddito medio per imprenditore, quota sul totale nazionale, rank per reddito.

WITH totals AS (
    SELECT anno, SUM(totale_reddito_eur) AS reddito_nazionale_eur
    FROM clean_input
    WHERE anno IS NOT NULL
    GROUP BY anno
)
SELECT
    c.anno,
    c.regione,
    c.cod_regione,
    c.numero_imprenditori,
    c.totale_reddito_eur,
    c.totale_perdita_eur,
    ROUND(c.totale_reddito_eur / NULLIF(c.numero_imprenditori, 0), 0) AS reddito_medio_imprenditore_eur,
    ROUND(100.0 * c.totale_reddito_eur / NULLIF(t.reddito_nazionale_eur, 0), 2) AS quota_reddito_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.totale_reddito_eur DESC) AS rank_reddito
FROM clean_input c
JOIN totals t USING (anno)
ORDER BY c.anno, rank_reddito
