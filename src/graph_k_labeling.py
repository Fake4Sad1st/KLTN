from __future__ import annotations
from typing import List, Tuple
from datetime import datetime
import os
import argparse
import igraph as ig


# ========== I/O + KHOẢNG CÁCH ==========
INF: int = 10**15

def read_graph(filename: str) -> Tuple[int, List[Tuple[int, int]]]:
    with open(filename, 'r') as f:
        n, m = map(int, f.readline().split())
        edges: List[Tuple[int, int]] = []
        for _ in range(m):
            a, b = map(int, f.readline().split())
            edges.append((a, b))
    return n, edges


def compute_distance_matrix(n: int, edges: List[Tuple[int, int]]) -> List[List[int]]:
    dist = [[INF] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dist[i][i] = 0
    for a, b in edges:
        dist[a][b] = 1
        dist[b][a] = 1
    for k in range(1, n + 1):
        for i in range(1, n + 1):
            dik = dist[i][k]
            if dik >= INF:
                continue
            for j in range(1, n + 1):
                    dist[i][j] = min(dist[i][j], dik + dist[k][j])
    return dist


def diameter_from_dist(dist: List[List[int]], n: int) -> int:
    diam = 0
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if dist[i][j] >= INF:
                raise ValueError("Graph is disconnected.")
            if i != j:
                dij = int(dist[i][j])
                if dij > diam:
                    diam = dij
    return diam


def compute_orbits(n: int, edges: List[Tuple[int, int]], graph_type: str, graph_level: str) -> List[int]:
    """
    Tính orbit của đồ thị sử dụng igraph.
    Trả về list các orbit, mỗi orbit là list các vertex (1-indexed).
    """
    if graph_type == "friendship" and int(graph_level) > 5:
        return [1, 2]

    if graph_type == "book" and int(graph_level) > 5:
        return [1, 3]
    
    # Tạo đồ thị igraph (0-indexed)
    g = ig.Graph()
    g.add_vertices(n)
    g.add_edges([(a-1, b-1) for a, b in edges])
    
    # Tính automorphism group và orbit
    # Sử dụng get_automorphisms_vf2() để lấy tất cả automorphisms
    automorphisms = g.get_automorphisms_vf2()
    
    # Tính orbit: các vertex có cùng orbit nếu có automorphism map chúng với nhau
    # Khởi tạo: mỗi vertex bắt đầu với orbit chỉ chứa chính nó
    orbits_dict = {}
    for v in range(n):
        orbits_dict[v] = set([v])
    
    # Cập nhật orbit từ các automorphisms
    for aut in automorphisms:
        for v in range(n):
            orbits_dict[v].add(aut[v])
    
    # Gom nhóm các vertex có cùng orbit
    # Hai vertex có cùng orbit nếu chúng có cùng tập orbit
    seen = set()
    orbit_vertices : List[int] = []
    for v in range(n):
        if v not in seen:
            orbit_set = orbits_dict[v]
            # Tìm tất cả vertex có cùng orbit_set
            for u in range(n):
                if orbits_dict[u] == orbit_set:
                    seen.add(u)
            orbit_vertices.append(v + 1)
    
    print_to_console(f"Orbit vertices: {orbit_vertices}")
    print_to_console(f"Number of orbit_vertices: {len(orbit_vertices)}")
    return orbit_vertices


# ========== VALIDATION ==========
def validate_labels(labels: List[int], dist: List[List[int]], K: int, n: int) -> Tuple[bool, str]:
    # Radio K-labeling condition:
    # For all i < j: |f(i) - f(j)| >= K + 1 - d(i, j)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            lhs = abs(labels[i] - labels[j])
            rhs = K + 1 - dist[i][j]
            if lhs < rhs:
                return False, (
                    f"Violation at pair ({i},{j}): |{labels[i]} - {labels[j]}| = {lhs} < {rhs} = K + 1 - d(i, j)"
                )
    return True, ""


# ========== INTERFACE + REGISTRY ==========
def build_C(dist: List[List[int]], n: int, K: int) -> List[List[int]]:
    # Constraint matrix C where C[i][j] is the minimum label difference required between i and j
    C: List[List[int]] = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i == j:
                C[i][j] = INF
            else:
                val = K + 1 - dist[i][j]
                C[i][j] = val if val > 0 else 0
    return C

# Import algorithm run functions
from algorithms.sat_pysat import run_sat_pysat
from algorithms.smt_z3 import run_smt_z3
from algorithms.ub_2020 import run_ub_2020
from algorithms.ub_2019 import run_ub_2019
from algorithms.gurobi_mip import run_gurobi
from algorithms.cplex_mip import run_cplex_mip
# from algorithms.lb_2012 import run_lb_2012
# from algorithms.lb_2017 import run_lb_2017

# Supported algorithms
GUROBI = "gurobi_mip"
CPLEX_MIP = "cplex_mip"
LB_2012 = "lb_2012"
LB_2017 = "lb_2017"
UB_2020 = "ub_2020"
UB_2019 = "ub_2019"
SAT_PYSAT = "sat_pysat"
SMT_Z3 = "smt_z3"

SUPPORTED_ALGORITHMS = [UB_2020, UB_2019, SAT_PYSAT, SMT_Z3, GUROBI, CPLEX_MIP]

# --- simple logging for CLI driver ---
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_logs_dir = os.path.join(_repo_root, "logs")
os.makedirs(_logs_dir, exist_ok=True)

_log_file_handle = None
saved_text: str = ""

def init_log_file(base_name: str) -> None:
    global _log_file_handle
    if _log_file_handle is not None:
        return
    fname = f"{base_name}.log"
    _log_file_handle = open(os.path.join(_logs_dir, fname), "a", buffering=1)

def print_to_console(*args, **kwargs) -> None:
    print(*args, **kwargs)
    global saved_text
    saved_text += f"{args[0]}\n"

def write_to_log_file() -> None:
    if _log_file_handle is not None:
        print(saved_text, file=_log_file_handle)
        _log_file_handle.flush()

# ========== CLI TỐI GIẢN: CHỈ CHỌN THUẬT TOÁN ==========
def main() -> None:
    parser = argparse.ArgumentParser(description="Radio k-labeling (CLI: --algo, --input)")
    parser.add_argument("--algo", required=True, help=f"Algorithm name. Available: {', '.join(SUPPORTED_ALGORITHMS)}")
    parser.add_argument("--input", required=True, help="Graph file path.")
    parser.add_argument("--delta", type=int, default=0, help="Difference between diameter and k.")
    # parser.add_argument("--bound", type=int, default=None, help="Test a specific span bound.")
    parser.add_argument("--lb", type=int, default=None, help="Lower bound for the span.")
    parser.add_argument("--ub", type=int, default=None, help="Upper bound for the span.")
    args = parser.parse_args()

    if args.algo not in SUPPORTED_ALGORITHMS:
        raise SystemExit(f"Algorithm '{args.algo}' is not supported. Available algorithms: {', '.join(SUPPORTED_ALGORITHMS)}")
    
    # if args.bound is not None and args.bound < 0:
    #     raise SystemExit(f"Bound must be non-negative, got {args.bound}")

    init_log_file(args.algo)
    print_to_console(f"==================================================")
    print_to_console(f"[{datetime.now().isoformat(timespec='seconds')}]")
    print_to_console(f"Input file: {args.input}")
    n, edges = read_graph(args.input)

    graph_type = args.input.split("/")[-2]
    graph_level = args.input.split("/")[-1].split(".")[0]
    short_input = graph_type + "_" + graph_level

    dist = compute_distance_matrix(n, edges)
    dia = diameter_from_dist(dist, n)
    K = dia + args.delta
    if K < 0:
        print_to_console(f"K should not be negative, got {K}")
        K = 0
    C = build_C(dist, n, K)
    
    print_to_console(f"Algorithm: {args.algo}")
    print_to_console(f"n={n}, diameter={dia}, delta={args.delta}")

    def validate(labels: List[int]):
        ok, msg = validate_labels(labels, dist, K, n)
        if ok: print_to_console("Validate: OK (satisfies radio constraint)")
        else:
            print_to_console(f"Validate: FAIL - {msg}")
            write_to_log_file()
            raise SystemExit(f"Validation failed!!!")

    global saved_text
    if args.algo == UB_2020:
        labels, span = run_ub_2020(n, C, args.delta, short_input)
        print_to_console(f"Span found = {span}")
        print_to_console(f"Labels: {labels[1:]}")
        validate(labels)
    
    elif args.algo == UB_2019:
        labels, span = run_ub_2019(n, C, dist, args.delta, short_input)
        print_to_console(f"Span found = {span}")
        print_to_console(f"Labels: {labels[1:]}")
        validate(labels)
    
    elif args.algo == GUROBI:
        labels, span, text = run_gurobi(n, C, K, args.delta, short_input)
        saved_text += text
        print_to_console(f"Span found = {span}")
        print_to_console(f"Labels: {labels[1:]}")
        validate(labels)

    elif args.algo == CPLEX_MIP:
        labels, span, text = run_cplex_mip(n, C, K, args.delta, short_input)
        saved_text += text
        print_to_console(f"Span found = {span}")
        print_to_console(f"Labels: {labels[1:]}")
        validate(labels)

    # elif args.algo == LB_2012:
    #     if args.delta > 0: raise SystemExit(f"Delta must be non-positive, got {args.delta}")
    #     lower_bound = run_lb_2012(n, dist, K, args.delta, short_input)
    #     print_to_console(f"LowerBound found = {lower_bound}")
    
    # elif args.algo == LB_2017:
    #     if args.delta > 0: raise SystemExit(f"Delta must be non-positive, got {args.delta}")
    #     lower_bound = run_lb_2017(n, K, args.delta, short_input, edges)
    #     print_to_console(f"LowerBound found = {lower_bound}")

    elif args.algo in [SAT_PYSAT, SMT_Z3]:
        if args.lb is not None: lower_bound = args.lb
        else: lower_bound = n - 1 if args.delta >= 0 else 0
        if args.ub is not None: upper_bound = args.ub
        else: upper_bound = (n - 1) * K
        orbit_vertices = compute_orbits(n, edges, graph_type, graph_level)
        if args.algo == SAT_PYSAT: labels, upper, lower, text = run_sat_pysat(n, C, args.delta, orbit_vertices, short_input, upper_bound, lower_bound)
        else: labels, upper, lower, text = run_smt_z3(n, C, args.delta, orbit_vertices, short_input, upper_bound, lower_bound)
        
        saved_text += text
        print_to_console(f"Upper bound = {upper}")
        print_to_console(f"Lower bound = {lower}")
        print_to_console(f"Labels: {labels[1:]}")
        validate(labels)

    write_to_log_file()

if __name__ == "__main__":
    main()
