"""IRAP — imposta, P.A., settori, valore della produzione, Italia vs estero.

Cinque dataset: `irap_imposta_regione`, `irap_imposta_pa_regione`,
`irap_imposta_settore`, `irap_vp_regime`, `irap_italia_estero`.
"""

import plotly.graph_objects as go
import streamlit as st
from sources import YEARS_IRAP, fmt_eur, fmt_num, load_mart, load_mart_flat

st.title("🏢 IRAP")
st.markdown(
    "L'imposta regionale sulle attività produttive: gettito e base imponibile per "
    "regione, il peso delle P.A., la composizione per settore e il valore della "
    "produzione per regime contabile."
)

tab_imp, tab_pa, tab_prod, tab_est = st.tabs(
    ["Imposta per regione", "P.A. e settori", "Valore della produzione", "Italia vs estero"]
)

# ══════════════════════════════════════════════════════════════════════
# TAB IMPOSTA PER REGIONE
# ══════════════════════════════════════════════════════════════════════
with tab_imp:
    anno_sel = st.selectbox(
        "Anno di presentazione", YEARS_IRAP, index=len(YEARS_IRAP) - 1, key="irap_imp_year"
    )
    df = load_mart("irap_imposta_regione", "mart_regioni_anno", anno_sel)

    if df.empty:
        st.warning("Nessun dato disponibile.")
    else:
        df = df.sort_values("imposta_eur", ascending=False)
        anno_di = int(df["anno"].max())
        aliquota = df["imposta_eur"].sum() / df["base_imponibile_eur"].sum() * 100

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric(
                "Contribuenti (somma regioni)",
                fmt_num(df["contribuenti"].sum()),
                help=(
                    "Dal a.i. 2022 le persone fisiche sono esonerate dall'IRAP "
                    "(L. 234/2021): il calo 2021→2022 (−37%) è di perimetro, non "
                    "di attività. A perimetro omogeneo i contribuenti crescono "
                    "dello 0,8%."
                ),
            )
        with k2:
            st.metric("Imposta IRAP", fmt_eur(df["imposta_eur"].sum(), compact=True))
        with k3:
            st.metric("Aliquota media effettiva", f"{aliquota:.2f}%")

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df["regione"],
                y=df["imposta_eur"] / 1e9,
                text=df["quota_base_pct"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            )
        )
        fig.update_layout(
            title=f"Imposta IRAP per regione ({anno_di}) — MLD €",
            height=520,
            margin={"t": 40, "b": 140},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(x=df["regione"], y=df["aliquota_effettiva_pct"], name="Aliquota effettiva")
        )
        fig2.update_layout(
            title=f"Aliquota IRAP effettiva per regione ({anno_di}) — imposta / base",
            height=460,
            margin={"t": 40, "b": 140},
            xaxis_tickangle=-45,
            yaxis_title="%",
        )
        st.plotly_chart(fig2, width="stretch")

        trend = load_mart_flat("irap_imposta_regione", "mart_imposta_anno")
        if not trend.empty:
            fig3 = go.Figure()
            fig3.add_trace(
                go.Scatter(
                    x=trend["anno"],
                    y=trend["imposta_eur"] / 1e9,
                    name="Imposta",
                    mode="lines+markers",
                )
            )
            fig3.update_layout(
                title="Imposta IRAP totale — MLD €",
                height=420,
                margin={"t": 40},
                yaxis_title="MLD €",
            )
            # Il perimetro cambia ad a.i. 2022 (esonero delle persone fisiche,
            # L. 234/2021): senza il marcatore il gradino si legge come crisi.
            fig3.add_vline(x=2022, line_dash="dash", line_color="#c0392b")
            fig3.add_annotation(
                x=2022,
                y=1,
                yref="paper",
                text="a.i. 2022: fuori le persone fisiche",
                showarrow=False,
                font={"size": 11, "color": "#c0392b"},
                yshift=12,
            )
            st.plotly_chart(fig3, width="stretch")

            dal_2015 = trend[trend["anno"] >= 2015]
            delta_2015 = trend.loc[trend["anno"] == 2015, "delta_base_pct"]
            nota_base = f" ({delta_2015.iloc[0]:.0f}%)" if not delta_2015.empty else ""
            st.caption(
                "⚠️ La base imponibile IRAP cambia definizione tra a.i. 2014 e 2015"
                f"{nota_base}: i trend si leggono **dal 2015**. L'aliquota effettiva è "
                "il rapporto imposta / base imponibile; dal 2015 resta tra il "
                f"{dal_2015['aliquota_effettiva_pct'].min():.1f}% e il "
                f"{dal_2015['aliquota_effettiva_pct'].max():.1f}%. La somma delle 21 "
                "regioni coincide con il totale della fonte in 8 anni su 10; ad a.i. "
                "2014 e 2015 è inferiore di 22 e 8 contribuenti (non attribuiti a una "
                "regione)."
            )

            r21 = trend.loc[trend["anno"] == 2021, "contribuenti"]
            r22 = trend.loc[trend["anno"] == 2022, "contribuenti"]
            nota_22 = ""
            if not r21.empty and not r22.empty:
                nota_22 = (
                    f" Contribuenti: {fmt_num(r21.iloc[0])} → {fmt_num(r22.iloc[0])} "
                    f"({(r22.iloc[0] / r21.iloc[0] - 1) * 100:.0f}%)."
                )
            st.caption(
                "⚠️ **Secondo cambio di perimetro ad a.i. 2022**: le persone fisiche "
                "sono esonerate dall'IRAP (L. 234/2021, art. 1 comma 8)."
                + nota_22
                + " A perimetro omogeneo (2021 al netto delle persone fisiche) i "
                "contribuenti crescono dello **0,8%**, la base del **12,3%** e "
                "l'imposta dell'**11,2%** (nota MEF a.i. 2022). **Non leggere la serie "
                "dei contribuenti a cavallo del 2021/2022.**"
            )

