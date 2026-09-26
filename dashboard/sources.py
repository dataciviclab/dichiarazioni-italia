"""Fonti dati per la dashboard Dichiarazioni Italia.

Multi-dataset: IVA regionale, IRPEF comunale, IVA settori, MEF IRPEF regionale,
IRES redditi, IRAP VP regime, IRAP Italia/Estero.

Pattern: load_mart_table per singolo anno, query_clean per aggregazioni multi-anno.
Tutti i dati risolvono su GCS quando local_root non è rilevabile.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from lab_connectors.duckdb import queries as _dq
from lab_connectors.duckdb.queries import (
    load_mart_table as _load_mart_table,
    query_clean as _query_clean,
)
from lab_connectors.formatters import fmt_eur, fmt_num, fmt_pct
from lab_connectors.registry import load_registry

# Forza risoluzione GCS
_dq._LOCAL_ROOT = None

PREFIX = "dichiarazioni-italia/"
YEARS = list(range(2015, 2025))

_registry = load_registry(
    Path(__file__).parent.parent / "registry" / "registry.json"
)


def _q(slug: str, sql: str, year: int = 2024):
    return _query_clean(slug, sql, [year], prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart(slug: str, table: str, year: int = 2024):
    """Carica un singolo mart table da GCS (cached 1h)."""
    return _load_mart_table(slug, table, year, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart_all(slug: str, table: str, years: list[int] = None):
    """Carica un mart table per tutti gli anni disponibili e fa UNION."""
    if years is None:
        years = YEARS
    frames = []
    for y in years:
        try:
            df = _load_mart_table(slug, table, y, prefix=PREFIX)
            if not df.empty:
                frames.append(df)
        except Exception:
            continue
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


@st.cache_data(ttl=3600, show_spinner=False)
def query_multi(slug: str, sql: str, years: list[int] = None):
    """Aggrega multi-anno dal clean layer via query_clean."""
    if years is None:
        years = YEARS
    return _query_clean(slug, sql, years, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def query_iva_regionale(sql: str, year: int = 2024):
    return _q("iva_regionale", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_iva_settori(sql: str, year: int = 2024):
    return _q("iva_sez_attivita", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_irpef_comunale(sql: str, year: int = 2024):
    return _q("irpef_comunale", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_mef_irpef(sql: str, year: int = 2025):
    return _q("mef_irpef_regionale", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_ires(sql: str, year: int = 2024):
    return _q("ires_redditi_regione", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_irap_regime(sql: str, year: int = 2024):
    return _q("irap_vp_regime", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_irap_estero(sql: str, year: int = 2024):
    return _q("irap_italia_estero", sql, year)


@st.cache_data(ttl=3600, show_spinner=False)
def query_sql(slug: str, sql: str, year: int = 2024):
    """Generic query su qualsiasi dataset."""
    return _q(slug, sql, year)


# ── Formattazione custom ──────────────────────────────────────────────

def fmt_trilioni(v: float) -> str:
    """Formatta in TRLN, MLD, MLN con 1 decimale."""
    if v is None or pd.isna(v):
        return "—"
    av = abs(v)
    if av >= 1e12:
        return f"€{v/1e12:.1f} T"
    if av >= 1e9:
        return f"€{v/1e9:.1f} B"
    if av >= 1e6:
        return f"€{v/1e6:.0f} M"
    if av >= 1e3:
        return f"€{v/1e3:.0f} K"
    return f"€{v:.0f}"


def fmt_delta_pct(val: float) -> str:
    """Formatta delta con segno."""
    if val is None or pd.isna(val):
        return "—"
    return f"{val:+.1f}%"
