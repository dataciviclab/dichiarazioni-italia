-- mart_anno.sql — acsp_professionisti_regione
-- Trend nazionale per anno d'imposta: numero società, compensi, spese, reddito
-- dichiarato, perdita dichiarata, reddito medio per società, margine
-- (reddito / compensi) e variazione % del reddito sull'anno precedente.
-- `compensi_eur` è il flusso lordo; `totale_reddito_eur` è il netto.

SELECT
    anno,
    SUM(numero_societa) AS numero_societa,
    SUM(compensi_eur) AS compensi_eur,
    SUM(totale_spese_eur) AS totale_spese_eur,
    SUM(totale_reddito_eur) AS totale_reddito_eur,
    SUM(totale_perdita_eur) AS totale_perdita_eur,
    ROUND(SUM(totale_reddito_eur) / NULLIF(SUM(numero_societa), 0), 0) AS reddito_medio_societa_eur,
    ROUND(100.0 * SUM(totale_reddito_eur) / NULLIF(SUM(compensi_eur), 0), 2) AS margine_pct,
    ROUND(
        100.0 * (SUM(totale_reddito_eur) - LAG(SUM(totale_reddito_eur)) OVER (ORDER BY anno))
        / NULLIF(LAG(SUM(totale_reddito_eur)) OVER (ORDER BY anno), 0), 2
    ) AS delta_reddito_pct
FROM clean_input
GROUP BY anno
ORDER BY anno
