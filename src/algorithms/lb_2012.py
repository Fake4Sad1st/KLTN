from typing import List
import os
import csv
from datetime import datetime

# --- simple logging/report helpers ---
filename = os.path.basename(__file__).split(".")[0]
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_reports_dir = os.path.join(_repo_root, "reports")
os.makedirs(_reports_dir, exist_ok=True)

def write_to_csv(row: dict) -> None:
    path = os.path.join(_reports_dir, f"{filename}.csv")
    write_header = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            w.writeheader()
        w.writerow(row)

def run_lb_2012(n: int, dist: List[List[int]], K: int, delta: int, input: str) -> int:
    lower_bound: int = -1
    if n == 1: lower_bound = 0
    elif n == 2: lower_bound = 1 if delta == 0 else 0
    else:
        b: int = 0
        for i1 in range(1, n + 1):
            for i2 in range(i1 + 1, n + 1):
                for i3 in range(i2 + 1, n + 1):
                    b = max(b, dist[i1][i2] + dist[i2][i3] + dist[i3][i1])
        
        tmp = (3 * (K + 1) - b + 1) // 2
        if delta == 0 and n % 2 == 0:
            lower_bound = tmp * ((n - 2) // 2) + 1
        else:
            lower_bound = tmp * ((n - 1) // 2)
    
    row = {
        "SavedAt": datetime.now().isoformat(timespec="seconds"),
        "Algorithm": filename,
        "Input": input,
        "N": n,
        "Delta": delta,
        "LowerBound": lower_bound,
    }

    write_to_csv(row)
    return lower_bound