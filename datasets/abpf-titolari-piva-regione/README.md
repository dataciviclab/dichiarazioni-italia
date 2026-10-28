# abpf-titolari-piva-regione

**Domanda guida:** Quanto dichiarano e quanto pagano le persone fisiche titolari di partita IVA, regione per regione — e quanto pesa il regime forfetario?

**Fonte:** MEF — Dipartimento delle Finanze
**URL:** https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php
**Dataset:** ABPFTIT0201 (Titolari di partita IVA — Tematica personalizzata — Regione)
**Formato:** CSV con 8 righe di metadati + riga vuota → header alla riga 10; letto **per nome** (`all_varchar: true`, `read.skip: 9`)
**Copertura:** 2015–2024 (10 anni, anno d'imposta)
**Nota:** L'URL MEF usa l'anno di presentazione (es. `2025ABPFTIT0201` = dichiarazioni 2025). Il clean converte in anno d'imposta sottraendo 1.
**Licenza:** CC BY (MEF)
**Valori:** in **euro** (convertiti da migliaia ×1000)

## Perché è letto per NOME (e non per posizione)

È l'unico dataset del repo che non usa la lettura posizionale. L'ordine delle colonne di questa vista **cambia tra gli anni**: tra il file 2012 e il 2025 si spostano **100 posizioni**. La lettura per posizione non è quindi praticabile.

Si legge per **nome** (`header: true` + `all_varchar: true`) e si referenziano solo le colonne presenti in **tutti** gli anni coperti. La finestra scelta è il **file 2016–2025** (a.i. 2015–2024): **144 colonne comuni**, le uniche che includono il **regime forfetario** e il **regime di vantaggio** (esistono dalla dichiarazione 2016, a.i. 2015). Partire dal file 2015 avrebbe dato 11 anni ma senza le due voci sui regimi agevolati — che sono la parte civicamente più rilevante.

`all_varchar` serve anche a proteggere i numeri: sono in formato italiano e lo sniffing di DuckDB tipizzerebbe `DOUBLE` le colonne i cui valori hanno un solo punto (`"121.330"`), corrompendole nelle macro `normalize_italian_*` (×10/÷10).

## Schema (98 colonne)

| Colonna | Tipo | Descrizione |
|---|---|---|
| `anno` | INTEGER | Anno d'imposta |
| `regione` | VARCHAR | Denominazione regione (21: Trentino diviso in P.A. Trento e Bolzano) |
| `cod_regione` | VARCHAR | Codice ISTAT regione (condiviso da Trento e Bolzano) |
| `numero_titolari` | INTEGER | Titolari di partita IVA |
| `acconti_versati_frequenza` | INTEGER | Acconti versati — numero dichiarazioni |
| `acconti_versati_eur` | DOUBLE | Acconti versati — importo (€) |
| `addizionale_comunale_dovuta_frequenza` | INTEGER | Addizionale comunale dovuta — numero dichiarazioni |
| `addizionale_comunale_dovuta_eur` | DOUBLE | Addizionale comunale dovuta — importo (€) |
| `addizionale_regionale_dovuta_frequenza` | INTEGER | Addizionale regionale dovuta — numero dichiarazioni |
| `addizionale_regionale_dovuta_eur` | DOUBLE | Addizionale regionale dovuta — importo (€) |
| `altri_redditi_da_lavoro_autonomo_e_redditi_da_recupero_start_up_frequenza` | INTEGER | Altri redditi da lavoro autonomo e redditi da recupero start up — numero dichiarazioni |
| `altri_redditi_da_lavoro_autonomo_e_redditi_da_recupero_start_up_eur` | DOUBLE | Altri redditi da lavoro autonomo e redditi da recupero start up — importo (€) |
| `eccedenza_d_imposta_risultante_dalla_precedente_dichiarazione_frequenza` | INTEGER | Eccedenza d'imposta risultante dalla precedente dichiarazione — numero dichiarazioni |
| `eccedenza_d_imposta_risultante_dalla_precedente_dichiarazione_eur` | DOUBLE | Eccedenza d'imposta risultante dalla precedente dichiarazione — importo (€) |
| `imposta_lorda_frequenza` | INTEGER | Imposta lorda — numero dichiarazioni |
| `imposta_lorda_eur` | DOUBLE | Imposta lorda — importo (€) |
| `imposta_netta_frequenza` | INTEGER | Imposta netta — numero dichiarazioni |
| `imposta_netta_eur` | DOUBLE | Imposta netta — importo (€) |
| `irpef_a_credito_frequenza` | INTEGER | Irpef a credito — numero dichiarazioni |
| `irpef_a_credito_eur` | DOUBLE | Irpef a credito — importo (€) |
| `irpef_a_debito_frequenza` | INTEGER | Irpef a debito — numero dichiarazioni |
| `irpef_a_debito_eur` | DOUBLE | Irpef a debito — importo (€) |
| `iva_a_debito_frequenza` | INTEGER | Iva a debito — numero dichiarazioni |
| `iva_a_debito_eur` | DOUBLE | Iva a debito — importo (€) |
| `iva_detraibile_frequenza` | INTEGER | Iva detraibile — numero dichiarazioni |
| `iva_detraibile_eur` | DOUBLE | Iva detraibile — importo (€) |
| `perdita_da_lavoro_autonomo_frequenza` | INTEGER | Perdita da lavoro autonomo — numero dichiarazioni |
| `perdita_da_lavoro_autonomo_eur` | DOUBLE | Perdita da lavoro autonomo — importo (€) |
| `perdita_da_lavoro_autonomo_con_continuita_frequenza` | INTEGER | Perdita da lavoro autonomo con continuita' — numero dichiarazioni |
| `perdita_da_lavoro_autonomo_con_continuita_eur` | DOUBLE | Perdita da lavoro autonomo con continuita' — importo (€) |
| `perdita_da_partecipazione_frequenza` | INTEGER | Perdita da partecipazione — numero dichiarazioni |
| `perdita_da_partecipazione_eur` | DOUBLE | Perdita da partecipazione — importo (€) |
| `perdita_di_impresa_in_contabilita_ordinaria_frequenza` | INTEGER | Perdita di impresa in contabilita' ordinaria — numero dichiarazioni |
| `perdita_di_impresa_in_contabilita_ordinaria_eur` | DOUBLE | Perdita di impresa in contabilita' ordinaria — importo (€) |
| `perdita_di_impresa_in_contabilita_ordinaria_con_continuita_frequenza` | INTEGER | Perdita di impresa in contabilita' ordinaria con continuita' — numero dichiarazioni |
| `perdita_di_impresa_in_contabilita_ordinaria_con_continuita_eur` | DOUBLE | Perdita di impresa in contabilita' ordinaria con continuita' — importo (€) |
| `perdita_di_impresa_in_contabilita_semplificata_frequenza` | INTEGER | Perdita di impresa in contabilita' semplificata — numero dichiarazioni |
| `perdita_di_impresa_in_contabilita_semplificata_eur` | DOUBLE | Perdita di impresa in contabilita' semplificata — importo (€) |
| `perdita_di_impresa_in_contabilita_semplificata_con_continuita_frequenza` | INTEGER | Perdita di impresa in contabilita' semplificata con continuita' — numero dichiarazioni |
| `perdita_di_impresa_in_contabilita_semplificata_con_continuita_eur` | DOUBLE | Perdita di impresa in contabilita' semplificata con continuita' — importo (€) |
| `plusvalenze_di_natura_finanziaria_frequenza` | INTEGER | Plusvalenze di natura finanziaria — numero dichiarazioni |
| `plusvalenze_di_natura_finanziaria_eur` | DOUBLE | Plusvalenze di natura finanziaria — importo (€) |
| `redditi_diversi_frequenza` | INTEGER | Redditi diversi — numero dichiarazioni |
| `redditi_diversi_eur` | DOUBLE | Redditi diversi — importo (€) |
| `reddito_agricolo_dichiarato_frequenza` | INTEGER | Reddito agricolo dichiarato — numero dichiarazioni |
| `reddito_agricolo_dichiarato_eur` | DOUBLE | Reddito agricolo dichiarato — importo (€) |
| `reddito_complessivo_frequenza` | INTEGER | Reddito complessivo — numero dichiarazioni |
| `reddito_complessivo_eur` | DOUBLE | Reddito complessivo — importo (€) |
| `reddito_complessivo_al_netto_della_cedolare_secca_frequenza` | INTEGER | Reddito complessivo al netto della cedolare secca — numero dichiarazioni |
| `reddito_complessivo_al_netto_della_cedolare_secca_eur` | DOUBLE | Reddito complessivo al netto della cedolare secca — importo (€) |
| `reddito_d_impresa_dichiarato_frequenza` | INTEGER | Reddito d'impresa dichiarato — numero dichiarazioni |
| `reddito_d_impresa_dichiarato_eur` | DOUBLE | Reddito d'impresa dichiarato — importo (€) |
| `reddito_da_allevamento_e_produzione_di_vegetali_frequenza` | INTEGER | Reddito da allevamento e produzione di vegetali — numero dichiarazioni |
| `reddito_da_allevamento_e_produzione_di_vegetali_eur` | DOUBLE | Reddito da allevamento e produzione di vegetali — importo (€) |
| `reddito_da_fabbricati_frequenza` | INTEGER | Reddito da fabbricati — numero dichiarazioni |
| `reddito_da_fabbricati_eur` | DOUBLE | Reddito da fabbricati — importo (€) |
| `reddito_da_lavoro_autonomo_con_continuita_frequenza` | INTEGER | Reddito da lavoro autonomo con continuita'* — numero dichiarazioni |
| `reddito_da_lavoro_autonomo_con_continuita_eur` | DOUBLE | Reddito da lavoro autonomo con continuita'* — importo (€) |
| `reddito_da_lavoro_autonomo_frequenza` | INTEGER | Reddito da lavoro autonomo* — numero dichiarazioni |
| `reddito_da_lavoro_autonomo_eur` | DOUBLE | Reddito da lavoro autonomo* — importo (€) |
| `reddito_da_partecipazione_frequenza` | INTEGER | Reddito da partecipazione* — numero dichiarazioni |
| `reddito_da_partecipazione_eur` | DOUBLE | Reddito da partecipazione* — importo (€) |
| `reddito_dei_terreni_frequenza` | INTEGER | Reddito dei terreni — numero dichiarazioni |
| `reddito_dei_terreni_eur` | DOUBLE | Reddito dei terreni — importo (€) |
| `reddito_di_capitale_sez_ia_e_ib_frequenza` | INTEGER | Reddito di capitale (sez. IA e IB) — numero dichiarazioni |
| `reddito_di_capitale_sez_ia_e_ib_eur` | DOUBLE | Reddito di capitale (sez. IA e IB) — importo (€) |
| `reddito_di_impresa_in_contabilita_ordinaria_con_continuita_frequenza` | INTEGER | Reddito di impresa in contabilita' ordinaria con continuita'* — numero dichiarazioni |
| `reddito_di_impresa_in_contabilita_ordinaria_con_continuita_eur` | DOUBLE | Reddito di impresa in contabilita' ordinaria con continuita'* — importo (€) |
| `reddito_di_impresa_in_contabilita_ordinaria_frequenza` | INTEGER | Reddito di impresa in contabilita' ordinaria* — numero dichiarazioni |
| `reddito_di_impresa_in_contabilita_ordinaria_eur` | DOUBLE | Reddito di impresa in contabilita' ordinaria* — importo (€) |
| `reddito_di_impresa_in_contabilita_semplificata_con_continuita_frequenza` | INTEGER | Reddito di impresa in contabilita' semplificata con continuita'* — numero dichiarazioni |
| `reddito_di_impresa_in_contabilita_semplificata_con_continuita_eur` | DOUBLE | Reddito di impresa in contabilita' semplificata con continuita'* — importo (€) |
| `reddito_di_impresa_in_contabilita_semplificata_frequenza` | INTEGER | Reddito di impresa in contabilita' semplificata* — numero dichiarazioni |
| `reddito_di_impresa_in_contabilita_semplificata_eur` | DOUBLE | Reddito di impresa in contabilita' semplificata* — importo (€) |
| `reddito_di_lavoro_dipendente_e_assimilati_frequenza` | INTEGER | Reddito di lavoro dipendente e assimilati — numero dichiarazioni |
| `reddito_di_lavoro_dipendente_e_assimilati_eur` | DOUBLE | Reddito di lavoro dipendente e assimilati — importo (€) |
| `reddito_di_spettanza_dell_imprenditore_in_contabilita_ordinaria_con_continuita_frequenza` | INTEGER | Reddito di spettanza dell'imprenditore in contabilita' ordinaria con continuita'* — numero dichiarazioni |
| `reddito_di_spettanza_dell_imprenditore_in_contabilita_ordinaria_con_continuita_eur` | DOUBLE | Reddito di spettanza dell'imprenditore in contabilita' ordinaria con continuita'* — importo (€) |
| `reddito_di_spettanza_dell_imprenditore_in_contabilita_ordinaria_frequenza` | INTEGER | Reddito di spettanza dell'imprenditore in contabilita' ordinaria* — numero dichiarazioni |
| `reddito_di_spettanza_dell_imprenditore_in_contabilita_ordinaria_eur` | DOUBLE | Reddito di spettanza dell'imprenditore in contabilita' ordinaria* — importo (€) |
| `reddito_di_spettanza_dell_imprenditore_in_contabilita_semplificata_con_continuita_frequenza` | INTEGER | Reddito di spettanza dell'imprenditore in contabilita' semplificata con continuita'* — numero dichiarazioni |
| `reddito_di_spettanza_dell_imprenditore_in_contabilita_semplificata_con_continuita_eur` | DOUBLE | Reddito di spettanza dell'imprenditore in contabilita' semplificata con continuita'* — importo (€) |
| `reddito_di_spettanza_dell_imprenditore_in_contabilita_semplificata_frequenza` | INTEGER | Reddito di spettanza dell'imprenditore in contabilita' semplificata* — numero dichiarazioni |
| `reddito_di_spettanza_dell_imprenditore_in_contabilita_semplificata_eur` | DOUBLE | Reddito di spettanza dell'imprenditore in contabilita' semplificata* — importo (€) |
| `reddito_imponibile_frequenza` | INTEGER | Reddito imponibile — numero dichiarazioni |
| `reddito_imponibile_eur` | DOUBLE | Reddito imponibile — importo (€) |
| `reddito_imponibile_addizionale_frequenza` | INTEGER | Reddito imponibile addizionale — numero dichiarazioni |
| `reddito_imponibile_addizionale_eur` | DOUBLE | Reddito imponibile addizionale — importo (€) |
| `reddito_netto_regime_di_vantaggio_frequenza` | INTEGER | Reddito netto (regime di vantaggio) — numero dichiarazioni |
| `reddito_netto_regime_di_vantaggio_eur` | DOUBLE | Reddito netto (regime di vantaggio) — importo (€) |
| `reddito_netto_regime_forfetario_frequenza` | INTEGER | Reddito netto (regime forfetario) — numero dichiarazioni |
| `reddito_netto_regime_forfetario_eur` | DOUBLE | Reddito netto (regime forfetario) — importo (€) |
| `reddito_professionale_dichiarato_frequenza` | INTEGER | Reddito professionale dichiarato — numero dichiarazioni |
| `reddito_professionale_dichiarato_eur` | DOUBLE | Reddito professionale dichiarato — importo (€) |
| `tassazione_separata_con_opzione_tassazione_ordinaria_frequenza` | INTEGER | Tassazione separata con opzione tassazione ordinaria — numero dichiarazioni |
| `tassazione_separata_con_opzione_tassazione_ordinaria_eur` | DOUBLE | Tassazione separata con opzione tassazione ordinaria — importo (€) |
| `volume_d_affari_frequenza` | INTEGER | Volume d'affari — numero dichiarazioni |
| `volume_d_affari_eur` | DOUBLE | Volume d'affari — importo (€) |

## Mart

- `mart_regione_anno` — regione × anno: titolari, reddito complessivo, imposta netta, volume d'affari, reddito medio per titolare, **aliquota media effettiva**, quota sul reddito nazionale, `rank_reddito`
- `mart_anno` — nazionale per anno (multi-year): titolari, reddito complessivo e imponibile, imposta netta, volume d'affari, **reddito da regime forfetario e da regime di vantaggio**, reddito medio, aliquota media, variazione % del reddito

## Cosa dicono i dati

- **Il regime forfetario esplode**: 0,82 mld (a.i. 2015) → **31,8 mld** (a.i. 2024), dal **0,9% al 29,3%** del reddito complessivo dei titolari di partita IVA. Nello stesso periodo il **regime di vantaggio** crolla: 4,57 → **0,15 mld**.
- **3,8 milioni di titolari** (a.i. 2024): circa il **9% dei contribuenti IRPEF** (42,0 milioni). Reddito complessivo 108,7 mld, imposta netta 25,5 mld.
- **Aliquota media effettiva** (imposta netta / reddito imponibile): dal 25,4% (2015) al **28,1%** (2024).
- **Concentrazione**: la Lombardia fa il **20,8%** del reddito complessivo nazionale dei titolari (a.i. 2023), con il 16,8% dei titolari.

## Note metodologiche

- **⚠️ Le colonne NON sono additive.** Sono grandezze dichiarate su righe diverse del modello. In particolare `reddito_complessivo` è il reddito **totale della persona** (include anche lavoro dipendente e pensioni), non la somma delle voci per tipo di reddito, che a loro volta si sovrappongono in parte. E `reddito_netto_regime_forfetario` / `reddito_netto_regime_di_vantaggio` sono redditi di **regimi alternativi**, non componenti da sommare al complessivo.
- **Perimetro**: persone fisiche **titolari di partita IVA** (modello ABPF). Non include le persone fisiche senza partita IVA (in `irpef_comunale` / `mef_irpef_regionale`) né le società (`ires_redditi_regione`, `acsp_*`).
- **Colonne che cambiano tra gli anni**: il dataset espone solo le 144 colonne comuni al periodo coperto. Restano fuori, tra le altre, `Reddito minimo dichiarato` (file 2012–2015) e `Reddito da partecipazione` (solo file 2012). Le serie di quelle voci non sono ricostruibili senza spezzare il dataset.
- **Righe escluse**: header (`Codice` = 'Codice'), `TOTALE` ('0'), `Non indicata` ('00'), la riga `(*) Comprensivo dei valori nulli` e la nota finale (codice NULL). Le 21 regioni includono Trento e Bolzano separati, entrambi con `cod_regione = '04'`: la chiave è `[anno, regione]`.
- **`***` = dato oscurato dalla fonte** (riservatezza): la cella diventa `NULL`, non zero.
- **Valori in migliaia di euro**: gli `*_eur` sono convertiti in euro (×1000). Le colonne "Media" della fonte sono scartate.
