import time, os, csv, math
from datetime import datetime
from typing import List, Optional, Tuple

from pysat.solvers import Glucose3
from threading import Timer

TIME_LIMIT = 600
# using integer to represent status
STATUS_SAT = 0
STATUS_TIMEOUT = 1
STATUS_UNSAT = 2

filename = os.path.basename(__file__).split(".")[0]
num_clauses: int
n: int
m: int
C: List[List[int]]
sat_solver: Optional[Glucose3] = None
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

# ============================== SAT SOLVER ==============================
def _K(i: int, j: int) -> int:
    # K_{i,j}: vertex i has label == j.
    # j ranges from 0 to m
    return (i - 1) * (m + 1) + j + 1

def _X(i: int, j: int) -> int:
    # X_{i,j}: vertex i has label <= j.
    # j ranges from 1 to m, X_{i,0} = K_{i,0} (for convenience)
    if j == 0: return _K(i, 0)
    return n * (m + 1) + (i - 1) * m + j

def _add_clause(clause: List[int]) -> None:
    assert sat_solver is not None
    sat_solver.add_clause(clause)
    global num_clauses
    num_clauses += 1

def add_exactly_one_constraints():
    """
    Add constraints to ensure exactly one label per vertex using improved encoding.
    Uses X (unary: label <= j) and K (equality) variables.
    Labels range from 0 to m (0-based).
    """
    for i in range(1, n + 1):
        for j in range(0, m + 1):
            # If label == j then label <= j
            _add_clause([-_K(i, j), _X(i, j)])
            if j > 0:
                # If label == j then label > j-1 (i.e., not label <= j-1)
                _add_clause([-_K(i, j), -_X(i, j - 1)])
                # If label <= j, then either label == j or label <= j-1
                _add_clause([-_X(i, j), _K(i, j), _X(i, j - 1)])
                # If label <= j-1 then label <= j
                _add_clause([_X(i, j), -_X(i, j - 1)])
        # X(i, m) is always True (label <= m since m = bound and labels are in [0, m])
        _add_clause([_X(i, m)])
    
def add_radio_constraints():
    """
    For each pair (u, v), if label[u] = val, then label[v] cannot be in [val-req+1, val+req-1].
    """
    for u in range(1, n + 1):
        for v in range(1, n + 1):
            if u == v: continue

            req = C[u][v]  # Required difference: |label[u] - label[v]| >= req
            if req <= 0: continue
            
            # For each possible label value for u (0-based: 0..m)
            for val in range(0, m + 1):
                '''
                If label[u] = val, then label[v] must NOT be in [val-req+1, val+req-1]
                This means:
                - Either label[v] < val-req+1  (i.e., label[v] <= val-req)
                - Or label[v] >= val+req  (i.e., not label[v] <= val+req-1)
                '''
                lower_bound = val - req  # label[v] must be <= this
                upper_bound = val + req - 1  # label[v] must NOT be <= this (i.e., label[v] >= val+req)
                
                # Case 1: Both boundaries are valid (lower_bound >= 0 and upper_bound < m)
                if lower_bound >= 0 and upper_bound < m:
                    # label[v] <= lower_bound OR NOT(label[v] <= upper_bound)
                    _add_clause([-_K(u, val), _X(v, lower_bound), -_X(v, upper_bound)])
                # Case 2: Lower boundary invalid (lower_bound < 0), so we only need upper_bound
                elif upper_bound < m:
                    _add_clause([-_K(u, val), -_X(v, upper_bound)])
                # Case 3: Upper boundary invalid (upper_bound >= m), so we only need lower_bound
                elif lower_bound >= 0:
                    _add_clause([-_K(u, val), _X(v, lower_bound)])

def add_special_constraints(orbit_vertices: List[int]):
    # At least one vertex in orbit_vertices must have label 0
    lst = []
    for i in range(1, n + 1):
        if i in orbit_vertices: lst.append(_K(i, 0))
    _add_clause(lst)
    # At least one vertex must have label m
    lst = []
    for i in range(1, n + 1): lst.append(_K(i, m))
    _add_clause(lst)

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

def run_glucose(bound: int) -> Tuple[str, float]:
    print_to_console(f"[SAT_pysat] Checking span {bound} ...")
    assert sat_solver is not None
    interrupted = [False]
    
    def interrupt(solver):
        solver.interrupt()
        interrupted[0] = True
    
    timer = Timer(TIME_LIMIT, interrupt, [sat_solver])
    timer.start()
    
    start_time = time.time()
    sat_status = sat_solver.solve_limited(expect_interrupt=True)
    elapsed_time = float(format(time.time() - start_time, ".3f"))
    timer.cancel()

    if sat_status is False:
        print_to_console(f"[SAT_pysat] UNSAT: No solution exists. Time: {elapsed_time}s")
        return "unsat", elapsed_time
    else:
        solution = sat_solver.get_model()
        if solution is None:
            print_to_console(f"[SAT_pysat] TIMEOUT: Cannot determine satisfiability. Time: {TIME_LIMIT}s")
            return "timeout", TIME_LIMIT
        
        # Extract labels from model (0-based)
        global saved_labels
        saved_labels = [0] * (n + 1)
        solution_set = set(solution)
        # Extract from K variables: find which K(i, j) is True
        for i in range(1, n + 1):
            for j in range(0, m + 1):
                if _K(i, j) in solution_set:
                    saved_labels[i] = j
                    break
        print_to_console(f"[SAT_pysat] Solution found. Time: {elapsed_time}s")
        return "sat", elapsed_time

def test_bound(delta: int, orbit_vertices: List[int], input: str, bound: int) -> int:
    global num_clauses, n, m, sat_solver, saved_rows, total_time
    num_clauses = 0
    m = bound
    sat_solver = Glucose3(use_timer=True)

    add_exactly_one_constraints()
    add_radio_constraints()
    add_special_constraints(orbit_vertices)
    
    num_variables = n * (m + 1) + n * m  # K and X variables
    
    # print_to_console(f"[SAT_pysat] Constraints added. Statistics:")
    # print_to_console(f"[SAT_pysat]   - Variables: {num_variables} (K: {n * (m + 1)}, X: {n * m})")
    # print_to_console(f"[SAT_pysat]   - Clauses: {num_clauses}")

    # Prepare CSV row before solving so test_bound can fill status/time
    row = {
        "SavedAt": datetime.now().isoformat(timespec="seconds"),
        "Algorithm": filename,
        "Input": input,
        "Delta": delta,
        "N": n,
        "Bound": bound,
        "Variables": num_variables,
        "Clauses": num_clauses,
    }
    status, elapsed_time = run_glucose(bound)
    sat_solver.delete()

    row["Result"] = status
    row["Time"] = elapsed_time
    total_time += elapsed_time
    saved_rows.append(row)

    if status == "sat": return STATUS_SAT
    elif status == "timeout": return STATUS_TIMEOUT
    return STATUS_UNSAT

def run_sat_pysat(_n: int, _C: List[List[int]], delta: int, orbit_vertices: List[int], input: str, ub: int, lb: int) -> Tuple[List[int], int, int, str]:
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

