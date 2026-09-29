import numpy as np, pandas as pd
from pathlib import Path
RNG = np.random.default_rng(7)
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/"data"; DATA.mkdir(parents=True, exist_ok=True)
dates = pd.date_range("2024-03-01","2024-03-14",freq="D")
rows=[]
for d in dates:
  for region in ["NAM","EU","APAC"]:
    for _ in range(int(RNG.integers(40,90))):
      rows.append({"event_id":f"E{len(rows)+1:06d}","dt":d.strftime("%Y-%m-%d"),"region":region,
        "channel":RNG.choice(["web","app","store"]),"amount":round(float(RNG.uniform(5,200)),2)})
pd.DataFrame(rows).to_csv(DATA/"events_raw.csv", index=False)
print("Wrote", DATA/"events_raw.csv")

