from typing import List, Set, Tuple
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

def build_adjacency_list(n: int, edges: List[Tuple[int, int]]) -> List[Set[int]]:
    """Build adjacency list from edges. Vertices are 1-indexed."""
    adj = [set() for _ in range(n + 1)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj

def get_neighbors(adj: List[Set[int]], vertices: Set[int]) -> Set[int]:
    """Get all neighbors of vertices in the given set."""
    neighbors = set()
    for v in vertices:
        neighbors.update(adj[v])
    return neighbors

def enumerate_maximal_cliques(n: int, adj: List[Set[int]]) -> List[Set[int]]:
    """
    Find all maximal cliques using Bron-Kerbosch algorithm with pivoting.
    Returns a list of sets, each representing a maximal clique.
    """
    all_cliques = []
    
    def bron_kerbosch(R: Set[int], P: Set[int], X: Set[int]) -> None:
        if not P and not X:
            # Found a maximal clique
            all_cliques.append(R.copy())
            return
        
        # Choose pivot u from P ∪ X with maximum degree in P ∪ X
        union = P | X
        if not union:
            return
        
        u = max(union, key=lambda v: len(adj[v] & union))
        
        # Iterate over vertices in P that are not neighbors of u
        candidates = P - adj[u]
        
        for v in list(candidates):
            bron_kerbosch(
                R | {v},
                P & adj[v],
                X & adj[v]
            )
            P.remove(v)
            X.add(v)
    
    # Start with all vertices in P
    initial_P = set(range(1, n + 1))
    bron_kerbosch(set(), initial_P, set())
    
    print(f"All cliques: {all_cliques}")
    return all_cliques

def compute_layers(n: int, adj: List[Set[int]], L_0: Set[int], p: int) -> List[Set[int]]:
    """
    Compute layers L_0, L_1, ..., L_p.
    L_0 is given, and L_{i+1} = N(L_i) - (L_0 ∪ L_1 ∪ ... ∪ L_i).
    Returns list of layers.
    """
    layers = [L_0]
    all_covered = L_0.copy()
    
    for i in range(p):
        neighbors = get_neighbors(adj, layers[i])
        L_next = neighbors - all_covered
        assert len(L_next) > 0
        layers.append(L_next)
        all_covered.update(L_next)
    
    return layers

def compute_lower_bound_for_layers(layers: List[Set[int]], p: int) -> int:
    """
    Compute the lower bound using the formula:
    rck(G) >= (|Dk| - 2p - 1) + (α + β) + 2(∑_{i=0}^{p} |L_i|(p - i))
    
    We try all possible values of α and β (which indicate which layers
    contain vertices a_1 and a_{|Dk|}).
    """
    # |Dk| = total vertices in all layers
    Dk_size = sum(len(L_i) for L_i in layers)
    
    if Dk_size == 0:
        return 0
    
    # Try all possible values of α and β from {0, 1, ..., p}
    # Check if the layers have vertices
    # Compute the sum: ∑_{i=0}^{p} |L_i|(p - i)
    sum_term = sum(len(layers[i]) * (p - i) for i in range(min(p + 1, len(layers))))
    
    # Apply the formula
    if len(layers[0]) == 1:
        lower_bound = (Dk_size - 2 * p - 1) + 1 + 2 * sum_term
    else:
        lower_bound = (Dk_size - 2 * p - 1) + 2 * sum_term
    
    return lower_bound

def run_lb_2017(n: int, K: int, delta: int, input: str, edges: List[Tuple[int, int]]) -> int:
    """
    Compute lower bound using the 2017 formula based on layers.
    
    Args:
        n: number of vertices
        K: k value for radio k-coloring
        delta: difference between diameter and k
        input: input file name for logging
        edges: list of edges (required for building adjacency list)
    """
    lower_bound: int = 0
    if n == 1: lower_bound = 0
    elif n == 2: lower_bound = 1 if delta == 0 else 0
    elif K < 1: lower_bound = 0
    else:
        # Build adjacency list
        adj = build_adjacency_list(n, edges)
        
        p = K // 2
        best_lower_bound = 0
        
        if K % 2 == 0:
            # k = 2p (even): Try all vertices as L_0
            for start_vertex in range(1, n + 1):
                L_0 = {start_vertex}
                layers = compute_layers(n, adj, L_0, p)
                lb = compute_lower_bound_for_layers(layers, p)
                best_lower_bound = max(best_lower_bound, lb)
        else:
            # k = 2p + 1 (odd): Try all maximal cliques as L_0
            all_cliques = enumerate_maximal_cliques(n, adj)
            
            if not all_cliques:
                # If no cliques found (shouldn't happen), use single vertices
                all_cliques = [{v} for v in range(1, n + 1)]
            
            for clique in all_cliques:
                L_0 = clique
                layers = compute_layers(n, adj, L_0, p)
                lb = compute_lower_bound_for_layers(layers, p)
                best_lower_bound = max(best_lower_bound, lb)
        
        lower_bound = max(0, best_lower_bound)
    
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