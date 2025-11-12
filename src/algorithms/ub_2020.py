from typing import List, Tuple
import os
import csv
from datetime import datetime

INF: int = 10**15

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

def _run_from_start(C0: List[List[int]], n: int, start: int) -> Tuple[List[int], int]:
    C = [row[:] for row in C0]
    labels = [0] * (n + 1)
    l = start
    uncolored = set(range(1, n + 1))
    uncolored.remove(l)
    for _ in range(n - 1):
        p = min(uncolored, key=lambda v: C[l][v])
        m = C[l][p]
        labels[p] = m
        uncolored.remove(p)
        for j in uncolored:
            C[p][j] = max(C[p][j] + m, C[l][j])
        l = p
    span = max(labels[1:])
    return labels, span

def run_ub_2020(n: int, C: List[List[int]], delta: int, input: str) -> Tuple[List[int], int]:
    best_labels, best_span = [0] * (n + 1), INF
    for s in range(1, n + 1):
        labels, span = _run_from_start(C, n, s)
        if span < best_span:
            best_labels, best_span = labels, span
    
    row = {
        "SavedAt": datetime.now().isoformat(timespec="seconds"),
        "Algorithm": filename,
        "Input": input,
        "n": n,
        "delta": delta,
        "Span": best_span,
    }

    write_to_csv(row)
    return best_labels, best_span