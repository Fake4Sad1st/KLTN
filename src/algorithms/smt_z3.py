import time, os, csv, math
from datetime import datetime
from typing import List, Tuple
from z3 import Solver, Ints, Or, sat, unsat

TIME_LIMIT = 600
# using integer to represent status
STATUS_SAT = 0
STATUS_TIMEOUT = 1
STATUS_UNSAT = 2

filename = os.path.basename(__file__).split(".")[0]
n: int
C: List[List[int]]
saved_labels: List[int]
saved_text: str = ""
saved_rows: List[dict] = []
total_time: float = 0.0

# ============================== LOGGING + REPORTING ==============================
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_reports_dir = os.path.join(_repo_root, "reports")
os.makedirs(_reports_dir, exist_ok=True)

def print_to_console(*args, **kwargs) -> None:
    print(*args, **kwargs)
    global saved_text
    saved_text += f"{args[0]}\n"

def write_to_csv(rows: List[dict], csv_name: str) -> None:
    path = os.path.join(_reports_dir, f"{csv_name}.csv")
    write_header = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        for row in rows:
            w = csv.DictWriter(f, fieldnames=list(row.keys()))
            if write_header:
                w.writeheader()
                write_header = False
            w.writerow(row)

# ============================== SMT SOLVER ==============================
def run_z3(orbit_vertices: List[int], bound: int) -> Tuple[str, float]:
    s = Solver()
    s.set("timeout", TIME_LIMIT * 1000)
    
    # Create Z3 variables
    labels = Ints([f"label_{i}" for i in range(1, n + 1)])
    
    lst = []
    for i in range(n):
        if i in orbit_vertices: lst.append(labels[i] == 0)
        s.add(labels[i] >= 0)
        s.add(labels[i] <= bound)
    s.add(Or(lst))
    
    # At least one vertex must have label bound
    lst = []
    for i in range(n): lst.append(labels[i] == bound)
    s.add(Or(lst))
    
    # Radio constraints
    for i in range(n):
        for j in range(i + 1, n):
            diff = C[i + 1][j + 1]
            if diff <= 0: continue
            s.add(
                Or(
                    labels[i] - labels[j] >= diff,
                    labels[j] - labels[i] >= diff
                )
            )
    
    print_to_console(f"[SMT_z3] Checking span {bound}...")
    start_time = time.time()
    result = s.check()
    elapsed_time = float(format(time.time() - start_time, ".3f"))
    
    if result == sat:
        model = s.model()
        global saved_labels
        saved_labels = [0] * (n + 1)
        for i in range(n):
            label_val = model[labels[i]]
            if label_val is not None:
                saved_labels[i + 1] = int(str(label_val))
        print_to_console(f"[SMT_z3] Solution found. Time: {elapsed_time}s")
        return "sat", elapsed_time
    elif result == unsat:
        print_to_console(f"[SMT_z3] UNSAT: No solution exists. Time: {elapsed_time}s")
        return "unsat", elapsed_time
    else:
        print_to_console(f"[SMT_z3] TIMEOUT: Cannot determine satisfiability. Time: {TIME_LIMIT}s")
        return "timeout", TIME_LIMIT

def test_bound(delta: int, orbit_vertices: List[int], input: str, bound: int) -> int:
    global saved_rows, total_time
    row = {
        "SavedAt": datetime.now().isoformat(timespec="seconds"),
        "Algorithm": filename,
        "Input": input,
        "Delta": delta,
        "N": n,
        "Bound": bound,
    }
    status, elapsed_time = run_z3(orbit_vertices, bound)
    row["Result"] = status
    row["Time"] = elapsed_time
    total_time += elapsed_time
    saved_rows.append(row)

    if status == "sat": return STATUS_SAT
    elif status == "timeout": return STATUS_TIMEOUT
    return STATUS_UNSAT

def format_time(seconds: float) -> str:
    total_seconds = int(math.floor(seconds))
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
    elif minutes > 0:
        parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
    else:
        parts.append(f"{secs}s")
    
    return "".join(parts)

def run_smt_z3(_n: int, _C: List[List[int]], delta: int, orbit_vertices: List[int], input: str, ub: int, lb: int) -> Tuple[List[int], int, int, str]:
    global n, C, saved_labels
    n = _n
    C = _C
    saved_labels = [0] * (n + 1)

    if _n == 1: ub, lb = 0, 0
    else:
        # Find the smallest span that satisfies the radio constraint
        L = lb
        R = ub
        newR = -1
        while L <= R:
            if R - L >= 8: mid = R - ((R - L) // 8)
            else: mid = R - ((R - L) // 4)
            status = test_bound(delta, orbit_vertices, input, mid)
            if status == STATUS_SAT:
                ub = mid
                R = mid - 1
            else:
                if status == STATUS_UNSAT: lb = mid + 1
                elif newR == -1: newR = mid
                L = mid + 1
        # Find the largest span that doesn't satisfy the radio constraint
        L = lb
        R = newR - 1 if newR != -1 else ub - 1
        while L <= R:
            if R - L >= 8: mid = L + ((R - L) // 8)
            else: mid = L + ((R - L) // 4)
            status = test_bound(delta, orbit_vertices, input, mid)
            if status == STATUS_UNSAT:
                lb = mid + 1
                L = mid + 1
            else: R = mid - 1
        
    row = {
        "SavedAt": datetime.now().isoformat(timespec="seconds"),
        "Algorithm": filename,
        "Input": input,
        "Delta": delta,
        "N": n,
        "UpperBound": ub,
        "LowerBound": lb,
        "TotalTime": format_time(total_time),
    }
    write_to_csv([row], f"{filename}_final")
    write_to_csv(saved_rows, filename)

    return saved_labels, ub, lb, saved_text

