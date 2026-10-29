"""Fonti dati per la dashboard Dichiarazioni Italia.

Un dataset = una vista MEF. Due forme di mart:

- **per anno** — ``{slug}/{anno_cartella}/{table}.parquet`` → ``load_mart``
- **flat** (multi-anno, alla radice) — ``{slug}/{table}.parquet`` → ``load_mart_flat``

L'anno passato a ``load_mart`` è l'**anno di presentazione** (nome della
cartella), che NON coincide con l'anno d'imposta (colonna ``anno``) mostrato
nei grafici: vedi ``_folders`` per la convenzione, verificata dataset per
dataset.

Tutti i dati risolvono su GCS quando ``local_root`` non è rilevabile.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from lab_connectors.duckdb import queries as _dq
from lab_connectors.duckdb.queries import (
    load_mart_flat as _load_mart_flat,
    load_mart_table as _load_mart_table,
    query_clean as _query_clean,
    years_from_registry,
)
from lab_connectors.formatters import fmt_eur, fmt_num, fmt_pct
from lab_connectors.registry import load_registry

# Forza risoluzione GCS
_dq._LOCAL_ROOT = None

PREFIX = "dichiarazioni-italia/"

_registry = load_registry(Path(__file__).parent.parent / "registry" / "registry.json")


def _folders(slug: str, offset: int) -> list[int]:
    """Anni-cartella disponibili = intervallo del registry + ``offset``.

    ``offset`` = cartella − ``period``. La convenzione **non è uniforme** nel
    registry: verificato il 2026-10-29 confrontando il nome della cartella con
    la colonna ``anno`` (o ``anno_di_imposta``) del mart.

    +1 = URL MEF con anno di presentazione (la maggior parte dei dataset)
     0 = cartella = anno d'imposta (``irpef_comunale``, ``mef_irpef_regionale``)
     0 = ``iva_sez_attivita``, l'unico con ``period`` già in anni-cartella
    """
    anni = years_from_registry(_registry, slug=slug)
    if not anni:
        return []
    return list(range(min(anni) + offset, max(anni) + offset + 1))


def _comuni(*liste: list[int]) -> list[int]:
    """Anni presenti in tutte le liste (intersezione)."""
    if not liste:
        return []
    return sorted(set.intersection(*(set(lista) for lista in liste)))


# ── Anni-cartella per dataset ─────────────────────────────────────────
YEARS_IVA = _folders("iva_regionale", 1)                      # a.i. 2014-2024
YEARS_IVA_SETTORI = _folders("iva_sez_attivita", 0)            # a.i. 2014-2024
YEARS_IRPEF_TIPOLOGIE = _folders("irpef_imposta_tipologia", 1)  # a.i. 2012-2024
YEARS_IRPEF_COMUNI = _folders("irpef_comunale", 0)             # a.i. 2015-2024
YEARS_MEF_IRPEF = _folders("mef_irpef_regionale", 0)           # a.i. 2017-2025
YEARS_ACSP = _folders("acsp_tutte_regione", 1)                 # a.i. 2013-2024
YEARS_ACSP_TIPOLOGIE = _comuni(                                # a.i. 2018-2024
    YEARS_ACSP,
    _folders("acsp_imprese_regione", 1),
    _folders("acsp_professionisti_regione", 1),
)
YEARS_ABPF = _folders("abpf_titolari_piva_regione", 1)         # a.i. 2015-2024
YEARS_IRAP = _folders("irap_imposta_regione", 1)               # a.i. 2014-2023
YEARS_IRES = _folders("ires_redditi_regione", 1)               # a.i. 2014-2023


# ── Loader ────────────────────────────────────────────────────────────

def _q(slug: str, sql: str, year: int):
    return _query_clean(slug, sql, [year], prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart(slug: str, table: str, year: int):
    """Mart di un singolo anno-cartella (cached 1h)."""
    return _load_mart_table(slug, table, year, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart_all(slug: str, table: str, years: list[int]):
    """Mart per-anno unito su più anni (UNIONByName)."""
    frames = []
    for y in years:
        try:
            df = _load_mart_table(slug, table, y, prefix=PREFIX)
        except Exception:
            continue
        if not df.empty:
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart_flat(slug: str, table: str):
    """Mart multi-anno flat: ``{slug}/{table}.parquet``, una riga per anno."""
    return _load_mart_flat(slug, table, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def query_multi(slug: str, sql: str, years: list[int]):
    """Aggrega multi-anno dal clean layer."""
    return _query_clean(slug, sql, years, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def query_clean(slug: str, sql: str, year: int):
    """Query sul clean layer di un singolo anno."""
    return _q(slug, sql, year)


def dataset_period(slug: str) -> dict[str, int]:
    """Periodo (anni d'imposta) di un dataset pubblicato, dal registry."""
    for ds in _registry.datasets:
        if getattr(ds, "slug", None) != slug:
            continue
        periodo = getattr(ds, "period", {})
        if isinstance(periodo, dict):
            return {"start": int(periodo["start"]), "end": int(periodo["end"])}
        return {"start": int(periodo.start), "end": int(periodo.end)}
    return {}
