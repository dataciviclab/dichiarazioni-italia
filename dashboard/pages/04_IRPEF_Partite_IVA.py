"""Titolari di partita IVA (ABPF) — regimi agevolati, reddito e imposta, regioni.

Un dataset (`abpf_titolari_piva_regione`) con due mart: `mart_anno` (nazionale
multi-anno) e `mart_regione_anno` (regionale).
"""

import plotly.graph_objects as go
import streamlit as st
from sources import YEARS_ABPF, fmt_eur, fmt_num, load_mart, load_mart_flat

st.title("🧾 IRPEF — titolari di partita IVA")
st.markdown(
    "Le **persone fisiche con partita IVA** (modello ABPF): redditi, imposta e "
    "regimi agevolati. Non include chi non ha la partita IVA né le società."
)

tab_regimi, tab_reddito, tab_regioni = st.tabs(
    ["Regimi agevolati", "Reddito e imposta", "Regioni"]
)

trend = load_mart_flat("abpf_titolari_piva_regione", "mart_anno")

# ══════════════════════════════════════════════════════════════════════
# TAB REGIMI AGEVOLATI
# ══════════════════════════════════════════════════════════════════════
with tab_regimi:
    if trend.empty:
        st.warning("Nessun dato disponibile.")
    else:
        ultimo = trend.sort_values("anno").iloc[-1]
        anno_di = int(ultimo["anno"])
        tot = ultimo["reddito_complessivo_eur"]
        forf = ultimo["reddito_forfetario_eur"]
        vant = ultimo["reddito_vantaggio_eur"]

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Titolari di partita IVA", fmt_num(ultimo["numero_titolari"]))
        with k2:
            st.metric(
                "Reddito da regime forfetario",
                fmt_eur(forf, compact=True),
                delta=f"{forf / tot * 100:.1f}% del complessivo" if tot else None,
                delta_color="off",
            )
        with k3:
            st.metric(
                "Reddito da regime di vantaggio",
                fmt_eur(vant, compact=True),
                delta=f"{vant / tot * 100:.2f}% del complessivo" if tot else None,
                delta_color="off",
            )

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=trend["anno"],
                y=trend["reddito_forfetario_eur"] / 1e9,
                name="Regime forfetario",
                mode="lines+markers",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=trend["anno"],
                y=trend["reddito_vantaggio_eur"] / 1e9,
                name="Regime di vantaggio",
                mode="lines+markers",
            )
        )
        fig.update_layout(
            title="Il forfetario esplode, il regime di vantaggio si esaurisce — MLD €",
            height=460,
            margin={"t": 40},
            yaxis_title="MLD €",
            legend={"orientation": "h", "y": -0.2},
        )
        st.plotly_chart(fig, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=trend["anno"],
                y=trend["reddito_forfetario_eur"] / trend["reddito_complessivo_eur"] * 100,
                name="Quota forfetario",
                mode="lines+markers",
            )
        )
        fig2.update_layout(
            title="Quota del regime forfetario sul reddito complessivo dei titolari",
            height=420,
            margin={"t": 40},
            yaxis_title="%",
        )
        st.plotly_chart(fig2, width="stretch")

        st.markdown(
            f"Ad a.i. **{anno_di}** il regime forfetario vale **{fmt_eur(forf, compact=True)}** "
            f"({forf / tot * 100:.1f}% del reddito complessivo dei titolari) contro "
            f"**{fmt_eur(vant, compact=True)}** del regime di vantaggio. Il dataset copre dal "
            "a.i. 2015 perché da lì la fonte pubblica le due voci."
        )

# ══════════════════════════════════════════════════════════════════════
# TAB REDDITO E IMPOSTA
# ══════════════════════════════════════════════════════════════════════
with tab_reddito:
    if trend.empty:
        st.warning("Nessun dato disponibile.")
    else:
        t = trend.sort_values("anno")
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=t["anno"], y=t["reddito_complessivo_eur"] / 1e9,
                name="Reddito complessivo", mode="lines+markers",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=t["anno"], y=t["reddito_imponibile_eur"] / 1e9,
                name="Reddito imponibile", mode="lines+markers",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=t["anno"], y=t["imposta_netta_eur"] / 1e9,
                name="Imposta netta", mode="lines+markers",
            )
        )
        fig.update_layout(
            title="Reddito e imposta dei titolari di partita IVA — MLD €",
            height=460,
            margin={"t": 40},
            yaxis_title="MLD €",
            legend={"orientation": "h", "y": -0.2},
        )
        st.plotly_chart(fig, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=t["anno"], y=t["aliquota_media_pct"],
                name="Aliquota media effettiva", mode="lines+markers",
            )
        )
        fig2.update_layout(
            title="Aliquota media effettiva (imposta netta / reddito imponibile)",
            height=420,
            margin={"t": 40},
            yaxis_title="%",
        )
        st.plotly_chart(fig2, width="stretch")

        ultimo = t.iloc[-1]
        st.markdown(
            f"Ad a.i. **{int(ultimo['anno'])}**: **{fmt_num(ultimo['numero_titolari'])}** "
            f"titolari, **{fmt_eur(ultimo['reddito_complessivo_eur'], compact=True)}** di reddito "
            f"complessivo e **{fmt_eur(ultimo['imposta_netta_eur'], compact=True)}** di imposta netta."
        )
        st.caption(
            "⚠️ `reddito_complessivo` è il reddito **totale della persona** (include "
            "anche lavoro dipendente e pensioni), non la somma delle voci per tipo di "
            "reddito. L'aliquota media è calcolata sul **reddito imponibile**, non sul "
            "complessivo."
        )

# ══════════════════════════════════════════════════════════════════════
# TAB REGIONI
# ══════════════════════════════════════════════════════════════════════
with tab_regioni:
    anno_sel = st.selectbox(
        "Anno di presentazione", YEARS_ABPF, index=len(YEARS_ABPF) - 1, key="abpf_year"
    )
    df = load_mart("abpf_titolari_piva_regione", "mart_regione_anno", anno_sel)
    if df.empty:
        st.warning("Nessun dato disponibile.")
    else:
        df = df.sort_values("reddito_complessivo_eur", ascending=False)
        anno_di = int(df["anno"].max())

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df["regione"], y=df["reddito_complessivo_eur"] / 1e9,
                text=df["quota_reddito_pct"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside", name="Reddito complessivo",
            )
        )
        fig.update_layout(
            title=f"Reddito complessivo dei titolari per regione ({anno_di}) — MLD €",
            height=520, margin={"t": 40, "b": 140}, xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(x=df["regione"], y=df["aliquota_media_pct"], name="Aliquota media")
        )
        fig2.update_layout(
            title=f"Aliquota media effettiva per regione ({anno_di})",
            height=460, margin={"t": 40, "b": 140}, xaxis_tickangle=-45, yaxis_title="%",
        )
        st.plotly_chart(fig2, width="stretch")

        st.caption(
            "Le regioni sono 21: Trentino-Alto Adige è diviso in P.A. Trento e Bolzano, "
            "entrambe con codice regione `04`."
        )

st.caption("Dati: MEF — Dichiarazioni, Persone fisiche titolari di partita IVA (ABPF)")
