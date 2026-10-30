"""IRPEF — persone fisiche: chi paga, quanto reddito, dove.

Quattro viste sullo stesso perimetro:
- `irpef_imposta_tipologia` — imposta netta per tipologia di contribuente
- `irpef_calcolo_tipologia` — lorda, detrazioni e netta per tipologia e regione
- `irpef_comunale` — reddito e imposta per comune (~7.900 comuni)
- `mef_irpef_regionale` — contribuenti per regione e classe di reddito
"""

import plotly.graph_objects as go
import streamlit as st
from sources import (
    YEARS_IRPEF_CALCOLO,
    YEARS_IRPEF_COMUNI,
    YEARS_IRPEF_TIPOLOGIE,
    YEARS_MEF_IRPEF,
    fmt_eur,
    fmt_num,
    load_mart,
    load_mart_flat,
)

st.title("👤 IRPEF — persone fisiche")
st.markdown(
    "L'IRPEF pagata dalle persone fisiche: per **tipologia** di contribuente, per "
    "**comune** di residenza e per **classe di reddito**."
)

tab_tip, tab_comuni, tab_classi = st.tabs(["Tipologie", "Comuni", "Regioni e classi"])

# ══════════════════════════════════════════════════════════════════════
# TAB TIPOLOGIE — chi paga
# ══════════════════════════════════════════════════════════════════════
with tab_tip:
    anno_sel = st.selectbox(
        "Anno di presentazione",
        YEARS_IRPEF_TIPOLOGIE,
        index=len(YEARS_IRPEF_TIPOLOGIE) - 1,
        key="irpef_tip_year",
    )
    df = load_mart("irpef_imposta_tipologia", "mart_tipologie_anno", anno_sel)

    if df.empty:
        st.warning("Nessun dato disponibile.")
    else:
        df = df.sort_values("imposta_netta_eur", ascending=False)
        anno_di = int(df["anno"].max())
        tot = df["imposta_netta_eur"].sum()
        per_nome = df["tipologia"].str.contains("dipendente|pensionat", case=False, regex=True)
        quota_lavoro = df.loc[per_nome, "imposta_netta_eur"].sum() / tot * 100

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Contribuenti", fmt_num(df["numero_contribuenti"].sum()))
        with k2:
            st.metric("Imposta netta", fmt_eur(tot, compact=True))
        with k3:
            st.metric("Dipendenti + pensionati", f"{quota_lavoro:.1f}% dell'imposta")

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df["tipologia"],
                y=df["imposta_netta_eur"] / 1e9,
                text=df["quota_imposta_pct"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            )
        )
        fig.update_layout(
            title=f"Imposta netta IRPEF per tipologia ({anno_di}) — MLD €",
            height=520,
            margin={"t": 40, "b": 200},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=df["tipologia"],
                y=df["imposta_media_contribuente_eur"],
                name="Imposta media",
            )
        )
        fig2.update_layout(
            title=f"Imposta media per contribuente ({anno_di}) — €",
            height=480,
            margin={"t": 40, "b": 200},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig2, width="stretch")

        trend = load_mart_flat("irpef_imposta_tipologia", "mart_anno")
        if not trend.empty:
            fig3 = go.Figure()
            fig3.add_trace(
                go.Scatter(
                    x=trend["anno"],
                    y=trend["imposta_netta_eur"] / 1e9,
                    name="Imposta netta",
                    mode="lines+markers",
                )
            )
            fig3.update_layout(
                title="Imposta netta IRPEF totale — MLD €",
                height=420,
                margin={"t": 40},
                yaxis_title="MLD €",
            )
            st.plotly_chart(fig3, width="stretch")

        st.caption(
            "Le tipologie sono additive (la somma coincide con il `TOTALE` della "
            "fonte) tranne ad a.i. 2015, dove la fonte oscura una voce e il totale. "
            "La media divide per **tutti** i contribuenti della tipologia."
        )

        # ── Dal lordo al netto ────────────────────────────────────────────
        # irpef_imposta_tipologia espone solo la netta: qui si vede il passaggio
        # che manca, dalle sei viste "Calcolo dell'Irpef" (AETIP*0201).
        st.subheader("Dal lordo al netto: quanto restituiscono le detrazioni")
        anno_calc = st.selectbox(
            "Anno di presentazione",
            YEARS_IRPEF_CALCOLO,
            index=len(YEARS_IRPEF_CALCOLO) - 1,
            key="irpef_calc_year",
        )
        calc = load_mart_flat("irpef_calcolo_tipologia", "mart_tipologie_anno")
        if not calc.empty:
            calc = calc[calc["anno"] == anno_calc - 1]
            calc = calc.sort_values("imposta_lorda_eur", ascending=False)

        if calc.empty:
            st.info("Dati non disponibili per l'anno selezionato.")
        else:
            lorda = calc["imposta_lorda_eur"].sum()
            detr = calc["detrazioni_eur"].sum()
            netta = calc["imposta_netta_eur"].sum()

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Imposta lorda", fmt_eur(lorda, compact=True))
            with c2:
                st.metric(
                    "Detrazioni",
                    fmt_eur(detr, compact=True),
                    f"{detr / lorda * 100:.1f}% della lorda" if lorda else None,
                    delta_color="off",
                )
            with c3:
                st.metric("Imposta netta", fmt_eur(netta, compact=True))

            fig4 = go.Figure()
            for colonna, nome, colore in (
                ("imposta_lorda_eur", "Lorda", "#8a94a6"),
                ("detrazioni_eur", "Detrazioni", "#d1495b"),
                ("imposta_netta_eur", "Netta", "#2e86ab"),
            ):
                fig4.add_trace(
                    go.Bar(
                        x=calc["tipologia"],
                        y=calc[colonna] / 1e9,
                        name=nome,
                        marker_color=colore,
                    )
                )
            fig4.update_layout(
                title=(
                    f"Imposta lorda, detrazioni e netta per tipologia "
                    f"(a.i. {int(calc['anno'].max())}) — MLD €"
                ),
                barmode="group",
                height=520,
                margin={"t": 40, "b": 200},
                xaxis_tickangle=-45,
                yaxis_title="MLD €",
            )
            st.plotly_chart(fig4, width="stretch")

            fig5 = go.Figure()
            fig5.add_trace(
                go.Bar(
                    x=calc["tipologia"],
                    y=calc["incidenza_detrazioni_pct"],
                    text=calc["incidenza_detrazioni_pct"].apply(lambda x: f"{x:.0f}%"),
                    textposition="outside",
                    marker_color="#d1495b",
                )
            )
            fig5.update_layout(
                title="Quanto pesano le detrazioni sulla lorda, per tipologia — %",
                height=440,
                margin={"t": 40, "b": 200},
                xaxis_tickangle=-45,
                yaxis_title="%",
            )
            st.plotly_chart(fig5, width="stretch")

            st.caption(
                "⚠️ Le sei tipologie **non sono una partizione** dell'IRPEF: coprono "
                "circa il 94% dei contribuenti e il 99% del gettito. Le detrazioni "
                "valgono circa un terzo della lorda per i dipendenti e meno di un "
                "decimo per le partite IVA: il vantaggio di queste ultime sta "
                "nell'aliquota lorda, non nelle detrazioni."
            )

