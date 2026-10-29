-- mart.sql: mef-irpef-regionale
-- Aggregato per regione × anno: contribuenti nelle due code della distribuzione.
-- Fonte: REG_tipo_reddito.
--
-- La fonte pubblica 34 classi di reddito, identiche in tutti i 9 anni coperti
-- (verificato file per file). La mappatura è ESPLICITA, una riga per classe:
--   - fascia inferiore: reddito <= 0            (3 classi)
--   - fascia superiore: reddito >= 10.000 €     (20 classi)
--   - fascia media: le 11 classi restanti, che non entrano in nessuna delle due
--
-- ⚠️ La versione precedente elencava etichette che NON esistono nella fonte
-- ("da 10.000 a 15.000", "da 20.000 a 25.000", "maggiore di 30.000", …) e
-- chiudeva con `ELSE 99` sotto la soglia `>= 17`: le 21 classi non mappate
-- ricadevano quindi nella fascia alta, che misurava di fatto "reddito > 6.000 €"
-- invece di ">= 10.000 €" (verificato: la colonna coincideva con
-- totale − classi mappate <= 6.000 su Campania, Abruzzo e Lombardia).
--
-- Con il LEFT JOIN e senza ELSE, una classe non mappata NON entra in nessuna
-- fascia e viene contata in `classi_non_mappate`: la regola `ranges` nel
-- dataset.yml impone che sia 0, quindi un cambio di etichette a monte fa
-- fallire la validazione invece di produrre numeri sbagliati.

WITH classi AS (
    SELECT * FROM (VALUES
        ('minore di -1.000',      'inferiore'),
        ('da -1.000 a 0',         'inferiore'),
        ('zero',                  'inferiore'),
        ('da 0 a 1.000',          'media'),
        ('da 1.000 a 1.500',      'media'),
        ('da 1.500 a 2.000',      'media'),
        ('da 2.000 a 2.500',      'media'),
        ('da 2.500 a 3.000',      'media'),
        ('da 3.000 a 3.500',      'media'),
        ('da 3.500 a 4.000',      'media'),
        ('da 4.000 a 5.000',      'media'),
        ('da 5.000 a 6.000',      'media'),
        ('da 6.000 a 7.500',      'media'),
        ('da 7.500 a 10.000',     'media'),
        ('da 10.000 a 12.000',    'superiore'),
        ('da 12.000 a 15.000',    'superiore'),
        ('da 15.000 a 20.000',    'superiore'),
        ('da 20.000 a 26.000',    'superiore'),
        ('da 26.000 a 29.000',    'superiore'),
        ('da 29.000 a 35.000',    'superiore'),
        ('da 35.000 a 40.000',    'superiore'),
        ('da 40.000 a 50.000',    'superiore'),
        ('da 50.000 a 55.000',    'superiore'),
        ('da 55.000 a 60.000',    'superiore'),
        ('da 60.000 a 70.000',    'superiore'),
        ('da 70.000 a 75.000',    'superiore'),
        ('da 75.000 a 80.000',    'superiore'),
        ('da 80.000 a 90.000',    'superiore'),
        ('da 90.000 a 100.000',   'superiore'),
        ('da 100.000 a 120.000',  'superiore'),
        ('da 120.000 a 150.000',  'superiore'),
        ('da 150.000 a 200.000',  'superiore'),
        ('da 200.000 a 300.000',  'superiore'),
        ('oltre 300.000',         'superiore')
    ) AS t(classe_reddito, banda)
),
base AS (
    SELECT
        c.anno,
        c.regione,
        c.classe_reddito,
        c.numero_contribuenti,
        m.banda
    FROM clean_input c
    LEFT JOIN classi m USING (classe_reddito)
)
SELECT
    anno,
    regione,
    SUM(numero_contribuenti)                                              AS totale_contribuenti,
    SUM(CASE WHEN banda = 'inferiore' THEN numero_contribuenti ELSE 0 END) AS contribuenti_fascia_inferiore,
    SUM(CASE WHEN banda = 'superiore' THEN numero_contribuenti ELSE 0 END) AS contribuenti_fascia_superiore,
    ROUND(
        100.0 * SUM(CASE WHEN banda = 'inferiore' THEN numero_contribuenti ELSE 0 END)
        / NULLIF(SUM(numero_contribuenti), 0),
        2
    )                                                                     AS pct_fascia_inferiore,
    ROUND(
        100.0 * SUM(CASE WHEN banda = 'superiore' THEN numero_contribuenti ELSE 0 END)
        / NULLIF(SUM(numero_contribuenti), 0),
        2
    )                                                                     AS pct_fascia_superiore,
    COUNT(DISTINCT classe_reddito)                                        AS num_classi_presente,
    -- guardia: deve restare 0 (regola `ranges` in dataset.yml)
    SUM(CASE WHEN banda IS NULL THEN 1 ELSE 0 END)                        AS classi_non_mappate
FROM base
GROUP BY anno, regione
ORDER BY anno, regione
