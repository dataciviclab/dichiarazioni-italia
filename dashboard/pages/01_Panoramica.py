"""Panoramica — le quattro imposte e i perimetri IRPEF, con l'indice del cruscotto.

La pagina non somma niente: i perimetri (IVA, IRPEF, IRAP, IRES) non sono
additivi e i dataset IRPEF per forma giuridica sono sottoinsiemi.
"""

import streamlit as st
from sources import (
    YEARS_IRES,
    dataset_period,
    fmt_eur,
    fmt_num,
    load_mart,
    load_mart_flat,
)

st.title("📊 Dichiarazioni Italia")
st.markdown(
    "Le dichiarazioni fiscali italiane (MEF — Dipartimento delle Finanze): "
    "**IVA, IRPEF, IRAP, IRES**. 18 dataset, una pagina per imposta."
)

# ══════════════════════════════════════════════════════════════════════
# LE QUATTRO IMPOSTE
# ══════════════════════════════════════════════════════════════════════
st.subheader("Le quattro imposte")

iva = load_mart_flat("iva_regionale", "mart_sintesi_nazionale").sort_values("anno")
irpef = load_mart_flat("irpef_imposta_tipologia", "mart_anno").sort_values("anno")
irap = load_mart_flat("irap_imposta_regione", "mart_imposta_anno").sort_values("anno")
ires = load_mart("ires_redditi_regione", "mart_regioni_anno", max(YEARS_IRES))

k1, k2, k3, k4 = st.columns(4)
with k1:
    if not iva.empty:
        ultimo = iva.iloc[-1]
        st.metric(
            "IVA — imposta dovuta",
            fmt_eur(ultimo["imposta_dovuta_eur"], compact=True),
            delta=f"a.i. {int(ultimo['anno'])}",
            delta_color="off",
        )
        st.caption(f"{fmt_eur(ultimo['volume_affari_eur'], compact=True)} di volume d'affari")
with k2:
    if not irpef.empty:
        ultimo = irpef.iloc[-1]
        st.metric(
            "IRPEF — imposta netta",
            fmt_eur(ultimo["imposta_netta_eur"], compact=True),
            delta=f"a.i. {int(ultimo['anno'])}",
            delta_color="off",
        )
        st.caption(f"{fmt_num(ultimo['numero_contribuenti'])} contribuenti")
with k3:
    if not irap.empty:
        ultimo = irap.iloc[-1]
        st.metric(
            "IRAP — imposta",
            fmt_eur(ultimo["imposta_eur"], compact=True),
            delta=f"a.i. {int(ultimo['anno'])}",
            delta_color="off",
        )
        st.caption(f"{fmt_eur(ultimo['base_imponibile_eur'], compact=True)} di base imponibile")
with k4:
    if not ires.empty:
        anno_ires = int(ires["anno"].max())
        st.metric(
            "IRES — reddito d'impresa",
            fmt_eur(ires["reddito_totale_eur"].sum(), compact=True),
            delta=f"a.i. {anno_ires}",
            delta_color="off",
        )
        st.caption(f"{fmt_num(ires['n_dichiarazioni'].sum())} dichiarazioni")

# ══════════════════════════════════════════════════════════════════════
# I PERIMETRI IRPEF
# ══════════════════════════════════════════════════════════════════════
st.subheader("Dentro l'IRPEF: i perimetri per forma giuridica")

acsp = load_mart_flat("acsp_tutte_regione", "mart_anno").sort_values("anno")
abpf = load_mart_flat("abpf_titolari_piva_regione", "mart_anno").sort_values("anno")

c1, c2, c3 = st.columns(3)
with c1:
    if not irpef.empty:
        ultimo = irpef.iloc[-1]
        st.metric("IRPEF — totale", fmt_eur(ultimo["imposta_netta_eur"], compact=True))
        st.caption(f"tutte le tipologie di contribuente, a.i. {int(ultimo['anno'])}")
