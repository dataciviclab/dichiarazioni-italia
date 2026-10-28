-- mart_regione_anno.sql — acsp_professionisti_regione
-- Regione × anno: numero società, compensi, spese, reddito dichiarato, reddito
-- medio per società, margine (reddito / compensi), quote sul totale nazionale
-- e rank per reddito.
-- `compensi_eur` è il flusso lordo professionale; `totale_reddito_eur` è il
-- netto: il rapporto tra i due è il margine, la misura che caratterizza la
-- professione (a.i. 2023: ~50% a livello nazionale).

WITH totals AS (
    SELECT
        anno,
        SUM(totale_reddito_eur) AS reddito_nazionale_eur,
        SUM(compensi_eur)       AS compensi_nazionali_eur
    FROM clean_input
    WHERE anno IS NOT NULL
    GROUP BY anno
)
SELECT
    c.anno,
    c.regione,
    c.cod_regione,
    c.numero_societa,
    c.compensi_eur,
    c.totale_spese_eur,
    c.totale_reddito_eur,
    ROUND(c.totale_reddito_eur / NULLIF(c.numero_societa, 0), 0) AS reddito_medio_societa_eur,
    ROUND(100.0 * c.totale_reddito_eur / NULLIF(c.compensi_eur, 0), 2) AS margine_pct,
    ROUND(100.0 * c.compensi_eur / NULLIF(t.compensi_nazionali_eur, 0), 2) AS quota_compensi_pct,
    ROUND(100.0 * c.totale_reddito_eur / NULLIF(t.reddito_nazionale_eur, 0), 2) AS quota_reddito_pct,
    RANK() OVER (PARTITION BY c.anno ORDER BY c.totale_reddito_eur DESC) AS rank_reddito
FROM clean_input c
JOIN totals t USING (anno)
ORDER BY c.anno, rank_reddito
