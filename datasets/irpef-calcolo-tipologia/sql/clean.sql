-- clean.sql — irpef_calcolo_tipologia
-- IRPEF: calcolo dell'imposta per tipologia di contribuente e regione
-- (famiglia MEF AETIP*0201, tematica "Calcolo dell'Irpef").
--
-- Sei viste con schema identico (18 colonne), popolazioni diverse:
--   AETIPLD0201 lavoratori dipendenti      AETIPPE0201 pensionati
--   AETPFGA0201 imprenditori               AETPREA0201 autonomi con P.IVA
--   AETPRHA0201 partecipanti s.d.p.        AETIPRB0201 proprietari di fabbricati
-- La tipologia NON è nel dato: arriva da `inject_column` (dataset.yml).
--
-- Lettura POSIZIONALE, tutte le colonne VARCHAR (vedi dataset.yml): i numeri
-- sono in formato italiano e vanno normalizzati dalle macro, che lavorano su
-- stringhe. Con `source: auto` lo sniffer tipizza DOUBLE le colonne con valori
-- piccoli/ambigui e `normalize_italian_*` le corrompe (×10 / ÷10).
--
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
-- Valori raw in migliaia di euro → ×1000.
--
-- Esclusi: la riga di header (letta come dato, `codice` = 'Codice'), le righe
-- `TOTALE`, l'eventuale `Non indicata` e la nota finale (codice vuoto).
-- ⚠️ AETPFGA0201 contiene DUE righe `TOTALE`, la seconda con valori esattamente
-- doppi (890.472 → 1.780.944 contribuenti a.i. 2023): si escludono per codice
-- '0', non per etichetta — filtrando per nome si raddoppierebbe il dataset.

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER)                              AS anno,
        normalize_string(regione)                                AS regione,
        LPAD(normalize_string(codice), 2, '0')                   AS cod_regione,
        normalize_string(cod_tipologia)                          AS cod_tipologia,
        normalize_string(tipologia)                              AS tipologia,
        normalize_italian_integer(contribuenti)                  AS contribuenti,
        normalize_italian_integer(reddito_complessivo_frequenza) AS reddito_complessivo_frequenza,
        normalize_italian_number(reddito_complessivo_ammontare)  AS _reddito_complessivo,
        normalize_italian_integer(reddito_imponibile_frequenza)  AS reddito_imponibile_frequenza,
        normalize_italian_number(reddito_imponibile_ammontare)   AS _reddito_imponibile,
        normalize_italian_integer(imposta_lorda_frequenza)       AS imposta_lorda_frequenza,
        normalize_italian_number(imposta_lorda_ammontare)        AS _imposta_lorda,
        normalize_italian_integer(detrazioni_frequenza)          AS detrazioni_frequenza,
        normalize_italian_number(detrazioni_ammontare)           AS _detrazioni,
        normalize_italian_integer(imposta_netta_frequenza)       AS imposta_netta_frequenza,
        normalize_italian_number(imposta_netta_ammontare)        AS _imposta_netta
    FROM raw_input
    WHERE normalize_string(codice) IS NOT NULL
      AND normalize_string(codice) NOT IN ('Codice', '0')
      AND normalize_string(regione) NOT IN ('TOTALE', 'Non indicata', 'Regione')
)
SELECT
    anno,
    regione,
    cod_regione,
    cod_tipologia,
    tipologia,
    contribuenti,
    reddito_complessivo_frequenza,
    ROUND(_reddito_complessivo * 1000, 0) AS reddito_complessivo_eur,
    reddito_imponibile_frequenza,
    ROUND(_reddito_imponibile * 1000, 0)  AS reddito_imponibile_eur,
    imposta_lorda_frequenza,
    ROUND(_imposta_lorda * 1000, 0)       AS imposta_lorda_eur,
    detrazioni_frequenza,
    ROUND(_detrazioni * 1000, 0)          AS detrazioni_eur,
    imposta_netta_frequenza,
    ROUND(_imposta_netta * 1000, 0)       AS imposta_netta_eur
FROM raw_parsed
