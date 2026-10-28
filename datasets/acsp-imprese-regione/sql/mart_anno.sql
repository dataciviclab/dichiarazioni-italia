-- mart_anno.sql — acsp_imprese_regione
-- Trend nazionale per anno d'imposta: numero imprenditori, reddito e perdita
-- dichiarati, **determinazione del reddito d'impresa** (contabilità ordinaria e
-- semplificata, blocchi, componenti, differenza), reddito medio per imprenditore
-- e variazione % sull'anno precedente.
--
-- `rapporto_blocco1_ordinaria` è una **guardia**: la fonte non etichetta i due
-- blocchi di colonne con lo stesso nome (`reddito_impresa_blocco1` / `_blocco2`),
-- la corrispondenza ordinaria/semplificata è un'inferenza (vedi README). Il
-- rapporto vale 1,07-1,19 su tutti gli anni; se la fonte riordinasse i blocchi
-- darebbe ~0,84-0,94 → la range rule in dataset.yml fa fallire la validazione
-- invece di scambiare le etichette in silenzio.

SELECT
    anno,
    SUM(numero_imprenditori) AS numero_imprenditori,
    SUM(totale_reddito_eur) AS totale_reddito_eur,
    SUM(totale_perdita_eur) AS totale_perdita_eur,
    -- Determinazione del reddito d'impresa
    SUM(reddito_impresa_ordinaria_eur) AS reddito_impresa_ordinaria_eur,
    SUM(reddito_impresa_semplificata_eur) AS reddito_impresa_semplificata_eur,
    SUM(reddito_impresa_blocco1_eur) AS reddito_impresa_blocco1_eur,
    SUM(reddito_impresa_blocco2_eur) AS reddito_impresa_blocco2_eur,
    SUM(ricavi_vendite_eur) AS ricavi_vendite_eur,
    SUM(componenti_positivi_eur) AS componenti_positivi_eur,
    SUM(componenti_negativi_eur) AS componenti_negativi_eur,
    SUM(differenza_eur) AS differenza_eur,
    -- Sintesi
    ROUND(SUM(totale_reddito_eur) / NULLIF(SUM(numero_imprenditori), 0), 0) AS reddito_medio_imprenditore_eur,
    ROUND(
        100.0 * (SUM(totale_reddito_eur) - LAG(SUM(totale_reddito_eur)) OVER (ORDER BY anno))
        / NULLIF(LAG(SUM(totale_reddito_eur)) OVER (ORDER BY anno), 0), 2
    ) AS delta_reddito_pct,
    -- Guardia dell'inferenza dei blocchi (vedi commento in testa)
    ROUND(
        SUM(reddito_impresa_blocco1_eur) / NULLIF(SUM(reddito_impresa_ordinaria_eur), 0), 3
    ) AS rapporto_blocco1_ordinaria
FROM clean_input
GROUP BY anno
ORDER BY anno
