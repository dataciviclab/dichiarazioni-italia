"""Comuni IRPEF — Reddito medio, fasce reddituali, benchmark."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from sources import load_mart, YEARS, fmt_trilioni, fmt_num

st.title("🏘️ Comuni (IRPEF)")
st.markdown("Reddito medio per contribuente, fasce reddituali e confronto con media nazionale.")

# ── Load data ────────────────────────────────────────────────────────
year = st.selectbox("Anno", YEARS, index=len(YEARS) - 1, key="comuni_year")

df = load_mart("irpef_comunale", "mart_comuni", year)
df_fasce = load_mart("irpef_comunale", "mart_fasce", year)

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
    st.metric("Reddito medio nazionale", f"€{media:,.0f}")
with k3:
    n_elevato = (df["fascia_reddito"] == "ELEVATO").sum()
    st.metric("Fascia ELEVATO", f"{n_elevato} comuni")
with k4:
    n_basso = (df["fascia_reddito"] == "BASSO").sum()
    st.metric("Fascia BASSO", f"{n_basso} comuni")

# ── Contribuenti per fascia reddituale ──────────────────────────────
st.subheader("Contribuenti per fascia di reddito")

if not df_fasce.empty:
    fascia_labels = ["fascia_zero", "fascia_0_10k", "fascia_10_15k", "fascia_15_26k",
                     "fascia_26_55k", "fascia_55_75k", "fascia_75_120k", "fascia_oltre_120k"]
    fascia_names = ["< 0", "0-10k", "10-15k", "15-26k", "26-55k", "55-75k", "75-120k", "> 120k"]

    tot = [df_fasce[f].sum() for f in fascia_labels]
    totale = sum(tot)

    # Bar chart contribuenti per fascia
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=fascia_names, y=[t / 1e6 for t in tot],
        text=[f"{t/1e6:.1f}M" for t in tot],
        textposition="outside",
        marker_color=["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db", "#9b59b6", "#1abc9c", "#34495e"],
    ))
    fig.update_layout(
        title=f"Contribuenti IRPEF per fascia di reddito ({year})",
        xaxis_title="Fascia reddito complessivo",
        yaxis_title="Milioni di contribuenti",
        height=400,
        margin={"t": 40, "b": 40},
    )
    st.plotly_chart(fig, width="stretch")

    # Percentuali
    pct = [t / totale * 100 for t in tot]
    kp1, kp2, kp3 = st.columns(3)
    with kp1:
        st.metric("Fascia più popolosa", f"{fascia_names[tot.index(max(tot))]}",
                  f"{max(tot)/1e6:.1f}M ({max(pct):.1f}%)")
    with kp2:
        st.metric("Reddito > €55k", f"{(tot[5]+tot[6]+tot[7])/1e6:.1f}M",
                  f"{(tot[5]+tot[6]+tot[7])/totale*100:.1f}% del totale")
    with kp3:
        st.metric("Rapporto alta/bassa", f"{df_fasce['rapporto_alta_bassa'].mean():.2f}",
                  help="Ratio contribuenti >55k / <10k per provincia")

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
    st.metric("Reddito medio", f"€{row['reddito_medio_per_contribuente']:,.0f}")
with rc2:
    st.metric("Media nazionale", f"€{row['media_nazionale_reddito']:,.0f}")
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
with st.expander("Top 50 comuni per reddito medio"):
    st.dataframe(
        df[["denominazione_comune", "sigla_provincia", "regione",
            "numero_contribuenti", "reddito_medio_per_contribuente",
            "fascia_reddito", "percentile_nazionale_reddito"]].head(50),
        use_container_width=True, hide_index=True,
    )

st.caption("Dati: MEF — IRPEF su base comunale · reddito imponibile medio per contribuente")
