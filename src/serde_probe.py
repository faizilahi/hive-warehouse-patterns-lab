from __future__ import annotations
from pathlib import Path

def probe_partition(part_dir: Path) -> dict:
    marker = part_dir / "_METADATA_SERDE.txt"
    declared = marker.read_text(encoding="utf-8").splitlines()[0].strip() if marker.exists() else "unknown"
    pq = list(part_dir.glob("*.parquet"))
    actual = "parquet" if pq else "empty"
    conflict = ("LazySimple" in declared and actual == "parquet")
    count_marker = part_dir / "_FILE_COUNT.txt"
    file_count = int(count_marker.read_text(encoding="utf-8").strip()) if count_marker.exists() else len(pq)
    return {
        "path": part_dir.as_posix(),
        "serde_declared": declared,
        "actual_format": actual,
        "file_count": file_count,
        "serde_conflict": conflict,
    }
