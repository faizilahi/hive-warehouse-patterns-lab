from __future__ import annotations
from pathlib import Path
import pandas as pd

def coalesce(part_dir: Path, target_files: int = 24) -> dict:
    frames = [pd.read_parquet(f) for f in sorted(part_dir.glob("*.parquet"))]
    if not frames:
        return {"files_before": 0, "files_after": 0, "rows": 0}
    df = pd.concat(frames, ignore_index=True)
    count_marker = part_dir / "_FILE_COUNT.txt"
    before = int(count_marker.read_text(encoding="utf-8").strip()) if count_marker.exists() else len(frames)
    out = part_dir / "_coalesced"
    out.mkdir(exist_ok=True)
    for old in out.glob("*.parquet"):
        old.unlink()
    n = len(df)
    base, rem = divmod(n, target_files)
    sizes = [base + (1 if i < rem else 0) for i in range(target_files)]
    start = written = 0
    for i, sz in enumerate(sizes):
        if sz == 0:
            continue
        df.iloc[start:start + sz].to_parquet(out / f"part-{i:05d}.parquet", index=False)
        written += 1
        start += sz
    return {"files_before": before, "files_after": written, "rows": int(n)}
