-- clean.sql — acsp_imprese_regione
-- Società di persone con reddito d'impresa (modello ACSP, "Imprese"): redditi
-- dichiarati e determinazione del reddito d'impresa per regione.
-- Vista MEF analisi_stat ACSPIMP0201 — "Imprese" — "Regione".
--
-- Lettura POSIZIONALE con tutte le colonne VARCHAR (vedi dataset.yml): i numeri
-- sono in formato italiano e le macro normalizzano stringhe. Con `source: auto`
-- lo sniffing tipizza DOUBLE le colonne i cui valori hanno un solo punto
-- (es. "121.330") e la macro le corrompe (×10/÷10).
--
-- Copertura dal file 2015: il file 2014 ha un layout diverso (73 celle, 3 colonne
-- "Ricavi di cui art. 85 a) e b)" in più e 3 posizioni spostate), quindi la
-- lettura posizionale non lo copre. Dal 2015 al 2025 l'ordine è identico.
--
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
-- Ammontari in migliaia di euro → ×1000. Colonne "Media" scartate.
-- `***` = dato oscurato dalla fonte (privacy) → NULL via TRY_CAST.
-- Righe escluse: la riga di header (letta come dato con skip: 9, codice='Codice'),
-- `TOTALE` (codice='0') e la riga-nota finale (codice NULL).
--
-- ⚠️ La fonte ha DUE blocchi di colonne con lo stesso nome (`Erogazioni liberali`,
-- `Reddito di impresa`, `Perdita di impresa`): il primo precede i componenti
-- contabili, il secondo li segue. Qui sono disambiguati come `*_blocco1` /
-- `*_blocco2`. L'aritmetica mostra che il blocco centrale (`ricavi_vendite`,
-- `componenti_positivi`, `componenti_negativi`, `differenza`) è la determinazione
-- in **contabilità semplificata** (`differenza = componenti_positivi - componenti_negativi`),
-- quindi `_blocco1` corrisponde alla contabilità ordinaria e `_blocco2` alla
-- semplificata — la fonte non etichetta i blocchi.

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER)                AS anno,
        normalize_string(regione)                  AS regione,
        LPAD(normalize_string(codice), 2, '0')     AS cod_regione,
        normalize_italian_integer(numero_imprenditori) AS numero_imprenditori,
        normalize_italian_integer(reddito_impresa_ordinaria_frequenza)   AS reddito_impresa_ordinaria_frequenza,
        normalize_italian_number(reddito_impresa_ordinaria_ammontare)    AS _reddito_impresa_ordinaria_eur,
        normalize_italian_integer(reddito_impresa_semplificata_frequenza)   AS reddito_impresa_semplificata_frequenza,
        normalize_italian_number(reddito_impresa_semplificata_ammontare)    AS _reddito_impresa_semplificata_eur,
        normalize_italian_integer(reddito_partecipazione_frequenza)   AS reddito_partecipazione_frequenza,
        normalize_italian_number(reddito_partecipazione_ammontare)    AS _reddito_partecipazione_eur,
        normalize_italian_integer(capitali_diversi_frequenza)   AS capitali_diversi_frequenza,
        normalize_italian_number(capitali_diversi_ammontare)    AS _capitali_diversi_eur,
        normalize_italian_integer(redditi_tassazione_separata_frequenza)   AS redditi_tassazione_separata_frequenza,
        normalize_italian_number(redditi_tassazione_separata_ammontare)    AS _redditi_tassazione_separata_eur,
        normalize_italian_integer(totale_reddito_frequenza)   AS totale_reddito_frequenza,
        normalize_italian_number(totale_reddito_ammontare)    AS _totale_reddito_eur,
        normalize_italian_integer(totale_perdita_frequenza)   AS totale_perdita_frequenza,
        normalize_italian_number(totale_perdita_ammontare)    AS _totale_perdita_eur,
        normalize_italian_integer(utile_conto_economico_frequenza)   AS utile_conto_economico_frequenza,
        normalize_italian_number(utile_conto_economico_ammontare)    AS _utile_conto_economico_eur,
        normalize_italian_integer(perdita_conto_economico_frequenza)   AS perdita_conto_economico_frequenza,
        normalize_italian_number(perdita_conto_economico_ammontare)    AS _perdita_conto_economico_eur,
        normalize_italian_integer(variazioni_aumento_frequenza)   AS variazioni_aumento_frequenza,
        normalize_italian_number(variazioni_aumento_ammontare)    AS _variazioni_aumento_eur,
        normalize_italian_integer(variazioni_diminuzione_frequenza)   AS variazioni_diminuzione_frequenza,
        normalize_italian_number(variazioni_diminuzione_ammontare)    AS _variazioni_diminuzione_eur,
        normalize_italian_integer(erogazioni_liberali_blocco1_frequenza)   AS erogazioni_liberali_blocco1_frequenza,
        normalize_italian_number(erogazioni_liberali_blocco1_ammontare)    AS _erogazioni_liberali_blocco1_eur,
        normalize_italian_integer(reddito_impresa_blocco1_frequenza)   AS reddito_impresa_blocco1_frequenza,
        normalize_italian_number(reddito_impresa_blocco1_ammontare)    AS _reddito_impresa_blocco1_eur,
        normalize_italian_integer(perdita_impresa_blocco1_frequenza)   AS perdita_impresa_blocco1_frequenza,
        normalize_italian_number(perdita_impresa_blocco1_ammontare)    AS _perdita_impresa_blocco1_eur,
        normalize_italian_integer(ricavi_vendite_frequenza)   AS ricavi_vendite_frequenza,
        normalize_italian_number(ricavi_vendite_ammontare)    AS _ricavi_vendite_eur,
        normalize_italian_integer(componenti_positivi_frequenza)   AS componenti_positivi_frequenza,
        normalize_italian_number(componenti_positivi_ammontare)    AS _componenti_positivi_eur,
        normalize_italian_integer(componenti_negativi_frequenza)   AS componenti_negativi_frequenza,
        normalize_italian_number(componenti_negativi_ammontare)    AS _componenti_negativi_eur,
        normalize_italian_integer(differenza_frequenza)   AS differenza_frequenza,
        normalize_italian_number(differenza_ammontare)    AS _differenza_eur,
        normalize_italian_integer(erogazioni_liberali_blocco2_frequenza)   AS erogazioni_liberali_blocco2_frequenza,
        normalize_italian_number(erogazioni_liberali_blocco2_ammontare)    AS _erogazioni_liberali_blocco2_eur,
        normalize_italian_integer(reddito_impresa_blocco2_frequenza)   AS reddito_impresa_blocco2_frequenza,
        normalize_italian_number(reddito_impresa_blocco2_ammontare)    AS _reddito_impresa_blocco2_eur,
        normalize_italian_integer(perdita_impresa_blocco2_frequenza)   AS perdita_impresa_blocco2_frequenza,
        normalize_italian_number(perdita_impresa_blocco2_ammontare)    AS _perdita_impresa_blocco2_eur,
        normalize_italian_integer(altri_ricavi_frequenza)   AS altri_ricavi_frequenza,
        normalize_italian_number(altri_ricavi_ammontare)    AS _altri_ricavi_eur
    FROM raw_input
    WHERE normalize_string(codice) IS NOT NULL
      AND normalize_string(codice) NOT IN ('Codice', '0')
)
SELECT
    anno,
    regione,
    cod_regione,
    numero_imprenditori,
    reddito_impresa_ordinaria_frequenza, ROUND(_reddito_impresa_ordinaria_eur * 1000, 0) AS reddito_impresa_ordinaria_eur,
    reddito_impresa_semplificata_frequenza, ROUND(_reddito_impresa_semplificata_eur * 1000, 0) AS reddito_impresa_semplificata_eur,
    reddito_partecipazione_frequenza, ROUND(_reddito_partecipazione_eur * 1000, 0) AS reddito_partecipazione_eur,
    capitali_diversi_frequenza, ROUND(_capitali_diversi_eur * 1000, 0) AS capitali_diversi_eur,
    redditi_tassazione_separata_frequenza, ROUND(_redditi_tassazione_separata_eur * 1000, 0) AS redditi_tassazione_separata_eur,
    totale_reddito_frequenza, ROUND(_totale_reddito_eur * 1000, 0) AS totale_reddito_eur,
    totale_perdita_frequenza, ROUND(_totale_perdita_eur * 1000, 0) AS totale_perdita_eur,
    utile_conto_economico_frequenza, ROUND(_utile_conto_economico_eur * 1000, 0) AS utile_conto_economico_eur,
    perdita_conto_economico_frequenza, ROUND(_perdita_conto_economico_eur * 1000, 0) AS perdita_conto_economico_eur,
    variazioni_aumento_frequenza, ROUND(_variazioni_aumento_eur * 1000, 0) AS variazioni_aumento_eur,
    variazioni_diminuzione_frequenza, ROUND(_variazioni_diminuzione_eur * 1000, 0) AS variazioni_diminuzione_eur,
    erogazioni_liberali_blocco1_frequenza, ROUND(_erogazioni_liberali_blocco1_eur * 1000, 0) AS erogazioni_liberali_blocco1_eur,
    reddito_impresa_blocco1_frequenza, ROUND(_reddito_impresa_blocco1_eur * 1000, 0) AS reddito_impresa_blocco1_eur,
    perdita_impresa_blocco1_frequenza, ROUND(_perdita_impresa_blocco1_eur * 1000, 0) AS perdita_impresa_blocco1_eur,
    ricavi_vendite_frequenza, ROUND(_ricavi_vendite_eur * 1000, 0) AS ricavi_vendite_eur,
    componenti_positivi_frequenza, ROUND(_componenti_positivi_eur * 1000, 0) AS componenti_positivi_eur,
    componenti_negativi_frequenza, ROUND(_componenti_negativi_eur * 1000, 0) AS componenti_negativi_eur,
    differenza_frequenza, ROUND(_differenza_eur * 1000, 0) AS differenza_eur,
    erogazioni_liberali_blocco2_frequenza, ROUND(_erogazioni_liberali_blocco2_eur * 1000, 0) AS erogazioni_liberali_blocco2_eur,
    reddito_impresa_blocco2_frequenza, ROUND(_reddito_impresa_blocco2_eur * 1000, 0) AS reddito_impresa_blocco2_eur,
    perdita_impresa_blocco2_frequenza, ROUND(_perdita_impresa_blocco2_eur * 1000, 0) AS perdita_impresa_blocco2_eur,
    altri_ricavi_frequenza, ROUND(_altri_ricavi_eur * 1000, 0) AS altri_ricavi_eur
FROM raw_parsed
