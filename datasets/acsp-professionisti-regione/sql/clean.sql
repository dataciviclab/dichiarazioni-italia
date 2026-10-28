-- clean.sql — acsp_professionisti_regione
-- Società di persone (modello ACSP): Redditi e compensi dichiarati dalle società di persone professionali per regione.
-- Vista MEF analisi_stat ACSPPROF0201 — "Professionisti" — "Regione".
--
-- Lettura POSIZIONALE con tutte le colonne VARCHAR (vedi dataset.yml): i numeri
-- sono in formato italiano e vanno normalizzati dalle macro, che lavorano su
-- stringhe. Con `source: auto` lo sniffing di DuckDB tipizza DOUBLE le colonne i
-- cui valori hanno un solo punto (es. "121.330" è un float valido) e la macro le
-- corrompe (×10 / ÷10); l'inferenza è PER FILE, quindi un campione di anni non
-- basta a escluderlo. Qui l'ordine delle colonne è verificato identico in tutti
-- gli anni, quindi la lettura posizionale è sicura.
--
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
-- Ammontari in migliaia di euro → ×1000. Colonne "Media" scartate.
-- `***` = dato oscurato dalla fonte (privacy) → NULL via TRY_CAST.
-- Righe escluse: la riga di header (letta come dato con skip: 9, codice='Codice'),
-- `TOTALE` (codice='0') e la riga-nota finale (codice NULL).

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER)                     AS anno,
        normalize_string(regione)                       AS regione,
        LPAD(normalize_string(codice), 2, '0')          AS cod_regione,
        normalize_italian_integer(numero_societa)       AS numero_societa,
        normalize_italian_integer(reddito_lavoro_autonomo_frequenza)      AS reddito_lavoro_autonomo_frequenza,
        normalize_italian_number(reddito_lavoro_autonomo_ammontare)       AS _reddito_lavoro_autonomo_eur,
        normalize_italian_integer(perdita_lavoro_autonomo_frequenza)      AS perdita_lavoro_autonomo_frequenza,
        normalize_italian_number(perdita_lavoro_autonomo_ammontare)       AS _perdita_lavoro_autonomo_eur,
        normalize_italian_integer(reddito_partecipazione_associazione_frequenza)      AS reddito_partecipazione_associazione_frequenza,
        normalize_italian_number(reddito_partecipazione_associazione_ammontare)       AS _reddito_partecipazione_associazione_eur,
        normalize_italian_integer(capitali_diversi_frequenza)      AS capitali_diversi_frequenza,
        normalize_italian_number(capitali_diversi_ammontare)       AS _capitali_diversi_eur,
        normalize_italian_integer(totale_reddito_frequenza)      AS totale_reddito_frequenza,
        normalize_italian_number(totale_reddito_ammontare)       AS _totale_reddito_eur,
        normalize_italian_integer(totale_perdita_frequenza)      AS totale_perdita_frequenza,
        normalize_italian_number(totale_perdita_ammontare)       AS _totale_perdita_eur,
        normalize_italian_integer(compensi_non_annotati_isa_frequenza)      AS compensi_non_annotati_isa_frequenza,
        normalize_italian_number(compensi_non_annotati_isa_ammontare)       AS _compensi_non_annotati_isa_eur,
        normalize_italian_integer(compensi_non_annotati_frequenza)      AS compensi_non_annotati_frequenza,
        normalize_italian_number(compensi_non_annotati_ammontare)       AS _compensi_non_annotati_eur,
        normalize_italian_integer(compensi_frequenza)      AS compensi_frequenza,
        normalize_italian_number(compensi_ammontare)       AS _compensi_eur,
        normalize_italian_integer(spese_immobili_frequenza)      AS spese_immobili_frequenza,
        normalize_italian_number(spese_immobili_ammontare)       AS _spese_immobili_eur,
        normalize_italian_integer(spese_lavoro_dipendente_frequenza)      AS spese_lavoro_dipendente_frequenza,
        normalize_italian_number(spese_lavoro_dipendente_ammontare)       AS _spese_lavoro_dipendente_eur,
        normalize_italian_integer(compensi_terzi_frequenza)      AS compensi_terzi_frequenza,
        normalize_italian_number(compensi_terzi_ammontare)       AS _compensi_terzi_eur,
        normalize_italian_integer(totale_spese_frequenza)      AS totale_spese_frequenza,
        normalize_italian_number(totale_spese_ammontare)       AS _totale_spese_eur
    FROM raw_input
    WHERE normalize_string(codice) IS NOT NULL
      AND normalize_string(codice) NOT IN ('Codice', '0')
)
SELECT
    anno,
    regione,
    cod_regione,
    numero_societa,
    reddito_lavoro_autonomo_frequenza, ROUND(_reddito_lavoro_autonomo_eur * 1000, 0) AS reddito_lavoro_autonomo_eur,
    perdita_lavoro_autonomo_frequenza, ROUND(_perdita_lavoro_autonomo_eur * 1000, 0) AS perdita_lavoro_autonomo_eur,
    reddito_partecipazione_associazione_frequenza, ROUND(_reddito_partecipazione_associazione_eur * 1000, 0) AS reddito_partecipazione_associazione_eur,
    capitali_diversi_frequenza, ROUND(_capitali_diversi_eur * 1000, 0) AS capitali_diversi_eur,
    totale_reddito_frequenza, ROUND(_totale_reddito_eur * 1000, 0) AS totale_reddito_eur,
    totale_perdita_frequenza, ROUND(_totale_perdita_eur * 1000, 0) AS totale_perdita_eur,
    compensi_non_annotati_isa_frequenza, ROUND(_compensi_non_annotati_isa_eur * 1000, 0) AS compensi_non_annotati_isa_eur,
    compensi_non_annotati_frequenza, ROUND(_compensi_non_annotati_eur * 1000, 0) AS compensi_non_annotati_eur,
    compensi_frequenza, ROUND(_compensi_eur * 1000, 0) AS compensi_eur,
    spese_immobili_frequenza, ROUND(_spese_immobili_eur * 1000, 0) AS spese_immobili_eur,
    spese_lavoro_dipendente_frequenza, ROUND(_spese_lavoro_dipendente_eur * 1000, 0) AS spese_lavoro_dipendente_eur,
    compensi_terzi_frequenza, ROUND(_compensi_terzi_eur * 1000, 0) AS compensi_terzi_eur,
    totale_spese_frequenza, ROUND(_totale_spese_eur * 1000, 0) AS totale_spese_eur
FROM raw_parsed
