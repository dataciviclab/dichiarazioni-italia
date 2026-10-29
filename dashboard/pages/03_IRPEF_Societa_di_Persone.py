"""Società di persone (ACSP) — gerarchia per tipologia, distribuzione, regioni.

Cinque dataset: `acsp_tutte_regione` (aggregato), `acsp_imprese_regione`,
`acsp_professionisti_regione` (le due tipologie maggiori), e le due viste per
classe di reddito e di volume d'affari.
"""

import plotly.graph_objects as go
import streamlit as st
from sources import (
    YEARS_ACSP,
    YEARS_ACSP_TIPOLOGIE,
    fmt_eur,
    fmt_num,
    load_mart,
    load_mart_flat,
)

st.title("👥 IRPEF — società di persone")
st.markdown(
    "Il reddito dichiarato dalle **società di persone** (tassato in capo ai soci): "
    "la gerarchia per tipologia, la distribuzione per classe di reddito e di volume "
    "d'affari, il dettaglio regionale."
)

tab_ger, tab_reddito, tab_volume, tab_regioni = st.tabs(
    ["Tipologie", "Classi di reddito", "Classi di volume d'affari", "Regioni"]
)

# ══════════════════════════════════════════════════════════════════════
# TAB TIPOLOGIE — la gerarchia
# ══════════════════════════════════════════════════════════════════════
with tab_ger:
    anno_sel = st.selectbox(
        "Anno di presentazione",
        YEARS_ACSP_TIPOLOGIE,
        index=len(YEARS_ACSP_TIPOLOGIE) - 1,
        key="acsp_tip_year",
    )
    tutte = load_mart("acsp_tutte_regione", "mart_regione_anno", anno_sel)
    imprese = load_mart("acsp_imprese_regione", "mart_regione_anno", anno_sel)
    prof = load_mart("acsp_professionisti_regione", "mart_regione_anno", anno_sel)

    if tutte.empty:
        st.warning("Nessun dato ACSP disponibile.")
    else:
        anno_di = int(tutte["anno"].max())
        soc_tutte = tutte["numero_societa"].sum()
        red_tutte = tutte["totale_reddito_eur"].sum()
        soc_imp = imprese["numero_imprenditori"].sum() if not imprese.empty else 0
        red_imp = imprese["totale_reddito_eur"].sum() if not imprese.empty else 0
        soc_pro = prof["numero_societa"].sum() if not prof.empty else 0
        red_pro = prof["totale_reddito_eur"].sum() if not prof.empty else 0
        soc_altre = soc_tutte - soc_imp - soc_pro
        red_altre = red_tutte - red_imp - red_pro

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Società dichiaranti", fmt_num(soc_tutte))
        with k2:
            st.metric("Reddito dichiarato", fmt_eur(red_tutte, compact=True))
        with k3:
            st.metric(
                "Reddito medio per società",
                fmt_eur(red_tutte / soc_tutte, compact=True) if soc_tutte else "—",
            )

        etichette = ["Imprese", "Professionisti", "Altre tipologie"]
        soc = [soc_imp, soc_pro, soc_altre]
        red = [red_imp, red_pro, red_altre]

        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(
                go.Pie(labels=etichette, values=soc, hole=0.45, textinfo="label+percent")
            )
            fig.update_layout(
                title=f"Società per tipologia ({anno_di})", height=380, margin={"t": 40}
            )
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig2 = go.Figure(
                go.Pie(labels=etichette, values=red, hole=0.45, textinfo="label+percent")
            )
            fig2.update_layout(
                title=f"Reddito dichiarato per tipologia ({anno_di})",
                height=380,
                margin={"t": 40},
            )
            st.plotly_chart(fig2, width="stretch")

        st.markdown(
            "La scomposizione per tipologia pubblicata copre le due voci maggiori "
            "(imprese e professionisti). Le voci minori — agricoltori e non titolari "
            "di partita IVA — restano in **Altre tipologie**: non sono pubblicate "
            "come dataset dedicato in questo repo."
        )
        st.caption(
            "Il dettaglio per tipologia è mostrato "
            f"**dal {YEARS_ACSP_TIPOLOGIE[0]}**: è il primo anno coperto anche "
            "dalla vista dei professionisti."
        )
        st.caption(
            "⚠️ Le colonne delle viste ACSP **non sono additive**: ogni voce è "
            "dichiarata su una riga diversa del modello. I totali qui mostrati sono "
            "somme di righe-regione, non somme di colonne."
        )

