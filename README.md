# Partition Autopsy: Telecom CDR Small Files

[Faiz Elahi](https://www.linkedin.com/in/faizilahi) — [pendataco.com](https://pendataco.com) — [github.com/faizilahi](https://github.com/faizilahi)

Synthetic data only. No vendor-customer employment claim.

A Hive-style CDR landing zone missed market `MKT-NE` on `2024-11-03` after a failed
`MSCK REPAIR` left the metastore high-water on `2024-11-02` while 14,200 tiny parquet
files sat on disk under the skipped partition.

## The partition that was skipped

`lake/cdr/dt=2024-11-03/market=MKT-NE/` held **48,210** rows. The overnight rollup
only listed metastore partitions, so NE contributed **0** rows to the AM dashboard.

## SerDe note

Metastore DDL still said `LazySimpleSerDe` (CSV) while landings were parquet.
`src/serde_probe.py` flags `serde_conflict=true` for that path.

## The predicate that saved the scan

Predicate `market='MKT-NE' AND dt='2024-11-03'` cut the file list from the full-day
scan to the NE shard only; coalesce rewrote **14,200** files down to **24**.

```powershell
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
python src/run_autopsy.py
```

Worked result: skipped rows **48210**, serde_conflict **true**, files before **14200**,
after coalesce **24**, predicate scan reduction **~76%**.
