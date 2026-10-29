#!/usr/bin/env python3
"""
Dichiarazioni Italia · Dashboard Streamlit
Le dichiarazioni fiscali italiane: IVA, IRPEF, IRAP, IRES.
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

# Una pagina per imposta: il territorio è un filtro dentro la pagina, non una pagina.
pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
        st.Page("pages/08_Query_SQL.py", title="Query SQL", icon="🧪"),
    ],
    "Per imposta": [
        st.Page("pages/02_IRPEF_Persone_Fisiche.py", title="IRPEF — persone fisiche", icon="👤"),
        st.Page(
            "pages/03_IRPEF_Societa_di_Persone.py",
            title="IRPEF — società di persone",
            icon="👥",
        ),
        st.Page("pages/04_IRPEF_Partite_IVA.py", title="IRPEF — partite IVA", icon="🧾"),
        st.Page("pages/05_IVA.py", title="IVA", icon="🧮"),
        st.Page("pages/06_IRAP.py", title="IRAP", icon="🏢"),
        st.Page("pages/07_IRES.py", title="IRES", icon="🏛️"),
    ],
}

pg = st.navigation(pages, position="sidebar")

st.sidebar.caption("Fonte: MEF — Dip. delle Finanze · CC BY")
st.sidebar.caption("[GitHub](https://github.com/dataciviclab/dichiarazioni-italia)")

pg.run()
