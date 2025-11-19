import time, os, csv
from datetime import datetime
from typing import List, Tuple
import z3
from z3 import Ints, Int, Or, sat, unsat

TOTAL_TIME_LIMIT = 1200
ONE_TIME_LIMIT = 20
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

def run_z3(orbit_vertices: List[int], bound: int, time_limit: int) -> Tuple[str, float]:
    s = z3.Solver()
    s.set("timeout", time_limit * 1000)
    
    # Create Z3 variables
    labels = Ints([f"label_{i}" for i in range(1, n + 1)])
    span = Int("span")
    
    lst = []
    for i in range(n):
        if i in orbit_vertices: lst.append(labels[i] == 0)
    s.add(Or(lst))

    for i in range(n):
        s.add(labels[i] >= 0)
        s.add(labels[i] <= span)
        for j in range(0, i):
            diff = C[i + 1][j + 1]
            if diff <= 0: continue
            s.add(
                Or(
                    labels[i] - labels[j] >= diff,
                    labels[i] - labels[j] <= -diff
                )
            )
    
    s.add(span <= bound)
    
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
        print_to_console(f"[SMT_z3] TIMEOUT: Cannot determine satisfiability. Time: {time_limit}s")
        return "timeout", time_limit


def run_smt_z3(_n: int, _C: List[List[int]], delta: int, orbit_vertices: List[int], input: str, ub: int, lb: int) -> Tuple[List[int], int, str]:
    def test_bound(bound: int, time_limit: int) -> int:
        global saved_rows, total_time
        row = {
            "SavedAt": datetime.now().isoformat(timespec="seconds"),
            "Algorithm": filename,
            "Input": input,
            "Delta": delta,
            "N": n,
            "Bound": bound,
        }
        status, elapsed_time = run_z3(orbit_vertices, bound, time_limit)
        row["Result"] = status
        row["Time"] = elapsed_time
        total_time += elapsed_time
        print_to_console(f"[SMT_z3] Total time: {format(total_time, '.3f')}s")
        saved_rows.append(row)

        if status == "sat": return STATUS_SAT
        elif status == "timeout": return STATUS_TIMEOUT
        return STATUS_UNSAT
    
    global n, C, saved_labels, total_time
    n = _n
    C = _C
    saved_labels = [0] * (n + 1)

    if _n == 1: ub, lb = 0, 0
    else:
        # Find the smallest span that satisfies the radio constraint
        status = test_bound(ub, TOTAL_TIME_LIMIT)
        assert status == STATUS_SAT
        L = lb
        R = ub - 1
        while L + 2 <= R and total_time < TOTAL_TIME_LIMIT:
            mid = (L + R) // 2
            time_limit = min(TOTAL_TIME_LIMIT - int(total_time), ONE_TIME_LIMIT)
            status = test_bound(mid, time_limit)
            if status == STATUS_SAT:
                ub = mid
                R = mid - 1
            else:
                if status == STATUS_UNSAT: lb = mid + 1
                L = mid + 1

        while ub > lb and total_time < TOTAL_TIME_LIMIT:
            status = test_bound(ub - 1, TOTAL_TIME_LIMIT - int(total_time))
            if status == STATUS_SAT:
                ub = ub - 1
            elif status == STATUS_UNSAT:
                lb = ub
            else:
                break
    
    status = "optimal" if ub == lb else "timeout"
    if status == "timeout": total_time = TOTAL_TIME_LIMIT
    else: total_time = float(format(total_time, ".3f"))
    print_to_console(f"[SMT_z3] Final span: {ub}. Status: {status}")
    row = {
        "SavedAt": datetime.now().isoformat(timespec="seconds"),
        "Algorithm": filename,
        "Input": input,
        "Delta": delta,
        "N": n,
        "Span": ub,
        "Status": status,
        "Time": total_time,
    }
    write_to_csv([row], f"{filename}_final")
    write_to_csv(saved_rows, filename)

    return saved_labels, ub, saved_text
