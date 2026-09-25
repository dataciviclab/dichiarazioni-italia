"""Settori ATECO — Analisi del volume d'affari IVA per settore economico."""

import streamlit as st
import plotly.graph_objects as go
from sources import load_mart, YEARS, fmt_trilioni

st.title("🏭 Settori ATECO")
st.markdown("Distribuzione del volume d'affari IVA per sezione di attività economica.")

# ── Load data ────────────────────────────────────────────────────────
available_years = [y for y in YEARS if y >= 2015]
year = st.selectbox("Anno", available_years, index=len(available_years) - 1, key="sett_year")

df = load_mart("iva_sez_attivita", "mart_settori_anno", year)

if df.empty:
    st.warning("Nessun dato settoriale disponibile.")
    st.stop()

df = df.sort_values("quota_volume_pct", ascending=False)

# ── KPI ──────────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Settori", len(df))
with k2:
    top = df.iloc[0]
    st.metric("Top settore", top["sezione_attivita"][:40])
with k3:
    st.metric("Quota top settore", f"{top['quota_volume_pct']:.1f}%")

# ── Donut chart top 6 + altri ───────────────────────────────────────
top6 = df.head(6).copy()
others_vol = df.iloc[6:]["volume_affari_eur"].sum()

labels = list(top6["sezione_attivita"]) + ["Altri"]
values = list(top6["volume_affari_eur"]) + [others_vol]

fig = go.Figure(data=[go.Pie(
    labels=labels, values=values, hole=0.4,
    textinfo="label+percent", textposition="outside",
)])
fig.update_layout(
    title=f"Distribuzione volume d'affari ({year})",
    height=500, margin={"t": 40, "b": 40}, showlegend=True,
)
st.plotly_chart(fig, width="stretch")

# ── Bar chart tutti i settori ────────────────────────────────────────
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=df["sezione_attivita"],
    y=df["quota_volume_pct"],
    text=df["quota_volume_pct"].apply(lambda x: f"{x:.1f}%"),
    textposition="outside",
))
fig2.update_layout(
    title="Quota volume per settore",
    xaxis_title="Settore", yaxis_title="% sul totale",
    height=600, margin={"t": 40, "b": 200}, xaxis_tickangle=-45,
)
st.plotly_chart(fig2, width="stretch")

# ── Tabella dettaglio ────────────────────────────────────────────────
with st.expander("Tabella completa"):
    st.dataframe(
        df[["sezione_attivita", "volume_affari_eur", "quota_volume_pct",
            "contribuenti", "va_fiscale_eur", "rank_volume"]],
        use_container_width=True, hide_index=True,
    )

# ── Trend settoriale ────────────────────────────────────────────────
if year > 2015:
    st.subheader(f"Confronto {year-1} vs {year}")
    df_prev = load_mart("iva_sez_attivita", "mart_settori_anno", year - 1)
    if not df_prev.empty:
        merged = df.merge(
            df_prev[["sezione_attivita", "volume_affari_eur"]],
            on="sezione_attivita", suffixes=("", "_prev"),
        )
        merged["delta_pct"] = (merged["volume_affari_eur"] - merged["volume_affari_eur_prev"]) / merged["volume_affari_eur_prev"] * 100
        merged = merged.sort_values("delta_pct", ascending=False)

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=merged["sezione_attivita"], y=merged["delta_pct"],
            text=merged["delta_pct"].apply(lambda x: f"{x:+.1f}%"),
            textposition="outside",
            marker_color=["#27ae60" if v > 0 else "#e74c3c" for v in merged["delta_pct"]],
        ))
        fig3.update_layout(
            title=f"Variazione volume d'affari {year-1} → {year}",
            height=500, margin={"t": 40, "b": 200}, xaxis_tickangle=-45,
        )
        st.plotly_chart(fig3, width="stretch")

st.caption("Dati: MEF — IVA per sezione di attività · ATECO")
