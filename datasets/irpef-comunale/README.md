# irpef-comunale

**Domanda principale:** Come varia la capacità fiscale tra comuni e regioni italiane?

Redditi IRPEF dichiarati da persone fisiche, per comune italiano. Include
numero contribuenti, imponibile, imposta netta, addizionali e distribuzione
per fasce di reddito.

---

## Fonte

MEF — Dipartimento delle Finanze. ZIP annuali pubblicati su:
```
https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/
Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_{year}.zip
```

Anni disponibili dalla fonte: **2000–2024** (URL pattern confermato).
Attualmente intakati: **2015–2024** (10 anni).

## Schema clean (52 colonne)

| Col | Nome | Note |
|:---:|------|------|
| 0 | `anno_di_imposta` | |
| 1 | `codice_catastale` | Chiave di join con `comuni_master` |
| 2 | `codice_istat_comune` | Chiave di join con `comuni_master` |
| 3–6 | Anagrafica comune | denominazione, provincia, regione |
| 7 | `numero_contribuenti` | Totale contribuenti del comune |
| 8–9 | Reddito da fabbricati | frequenza + ammontare |
| 10–11 | Reddito lav. dipendente | frequenza + ammontare |
| 12–13 | Reddito da pensione | frequenza + ammontare |
| 14–21 | Altri redditi | autonomo, impresa, partecipazione |
| 22–23 | `reddito_imponibile` | **freq + eur** — copertura 2019–2024 |
| 24–25 | `imposta_netta` | **freq + eur** — copertura 2019–2024 |
| 26–27 | Bonus / Trattamento | semantica varia per anno (vedi caveat) |
| 28–31 | Addizionali | regionale + comunale |
| 32–33 | Addizionale comunale | freq + eur |
| 34–35 | `reddito_complessivo` | **freq + eur** — solo 2023+ |
| 36–51 | Fasce reddito complessivo | 8 fasce × (freq + eur) |

## Copertura

| Dimensione | Valore |
|------------|--------|
| **Anni** | 2015–2024 (10 anni) |
| **Territorio** | ~7.900 comuni/anno |
| **Variabili** | 52 colonne (26 metriche × freq/eur) |
| **Contribuenti (Italia, 2024)** | ~42,8M |

## Riga `Mancante/errata` (codice ISTAT `0`)

La fonte include, in ogni annualità, una riga aggregata dei comuni non
riconosciuti: `codice_istat_comune = '0'`, `denominazione_comune = '0'`,
`sigla_provincia = '0'`. L'etichetta di `regione` cambia nel tempo:
`Non indicato` nel 2015-2017, `Mancante/errata` dal 2018.

Nel 2024 vale **5.305 contribuenti**, 59,36 mln € di reddito imponibile e
17,03 mln € di imposta — 3 ordini di grandezza sotto un comune medio.

- **Nel clean resta**: è un dato della fonte, e il clean è raw-faithful.
- **Nei mart è esclusa** (`codice_istat_comune <> '0'`): senza il filtro entra
  come pseudo-regione nei ranking, con `reddito_medio` di 11.190 €, il valore
  più basso d'Italia (issue #40).

## Trentino Alto Adige

La fonte cambia rappresentazione nel 2019: fino al 2018 una sola riga
`Trentino Alto Adige`, dal 2019 le due province autonome
`Trentino Alto Adige(P.A.Bolzano)` e `Trentino Alto Adige(P.A.Trento)`.
`codice_istat_regione` resta `04` in entrambi i casi.

Il `clean.sql` normalizza sempre alle due P.A. usando `sigla_provincia`
(BZ/TN), così la serie regionale ha **21 unità in ogni annualità** e le
etichette sono le stesse dal 2015 al 2024. Senza la normalizzazione il 2015-2018
produce 20 righe e il 2019-2024 ne produce 21.

## Join con altri dataset

Tramite `codice_istat_comune` (6 cifre) si collega a `comuni_master` e quindi
a tutti i dataset del Join Map Registry (`registry/join_map.yaml`).

Usato in `candidates/unified-comuni/` per la colonna `reddito_imponibile_eur`
(copertura 2019–2024) e `reddito_procapite` (calcolato su popolazione ISTAT).

## Mart disponibili

| Mart | Descrizione | Cardinalità |
|------|-------------|-------------|
| `mart_comuni` | Arricchimento + benchmark reddituale: reddito medio/contribuente, reddito pro-capite (join popolazione), aliquota effettiva, media nazionale/regionale, percentile, fascia, rank regionale | ~7.900 righe/anno |
| `mart_sintesi` | Statistiche regionali: contribuenti, redditi, imposte, composizione fonti (lavoro, pensione, autonomo), disuguaglianza intra-regionale (CV, delta max-min) | **21 righe/anno** |
| `mart_trend` | CAGR reddito per comune e regione (multi-anno via glob) | ~7.900 comuni + 21 regioni |
| `mart_fasce` | Distribuzione contribuenti per fascia di reddito (0-10k, …, oltre 120k) per provincia, con rapporto alta/bassa | ~107 righe/anno |

## Limiti

- **`reddito_complessivo_eur`** popolato solo dal 2023. Per 2019–2022 usare `reddito_imponibile_eur`.
- **Bonus vs Trattamento** (col 26–27): il MEF ha cambiato semantica nel 2021. Non confrontabili direttamente.
- **Somalettura regionale**: la somma dei comuni può non coincidere con i totali regionali ufficiali.
- **Riga `Mancante/errata`** (ISTAT `0`): presente nel clean, esclusa dai mart — vedi sezione dedicata.

## Note tecniche

Vedi `notes.md` per dettagli su struttura raw, schema, e caveat operativi.

Il layer pubblico (notebook, analisi) vive in `dataciviclab/analisi/irpef-comunale/`.
