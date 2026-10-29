"""IVA — sintesi nazionale, regioni e settori ATECO.

Due dataset: `iva_regionale` (regione) e `iva_sez_attivita` (sezione ATECO).
Il mart flat `mart_sintesi_nazionale` copre l'intero periodo.
"""

import plotly.graph_objects as go
import streamlit as st
from sources import (
    YEARS_IVA,
    YEARS_IVA_SETTORI,
    fmt_eur,
    fmt_num,
    load_mart,
    load_mart_flat,
)

st.title("🧮 IVA")
st.markdown(
    "Il volume d'affari dichiarato ai fini IVA: totale nazionale, confronto "
    "regionale e composizione per sezione di attività economica."
)

tab_naz, tab_reg, tab_set = st.tabs(["Sintesi nazionale", "Regioni", "Settori ATECO"])

# ══════════════════════════════════════════════════════════════════════
# TAB SINTESI NAZIONALE
# ══════════════════════════════════════════════════════════════════════
with tab_naz:
    df = load_mart_flat("iva_regionale", "mart_sintesi_nazionale").sort_values("anno")

    if df.empty:
        st.warning("Nessun dato IVA disponibile.")
    else:
        ultimo = df.iloc[-1]
        anno_di = int(ultimo["anno"])

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric(
                "Volume d'affari",
                fmt_eur(ultimo["volume_affari_eur"], compact=True),
                delta=f"{ultimo['delta_volume_pct']:+.1f}%" if ultimo["delta_volume_pct"] == ultimo["delta_volume_pct"] else None,
            )
        with k2:
            st.metric("Contribuenti IVA", fmt_num(ultimo["contribuenti"]))
        with k3:
            st.metric("Valore aggiunto fiscale", fmt_eur(ultimo["va_fiscale_eur"], compact=True))
        with k4:
            st.metric("Imposta dovuta", fmt_eur(ultimo["imposta_dovuta_eur"], compact=True))

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["anno"],
                y=df["volume_affari_eur"] / 1e12,
                mode="lines+markers",
                name="Volume d'affari",
                line={"width": 3},
            )
        )
        fig.update_layout(
            title="Volume d'affari IVA nazionale — TRLN €",
            xaxis_title="Anno d'imposta",
            yaxis_title="TRLN €",
            height=380,
            margin={"t": 40, "b": 40},
        )
        st.plotly_chart(fig, width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            fig2 = go.Figure()
            fig2.add_trace(
                go.Bar(x=df["anno"], y=df["imposta_dovuta_eur"] / 1e9, name="Imposta dovuta")
            )
            fig2.add_trace(
                go.Bar(x=df["anno"], y=df["imposta_credito_eur"] / 1e9, name="Imposta a credito")
            )
            fig2.update_layout(
                barmode="group",
                title="Imposta dovuta vs credito — MLD €",
                height=380,
                margin={"t": 40, "b": 40},
            )
            st.plotly_chart(fig2, width="stretch")
        with c2:
            fig3 = go.Figure()
            fig3.add_trace(
                go.Scatter(
                    x=df["anno"],
                    y=df["quota_contribuenti_credito_pct"],
                    mode="lines+markers",
                    name="% a credito",
                )
            )
            fig3.update_layout(
                title="Contribuenti IVA a credito",
                yaxis_title="%",
                height=380,
                margin={"t": 40, "b": 40},
            )
            st.plotly_chart(fig3, width="stretch")

        st.markdown(
            f"Ad a.i. **{anno_di}**: **{fmt_eur(ultimo['va_per_dichiarante_eur'])}** "
            f"di valore aggiunto fiscale per dichiarazione con VA, "
            f"**{ultimo['quota_contribuenti_credito_pct']:.1f}%** dei contribuenti a credito."
        )
        st.caption(
            "Il valore aggiunto per dichiarante è quello pubblicato dal mart: divide "
            "per la **frequenza della voce**, non per i contribuenti totali."
        )

# ══════════════════════════════════════════════════════════════════════
# TAB REGIONI
# ══════════════════════════════════════════════════════════════════════
with tab_reg:
    year = st.selectbox(
        "Anno di presentazione", YEARS_IVA, index=len(YEARS_IVA) - 1, key="iva_reg_year"
    )
    df = load_mart("iva_regionale", "mart_regioni_anno", year)

    if df.empty:
        st.warning("Nessun dato disponibile per l'anno selezionato.")
    else:
        df = df.sort_values("quota_volume_pct", ascending=False)
        top = df.iloc[0]

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Regioni", len(df))
        with k2:
            st.metric(f"Top: {top['regione']}", f"{top['quota_volume_pct']:.1f}%")
        with k3:
            st.metric("Top 3", f"{df.head(3)['quota_volume_pct'].sum():.1f}%")

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df["regione"],
                y=df["quota_volume_pct"],
                text=df["quota_volume_pct"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            )
        )
        fig.update_layout(
            title=f"Quota di volume d'affari per regione ({int(df['anno'].max())})",
            xaxis_title="Regione",
            yaxis_title="% sul totale nazionale",
            height=500,
            margin={"t": 40, "b": 120},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")

        st.subheader("Dettaglio regione")
        regione_sel = st.selectbox(
            "Seleziona regione", sorted(df["regione"].unique()), key="iva_det_regione"
        )
        row = df[df["regione"] == regione_sel].iloc[0]

        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.metric("Volume d'affari", fmt_eur(row["volume_affari_eur"], compact=True))
        with rc2:
            st.metric("Quota nazionale", f"{row['quota_volume_pct']:.1f}%")
        with rc3:
            st.metric("Contribuenti", fmt_num(row["contribuenti"]))
        with rc4:
            st.metric("Volume per dichiarante", fmt_eur(row["volume_per_dichiarante_eur"]))

        st.subheader("Trend regionale")
        trend = load_mart_flat("iva_regionale", "mart_trend_regioni")
        if not trend.empty:
            trend = trend.sort_values("delta_volume_pct", ascending=False)
            fig2 = go.Figure()
            fig2.add_trace(
                go.Bar(
                    x=trend["regione"],
                    y=trend["delta_volume_pct"],
                    text=trend["delta_volume_pct"].apply(lambda x: f"{x:+.1f}%"),
                    textposition="outside",
                )
            )
            fig2.update_layout(
                title=(
                    "Crescita del volume d'affari "
                    f"({int(trend['anno_inizio'].min())} → {int(trend['anno_fine'].max())})"
                ),
                xaxis_title="Regione",
                yaxis_title="Variazione %",
                height=500,
                margin={"t": 40, "b": 120},
                xaxis_tickangle=-45,
            )
            st.plotly_chart(fig2, width="stretch")

            with st.expander("Tabella trend regioni"):
                st.dataframe(
                    trend[
                        [
                            "regione",
                            "anno_inizio",
                            "anno_fine",
                            "delta_volume_pct",
                            "delta_contribuenti_pct",
                        ]
                    ],
                    width="stretch",
                    hide_index=True,
                )

# ══════════════════════════════════════════════════════════════════════
# TAB SETTORI ATECO
# ══════════════════════════════════════════════════════════════════════
with tab_set:
    year_set = st.selectbox(
        "Anno di presentazione",
        YEARS_IVA_SETTORI,
        index=len(YEARS_IVA_SETTORI) - 1,
        key="iva_set_year",
    )
    df = load_mart("iva_sez_attivita", "mart_settori_anno", year_set)

    if df.empty:
        st.warning("Nessun dato settoriale disponibile.")
    else:
        df = df.sort_values("quota_volume_pct", ascending=False)
        top = df.iloc[0]
        anno_di = int(df["anno"].max())

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Sezioni", len(df))
        with k2:
            st.metric("Top settore", top["sezione_attivita"][:40])
        with k3:
            st.metric("Quota top settore", f"{top['quota_volume_pct']:.1f}%")

        top6 = df.head(6)
        labels = list(top6["sezione_attivita"]) + ["Altri"]
        values = list(top6["volume_affari_eur"]) + [df.iloc[6:]["volume_affari_eur"].sum()]
        fig = go.Figure(
            go.Pie(labels=labels, values=values, hole=0.4, textinfo="label+percent")
        )
        fig.update_layout(
            title=f"Distribuzione del volume d'affari ({anno_di})",
            height=500,
            margin={"t": 40, "b": 40},
        )
        st.plotly_chart(fig, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=df["sezione_attivita"],
                y=df["quota_volume_pct"],
                text=df["quota_volume_pct"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            )
        )
        fig2.update_layout(
            title="Quota di volume per sezione",
            xaxis_title="Sezione",
            yaxis_title="% sul totale",
            height=600,
            margin={"t": 40, "b": 200},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig2, width="stretch")

        with st.expander("Tabella completa"):
            st.dataframe(
                df[
                    [
                        "sezione_attivita",
                        "volume_affari_eur",
                        "quota_volume_pct",
                        "contribuenti",
                        "va_fiscale_eur",
                        "rank_volume",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )

        pos = YEARS_IVA_SETTORI.index(year_set)
        if pos > 0:
            anno_prev = YEARS_IVA_SETTORI[pos - 1]
            df_prev = load_mart("iva_sez_attivita", "mart_settori_anno", anno_prev)
            if not df_prev.empty:
                merged = df.merge(
                    df_prev[["sezione_attivita", "volume_affari_eur"]],
                    on="sezione_attivita",
                    suffixes=("", "_prev"),
                )
                merged["delta_pct"] = (
                    (merged["volume_affari_eur"] - merged["volume_affari_eur_prev"])
                    / merged["volume_affari_eur_prev"]
                    * 100
                )
                merged = merged.sort_values("delta_pct", ascending=False)

                fig3 = go.Figure()
                fig3.add_trace(
                    go.Bar(
                        x=merged["sezione_attivita"],
                        y=merged["delta_pct"],
                        text=merged["delta_pct"].apply(lambda x: f"{x:+.1f}%"),
                        textposition="outside",
                    )
                )
                fig3.update_layout(
                    title=(
                        "Variazione del volume d'affari "
                        f"a.i. {int(df_prev['anno'].max())} → {anno_di}"
                    ),
                    height=500,
                    margin={"t": 40, "b": 200},
                    xaxis_tickangle=-45,
                )
                st.plotly_chart(fig3, width="stretch")

st.caption("Dati: MEF — IVA · ATECO")
