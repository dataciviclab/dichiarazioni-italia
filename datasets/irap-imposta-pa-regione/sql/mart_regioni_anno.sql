-- mart_regioni_anno.sql — irap_imposta_pa_regione
-- Regione × anno: base imponibile e imposta netta delle P.A., aliquota
-- effettiva (imposta / base), quota sulla base nazionale e rank per imposta.
--
-- imposta_debito_eur / imposta_credito_eur sono la scomposizione della fonte:
-- gli enti con credito d'imposta non versano (o recuperano) l'IRAP.

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
    c.regione,
    c.cod_regione,
    c.base_imponibile_frequenza,
    c.base_imponibile_eur,
    c.imposta_netta_frequenza,
    c.imposta_netta_eur,
    c.imposta_debito_eur,
    c.imposta_credito_eur,
    ROUND(100.0 * c.imposta_netta_eur / NULLIF(c.base_imponibile_eur, 0), 2) AS aliquota_effettiva_pct,
    ROUND(100.0 * c.base_imponibile_eur / NULLIF(t.base_nazionale_eur, 0), 2) AS quota_base_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.imposta_netta_eur DESC) AS rank_imposta
FROM clean_input c
JOIN totals t USING (anno)
ORDER BY c.anno, rank_imposta