# ══════════════════════════════════════════════════════════════════════
# TAB COMUNI — dove
# ══════════════════════════════════════════════════════════════════════
with tab_comuni:
    anno_com = st.selectbox(
        "Anno di presentazione",
        YEARS_IRPEF_COMUNI,
        index=len(YEARS_IRPEF_COMUNI) - 1,
        key="irpef_com_year",
    )
    df_com = load_mart("irpef_comunale", "mart_comuni", anno_com)
    df_fasce = load_mart("irpef_comunale", "mart_fasce", anno_com)

    if df_com.empty:
        st.warning("Nessun dato comunale disponibile.")
    else:
        df_com = df_com[df_com["numero_contribuenti"] > 100].copy()
        # La fonte ha una riga aggregata dei comuni non riconosciuti (codice 0,
        # regione "Mancante/errata"): non è un comune, va esclusa dai conteggi.
        df_com = df_com[df_com["codice_istat_comune"] != "0"].copy()
        df_com = df_com.sort_values("reddito_medio_per_contribuente", ascending=False)

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Comuni", fmt_num(len(df_com)))
        with k2:
            st.metric(
                "Reddito medio nazionale",
                fmt_eur(df_com["media_nazionale_reddito"].iloc[0]),
            )
        with k3:
            st.metric(
                "Fascia ELEVATO", f"{(df_com['fascia_reddito'] == 'ELEVATO').sum()} comuni"
            )
        with k4:
            st.metric(
                "Fascia BASSO", f"{(df_com['fascia_reddito'] == 'BASSO').sum()} comuni"
            )

        st.subheader("Contribuenti per fascia di reddito")
        if not df_fasce.empty:
            fascia_labels = [
                "fascia_zero",
                "fascia_0_10k",
                "fascia_10_15k",
                "fascia_15_26k",
                "fascia_26_55k",
                "fascia_55_75k",
                "fascia_75_120k",
                "fascia_oltre_120k",
            ]
            fascia_names = [
                "< 0",
                "0-10k",
                "10-15k",
                "15-26k",
                "26-55k",
                "55-75k",
                "75-120k",
                "> 120k",
            ]
            tot_fasce = [df_fasce[f].sum() for f in fascia_labels]
            totale = sum(tot_fasce)

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=fascia_names,
                    y=[t / 1e6 for t in tot_fasce],
                    text=[f"{t / 1e6:.1f}M" for t in tot_fasce],
                    textposition="outside",
                )
            )
            fig.update_layout(
                title=f"Contribuenti IRPEF per fascia di reddito ({anno_com})",
                xaxis_title="Fascia reddito complessivo",
                yaxis_title="Milioni di contribuenti",
                height=400,
                margin={"t": 40, "b": 40},
            )
            st.plotly_chart(fig, width="stretch")

            kp1, kp2, kp3 = st.columns(3)
            with kp1:
                st.metric(
                    "Fascia più popolosa",
                    fascia_names[tot_fasce.index(max(tot_fasce))],
                    f"{max(tot_fasce) / 1e6:.1f}M ({max(tot_fasce) / totale * 100:.1f}%)",
                )
            with kp2:
                oltre = sum(tot_fasce[5:])
                st.metric(
                    "Reddito > €55k",
                    f"{oltre / 1e6:.1f}M",
                    f"{oltre / totale * 100:.1f}% del totale",
                )
            with kp3:
                st.metric(
                    "Rapporto alta/bassa",
                    f"{df_fasce['rapporto_alta_bassa'].mean():.2f}",
                    help="Ratio contribuenti >55k / <10k per provincia",
                )

        st.subheader("Distanza dalla media nazionale")
        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=df_com.head(30)["denominazione_comune"],
                y=df_com.head(30)["distanza_media_nazionale_pct"],
                text=df_com.head(30)["distanza_media_nazionale_pct"].apply(
                    lambda x: f"{x:+.1f}%"
                ),
                textposition="outside",
            )
        )
        fig2.update_layout(
            title="Top 30 comuni — distanza % dalla media nazionale",
            height=450,
            margin={"t": 40, "b": 120},
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig2, width="stretch")

        st.subheader("Dettaglio comune")
        comuni = sorted(df_com["denominazione_comune"].unique())
        comune_sel = st.selectbox("Comune", comuni, key="irpef_sel_comune")
        row = df_com[df_com["denominazione_comune"] == comune_sel].iloc[0]

        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.metric("Reddito medio", fmt_eur(row["reddito_medio_per_contribuente"]))
        with rc2:
            st.metric("Media nazionale", fmt_eur(row["media_nazionale_reddito"]))
        with rc3:
            st.metric("Fascia", row["fascia_reddito"])
        with rc4:
            st.metric("Percentile", f"{row['percentile_nazionale_reddito'] * 100:.1f}%")

        st.metric(
            "Distanza dalla media nazionale",
            f"{row['distanza_media_nazionale_pct']:+.1f}%",
            delta=f"{'Sopra' if row['distanza_media_nazionale_pct'] > 0 else 'Sotto'} la media",
        )

        with st.expander("Top 50 comuni per reddito medio"):
            st.dataframe(
                df_com[
                    [
                        "denominazione_comune",
                        "sigla_provincia",
                        "regione",
                        "numero_contribuenti",
                        "reddito_medio_per_contribuente",
                        "fascia_reddito",
                        "percentile_nazionale_reddito",
                    ]
                ].head(50),
                width="stretch",
                hide_index=True,
            )

        st.caption(
            "Sono esclusi i comuni con meno di 100 contribuenti. Il reddito è quello "
            "**imponibile medio per contribuente**."
        )

