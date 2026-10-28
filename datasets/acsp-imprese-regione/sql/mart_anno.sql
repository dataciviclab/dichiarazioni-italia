-- mart_anno.sql — acsp_imprese_regione
-- Trend nazionale per anno d'imposta: numero imprenditori, reddito e perdita
-- dichiarati, reddito medio per imprenditore e variazione % sull'anno precedente.

SELECT
    anno,
    SUM(numero_imprenditori) AS numero_imprenditori,
    SUM(totale_reddito_eur) AS totale_reddito_eur,
    SUM(totale_perdita_eur) AS totale_perdita_eur,
    ROUND(SUM(totale_reddito_eur) / NULLIF(SUM(numero_imprenditori), 0), 0) AS reddito_medio_imprenditore_eur,
    ROUND(
        100.0 * (SUM(totale_reddito_eur) - LAG(SUM(totale_reddito_eur)) OVER (ORDER BY anno))
        / NULLIF(LAG(SUM(totale_reddito_eur)) OVER (ORDER BY anno), 0), 2
    ) AS delta_reddito_pct
FROM clean_input
GROUP BY anno
ORDER BY anno
