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

def run_ub_2019(n: int, C: List[List[int]], dist: List[List[int]], delta: int, input: str) -> Tuple[List[int], int]:
    def run_algo_1(start: int) -> Tuple[List[int], int]:
        labels = [0] * (n + 1)
        # Step 1: Choose vertex start and col(start) = 0
        labels[start] = 0
        # Step 2: S = {start}
        S = {start}
        uncolored = set(range(1, n + 1))
        uncolored.remove(start)
        
        # Step 8: Repeat Step 3 to Step 6 until all vertices are colored
        while uncolored:
            # Step 3: For all v ∈ V(G) - S, compute temp(v) = max_{t∈S} {col(t) + max[k + 1 - d(t, v), 0]}
            # Since C[t][v] = max[k + 1 - d(t, v), 0], we have temp(v) = max_{t∈S} {labels[t] + C[t][v]}
            temp = {}
            for v in uncolored:
                temp[v] = max(labels[t] + C[t][v] for t in S)
            # Step 4: Let min_val = min_{v ∈ V(G) - S} {temp(v)}
            # Step 5: Choose a vertex v ∈ V(G) - S such that temp(v) = min
            v = min(uncolored, key=lambda v: temp[v])
            min_val = temp[v]
            # Step 6: Give col(v) = min
            labels[v] = min_val
            # Step 7: S = S U {v}
            S.add(v)
            uncolored.remove(v)
        
        span = max(labels[1:])
        return labels, span


    def run_algo_2(start: int) -> Tuple[List[int], int]:
        labels = [0] * (n + 1)
        # Step 1: Choose vertex start and col(start) = 0
        labels[start] = 0
        # Step 2: S = {start}
        S = {start}
        uncolored = set(range(1, n + 1))
        uncolored.remove(start)
        
        # Initialize u = start
        u = start
        
        # Step 3: Choose vertex v from V(G) - S such that d(u, v) is maximum
        if uncolored:
            v = max(uncolored, key=lambda w: dist[u][w])
            # Step 4: col(v) = C[u][v]
            labels[v] = C[u][v]
            # Step 5: S = {u, v}
            S.add(v)
            uncolored.remove(v)
        else:
            # If no uncolored vertices, return
            span = max(labels[1:])
            return labels, span
        
        # Step 13: Repeat Step 6 to Step 11 until all vertices are colored
        while uncolored:
            # Step 6: Let S1 be the set of uncolored vertices w ∈ V - S for which d(u, w) + d(w, v) is maximum
            max_sum = max(dist[u][w] + dist[w][v] for w in uncolored)
            S1 = {w for w in uncolored if dist[u][w] + dist[w][v] == max_sum}
            # Step 7: For all w in S1, compute temp(w) = max_{t∈S} {col(t) + max{k + 1 - d(t, w), 0}}
            # Since C[t][w] = max{k + 1 - d(t, w), 0}, we have temp(w) = max_{t∈S} {labels[t] + C[t][w]}
            temp = {}
            for w in S1:
                temp[w] = max(labels[t] + C[t][w] for t in S)
            # Step 8: Let min = min_{w∈S1} {temp(w)}
            # Step 9: Choose vertex w' from S1 such that temp(w') = min
            w_prime = min(S1, key=lambda w: temp[w])
            min_val = temp[w_prime]
            # Step 10: col(w') = temp(w')
            labels[w_prime] = min_val
            # Step 11: S = S U {w'}
            S.add(w_prime)
            uncolored.remove(w_prime)
            # Step 12: Update u = v and v = w'
            u, v = v, w_prime
        
        span = max(labels[1:])
        return labels, span


    bl1, bs1 = [0] * (n + 1), INF
    for s in range(1, n + 1):
        labels, span = run_algo_1(s)
        if span < bs1:
            bl1, bs1 = labels, span

    bl2, bs2 = [0] * (n + 1), INF
    for s in range(1, n + 1):
        labels, span = run_algo_2(s)
        if span < bs2:
            bl2, bs2 = labels, span
    
    if bs1 <= bs2:
        best_labels, best_span = bl1, bs1
    else:
        best_labels, best_span = bl2, bs2
    
    row = {
        "SavedAt": datetime.now().isoformat(timespec="seconds"),
        "Algorithm": filename,
        "Input": input,
        "N": n,
        "Delta": delta,
        "Span1": bs1,
        "Span2": bs2,
        "BestSpan": best_span,
    }

    write_to_csv(row)
    return best_labels, best_span