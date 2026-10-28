-- mart_classe_volume_affari_anno.sql — acsp_tutte_classi_volume
-- Classi di volume d'affari in euro × anno: numero società, totale reddito dichiarato, reddito medio per
-- società, quota sul totale nazionale e rank per reddito.

WITH totals AS (
    SELECT anno, SUM(totale_reddito_eur) AS reddito_nazionale_eur
    FROM clean_input
    WHERE anno IS NOT NULL
    GROUP BY anno
)
SELECT
    c.anno,
    c.classe_volume_affari,
    c.codice,
    c.numero_societa,
    c.totale_reddito_eur,
    ROUND(c.totale_reddito_eur / NULLIF(c.numero_societa, 0), 0) AS reddito_medio_societa_eur,
    ROUND(100.0 * c.totale_reddito_eur / NULLIF(t.reddito_nazionale_eur, 0), 2) AS quota_reddito_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.totale_reddito_eur DESC) AS rank_reddito
FROM clean_input c
JOIN totals t USING (anno)
ORDER BY c.anno, rank_reddito
