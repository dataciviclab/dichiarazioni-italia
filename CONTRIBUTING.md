# Contribuire a dichiarazioni-italia

## Come partecipare

1. **Issue**: segnala bug, proponi un nuovo dataset, o suggerisci miglioramenti
2. **Discussion**: fai domande o proponi idee
3. **Pull Request**: contribuisci con codice o dati

## Setup locale

```bash
# Installa toolkit
pip install dataciviclab-toolkit

# Verifica i dataset
make check

# Esegui tutte le pipeline
make run-all
```

## Struttura del repo

```
datasets/           dataset.yml per ogni dataset
  <dataset>/
    dataset.yml     contratto pipeline
    sql/
      clean.sql     pulizia dati
      mart*.sql     aggregazioni analitiche
out/                output pipeline (non committare)
support_datasets/   dataset di supporto
```

## Aggiungere un nuovo dataset

1. Crea `datasets/<nome>/dataset.yml` seguendo lo standard
2. Scrivi `sql/clean.sql` e `sql/mart.sql`
3. Esegui `toolkit run -c datasets/<nome>/dataset.yml`
4. Verifica che tutti gli anni passino
5. Apri una PR

## Regole

- Segui lo standard pipeline (vedi `analysis/lab-ops/standards/pipeline.md`)
- `clean.sql` legge solo da `raw_input`
- `mart*.sql` legge solo da `clean_input`
- Non committare output (`out/`, `*.parquet`)
- Test: ogni dataset deve passare `toolkit run` su tutti gli anni

## Licenza

Contribuendo, accetti che i tuoi contributi siano rilasciati sotto licenza MIT.
