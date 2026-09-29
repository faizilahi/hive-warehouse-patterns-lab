"""Telecom CDR partitions with deliberate small-files + stale metastore."""
from __future__ import annotations
import json, shutil
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LAKE, DATA = ROOT / "lake" / "cdr", ROOT / "data"
RNG = np.random.default_rng(1103)
MARKETS = ["MKT-NE", "MKT-SE", "MKT-MW", "MKT-W"]

def write_part(dt, market, n_rows, small):
    part = LAKE / f"dt={dt}" / f"market={market}"
    if part.exists():
        shutil.rmtree(part)
    part.mkdir(parents=True)
    df = pd.DataFrame({
        "cdr_id": [f"{dt}-{market}-{i:06d}" for i in range(n_rows)],
        "imsi_hash": [f"H{int(RNG.integers(1e8,9e8))}" for _ in range(n_rows)],
        "event_type": RNG.choice(["VOICE","SMS","DATA"], n_rows),
        "duration_sec": RNG.integers(0, 600, n_rows),
        "bytes": RNG.integers(0, 5_000_000, n_rows),
        "cell_id": [f"C{int(RNG.integers(100,999))}" for _ in range(n_rows)],
    })
    df.to_parquet(part / "part-00000.parquet", index=False)
    if small:
        n_files = 14200 if (dt == "2024-11-03" and market == "MKT-NE") else 200
        # Represent small-files pressure without creating 14k parquet objects on disk
        (part / "_FILE_COUNT.txt").write_text(str(n_files), encoding="utf-8")
        for fi in range(1, min(48, n_files)):
            (part / f"part-{fi:05d}.stub").write_bytes(b"")
        files = n_files
    else:
        (part / "_FILE_COUNT.txt").write_text("1", encoding="utf-8")
        files = 1
    serde = "LazySimpleSerDe" if (dt == "2024-11-03" and market == "MKT-NE") else "ParquetHiveSerDe"
    (part / "_METADATA_SERDE.txt").write_text(serde + "\n", encoding="utf-8")
    return {"dt": dt, "market": market, "rows": n_rows, "files": files, "serde": serde}

def main():
    if LAKE.exists():
        shutil.rmtree(LAKE)
    LAKE.mkdir(parents=True)
    DATA.mkdir(parents=True, exist_ok=True)
    metas = []
    for dt in ["2024-11-01", "2024-11-02"]:
        for m in MARKETS:
            metas.append(write_part(dt, m, int(RNG.integers(8000, 12000)), False))
    metas.append(write_part("2024-11-03", "MKT-NE", 48210, True))
    for m in ["MKT-SE", "MKT-MW", "MKT-W"]:
        # other markets also fragmented so predicate pruning is meaningful
        part_meta = write_part("2024-11-03", m, int(RNG.integers(9000, 11000)), True)
        # override file count representation to ~15k each without NE's exact 14200
        part = LAKE / "dt=2024-11-03" / f"market={m}"
        (part / "_FILE_COUNT.txt").write_text("15000", encoding="utf-8")
        part_meta["files"] = 15000
        metas.append(part_meta)
    metastore = {
        "table": "cdr_events",
        "last_repaired_dt": "2024-11-02",
        "partitions_registered": [m for m in metas if m["dt"] <= "2024-11-02"],
    }
    (DATA / "metastore_snapshot.json").write_text(json.dumps(metastore, indent=2), encoding="utf-8")
    pd.DataFrame(metas).to_csv(DATA / "partition_inventory_seed.csv", index=False)
    print("CDR lake ready", len(metas), "partitions")

if __name__ == "__main__":
    main()