# ══════════════════════════════════════════════════════════════════════
# TAB P.A. E SETTORI
# ══════════════════════════════════════════════════════════════════════
with tab_pa:
    anno_pa = st.selectbox(
        "Anno di presentazione", YEARS_IRAP, index=len(YEARS_IRAP) - 1, key="irap_pa_year"
    )
    df_pa = load_mart("irap_imposta_pa_regione", "mart_regioni_anno", anno_pa)
    df_set = load_mart("irap_imposta_settore", "mart_settori_anno", anno_pa)
    df_tot = load_mart("irap_imposta_regione", "mart_regioni_anno", anno_pa)

    if df_pa.empty and df_set.empty:
        st.warning("Nessun dato disponibile.")
    else:
        n_settori = df_set["sezione_attivita"].nunique() if not df_set.empty else 0
        c1, c2 = st.columns(2)
        with c1:
            if not df_pa.empty:
                d = df_pa.sort_values("imposta_netta_eur", ascending=False)
                fig = go.Figure()
                fig.add_trace(
                    go.Bar(x=d["regione"], y=d["imposta_netta_eur"] / 1e9, name="P.A.")
                )
                fig.update_layout(
                    title=(
                        f"IRAP delle P.A. per regione ({int(d['anno'].max())}) — MLD €"
                    ),
                    height=520,
                    margin={"t": 40, "b": 160},
                    xaxis_tickangle=-45,
                )
                st.plotly_chart(fig, width="stretch")
                quota = ""
                if not df_tot.empty and df_tot["imposta_eur"].sum():
                    share = (
                        d["imposta_netta_eur"].sum() / df_tot["imposta_eur"].sum() * 100
                    )
                    quota = f" — il **{share:.0f}%** del totale nazionale"
                st.markdown(
                    f"Le P.A. pagano **{fmt_eur(d['imposta_netta_eur'].sum(), compact=True)}** "
                    f"di IRAP{quota}."
                )
        with c2:
            if not df_set.empty:
                d = df_set.sort_values("imposta_eur", ascending=False)
                fig = go.Figure()
                fig.add_trace(
                    go.Bar(x=d["sezione_attivita"], y=d["imposta_eur"] / 1e9, name="Settore")
                )
                fig.update_layout(
                    title=(
                        f"IRAP per sezione ATECO ({int(d['anno'].max())}) — MLD €"
                    ),
                    height=520,
                    margin={"t": 40, "b": 200},
                    xaxis_tickangle=-45,
                )
                st.plotly_chart(fig, width="stretch")

        st.caption(
            "IRAP delle P.A.: base imponibile e imposta netta delle **attività "
            "istituzionali** esercitate dalle P.A. (vista complementare a quella "
            "totale: la differenza è il settore privato). IRAP per settore: "
            f"{n_settori} righe (21 sezioni ATECO + «Attività non classificabile»)."
        )

