"""IRES — reddito e perdita d'impresa delle società di capitali per regione."""

import plotly.graph_objects as go
import streamlit as st
from sources import YEARS_IRES, fmt_eur, fmt_num, load_mart, load_mart_all

st.title("🏛️ IRES")
st.markdown(
    "Il reddito d'impresa dichiarato ai fini IRES dalle **società di capitali**: "
    "reddito e perdita per regione."
)

anno_sel = st.selectbox(
    "Anno di presentazione", YEARS_IRES, index=len(YEARS_IRES) - 1, key="ires_year"
)
df = load_mart("ires_redditi_regione", "mart_regioni_anno", anno_sel)

if df.empty:
    st.warning("Nessun dato IRES disponibile.")
else:
    df = df.sort_values("reddito_totale_eur", ascending=False)
    anno_di = int(df["anno"].max())
    reddito = df["reddito_totale_eur"].sum()
    perdita = df["perdita_totale_eur"].sum()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Dichiarazioni", fmt_num(df["n_dichiarazioni"].sum()))
    with k2:
        st.metric("Reddito d'impresa", fmt_eur(reddito, compact=True))
    with k3:
        st.metric("Perdite dichiarate", fmt_eur(perdita, compact=True))
    with k4:
        st.metric("Saldo", fmt_eur(reddito - perdita, compact=True))

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df["regione"], y=df["reddito_totale_eur"] / 1e9, name="Reddito")
    )
    fig.add_trace(
        go.Bar(x=df["regione"], y=-df["perdita_totale_eur"] / 1e9, name="Perdita")
    )
    fig.update_layout(
        barmode="relative",
        title=f"Reddito vs perdita d'impresa per regione ({anno_di}) — MLD €",
        height=520,
        margin={"t": 40, "b": 140},
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig, width="stretch")

    df["reddito_medio_dichiarazione"] = df["reddito_totale_eur"] / df["reddito_totale_freq"]
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=df["regione"],
            y=df["reddito_medio_dichiarazione"],
            text=df["quota_reddito_pct"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            name="Reddito medio",
        )
    )
    fig2.update_layout(
        title=f"Reddito d'impresa medio per dichiarazione ({anno_di}) — €",
        height=500,
        margin={"t": 40, "b": 140},
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig2, width="stretch")

    trend = load_mart_all("ires_redditi_regione", "mart_regioni_anno", YEARS_IRES)
    if not trend.empty:
        serie = (
            trend.groupby("anno")[["reddito_totale_eur", "perdita_totale_eur"]]
            .sum()
            .reset_index()
            .sort_values("anno")
        )
        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatter(
                x=serie["anno"],
                y=serie["reddito_totale_eur"] / 1e9,
                name="Reddito",
                mode="lines+markers",
            )
        )
        fig3.add_trace(
            go.Scatter(
                x=serie["anno"],
                y=serie["perdita_totale_eur"] / 1e9,
                name="Perdita",
                mode="lines+markers",
            )
        )
        fig3.update_layout(
            title="Reddito e perdita d'impresa nel tempo — MLD €",
            height=440,
            margin={"t": 40},
            yaxis_title="MLD €",
            legend={"orientation": "h", "y": -0.2},
        )
        st.plotly_chart(fig3, width="stretch")

    with st.expander("Tabella per regione"):
        st.dataframe(
            df[
                [
                    "regione",
                    "n_dichiarazioni",
                    "reddito_totale_eur",
                    "perdita_totale_eur",
                    "reddito_medio_dichiarazione",
                    "quota_reddito_pct",
                    "rank_reddito",
                ]
            ],
            width="stretch",
            hide_index=True,
        )

    st.caption(
        "⚠️ **Reddito e perdita non si sommano**: sono due esiti alternativi della "
        "stessa dichiarazione (un'impresa dichiara reddito *o* perdita). Il saldo è "
        "`reddito − perdita`."
    )

st.caption("Dati: MEF — IRES")
