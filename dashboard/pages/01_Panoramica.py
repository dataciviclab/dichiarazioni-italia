"""Panoramica — Visione d'insieme delle dichiarazioni fiscali italiane."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from sources import load_mart, load_mart_all, query_multi, YEARS, fmt_trilioni, fmt_num, fmt_pct

st.title("📊 Dichiarazioni Italia")
st.markdown(
    "Le dichiarazioni fiscali italiane: IVA, IRPEF, IRAP, IRES. "
    "Dati MEF — Dipartimento delle Finanze."
)

# ── IVA Sintesi Nazionale (multi-anno dal clean) ──────────────────────
st.subheader("IVA — Sintesi Nazionale")

df_sintesi = query_multi(
    "iva_regionale",
    """SELECT anno,
              SUM(contribuenti) as contribuenti,
              SUM(volume_affari_eur) as volume,
              SUM(imposta_dovuta_eur) as imposta,
              SUM(va_fiscale_eur) as va
       FROM clean_input WHERE anno IS NOT NULL
       GROUP BY anno ORDER BY anno""",
)

if df_sintesi.empty:
    st.warning("Nessun dato IVA disponibile.")
    st.stop()

df_sintesi = df_sintesi.sort_values("anno")
df_sintesi["delta_volume_pct"] = df_sintesi["volume"].pct_change() * 100

latest = df_sintesi.iloc[-1]
prev = df_sintesi.iloc[-2] if len(df_sintesi) > 1 else None

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Volume d'affari", fmt_trilioni(latest["volume"]),
              delta=f"{latest['delta_volume_pct']:+.1f}%" if pd.notna(latest["delta_volume_pct"]) else None)
with k2:
    st.metric("Contribuenti IVA", fmt_num(latest["contribuenti"]))
with k3:
    st.metric("VA fiscale", fmt_trilioni(latest["va"]))
with k4:
    st.metric("Imposta dovuta", fmt_trilioni(latest["imposta"]))

# ── Trend Volume d'affari ────────────────────────────────────────────
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_sintesi["anno"],
    y=df_sintesi["volume"] / 1e12,
    mode="lines+markers",
    name="Volume d'affari",
    line=dict(width=3),
))
fig.update_layout(
    title="Volume d'affari IVA nazionale (TRLN €)",
    xaxis_title="Anno",
    yaxis_title="TRLN €",
    height=350,
    margin={"t": 40, "b": 40},
)
st.plotly_chart(fig, width="stretch")

# ── Trend Contribuenti ───────────────────────────────────────────────
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df_sintesi["anno"],
    y=df_sintesi["contribuenti"] / 1e6,
    mode="lines+markers",
    name="Contribuenti",
    line=dict(width=3, color="#e74c3c"),
))
fig2.update_layout(
    title="Contribuenti IVA (milioni)",
    xaxis_title="Anno",
    yaxis_title="Milioni",
    height=350,
    margin={"t": 40, "b": 40},
)
st.plotly_chart(fig2, width="stretch")

# ── Quote imposta dovuta vs credito ──────────────────────────────────
st.subheader("Composizione imposta")
col_left, col_right = st.columns(2)

with col_left:
    # Ricarica per imposta
    df_imp = query_multi(
        "iva_regionale",
        """SELECT anno,
                  SUM(imposta_dovuta_eur) as dovuta,
                  SUM(imposta_credito_eur) as credito
           FROM clean_input WHERE anno IS NOT NULL
           GROUP BY anno ORDER BY anno""",
    )
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=df_imp["anno"], y=df_imp["dovuta"] / 1e9, name="Imposta dovuta"))
    fig3.add_trace(go.Bar(x=df_imp["anno"], y=df_imp["credito"] / 1e9, name="Imposta a credito"))
    fig3.update_layout(barmode="group", title="Imposta dovuta vs credito (MLD €)", height=350, margin={"t": 40, "b": 40})
    st.plotly_chart(fig3, width="stretch")

with col_right:
    df_cred = query_multi(
        "iva_regionale",
        """SELECT anno,
                  SUM(imposta_credito_frequenza) as cred_freq,
                  SUM(va_frequenza) as va_freq
           FROM clean_input WHERE anno IS NOT NULL
           GROUP BY anno ORDER BY anno""",
    )
    df_cred["pct_credito"] = df_cred["cred_freq"] / df_cred["va_freq"] * 100
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=df_cred["anno"], y=df_cred["pct_credito"],
        mode="lines+markers", name="% a credito",
        line=dict(width=3, color="#27ae60"),
    ))
    fig4.update_layout(title="% Contribuenti a credito", yaxis_title="%", height=350, margin={"t": 40, "b": 40})
    st.plotly_chart(fig4, width="stretch")

# ── Nord vs Sud ──────────────────────────────────────────────────────
st.subheader("Nord vs Sud")

NORD = ["Piemonte", "Valle d'Aosta", "Lombardia", "Trentino Alto Adige (P.A. Bolzano)",
        "Trentino Alto Adige (P.A. Trento)", "Veneto", "Friuli Venezia Giulia",
        "Liguria", "Emilia Romagna"]
SUD = ["Abruzzo", "Molise", "Campania", "Puglia", "Basilicata", "Calabria",
       "Sicilia", "Sardegna"]
CENTRO = ["Toscana", "Umbria", "Marche", "Lazio"]

df_regioni = load_mart_all("iva_regionale", "mart_regioni_anno")

if not df_regioni.empty:
    # Ultimo anno disponibile
    max_anno = df_regioni["anno"].max()
    df_last = df_regioni[df_regioni["anno"] == max_anno].copy()

    def _macro(regione):
        if regione in NORD: return "Nord"
        if regione in SUD: return "Sud"
        if regione in CENTRO: return "Centro"
        return "Altro"

    df_last["macro"] = df_last["regione"].apply(_macro)
    macro_vol = df_last.groupby("macro")["volume_affari_eur"].sum()
    macro_pct = macro_vol / macro_vol.sum() * 100

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Nord", f"{macro_pct.get('Nord', 0):.1f}%",
                  help=f"{fmt_trilioni(macro_vol.get('Nord', 0))}")
    with k2:
        st.metric("Centro", f"{macro_pct.get('Centro', 0):.1f}%",
                  help=f"{fmt_trilioni(macro_vol.get('Centro', 0))}")
    with k3:
        st.metric("Sud + Isole", f"{macro_pct.get('Sud', 0):.1f}%",
                  help=f"{fmt_trilioni(macro_vol.get('Sud', 0))}")

    # Bar chart macro
    fig5 = go.Figure()
    colors = {"Nord": "#3498db", "Centro": "#f39c12", "Sud": "#e74c3c"}
    for macro in ["Nord", "Centro", "Sud"]:
        if macro in macro_pct:
            fig5.add_trace(go.Bar(
                x=[macro], y=[macro_pct[macro]],
                name=macro, marker_color=colors.get(macro, "#95a5a6"),
                text=[f"{macro_pct[macro]:.1f}%"], textposition="outside",
            ))
    fig5.update_layout(
        title=f"Distribuzione volume d'affari per macro-area ({max_anno})",
        yaxis_title="%", height=350, margin={"t": 40, "b": 40},
        showlegend=False,
    )
    st.plotly_chart(fig5, width="stretch")

# ── KPI aggiuntivi ──────────────────────────────────────────────────
st.subheader("Indicatori chiave")
ki1, ki2, ki3 = st.columns(3)
with ki1:
    st.metric("VA per dichiarante", fmt_trilioni(latest["va"] / latest["contribuenti"]))
with ki2:
    cred_pct = df_sintesi.iloc[-1].get("delta_volume_pct", 0)
    st.metric("Crescita volume annua", f"{latest['delta_volume_pct']:+.1f}%" if pd.notna(latest['delta_volume_pct']) else "—")
with ki3:
    if prev is not None and prev["contribuenti"] > 0:
        delta_c = (latest["contribuenti"] - prev["contribuenti"]) / prev["contribuenti"] * 100
        st.metric("Δ Contribuenti", f"{delta_c:+.1f}%")
    else:
        st.metric("Δ Contribuenti", "—")

st.caption("Dati: MEF Dip. delle Finanze · analisi_stat · CC BY 4.0")
