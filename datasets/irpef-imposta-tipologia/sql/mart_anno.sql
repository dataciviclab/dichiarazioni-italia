-- mart_anno.sql — irpef_imposta_tipologia
-- Trend nazionale: contribuenti, imposta netta, imposta media per contribuente
-- e variazione % dell'imposta sull'anno precedente.

SELECT
    anno,
    SUM(numero_contribuenti) AS numero_contribuenti,
    SUM(imposta_netta_frequenza) AS imposta_netta_frequenza,
    SUM(imposta_netta_eur) AS imposta_netta_eur,
    ROUND(SUM(imposta_netta_eur) / NULLIF(SUM(numero_contribuenti), 0), 0) AS imposta_media_contribuente_eur,
    ROUND(
        100.0 * (SUM(imposta_netta_eur) - LAG(SUM(imposta_netta_eur)) OVER (ORDER BY anno))
        / NULLIF(LAG(SUM(imposta_netta_eur)) OVER (ORDER BY anno), 0), 2
    ) AS delta_imposta_pct
FROM clean_input
GROUP BY anno
ORDER BY anno