with c2:
    if not abpf.empty:
        ultimo = abpf.iloc[-1]
        st.metric(
            "Titolari di partita IVA",
            fmt_eur(ultimo["reddito_complessivo_eur"], compact=True),
            delta=f"{fmt_num(ultimo['numero_titolari'])} soggetti",
            delta_color="off",
        )
        st.caption(f"imposta netta {fmt_eur(ultimo['imposta_netta_eur'], compact=True)}")
with c3:
    if not acsp.empty:
        ultimo = acsp.iloc[-1]
        st.metric(
            "Società di persone",
            fmt_eur(ultimo["totale_reddito_eur"], compact=True),
            delta=f"{fmt_num(ultimo['numero_societa'])} società",
            delta_color="off",
        )
        st.caption("reddito dichiarato dalle società (tassato in capo ai soci)")

st.caption(
    "⚠️ I perimetri **non sono additivi**. «IRPEF — totale» è l'imposta di tutte le "
    "tipologie di contribuente; titolari di partita IVA e società di persone sono "
    "**sottoinsiemi** con metriche diverse (reddito complessivo, reddito dichiarato "
    "dalla società), non quote di un totale. IVA, IRAP e IRES sono imposte distinte."
)

# ══════════════════════════════════════════════════════════════════════
# INDICE DEI DATASET
# ══════════════════════════════════════════════════════════════════════
st.subheader("Dati disponibili")

INDICE = [
    ("IRPEF · persone fisiche", "IRPEF per tipologia", "irpef_imposta_tipologia", "02 · IRPEF — persone fisiche"),
    ("IRPEF · persone fisiche", "Imposta lorda, detrazioni e netta", "irpef_calcolo_tipologia", "02 · IRPEF — persone fisiche"),
    ("IRPEF · persone fisiche", "Redditi per comune", "irpef_comunale", "02 · IRPEF — persone fisiche"),
    ("IRPEF · persone fisiche", "Redditi per regione e classe", "mef_irpef_regionale", "02 · IRPEF — persone fisiche"),
    ("IRPEF · società di persone", "Aggregato per regione", "acsp_tutte_regione", "03 · IRPEF — società di persone"),
    ("IRPEF · società di persone", "Imprese", "acsp_imprese_regione", "03 · IRPEF — società di persone"),
    ("IRPEF · società di persone", "Professionisti", "acsp_professionisti_regione", "03 · IRPEF — società di persone"),
    ("IRPEF · società di persone", "Classi di reddito", "acsp_tutte_classi_reddito", "03 · IRPEF — società di persone"),
    ("IRPEF · società di persone", "Classi di volume d'affari", "acsp_tutte_classi_volume", "03 · IRPEF — società di persone"),
    ("IRPEF · titolari di partita IVA", "Redditi, imposta, regimi agevolati", "abpf_titolari_piva_regione", "04 · IRPEF — partite IVA"),
    ("IVA", "Volume d'affari per regione", "iva_regionale", "05 · IVA"),
    ("IVA", "Volume d'affari per settore ATECO", "iva_sez_attivita", "05 · IVA"),
    ("IRAP", "Base imponibile e imposta per regione", "irap_imposta_regione", "06 · IRAP"),
    ("IRAP", "Attività istituzionali delle P.A.", "irap_imposta_pa_regione", "06 · IRAP"),
    ("IRAP", "Base e imposta per sezione ATECO", "irap_imposta_settore", "06 · IRAP"),
    ("IRAP", "Valore della produzione per regime", "irap_vp_regime", "06 · IRAP"),
    ("IRAP", "Produzione in Italia vs all'estero", "irap_italia_estero", "06 · IRAP"),
    ("IRES", "Reddito e perdita d'impresa per regione", "ires_redditi_regione", "07 · IRES"),
]

righe = []
for imposta, vista, slug, pagina in INDICE:
    periodo = dataset_period(slug)
    righe.append(
        {
            "Imposta": imposta,
            "Vista": vista,
            "Anni d'imposta": f"{periodo.get('start', '—')}–{periodo.get('end', '—')}",
            "Pagina": pagina,
        }
    )
st.dataframe(righe, width="stretch", hide_index=True)

st.caption("Dati: MEF — Dipartimento delle Finanze · analisi_stat · CC BY")
