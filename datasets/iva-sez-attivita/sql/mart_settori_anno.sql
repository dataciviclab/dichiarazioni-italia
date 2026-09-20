-- mart_settori_anno.sql — iva_sez_attivita
-- Quota % volume d'affari per settore sul totale nazionale.

WITH totals AS (
    SELECT anno, SUM(volume_affari_eur) AS volume_nazionale
    FROM clean_input
    GROUP BY anno
)
SELECT
    c.anno, c.sezione_attivita, c.codice, c.contribuenti,
    c.volume_frequenza, c.volume_affari_eur,
    c.acquisti_frequenza, c.acquisti_eur,
    c.va_frequenza, c.va_fiscale_eur,
    c.imposta_dovuta_frequenza, c.imposta_dovuta_eur,
    c.imposta_credito_frequenza, c.imposta_credito_eur,
    ROUND(c.volume_affari_eur * 100.0 / t.volume_nazionale, 2) AS quota_volume_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.volume_affari_eur DESC) AS rank_volume
FROM clean_input c
JOIN totals t USING (anno)