# ══════════════════════════════════════════════════════════════════════
# TAB CLASSI DI REDDITO
# ══════════════════════════════════════════════════════════════════════
with tab_reddito:
    anno_red = st.selectbox(
        "Anno di presentazione",
        YEARS_ACSP,
        index=len(YEARS_ACSP) - 1,
        key="acsp_red_year",
    )
    df = load_mart("acsp_tutte_classi_reddito", "mart_classe_reddito_anno", anno_red)
    if df.empty:
        st.warning("Nessun dato disponibile.")
    else:
        df = df.sort_values("codice")
        anno_di = int(df["anno"].max())
        tot_soc = df["numero_societa"].sum()
        tot_red = df["totale_reddito_eur"].sum()

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["classe_reddito"], y=df["numero_societa"], name="Società"))
        fig.update_layout(
            title=f"Società per classe di reddito dichiarato ({anno_di})",
            height=480,
            margin={"t": 40, "b": 160},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(x=df["classe_reddito"], y=df["totale_reddito_eur"] / 1e9, name="Reddito (mld €)")
        )
        fig2.update_layout(
            title=f"Reddito dichiarato per classe ({anno_di}) — MLD €",
            height=480,
            margin={"t": 40, "b": 160},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig2, width="stretch")

        top = df.loc[df["totale_reddito_eur"].idxmax()]
        st.markdown(
            f"**{fmt_num(tot_soc)}** società dichiarano **{fmt_eur(tot_red, compact=True)}** "
            f"in totale. La classe **{top['classe_reddito']}** raccoglie il "
            f"{top['numero_societa'] / tot_soc * 100:.1f}% delle società ma il "
            f"{top['totale_reddito_eur'] / tot_red * 100:.1f}% del reddito dichiarato."
        )
        st.caption(
            "Le classi a reddito nullo o negativo riportano `totale_reddito_eur = 0`: "
            "le perdite dichiarate stanno in una colonna separata (`totale_perdita_eur`) "
            "e non entrano nel reddito. La loro quota di reddito è quindi zero."
        )

# ══════════════════════════════════════════════════════════════════════
# TAB CLASSI DI VOLUME D'AFFARI
# ══════════════════════════════════════════════════════════════════════
with tab_volume:
    anno_vol = st.selectbox(
        "Anno di presentazione",
        YEARS_ACSP,
        index=len(YEARS_ACSP) - 1,
        key="acsp_vol_year",
    )
    df = load_mart("acsp_tutte_classi_volume", "mart_classe_volume_affari_anno", anno_vol)
    if df.empty:
        st.warning("Nessun dato disponibile.")
    else:
        df = df.sort_values("codice")
        anno_di = int(df["anno"].max())

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["classe_volume_affari"], y=df["numero_societa"]))
        fig.update_layout(
            title=f"Società per classe di volume d'affari ({anno_di})",
            height=480,
            margin={"t": 40, "b": 160},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df["classe_volume_affari"], y=df["totale_reddito_eur"] / 1e9))
        fig2.update_layout(
            title=f"Reddito dichiarato per classe di volume d'affari ({anno_di}) — MLD €",
            height=480,
            margin={"t": 40, "b": 160},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig2, width="stretch")

        st.caption(
            "La prima classe è **assenza di dichiarazione IVA**: non è un volume "
            "d'affari pari a zero. Alcune celle sono oscurate dalla fonte (`***` → NULL)."
        )

# ══════════════════════════════════════════════════════════════════════
# TAB REGIONI
# ══════════════════════════════════════════════════════════════════════
with tab_regioni:
    anno_reg = st.selectbox(
        "Anno di presentazione",
        YEARS_ACSP,
        index=len(YEARS_ACSP) - 1,
        key="acsp_reg_year",
    )
    df = load_mart("acsp_tutte_regione", "mart_regione_anno", anno_reg)
    if df.empty:
        st.warning("Nessun dato disponibile.")
    else:
        df = df.sort_values("totale_reddito_eur", ascending=False)
        anno_di = int(df["anno"].max())

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df["regione"],
                y=df["totale_reddito_eur"] / 1e9,
                text=df["quota_reddito_pct"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            )
        )
        fig.update_layout(
            title=f"Reddito dichiarato per regione ({anno_di}) — MLD €",
            height=520,
            margin={"t": 40, "b": 140},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")

        trend = load_mart_flat("acsp_tutte_regione", "mart_anno")
        if not trend.empty:
            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=trend["anno"],
                    y=trend["numero_societa"] / 1e3,
                    name="Società (migliaia)",
                    mode="lines+markers",
                    yaxis="y",
                )
            )
            fig2.add_trace(
                go.Scatter(
                    x=trend["anno"],
                    y=trend["reddito_medio_societa_eur"],
                    name="Reddito medio per società (€)",
                    mode="lines+markers",
                    yaxis="y2",
                )
            )
            fig2.update_layout(
                title="Meno società, più grandi",
                height=440,
                margin={"t": 40},
                yaxis={"title": "Società (migliaia)"},
                yaxis2={"title": "Reddito medio (€)", "overlaying": "y", "side": "right"},
                legend={"orientation": "h", "y": -0.2},
            )
            st.plotly_chart(fig2, width="stretch")
            primo = trend.sort_values("anno").iloc[0]
            ultimo = trend.sort_values("anno").iloc[-1]
            variazione = abs(ultimo["numero_societa"] / primo["numero_societa"] - 1) * 100
            st.caption(
                f"Tra a.i. {int(primo['anno'])} e a.i. {int(ultimo['anno'])} le società "
                f"calano del {variazione:.0f}% "
                f"({fmt_num(primo['numero_societa'])} → {fmt_num(ultimo['numero_societa'])}), "
                f"mentre il reddito medio per società sale da "
                f"{fmt_num(primo['reddito_medio_societa_eur'])} € a "
                f"{fmt_num(ultimo['reddito_medio_societa_eur'])} €. "
                "⚠️ Il reddito include l'anomalia della fonte ad a.i. 2017."
            )

st.caption("Dati: MEF — Dichiarazioni, Società di persone (ACSP)")
