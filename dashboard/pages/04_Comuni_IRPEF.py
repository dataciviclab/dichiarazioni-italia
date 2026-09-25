"""Comuni IRPEF — Reddito medio, fasce reddituali, benchmark."""

import streamlit as st
import plotly.graph_objects as go
from lab_connectors.formatters import fmt_eur, fmt_num, fmt_pct
from sources import load_mart, YEARS

st.title("🏘️ Comuni (IRPEF)")
st.markdown("Reddito medio per contribuente, fasce reddituali e confronto con media nazionale.")

# ── Load data ────────────────────────────────────────────────────────
year = st.selectbox("Anno", YEARS, index=len(YEARS) - 1, key="comuni_year")

df = load_mart("irpef_comunale", "mart_comuni", year)

if df.empty:
    st.warning("Nessun dato comunale disponibile.")
    st.stop()

df = df[df["numero_contribuenti"] > 100].copy()
df = df.sort_values("reddito_medio_per_contribuente", ascending=False)

# ── KPI nazionali ────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Comuni", fmt_num(len(df)))
with k2:
    media = df["media_nazionale_reddito"].iloc[0]
    st.metric("Reddito medio nazionale", fmt_eur(media))
with k3:
    n_elevato = (df["fascia_reddito"] == "ELEVATO").sum()
    st.metric("Fascia ELEVATO", f"{n_elevato} comuni")
with k4:
    n_basso = (df["fascia_reddito"] == "BASSO").sum()
    st.metric("Fascia BASSO", f"{n_basso} comuni")

# ── Distribuzione fasce reddituali ──────────────────────────────────
fascia_order = ["BASSO", "SOTTO_MEDIA", "MEDIA", "SOPRA_MEDIA", "ELEVATO"]
fascia_counts = df["fascia_reddito"].value_counts().reindex(fascia_order, fill_value=0)

fig = go.Figure(data=[go.Pie(
    labels=fascia_counts.index,
    values=fascia_counts.values,
    hole=0.4,
    textinfo="label+value",
    textposition="outside",
)])
fig.update_layout(
    title="Distribuzione comuni per fascia reddituale",
    height=400,
    margin={"t": 40, "b": 40},
)
st.plotly_chart(fig, width="stretch")

# ── Mappa: distanza dalla media nazionale ────────────────────────────
st.subheader("Distanza dalla media nazionale")
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=df.head(30)["denominazione_comune"],
    y=df.head(30)["distanza_media_nazionale_pct"],
    text=df.head(30)["distanza_media_nazionale_pct"].apply(lambda x: f"{x:+.1f}%"),
    textposition="outside",
    marker_color=["#27ae60" if v > 0 else "#e74c3c" for v in df.head(30)["distanza_media_nazionale_pct"]],
))
fig2.update_layout(
    title="Top 30 comuni — distanza % dalla media nazionale",
    height=450,
    margin={"t": 40, "b": 120},
    xaxis_tickangle=-45,
)
st.plotly_chart(fig2, width="stretch")

# ── Selettore comune ─────────────────────────────────────────────────
st.subheader("Dettaglio comune")
comuni = sorted(df["denominazione_comune"].unique())
comune_sel = st.selectbox("Comune", comuni, key="sel_comune")

row = df[df["denominazione_comune"] == comune_sel].iloc[0]

rc1, rc2, rc3, rc4 = st.columns(4)
with rc1:
    st.metric("Reddito medio", fmt_eur(row["reddito_medio_per_contribuente"]))
with rc2:
    st.metric("Media nazionale", fmt_eur(row["media_nazionale_reddito"]))
with rc3:
    st.metric("Fascia", row["fascia_reddito"])
with rc4:
    st.metric("Percentile", f"{row['percentile_nazionale_reddito']*100:.1f}%")

st.metric(
    "Distanza dalla media nazionale",
    f"{row['distanza_media_nazionale_pct']:+.1f}%",
    delta=f"{'Sopra' if row['distanza_media_nazionale_pct'] > 0 else 'Sotto'} la media",
)

# ── Tabella top comuni ──────────────────────────────────────────────
st.subheader("Top comuni per reddito medio")
with st.expander("Tabella completa"):
    st.dataframe(
        df[["denominazione_comune", "sigla_provincia", "regione",
            "numero_contribuenti", "reddito_medio_per_contribuente",
            "fascia_reddito", "percentile_nazionale_reddito"]].head(50),
        use_container_width=True,
        hide_index=True,
    )

st.caption("Dati: MEF — IRPEF su base comunale · reddito imponibile medio per contribuente")