# ══════════════════════════════════════════════════════════════════════
# TAB REGIONI E CLASSI — mef_irpef_regionale
# ══════════════════════════════════════════════════════════════════════
with tab_classi:
    anno_cl = st.selectbox(
        "Anno di presentazione",
        YEARS_MEF_IRPEF,
        index=len(YEARS_MEF_IRPEF) - 1,
        key="mef_irpef_year",
    )
    df_cl = load_mart("mef_irpef_regionale", "irpef_regione_classe", anno_cl)

    if df_cl.empty:
        st.warning("Nessun dato disponibile.")
    else:
        anno_di = int(df_cl["anno"].max())
        tot_contr = df_cl["totale_contribuenti"].sum()
        tot_inf = df_cl["contribuenti_fascia_inferiore"].sum()
        tot_sup = df_cl["contribuenti_fascia_superiore"].sum()
        pct_inf = tot_inf / tot_contr * 100 if tot_contr else 0
        pct_sup = tot_sup / tot_contr * 100 if tot_contr else 0

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Contribuenti", fmt_num(tot_contr))
        with k2:
            st.metric("Reddito ≤ 0", fmt_num(tot_inf), f"{pct_inf:.2f}% del totale")
        with k3:
            st.metric(
                "Reddito ≥ 10.000 €", fmt_num(tot_sup), f"{pct_sup:.2f}% del totale"
            )

        d = df_cl.sort_values("pct_fascia_inferiore", ascending=False)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=d["regione"],
                y=d["pct_fascia_inferiore"],
                name="Reddito ≤ 0",
                text=d["pct_fascia_inferiore"].apply(lambda x: f"{x:.1f}%"),
                textposition="outside",
            )
        )
        fig.add_trace(
            go.Bar(
                x=d["regione"],
                y=d["pct_fascia_superiore"],
                name="Reddito ≥ 10.000 €",
            )
        )
        fig.update_layout(
            barmode="group",
            title=f"Le due code della distribuzione del reddito per regione ({anno_di}) — %",
            height=520,
            margin={"t": 40, "b": 140},
            xaxis_tickangle=-45,
            yaxis_title="%",
            legend={"orientation": "h", "y": -0.25},
        )
        st.plotly_chart(fig, width="stretch")

        st.caption(
            "Fonte: `REG_tipo_reddito`, 34 classi di reddito (21 regioni). Sono "
            "mostrate le due code: reddito **≤ 0** (3 classi) e reddito **≥ 10.000 €** "
            "(20 classi). Le 11 classi intermedie (0–10.000 €) non entrano in nessuna "
            "delle due, quindi le due quote non sommano a 100."
        )

st.caption("Dati: MEF — Dipartimento delle Finanze · IRPEF")
