-- mart_regioni_anno.sql — ires_redditi_regione
-- Reddito impresa per regione con quota % sul totale nazionale.

WITH totals AS (
    SELECT anno, SUM(reddito_totale_eur) AS reddito_nazionale
    FROM clean_input
    GROUP BY anno
)
SELECT
    c.anno, c.regione, c.n_dichiarazioni,
    c.reddito_continuita_freq, c.reddito_continuita_eur,
    c.perdita_continuita_freq, c.perdita_continuita_eur,
    c.reddito_totale_freq, c.reddito_totale_eur,
    c.perdita_totale_freq, c.perdita_totale_eur,
    ROUND(c.reddito_totale_eur * 100.0 / t.reddito_nazionale, 2) AS quota_reddito_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.reddito_totale_eur DESC) AS rank_reddito
FROM clean_input c
JOIN totals t USING (anno)