# ══════════════════════════════════════════════════════════════════════
# TAB VALORE DELLA PRODUZIONE
# ══════════════════════════════════════════════════════════════════════
with tab_prod:
    anno_pr = st.selectbox(
        "Anno di presentazione", YEARS_IRAP, index=len(YEARS_IRAP) - 1, key="irap_prod_year"
    )
    df_reg = load_mart("irap_vp_regime", "mart_regioni_anno", anno_pr)

    if df_reg.empty:
        st.warning("Nessun dato disponibile.")
    else:
        df_reg = df_reg.sort_values("prod_netta_eur", ascending=False)
        anno_di = int(df_reg["anno"].max())
        lorda = (
            df_reg["vp_ord_eur"].sum()
            + df_reg["vp_forf_eur"].sum()
            + df_reg["vp_agr_eur"].sum()
            + df_reg["vp_arti_eur"].sum()
            + df_reg["vp_noncomm_eur"].sum()
        )
        deduzioni = df_reg["deduzioni_eur"].sum()

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Produzione netta", fmt_eur(df_reg["prod_netta_eur"].sum(), compact=True))
        with k2:
            st.metric("Produzione lorda", fmt_eur(lorda, compact=True))
        with k3:
            st.metric("Deduzioni", fmt_eur(deduzioni, compact=True))

        fig = go.Figure()
        for colonna, etichetta in (
            ("vp_ord_eur", "Ordinario"),
            ("vp_noncomm_eur", "Non commerciali"),
            ("vp_arti_eur", "Artigiani"),
            ("vp_forf_eur", "Forfetario"),
            ("vp_agr_eur", "Agricolo"),
        ):
            fig.add_trace(
                go.Bar(x=df_reg["regione"], y=df_reg[colonna] / 1e9, name=etichetta)
            )
        fig.update_layout(
            barmode="stack",
            title=f"Produzione lorda per regime ({anno_di}) — MLD €",
            height=520,
            margin={"t": 40, "b": 140},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")

        st.caption(
            "La **produzione netta** è la produzione lorda dei cinque regimi "
            "(ordinario, non commerciali, artigiani, forfetario, agricolo) al netto "
            "delle deduzioni: il mart pubblica entrambe le grandezze."
        )

# ══════════════════════════════════════════════════════════════════════
# TAB ITALIA VS ESTERO
# ══════════════════════════════════════════════════════════════════════
with tab_est:
    anno_est = st.selectbox(
        "Anno di presentazione", YEARS_IRAP, index=len(YEARS_IRAP) - 1, key="irap_est_year"
    )
    df_est = load_mart("irap_italia_estero", "mart_regioni_anno", anno_est)

    if df_est.empty:
        st.warning("Nessun dato disponibile.")
    else:
        df_est = df_est.sort_values("prod_netta_eur", ascending=False)
        anno_di = int(df_est["anno"].max())
        quota_estero = df_est["vp_estero_eur"].sum() / df_est["prod_netta_eur"].sum() * 100

        k1, k2 = st.columns(2)
        with k1:
            st.metric(
                "Produzione netta", fmt_eur(df_est["prod_netta_eur"].sum(), compact=True)
            )
        with k2:
            st.metric("Quota estera", f"{quota_estero:.2f}%")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_est["regione"], y=df_est["vp_italia_eur"] / 1e9, name="Italia"))
        fig.add_trace(go.Bar(x=df_est["regione"], y=df_est["vp_estero_eur"] / 1e9, name="Estero"))
        fig.update_layout(
            barmode="stack",
            title=f"Produzione netta: Italia vs estero ({anno_di}) — MLD €",
            height=500,
            margin={"t": 40, "b": 120},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=df_est["regione"],
                y=df_est["quota_estero_pct"],
                text=df_est["quota_estero_pct"].apply(lambda x: f"{x:.2f}%"),
                textposition="outside",
            )
        )
        fig2.update_layout(
            title=f"Quota di produzione estera per regione ({anno_di})",
            height=450,
            margin={"t": 40, "b": 120},
            xaxis_tickangle=-45,
            yaxis_title="%",
        )
        st.plotly_chart(fig2, width="stretch")

        st.caption(
            "La quota estera è il rapporto tra produzione netta realizzata all'estero "
            "e produzione netta totale dichiarata dalla regione."
        )

st.caption("Dati: MEF — IRAP")
