# Hive Warehouse Patterns Lab (Partitions & SerDe)

**Author:** [Faiz Elahi](https://github.com/faizilahi) (`faizilahi`) · **Type:** EDUCATIONAL LAB · **Synthetic data only**

---

## Educational disclaimer

This is an **educational portfolio lab**. Datasets are **synthetic**. It does **not** claim employment at a customer, hospital, bank, SAP shop, or Oracle estate. No real PHI/PII. No live cloud spend. No API keys required.

---

## Problem statement

Legacy lakes still speak Hive: external tables, partition columns, SerDe-shaped CSVs/Parquet, and MSCK-style repair thinking. Students need runnable partition pruning demos without a full Hadoop cluster.

**Domain focus:** Retail event warehouse

---

## Why this tool (HiveQL patterns (local parquet partition stand-in))

| Flat CSV dumps | Hive-style partitioned lake |
|---|---|
| Full scans | Partition filters on dt/region |
| Opaque formats | Explicit SerDe/schema notes |

---

## Architecture

```mermaid
flowchart LR
  GEN[generate_synthetic_data.py]
  DATA[data/*.csv]
  RUN[run_lab.py]
  OUT[output/*.csv]
  CHART[generate_charts.py]
  IMG[docs/images/*.png]
  GEN --> DATA --> RUN --> OUT
  OUT --> CHART --> IMG
```

See [`docs/architecture.md`](docs/architecture.md).

---

## Dataset dictionary

| Path | Grain | Notes |
|------|-------|-------|
| `data/events_raw.csv` | Event | Landing extract |
| `lake/events/dt=*/region=*/*.parquet` | Event | External-table style partitions |
| `output/partition_prune.csv` | Partition | Rows scanned teaching metric |

---

## Prerequisites

- Python 3.10+
- Packages in `requirements.txt`

---

## How to run

```powershell
cd "hive-warehouse-patterns-lab-"
python -m venv .venv
.\\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
python src/run_lab.py
python scripts/generate_charts.py
```

Inspect `output/summary.csv` and `docs/images/primary_metric.png`.

---

## Local vs cloud (honest)

**No Hadoop/Hive metastore.** Python + pandas/pyarrow write Hive-style `dt=.../region=...` folders and query them with DuckDB `hive_partitioning=true`. Honest stand-in for HiveQL habits.

---

## Results interpretation

Open `output/` CSVs and the PNGs under `docs/images/`. Numbers are synthetic teaching fixtures — use them to explain grain, filters, and control totals, not as real business KPIs.

---

## Limitations

- Stand-in engines (DuckDB/SQLite/pandas) replace paid MPP/warehouses where noted.
- Simplified schemas vs production SAP/Oracle/Hive estates.
- Charts are matplotlib teaching visuals, not vendor BI embeds.

---

## Exercises

1. Add a `channel` partition and show prune stats.
2. Document a SerDe mapping for a messy CSV.
3. Simulate a missing partition folder and an MSCK repair checklist.

---

## License / attribution

Educational portfolio content by Faiz Elahi. Synthetic data for teaching only.

