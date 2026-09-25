#!/usr/bin/env python3
"""
Dichiarazioni Italia · Dashboard Streamlit
Le dichiarazioni fiscali italiane: IRPEF, IVA, IRAP, IRES.
"""

import streamlit as st
from lab_connectors.branding import apply_branding

st.set_page_config(
    page_title="Dichiarazioni Italia · Dashboard",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_branding(
    repo_name="dichiarazioni-italia",
    repo_url="https://github.com/dataciviclab/dichiarazioni-italia",
)

pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Analisi": [
        st.Page("pages/02_Regioni.py", title="Regioni", icon="🗺️"),
        st.Page("pages/03_Settori.py", title="Settori ATECO", icon="🏭"),
        st.Page("pages/04_Comuni_IRPEF.py", title="Comuni (IRPEF)", icon="🏘️"),
        st.Page("pages/05_Imprese_IRAP.py", title="Imprese (IRAP)", icon="🏢"),
    ],
    "Strumenti": [
        st.Page("pages/06_SQL.py", title="Query SQL", icon="🧪"),
    ],
}

pg = st.navigation(pages, position="sidebar")

st.sidebar.caption("Fonte: MEF — Dip. delle Finanze · CC BY")
st.sidebar.caption("[GitHub](https://github.com/dataciviclab/dichiarazioni-italia)")

pg.run()
