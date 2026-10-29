-- mart_regione_anno.sql — abpf_titolari_piva_regione
-- Regione × anno: numero titolari di partita IVA, reddito complessivo, imposta
-- netta, volume d'affari, aliquota media effettiva e quota sul reddito nazionale.

WITH totals AS (
    SELECT anno, SUM(reddito_complessivo_eur) AS reddito_nazionale_eur
    FROM clean_input
    WHERE anno IS NOT NULL
    GROUP BY anno
)
SELECT
    c.anno,
    c.regione,
    c.cod_regione,
    c.numero_titolari,
    c.reddito_complessivo_eur,
    c.imposta_netta_eur,
    c.volume_d_affari_eur,
    ROUND(c.reddito_complessivo_eur / NULLIF(c.numero_titolari, 0), 0) AS reddito_medio_titolare_eur,
    ROUND(100.0 * c.imposta_netta_eur / NULLIF(c.reddito_imponibile_eur, 0), 2) AS aliquota_media_pct,
    ROUND(100.0 * c.reddito_complessivo_eur / NULLIF(t.reddito_nazionale_eur, 0), 2) AS quota_reddito_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.reddito_complessivo_eur DESC) AS rank_reddito
FROM clean_input c
JOIN totals t USING (anno)
ORDER BY c.anno, rank_reddito
