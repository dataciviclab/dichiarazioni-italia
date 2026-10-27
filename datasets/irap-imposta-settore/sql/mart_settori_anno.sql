-- mart_settori_anno.sql — irap_imposta_settore
-- Sezione di attività × anno: base imponibile, imposta, aliquota effettiva
-- (imposta / base), quota sulla base nazionale e rank per imposta.
-- L'aliquota effettiva misura il carico IRAP reale del settore, al netto di
-- deduzioni e credito d'imposta.

WITH totals AS (
    SELECT
        anno,
        SUM(base_imponibile_eur) AS base_nazionale_eur
    FROM clean_input
    WHERE anno IS NOT NULL
    GROUP BY anno
)
SELECT
    c.anno,
    c.sezione_attivita,
    c.codice,
    c.contribuenti,
    c.base_imponibile_frequenza,
    c.base_imponibile_eur,
    c.imposta_frequenza,
    c.imposta_eur,
    ROUND(100.0 * c.imposta_eur / NULLIF(c.base_imponibile_eur, 0), 2) AS aliquota_effettiva_pct,
    ROUND(100.0 * c.base_imponibile_eur / NULLIF(t.base_nazionale_eur, 0), 2) AS quota_base_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.imposta_eur DESC) AS rank_imposta
FROM clean_input c
JOIN totals t USING (anno)
ORDER BY c.anno, rank_imposta
