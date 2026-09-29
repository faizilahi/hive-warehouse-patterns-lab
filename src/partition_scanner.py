from __future__ import annotations
from pathlib import Path
import pandas as pd

def inventory(lake_root: Path) -> pd.DataFrame:
    rows = []
    for part in sorted(lake_root.glob("dt=*/market=*")):
        dt = part.parent.name.split("=", 1)[1]
        market = part.name.split("=", 1)[1]
        count_marker = part / "_FILE_COUNT.txt"
        if count_marker.exists():
            n_files = int(count_marker.read_text(encoding="utf-8-sig").strip())
        else:
            n_files = len(list(part.glob("*.parquet"))) + len(list(part.glob("*.stub")))
        n_rows = sum(len(pd.read_parquet(f)) for f in part.glob("*.parquet"))
        rows.append({
            "dt": dt, "market": market, "files": n_files, "rows": n_rows,
            "avg_rows_per_file": round(n_rows / n_files, 2) if n_files else 0,
            "small_file_flag": n_files > 100,
        })
    return pd.DataFrame(rows)

def predicate_scan(inv: pd.DataFrame, dt: str, market: str) -> dict:
    full = int(inv.loc[inv["dt"] == dt, "files"].sum())
    pruned = int(inv.loc[(inv["dt"] == dt) & (inv["market"] == market), "files"].sum())
    return {
        "dt": dt, "market": market,
        "files_full_day_scan": full,
        "files_after_predicate": pruned,
        "scan_reduction_pct": round((1 - pruned / full) * 100, 1) if full else 0.0,
    }
