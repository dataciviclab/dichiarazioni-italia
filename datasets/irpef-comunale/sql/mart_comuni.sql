-- mart_comuni — IRPEF Comunale: arricchimento + benchmark reddituale
--
-- Stessa cardinalità del clean (1 riga = 1 comune × anno).
-- Benchmark: media nazionale/regionale, percentile, fascia per reddito medio.
-- Rank regionale per reddito e aliquota.
-- NOTA: join con popolazione rimosso (disponibile on-the-fly da GCS).

with
base as (
    select
        c.anno_di_imposta as anno,
        c.codice_istat_comune,
        c.denominazione_comune,
        c.sigla_provincia,
        c.regione,
        c.numero_contribuenti,
        c.reddito_imponibile_eur,
        c.imposta_netta_eur,
        c.addizionale_comunale_dovuta_eur,
        c.addizionale_regionale_dovuta_eur,
        c.reddito_da_lavoro_dipendente_e_assimilati_eur,
        c.reddito_da_pensione_eur,
        c.reddito_da_fabbricati_eur,
        c.reddito_da_partecipazione_eur,
        c.reddito_da_lavoro_autonomo_comprensivo_valori_nulli_eur,
        c.reddito_complessivo_eur,
        -- Reddito medio per contribuente
        c.reddito_imponibile_eur / nullif(c.numero_contribuenti, 0) as reddito_medio_per_contribuente,
        -- Aliquota effettiva (imposta netta / reddito imponibile)
        c.imposta_netta_eur * 100.0 / nullif(c.reddito_imponibile_eur, 0) as aliquota_effettiva_pct,
        -- Addizionale comunale effettiva
        c.addizionale_comunale_dovuta_eur * 100.0 / nullif(c.reddito_imponibile_eur, 0) as addizionale_effettiva_pct
    from clean_input c
    where c.codice_istat_comune is not null
      and c.regione is not null
      and c.numero_contribuenti > 0
      and c.reddito_imponibile_eur > 0
)
select
    *,
    -- ================================================================
    -- BENCHMARK REDDITO MEDIO PER CONTRIBUENTE
    -- ================================================================
    round(avg(reddito_medio_per_contribuente) over (partition by anno), 0) as media_nazionale_reddito,
    round(avg(reddito_medio_per_contribuente) over (partition by anno, regione), 0) as media_regionale_reddito,
    round(stddev(reddito_medio_per_contribuente) over (partition by anno), 0) as std_nazionale_reddito,
    case
        when reddito_medio_per_contribuente is null then null
        else round(percent_rank() over (partition by anno order by reddito_medio_per_contribuente), 4)
    end as percentile_nazionale_reddito,
    -- Distanza % dalla media nazionale
    case
        when avg(reddito_medio_per_contribuente) over (partition by anno) <> 0
        then round((reddito_medio_per_contribuente - avg(reddito_medio_per_contribuente) over (partition by anno))
             / abs(avg(reddito_medio_per_contribuente) over (partition by anno)) * 100, 2)
    end as distanza_media_nazionale_pct,
    -- ================================================================
    -- BENCHMARK ALIQUOTA EFFETTIVA
    -- ================================================================
    round(avg(aliquota_effettiva_pct) over (partition by anno), 2) as media_nazionale_aliquota,
    round(avg(aliquota_effettiva_pct) over (partition by anno, regione), 2) as media_regionale_aliquota,
    case
        when aliquota_effettiva_pct is null then null
        else round(percent_rank() over (partition by anno order by aliquota_effettiva_pct), 4)
    end as percentile_aliquota,
    -- ================================================================
    -- RANK (regionale)
    -- ================================================================
    row_number() over (partition by anno, regione order by reddito_medio_per_contribuente desc) as rank_regionale_reddito,
    row_number() over (partition by anno, regione order by aliquota_effettiva_pct desc) as rank_regionale_aliquota,
    -- ================================================================
    -- FASCE QUALITATIVE
    -- ================================================================
    case
        when percent_rank() over (partition by anno order by reddito_medio_per_contribuente) >= 0.8 then 'ELEVATO'
        when percent_rank() over (partition by anno order by reddito_medio_per_contribuente) >= 0.6 then 'SOPRA_MEDIA'
        when percent_rank() over (partition by anno order by reddito_medio_per_contribuente) >= 0.4 then 'MEDIA'
        when percent_rank() over (partition by anno order by reddito_medio_per_contribuente) >= 0.2 then 'SOTTO_MEDIA'
        else 'BASSO'
    end as fascia_reddito
from base
order by anno, regione, denominazione_comune;
