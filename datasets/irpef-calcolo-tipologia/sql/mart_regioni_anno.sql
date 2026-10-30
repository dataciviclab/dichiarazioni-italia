-- mart_regioni_anno.sql — irpef_calcolo_tipologia
-- Regione × anno × tipologia: calcolo dell'imposta e aliquote effettive.
-- Serve per "quanto si paga lordo e quanto resta netto, regione per regione".

SELECT
    anno,
    regione,
    cod_regione,
    cod_tipologia,
    tipologia,
    contribuenti,
    reddito_complessivo_eur,
    reddito_imponibile_eur,
    imposta_lorda_eur,
    detrazioni_eur,
    imposta_netta_eur,
    ROUND(100.0 * imposta_lorda_eur / NULLIF(reddito_imponibile_eur, 0), 2) AS aliquota_lorda_pct,
    ROUND(100.0 * imposta_netta_eur / NULLIF(reddito_imponibile_eur, 0), 2) AS aliquota_netta_pct,
    ROUND(100.0 * detrazioni_eur / NULLIF(imposta_lorda_eur, 0), 2)         AS incidenza_detrazioni_pct,
    ROUND(
        reddito_imponibile_eur / NULLIF(contribuenti, 0),
        0
    ) AS reddito_imponibile_medio_eur,
    ROUND(
        imposta_netta_eur / NULLIF(contribuenti, 0),
        0
    ) AS imposta_netta_media_eur,
    RANK() OVER (
        PARTITION BY anno, cod_tipologia
        ORDER BY imposta_netta_eur DESC
    ) AS rank_imposta_tipologia
FROM clean_input
WHERE anno IS NOT NULL
ORDER BY anno, cod_tipologia, rank_imposta_tipologia
