-- clean.sql — irpef_imposta_tipologia
-- IRPEF: imposta netta per tipologia di soggetto in base al reddito prevalente.
-- Vista MEF analisi_stat AETPTOT0401 (Persone fisiche totali — Confronto tra
-- imposte nette). Grano nazionale × tipologia × anno d'imposta.
--
-- Lettura POSIZIONALE, tutte le colonne VARCHAR. `encoding: cp1252` è OBBLIGATORIO:
-- i file fino al 2019 (e il 2021) contengono un byte 0xC3 isolato al posto della
-- "a" accentata di "società". Con `encoding: utf-8` il reader del toolkit (Python
-- csv + pandas, perché qui si usa normalize_rows_to_columns) fallisce con
-- UnicodeDecodeError; con una lettura DuckDB diretta la riga verrebbe invece
-- scartata in silenzio (verificato: file 2019 → 18 righe vs 19).
--
-- `***` (dato oscurato) compare solo nel file 2016 (a.i. 2015), su 2 righe
-- (codice 15 e TOTALE): la cella diventa NULL e per quell'anno la somma delle
-- tipologie non è confrontabile con il TOTALE.
--
-- `anno` = anno d'imposta (l'URL MEF usa l'anno di presentazione: {year} - 1).
-- Ammontari in migliaia di euro → ×1000.
--
-- `tipologia` è **canonica**, derivata dal codice della fonte: le etichette di
-- origine variano tra anni (accento rotto, "societa'" vs "società", "da 770" vs
-- "da Mod.CU"). I codici 01-13 sono stabili; dal file 2019 la fonte inserisce
-- "Regime fiscale agevolato" come 14 e fa **slittare** 14→15 e 15→16, quindi il
-- codice non è una chiave stabile tra anni e non è esposto.
--
-- Righe escluse: la riga di header (letta come dato, codice='Codice'), `TOTALE`
-- (codice='0') e la nota finale (una sola cella → codice NULL).

WITH raw_parsed AS (
    SELECT
        CAST({year} - 1 AS INTEGER)                      AS anno,
        LPAD(normalize_string(column01), 2, '0')          AS codice,
        normalize_italian_integer(column02)               AS numero_contribuenti,
        normalize_italian_integer(column03)               AS imposta_netta_frequenza,
        normalize_italian_number(column04)                AS _imposta_netta_eur
    FROM raw_input
    WHERE normalize_string(column01) IS NOT NULL
      AND normalize_string(column01) NOT IN ('Codice', '0')
),
typed AS (
    SELECT
        anno,
        CASE
            WHEN codice = '01' THEN 'Lavoratore dipendente'
            WHEN codice = '02' THEN 'Pensionato'
            WHEN codice = '03' THEN 'Proprietario di fabbricati'
            WHEN codice = '04' THEN 'Redditi dominicali e/o agrari'
            WHEN codice = '05' THEN 'Imprenditore'
            WHEN codice = '06' THEN 'Lavoratore autonomo abituale con partita IVA'
            WHEN codice = '07' THEN 'Allevatore/Agricoltore'
            WHEN codice = '08' THEN 'Redditi da capitale'
            WHEN codice = '09' THEN 'Redditi diversi'
            WHEN codice = '10' THEN 'Lavoratore autonomo occasionale'
            WHEN codice = '11' THEN 'Partecipante in società di persone'
            WHEN codice = '12' THEN 'Plusvalenze di natura finanziaria'
            WHEN codice = '13' THEN 'Redditi a tassazione separata'
            -- dal file 2019 (a.i. 2018) la fonte inserisce il regime agevolato
            -- come 14 e fa slittare 14->15 e 15->16
            WHEN codice = '14' AND anno < 2018 THEN 'Autonomo/provvigioni/diversi (quadro 770)'
            WHEN codice = '14' THEN 'Regime fiscale agevolato'
            WHEN codice = '15' AND anno < 2018 THEN 'Redditi a tassazione sostitutiva'
            WHEN codice = '15' THEN 'Autonomo/provvigioni/diversi (Mod. CU)'
            WHEN codice = '16' THEN 'Redditi a tassazione sostitutiva'
        END AS tipologia,
        numero_contribuenti,
        imposta_netta_frequenza,
        _imposta_netta_eur
    FROM raw_parsed
)
SELECT
    anno,
    tipologia,
    numero_contribuenti,
    imposta_netta_frequenza,
    ROUND(_imposta_netta_eur * 1000, 0) AS imposta_netta_eur
FROM typed
WHERE tipologia IS NOT NULL
