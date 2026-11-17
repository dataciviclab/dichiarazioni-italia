#!/usr/bin/env python3
"""Audit delle etichette `regione` nei clean: la serie deve usare lo stesso set.

Copre una classe di bug che nessun controllo sul volume vede: **la stessa
entità scritta in modi diversi tra file annuali**. Ogni anno resta a 21
regioni, quindi un conteggio per anno passa; il drift si vede solo confrontando
l'insieme delle etichette sull'intera serie.

Caso reale (2026-11): `abpf_titolari_piva_regione` scriveva
"Trentino Alto Adige (Prov. Aut. Bolzano)" nel file 2016 e
"Trentino Alto Adige (P.A. Bolzano)" dal 2017. 21 etichette per anno, 23 sulla
serie: raggruppando per nome, Bolzano diventava due serie.

Le eccezioni volute — etichette che *devono* cambiare tra anni e sono già
gestite altrove — stanno in `scripts/audit_region_labels_allow.json`, con gli
anni in cui sono ammesse e la motivazione. Un'eccezione non dichiarata, o
un'etichetta che ricompare fuori dagli anni dichiarati, fa fallire l'audit.

Uso:
    python scripts/audit_region_labels.py --root out/data/clean
    python scripts/audit_region_labels.py --no-fail          # solo report

Exit code 0 se tutte le serie sono stabili (o hanno solo deriva dichiarata), 1
altrimenti.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import duckdb

YEAR_COLUMNS = ("anno", "anno_di_imposta")
DEFAULT_ALLOW = Path(__file__).with_name("audit_region_labels_allow.json")


def load_allow(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _parquet_paths(files: list[Path]) -> str:
    return ", ".join("'" + str(f).replace("'", "''") + "'" for f in files)


def _columns(con: duckdb.DuckDBPyConnection, files: list[Path]) -> set[str]:
    """Colonne dell'unione dei file: `regione` può mancare in alcune annualità."""
    rows = con.execute(
        f"describe select * from read_parquet([{_parquet_paths(files)}], union_by_name = true)"
    ).fetchall()
    return {row[0] for row in rows}


def _labels_by_year(
    con: duckdb.DuckDBPyConnection,
    files: list[Path],
    col: str,
    year_col: str,
) -> dict[int, set[str]]:
    rows = con.execute(
        f"""
        select distinct {year_col} as anno, {col} as etichetta
        from read_parquet([{_parquet_paths(files)}], union_by_name = true)
        where {col} is not null and {year_col} is not null
        """
    ).fetchall()
    years: dict[int, set[str]] = defaultdict(set)
    for anno, etichetta in rows:
        years[int(anno)].add(str(etichetta))
    return years


def _span(anni: list[int]) -> str:
    """'2015-2017' se contigui, altrimenti gli anni espliciti (con i buchi)."""
    if len(anni) == 1:
        return str(anni[0])
    if anni == list(range(anni[0], anni[-1] + 1)):
        return f"{anni[0]}-{anni[-1]}"
    return ", ".join(str(a) for a in anni)


def _is_consented(present: list[int], ranges: list[list[int]]) -> bool:
    """Tutti gli anni di presenza devono stare in almeno uno degli intervalli."""
    return all(any(lo <= a <= hi for lo, hi in ranges) for a in present)


def audit(root: Path, col: str, allow: dict[str, dict]) -> list[dict]:
    """Restituisce un record per ogni dataset controllato."""
    con = duckdb.connect()
    results: list[dict] = []

    for ds_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        files = sorted(ds_dir.glob("*/*.parquet"))
        if not files:
            continue

        cols = _columns(con, files)
        if col not in cols:
            continue
        year_col = next((c for c in YEAR_COLUMNS if c in cols), None)
        if year_col is None:
            results.append(
                {"dataset": ds_dir.name, "skipped": f"nessuna colonna anno tra {YEAR_COLUMNS}"}
            )
            continue

        by_year = _labels_by_year(con, files, col, year_col)
        if len(by_year) < 2:
            results.append({"dataset": ds_dir.name, "skipped": "una sola annualità"})
            continue

        series = set().union(*by_year.values())
        orphans: dict[str, list[int]] = {}
        for etichetta in sorted(series):
            present = [a for a, v in sorted(by_year.items()) if etichetta in v]
            if len(present) < len(by_year):
                orphans[etichetta] = present

        allowed = allow.get(ds_dir.name, {}).get("labels", {})
        consented: dict[str, list[int]] = {}
        for etichetta in list(orphans):
            ranges = allowed.get(etichetta)
            if ranges and _is_consented(orphans[etichetta], ranges):
                consented[etichetta] = orphans.pop(etichetta)

        results.append(
            {
                "dataset": ds_dir.name,
                "anni": f"{min(by_year)}-{max(by_year)}",
                "per_anno": max(len(v) for v in by_year.values()),
                "serie": len(series),
                "orphans": orphans,
                "consented": consented,
            }
        )

    return results


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", default="out/data/clean", help="directory dei clean")
    ap.add_argument("--col", default="regione", help="colonna da controllare")
    ap.add_argument("--allow", default=str(DEFAULT_ALLOW), help="eccezioni dichiarate")
    ap.add_argument("--no-fail", dest="fail_on_drift", action="store_false", help="solo report")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"· nessun clean in {root}: niente da controllare")
        return 0

    results = audit(root, args.col, load_allow(Path(args.allow)))
    checked = [r for r in results if "orphans" in r]
    drift = [r for r in checked if r["orphans"]]

    for r in checked:
        for etichetta, present in r["consented"].items():
            print(f"· {r['dataset']}: deriva dichiarata — '{etichetta}' solo in {_span(present)}")

    for r in drift:
        print(
            f"✗ {r['dataset']} ({r['anni']}): "
            f"{r['serie']} etichette sulla serie, max {r['per_anno']} in un anno"
        )
        for etichetta, present in r["orphans"].items():
            print(f"    '{etichetta}' presente solo in {_span(present)}")

    print(
        f"\n{len(checked)} dataset con '{args.col}': "
        f"{len(checked) - len(drift)} stabili, {len(drift)} con drift non dichiarato"
    )
    for r in results:
        if "skipped" in r:
            print(f"· {r['dataset']}: saltato ({r['skipped']})")

    if drift and args.fail_on_drift:
        # stdout è bufferizzato: senza flush la guida comparirebbe PRIMA del
        # report nei log CI, e il lettore vedrebbe l'istruzione prima della
        # diagnosi.
        sys.stdout.flush()
        print(
            "\nLa stessa entità scritta in modi diversi tra file annuali spezza le "
            "serie quando si raggruppa per nome.\n"
            "Se il cambio è voluto, normalizzalo nel clean.sql del dataset; se è "
            "un'etichetta che deve variare, dichiarala in "
            f"{Path(args.allow).name} con gli anni ammessi e la motivazione.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
