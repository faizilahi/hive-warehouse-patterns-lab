"""Write Hive-style partitions and prune-query with DuckDB."""
from pathlib import Path
import pandas as pd, duckdb
ROOT = Path(__file__).resolve().parents[1]
DATA, LAKE, OUT = ROOT/"data", ROOT/"lake"/"events", ROOT/"output"
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(DATA/"events_raw.csv", dtype={"region": str})
# SerDe teaching: CSV landing -> typed Parquet external layout
import shutil
if LAKE.exists():
  shutil.rmtree(LAKE)
for (dt, region), g in df.groupby(["dt","region"]):
  p = LAKE / f"dt={dt}" / f"region={region}"
  p.mkdir(parents=True, exist_ok=True)
  g.drop(columns=["dt","region"]).to_parquet(p/"part-0000.parquet", index=False)
con = duckdb.connect()
# hive_partitioning reads partition keys from folder names
q = f"""
SELECT dt, region, COUNT(*) AS events, ROUND(SUM(amount),2) AS amount
FROM read_parquet('{(LAKE).as_posix()}/**/*.parquet', hive_partitioning=true)
WHERE dt = '2024-03-05' AND region = 'NAM'
GROUP BY 1,2
"""
pruned = con.execute(q).df()
pruned.to_csv(OUT/"partition_prune.csv", index=False)
# Compare naive full scan count
full = con.execute(f"SELECT COUNT(*) c FROM read_parquet('{(LAKE).as_posix()}/**/*.parquet', hive_partitioning=true)").fetchone()[0]
pd.DataFrame([{"partition_filter":"dt=2024-03-05,region=NAM","returned_events":int(pruned['events'].sum() if len(pruned) else 0),"lake_total_events":int(full)}]).to_csv(OUT/"summary.csv", index=False)
print(pruned); print("Wrote Hive partition outputs")

