-- mart_tipologie_anno.sql — irpef_imposta_tipologia
-- Tipologia × anno: contribuenti, imposta netta, imposta media per contribuente,
-- quota sull'imposta nazionale e rank per imposta.

WITH tot AS (
    SELECT anno, SUM(imposta_netta_eur) AS imposta_nazionale_eur
    FROM clean_input GROUP BY anno
)
SELECT
    c.anno,
    c.tipologia,
    c.numero_contribuenti,
    c.imposta_netta_frequenza,
    c.imposta_netta_eur,
    ROUND(c.imposta_netta_eur / NULLIF(c.numero_contribuenti, 0), 0) AS imposta_media_contribuente_eur,
    ROUND(100.0 * c.imposta_netta_eur / NULLIF(t.imposta_nazionale_eur, 0), 2) AS quota_imposta_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.imposta_netta_eur DESC) AS rank_imposta
FROM clean_input c
JOIN tot t USING (anno)
ORDER BY c.anno, rank_imposta
