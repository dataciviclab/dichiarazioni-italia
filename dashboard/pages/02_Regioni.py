"""Regioni — Analisi regionale del volume d'affari IVA e confronti."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sources import load_mart, load_mart_all, YEARS, fmt_trilioni, fmt_num

st.title("🗺️ Regioni")
st.markdown("Confronto regionale del volume d'affari IVA, quote di mercato e trend.")

# ── Selectors ────────────────────────────────────────────────────────
year = st.selectbox("Anno", YEARS, index=len(YEARS) - 1, key="regioni_year")

# ── Load data ────────────────────────────────────────────────────────
df = load_mart("iva_regionale", "mart_regioni_anno", year)

if df.empty:
    st.warning("Nessun dato disponibile per l'anno selezionato.")
    st.stop()

df = df.sort_values("quota_volume_pct", ascending=False)

# ── KPI top line ─────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Regioni", len(df))
with k2:
    top = df.iloc[0]
    st.metric(f"Top: {top['regione']}", f"{top['quota_volume_pct']:.1f}%")
with k3:
    top3_quota = df.head(3)["quota_volume_pct"].sum()
    st.metric("Top 3", f"{top3_quota:.1f}%")

# ── Bar chart: quota volume per regione ──────────────────────────────
fig = go.Figure()
fig.add_trace(go.Bar(
    x=df["regione"],
    y=df["quota_volume_pct"],
    text=df["quota_volume_pct"].apply(lambda x: f"{x:.1f}%"),
    textposition="outside",
))
fig.update_layout(
    title=f"Quota volume d'affari per regione ({year})",
    xaxis_title="Regione",
    yaxis_title="% sul totale nazionale",
    height=500,
    margin={"t": 40, "b": 120},
    xaxis_tickangle=-45,
)
st.plotly_chart(fig, width="stretch")

# ── Dettaglio regione ────────────────────────────────────────────────
st.subheader("Dettaglio regione")
regione_sel = st.selectbox("Seleziona regione", sorted(df["regione"].unique()), key="det_regione")

row = df[df["regione"] == regione_sel].iloc[0]

rc1, rc2, rc3, rc4 = st.columns(4)
with rc1:
    st.metric("Volume d'affari", fmt_trilioni(row["volume_affari_eur"]))
with rc2:
    st.metric("Quota nazionale", f"{row['quota_volume_pct']:.1f}%")
with rc3:
    st.metric("Contribuenti", fmt_num(row["contribuenti"]))
with rc4:
    st.metric("Rank", f"#{int(row['rank_volume'])}")

# ── Trend regionale (multi-anno) ────────────────────────────────────
st.subheader("Trend regionale")
df_all = load_mart_all("iva_regionale", "mart_regioni_anno")

if not df_all.empty:
    trend_rows = []
    for reg, grp in df_all.groupby("regione"):
        grp = grp.sort_values("anno")
        first, last = grp.iloc[0], grp.iloc[-1]
        delta_vol = ((last["volume_affari_eur"] - first["volume_affari_eur"])
                     / first["volume_affari_eur"] * 100) if first["volume_affari_eur"] else 0
        delta_conv = ((last["contribuenti"] - first["contribuenti"])
                      / first["contribuenti"] * 100) if first["contribuenti"] else 0
        trend_rows.append({
            "regione": reg,
            "anno_inizio": int(first["anno"]),
            "anno_fine": int(last["anno"]),
            "delta_volume_pct": round(delta_vol, 1),
            "delta_contribuenti_pct": round(delta_conv, 1),
        })
    df_trend = pd.DataFrame(trend_rows).sort_values("delta_volume_pct", ascending=False)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_trend["regione"],
        y=df_trend["delta_volume_pct"],
        text=df_trend["delta_volume_pct"].apply(lambda x: f"{x:+.1f}%"),
        textposition="outside",
        marker_color=["#27ae60" if v > 0 else "#e74c3c" for v in df_trend["delta_volume_pct"]],
    ))
    fig2.update_layout(
        title="Crescita volume d'affari (primo vs ultimo anno disponibile)",
        xaxis_title="Regione",
        yaxis_title="Variazione %",
        height=500,
        margin={"t": 40, "b": 120},
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig2, width="stretch")

    with st.expander("Tabella trend regioni"):
        st.dataframe(
            df_trend[["regione", "anno_inizio", "anno_fine", "delta_volume_pct",
                       "delta_contribuenti_pct"]],
            use_container_width=True,
            hide_index=True,
        )

st.caption("Dati: MEF — IVA regionale")
