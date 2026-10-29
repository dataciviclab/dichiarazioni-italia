-- mart_anno.sql — abpf_titolari_piva_regione
-- Trend nazionale per anno d'imposta: titolari, reddito complessivo, imposta
-- netta, volume d'affari, regimi agevolati (forfetario, vantaggio), reddito
-- medio per titolare, aliquota media e variazione % del reddito.

SELECT
    anno,
    SUM(numero_titolari) AS numero_titolari,
    SUM(reddito_complessivo_eur) AS reddito_complessivo_eur,
    SUM(reddito_imponibile_eur) AS reddito_imponibile_eur,
    SUM(imposta_netta_eur) AS imposta_netta_eur,
    SUM(volume_d_affari_eur) AS volume_d_affari_eur,
    SUM(reddito_netto_regime_forfetario_eur) AS reddito_forfetario_eur,
    SUM(reddito_netto_regime_di_vantaggio_eur) AS reddito_vantaggio_eur,
    ROUND(SUM(reddito_complessivo_eur) / NULLIF(SUM(numero_titolari), 0), 0) AS reddito_medio_titolare_eur,
    ROUND(100.0 * SUM(imposta_netta_eur) / NULLIF(SUM(reddito_imponibile_eur), 0), 2) AS aliquota_media_pct,
    ROUND(
        100.0 * (SUM(reddito_complessivo_eur) - LAG(SUM(reddito_complessivo_eur)) OVER (ORDER BY anno))
        / NULLIF(LAG(SUM(reddito_complessivo_eur)) OVER (ORDER BY anno), 0), 2
    ) AS delta_reddito_pct
FROM clean_input
GROUP BY anno
ORDER BY anno
