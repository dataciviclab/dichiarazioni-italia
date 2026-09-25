"""Imprese IRAP — Valore produzione per regime, Italia vs estero, IRES."""

import streamlit as st
import plotly.graph_objects as go
from sources import load_mart, YEARS, fmt_trilioni, fmt_num

st.title("🏢 Imprese (IRAP)")
st.markdown(
    "Valore di produzione IRAP per regime contabile, produzione netta "
    "in Italia vs estero, e reddito d'impresa IRES."
)

tab_regime, tab_estero, tab_ires = st.tabs(["Regime contabile", "Italia vs Estero", "IRES Redditi"])

# ══════════════════════════════════════════════════════════════════════
# TAB REGIME CONTABILE
# ══════════════════════════════════════════════════════════════════════
with tab_regime:
    year_r = st.selectbox("Anno", YEARS, index=len(YEARS) - 1, key="irap_year")
    df_reg = load_mart("irap_vp_regime", "mart_regioni_anno", year_r)

    if df_reg.empty:
        st.warning("Nessun dato IRAP regime disponibile.")
    else:
        df_reg = df_reg.sort_values("prod_netta_eur", ascending=False)
        totale = df_reg["vp_ord_eur"].sum() + df_reg["vp_forf_eur"].sum() + df_reg["vp_agr_eur"].sum()

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Produzione lorda totale", fmt_trilioni(totale))
        with k2:
            st.metric("Regioni", len(df_reg))
        with k3:
            forf_pct = df_reg["vp_forf_eur"].sum() / totale * 100 if totale > 0 else 0
            st.metric("Quota forfetario", f"{forf_pct:.2f}%")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_reg["regione"], y=df_reg["vp_ord_eur"] / 1e9, name="Ordinario"))
        fig.add_trace(go.Bar(x=df_reg["regione"], y=df_reg["vp_forf_eur"] / 1e9, name="Forfetario"))
        fig.add_trace(go.Bar(x=df_reg["regione"], y=df_reg["vp_agr_eur"] / 1e9, name="Agricolo"))
        fig.update_layout(
            barmode="stack",
            title=f"Valore produzione per regime ({year_r}) — MLD €",
            height=500, margin={"t": 40, "b": 120}, xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")

# ══════════════════════════════════════════════════════════════════════
# TAB ITALIA VS ESTERO
# ══════════════════════════════════════════════════════════════════════
with tab_estero:
    year_e = st.selectbox("Anno", YEARS, index=len(YEARS) - 1, key="estero_year")
    df_est = load_mart("irap_italia_estero", "mart_regioni_anno", year_e)

    if df_est.empty:
        st.warning("Nessun dato Italia/Estero disponibile.")
    else:
        df_est = df_est.sort_values("prod_netta_eur", ascending=False)
        quota_estero = df_est["vp_estero_eur"].sum() / df_est["prod_netta_eur"].sum() * 100

        k1, k2 = st.columns(2)
        with k1:
            st.metric("Produzione netta totale", fmt_trilioni(df_est["prod_netta_eur"].sum()))
        with k2:
            st.metric("Quota estero media", f"{quota_estero:.2f}%")

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_est["regione"], y=df_est["vp_italia_eur"] / 1e9, name="Italia"))
        fig2.add_trace(go.Bar(x=df_est["regione"], y=df_est["vp_estero_eur"] / 1e9, name="Estero"))
        fig2.update_layout(
            barmode="stack",
            title=f"Produzione netta: Italia vs Estero ({year_e}) — MLD €",
            height=500, margin={"t": 40, "b": 120}, xaxis_tickangle=-45,
        )
        st.plotly_chart(fig2, width="stretch")

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=df_est["regione"], y=df_est["quota_estero_pct"],
            text=df_est["quota_estero_pct"].apply(lambda x: f"{x:.2f}%"),
            textposition="outside",
        ))
        fig3.update_layout(
            title=f"Quota produzione estera per regione ({year_e})",
            height=450, margin={"t": 40, "b": 120}, xaxis_tickangle=-45, yaxis_title="%",
        )
        st.plotly_chart(fig3, width="stretch")

# ══════════════════════════════════════════════════════════════════════
# TAB IRES REDDITI
# ══════════════════════════════════════════════════════════════════════
with tab_ires:
    year_i = st.selectbox("Anno", YEARS, index=len(YEARS) - 1, key="ires_year")
    df_ires = load_mart("ires_redditi_regione", "mart_regioni_anno", year_i)

    if df_ires.empty:
        st.warning("Nessun dato IRES disponibile.")
    else:
        df_ires = df_ires.sort_values("reddito_totale_eur", ascending=False)

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Dichiarazioni IRES", fmt_num(df_ires["n_dichiarazioni"].sum()))
        with k2:
            st.metric("Reddito totale", fmt_trilioni(df_ires["reddito_totale_eur"].sum()))
        with k3:
            st.metric("Perdita totale", fmt_trilioni(df_ires["perdita_totale_eur"].sum()))

        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df_ires["regione"], y=df_ires["reddito_totale_eur"] / 1e9, name="Reddito"))
        fig4.add_trace(go.Bar(x=df_ires["regione"], y=-df_ires["perdita_totale_eur"] / 1e9, name="Perdita"))
        fig4.update_layout(
            barmode="relative",
            title=f"Reddito vs Perdita d'impresa per regione ({year_i}) — MLD €",
            height=500, margin={"t": 40, "b": 120}, xaxis_tickangle=-45,
        )
        st.plotly_chart(fig4, width="stretch")

st.caption("Dati: MEF — IRAP e IRES")
