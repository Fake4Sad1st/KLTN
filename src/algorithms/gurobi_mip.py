from typing import List, Tuple
import os, csv, time
import gurobipy as gp
from gurobipy import GRB
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

def run_gurobi(n: int, C: List[List[int]], K: int, delta: int, input: str) -> Tuple[List[int], int, str]:
    def solve() -> Tuple[List[int], int, str, float]:
        # Tạo môi trường và model
        env = gp.Env(empty=True)
        env.setParam('LogToConsole', 0)
        env.setParam('Threads', 2)
        env.start()
        m = gp.Model("radio_k_labeling", env=env)
        m.setParam('OutputFlag', 0)
        m.setParam('TimeLimit', TIME_LIMIT)
        
        # Tạo biến: labels và span
        labels = {}
        for i in range(1, n + 1):
            labels[i] = m.addVar(vtype=GRB.INTEGER, lb=0, name=f"label_{i}")
        
        # span là maximum của tất cả labels
        span = m.addVar(vtype=GRB.INTEGER, lb=0, name="span")
        
        # Ràng buộc: labels[i] <= span cho mọi i
        for i in range(1, n + 1):
            m.addConstr(labels[i] <= span, name=f"span_constraint_{i}")
        
        # Ràng buộc radio: |labels[i] - labels[j]| >= C[i][j]
        # Sử dụng big-M với biến nhị phân
        M = n * K  # Big-M constant
        b = {}  # Biến nhị phân để mô hình OR constraint
        
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                req = C[i][j]
                if req <= 0: continue
                
                # Biến nhị phân: b[i][j] = 0 nếu labels[i] - labels[j] >= req
                #                b[i][j] = 1 nếu labels[j] - labels[i] >= req
                b[i, j] = m.addVar(vtype=GRB.BINARY, name=f"b_{i}_{j}")
                
                # Nếu b[i][j] = 0: labels[i] - labels[j] >= req
                m.addConstr(labels[i] - labels[j] >= req - M * b[i, j], name=f"radio1_{i}_{j}")

                # Nếu b[i][j] = 1: labels[j] - labels[i] >= req
                m.addConstr(labels[j] - labels[i] >= req - M * (1 - b[i, j]), name=f"radio2_{i}_{j}")
        
        # Hàm mục tiêu: minimize span
        m.setObjective(span, GRB.MINIMIZE)
        
        start_time = time.time()
        m.optimize()
        elapsed_time = float(format(time.time() - start_time, ".3f"))
        
        # Kiểm tra kết quả
        if m.status == GRB.OPTIMAL:
            status = "optimal"
            print_to_console(f"[GUROBI] Optimal solution found. Time: {elapsed_time}s")
        else:
            assert m.status == GRB.TIME_LIMIT and m.SolCount > 0
            elapsed_time = TIME_LIMIT
            status = "timeout"
            print_to_console(f"[GUROBI] Timeout. Time: {TIME_LIMIT}s")
        
        result_labels = [0] * (n + 1)
        for i in range(1, n + 1): result_labels[i] = int(labels[i].X)
        result_span = int(span.X)
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