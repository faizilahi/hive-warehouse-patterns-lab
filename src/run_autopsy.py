from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from serde_probe import probe_partition
from partition_scanner import inventory, predicate_scan
from coalesce_rewrite import coalesce

LAKE, OUT, DATA = ROOT / "lake" / "cdr", ROOT / "output", ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)

def main():
    inv = inventory(LAKE)
    inv.to_csv(OUT / "partition_inventory.csv", index=False)
    bad = LAKE / "dt=2024-11-03" / "market=MKT-NE"
    probe = probe_partition(bad)
    pred = predicate_scan(inv, "2024-11-03", "MKT-NE")
    coal = coalesce(bad, 24)
    meta = json.loads((DATA / "metastore_snapshot.json").read_text(encoding="utf-8"))
    ne_rows = int(inv.loc[(inv.dt == "2024-11-03") & (inv.market == "MKT-NE"), "rows"].iloc[0])
    autopsy = {
        "partition": "dt=2024-11-03/market=MKT-NE",
        "rows_on_disk": ne_rows,
        "registered_in_metastore": False,
        "metastore_hwm": meta["last_repaired_dt"],
        **probe, **pred, **coal,
    }
    pd.DataFrame([autopsy]).to_csv(OUT / "autopsy.csv", index=False)
    print(json.dumps(autopsy, indent=2))

if __name__ == "__main__":
    main()
