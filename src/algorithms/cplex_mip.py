from typing import List, Tuple
import os, csv, time
from docplex.mp.model import Model
from datetime import datetime

TIME_LIMIT = 1200

saved_text: str = ""

# --- simple logging/report helpers ---
filename = os.path.basename(__file__).split(".")[0]
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_reports_dir = os.path.join(_repo_root, "reports")
os.makedirs(_reports_dir, exist_ok=True)

def print_to_console(*args, **kwargs) -> None:
    print(*args, **kwargs)
    global saved_text
    saved_text += f"{args[0]}\n"

def write_to_csv(row: dict) -> None:
    path = os.path.join(_reports_dir, f"{filename}.csv")
    write_header = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            w.writeheader()
        w.writerow(row)

def run_cplex_mip(n: int, C: List[List[int]], K: int, delta: int, input: str) -> Tuple[List[int], int, str]:
    def solve() -> Tuple[List[int], int, str, float]:
        # Tạo mô hình CPLEX
        m = Model(name="radio_k_labeling")
        m.set_time_limit(TIME_LIMIT)
        m.parameters.threads = 1
        m.parameters.workmem = 2048 # MB
        
        # Tạo biến: labels và span
        labels = {}
        for i in range(1, n + 1):
            labels[i] = m.integer_var(lb=0, name=f"label_{i}")
        
        # span là maximum của tất cả labels
        span = m.integer_var(lb=0, name="span")
        
        # Ràng buộc: labels[i] <= span cho mọi i
        for i in range(1, n + 1):
            m.add_constraint(labels[i] <= span, ctname=f"span_constraint_{i}")
        

        # Sử dụng big-M với biến nhị phân
        M = (n + 1) * K  # Big-M constant
        b = {}  # Biến nhị phân để mô hình OR constraint
        
        # Ràng buộc radio: |labels[i] - labels[j]| >= C[i][j]
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                req = C[i][j]
                if req <= 0: continue
                
                m.add_constraint(m.logical_or(
                    (labels[i] - labels[j] >= req), 
                    (labels[j] - labels[i] >= req) 
                ), ctname=f"radio_or_{i}_{j}")
        
        # Hàm mục tiêu: minimize span
        m.minimize(span)
        
        start_time = time.time()
        sol = m.solve()
        elapsed_time = float(format(time.time() - start_time, ".3f"))
        
        # Kiểm tra kết quả
        result_labels = [0] * (n + 1)
        
        assert sol is not None
        assert hasattr(sol, 'solve_details') and hasattr(sol.solve_details, 'status')
        solve_status = str(sol.solve_details.status).lower()
        
        print_to_console(f"[CPLEX_MIP] Status: {solve_status}")
        is_optimal = solve_status == "integer optimal solution"
        
        if is_optimal:
            status = "optimal"
            print_to_console(f"[CPLEX_MIP] Optimal solution found. Time: {elapsed_time}s")
        else:
            status = "timeout"
            elapsed_time = TIME_LIMIT
            print_to_console(f"[CPLEX_MIP] Timeout. Time: {TIME_LIMIT}s")
        
        for i in range(1, n + 1): 
            result_labels[i] = int(round(labels[i].solution_value))
        result_span = int(round(span.solution_value))
        
        return result_labels, result_span, status, elapsed_time


    labels, span, status, time_run = solve()
    row = {
        "SavedAt": datetime.now().isoformat(timespec="seconds"),
        "Algorithm": filename,
        "Input": input,
        "N": n,
        "Delta": delta,
        "Span": span,
        "Status": status,
        "Time": time_run,
    }
    write_to_csv(row)

    return labels, span, saved_text