from __future__ import annotations
from typing import List, Tuple
import argparse
import random
import os


def write_graph(n: int, edges: List[Tuple[int, int]], output: str) -> None:
    norm = set()
    for u, v in edges:
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        norm.add((a, b))
    edges = sorted(norm)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w") as f:
        f.write(f"{n} {len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")


def path_graph(n: int) -> Tuple[int, List[Tuple[int, int]]]:
    if n < 1:
        return 0, []
    edges = [(i, i + 1) for i in range(1, n)]
    return n, edges


def cycle_graph(n: int) -> Tuple[int, List[Tuple[int, int]]]:
    if n <= 2:
        return path_graph(n)
    edges = [(i, i + 1) for i in range(1, n)]
    edges.append((n, 1))
    return n, edges


def complete_graph(n: int) -> Tuple[int, List[Tuple[int, int]]]:
    edges = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            edges.append((i, j))
    return n, edges


def star_graph(n: int, center: int = 1) -> Tuple[int, List[Tuple[int, int]]]:
    if n < 1:
        return 0, []
    if center < 1 or center > n:
        center = 1
    edges = []
    for v in range(2, n + 1):
        if v != center:
            edges.append((center, v))
    return n, edges


def grid_graph(rows: int, cols: int) -> Tuple[int, List[Tuple[int, int]]]:
    if rows < 1 or cols < 1:
        return 0, []
    def idx(r: int, c: int) -> int:
        return (r - 1) * cols + c
    n = rows * cols
    edges: List[Tuple[int, int]] = []
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            u = idx(r, c)
            if c + 1 <= cols:
                edges.append((u, idx(r, c + 1)))
            if r + 1 <= rows:
                edges.append((u, idx(r + 1, c)))
    return n, edges


def complete_bipartite(n1: int, n2: int) -> Tuple[int, List[Tuple[int, int]]]:
    if n1 < 0 or n2 < 0:
        return 0, []
    n = n1 + n2
    edges: List[Tuple[int, int]] = []
    for a in range(1, n1 + 1):
        for b in range(n1 + 1, n + 1):
            edges.append((a, b))
    return n, edges


def random_tree(n: int, seed: int | None = None) -> Tuple[int, List[Tuple[int, int]]]:
    if n <= 1:
        return n, []
    rng = random.Random(seed)
    prufer = [rng.randrange(1, n + 1) for _ in range(n - 2)]
    degree = [1] * (n + 1)
    for x in prufer:
        degree[x] += 1
    from heapq import heapify, heappush, heappop
    leaves = [i for i in range(1, n + 1) if degree[i] == 1]
    heapify(leaves)
    edges: List[Tuple[int, int]] = []
    for x in prufer:
        leaf = heappop(leaves)
        edges.append((leaf, x))
        degree[leaf] -= 1
        degree[x] -= 1
        if degree[x] == 1:
            heappush(leaves, x)
    u = heappop(leaves)
    v = heappop(leaves)
    edges.append((u, v))
    return n, edges


def random_gnp(n: int, p: float, seed: int | None = None) -> Tuple[int, List[Tuple[int, int]]]:
    rng = random.Random(seed)
    edges: List[Tuple[int, int]] = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            if rng.random() < p:
                edges.append((i, j))
    return n, edges


def triangular_snake(k: int) -> Tuple[int, List[Tuple[int, int]]]:
    # Δ_k-snake: triangles {2i-1, 2i, 2i+1} chained by a single cut vertex
    if k <= 0:
        return 0, []
    n = 2 * k + 1
    edges: List[Tuple[int, int]] = []
    for i in range(1, k + 1):
        a, b, c = 2 * i - 1, 2 * i, 2 * i + 1
        edges += [(a, b), (b, c), (c, a)]
    return n, edges


def cycle_snake(k: int, n: int) -> Tuple[int, List[Tuple[int, int]]]:
    # k copies of C_n chained; consecutive cycles share exactly one vertex
    if k <= 0 or n <= 0:
        return 0, []
    if n == 1:
        return k, [(i, i) for i in range(1, k + 1)]  # normalized out by write_graph
    if n == 2:
        # Chain of edges with shared vertex degenerates to a path
        return path_graph(k + 1)
    if n == 3:
        return triangular_snake(k)

    edges: List[Tuple[int, int]] = []
    # First cycle on vertices 1..n
    total_v = n
    cyc = list(range(1, n + 1))
    for i in range(n):
        u, v = cyc[i], cyc[(i + 1) % n]
        edges.append((u, v))
    # Choose a vertex on first cycle to connect to the next cycle
    shared = cyc[-1]

    # Remaining cycles
    for _ in range(2, k + 1):
        new_vs = list(range(total_v + 1, total_v + (n - 1) + 1))
        total_v += (n - 1)
        C = [shared] + new_vs
        for i in range(n):
            u, v = C[i], C[(i + 1) % n]
            edges.append((u, v))
        # Pick the next shared vertex to be maximally distant from the current shared in C
        shared = C[(n // 2)]

    return total_v, edges


def cartesian_product(n1: int, E1: List[Tuple[int, int]],
                      n2: int, E2: List[Tuple[int, int]]) -> Tuple[int, List[Tuple[int, int]]]:
    # Vertices are (x,y) with x in [1..n1], y in [1..n2], 1-indexed
    def idx(x: int, y: int) -> int:
        return (x - 1) * n2 + y

    edges: List[Tuple[int, int]] = []
    # Edges from E1 across all y
    for (u, v) in E1:
        for y in range(1, n2 + 1):
            edges.append((idx(u, y), idx(v, y)))
    # Edges from E2 across all x
    for (a, b) in E2:
        for x in range(1, n1 + 1):
            edges.append((idx(x, a), idx(x, b)))
    return n1 * n2, edges


def stacked_book(k: int, n: int = 2) -> Tuple[int, List[Tuple[int, int]]]:
    # User-requested: B_{k,n} = S_k x P_n with default n=2.
    # Here S_k denotes the star on k vertices (1 center + k leaves).
    if k < 1 or n < 1:
        return 0, []
    nS, ES = star_graph(k, center=1)
    nP, EP = path_graph(n)
    return cartesian_product(nS, ES, nP, EP)


def friendship_graph(k: int) -> Tuple[int, List[Tuple[int, int]]]:
    # F_k: k triangles sharing one common center
    if k <= 0:
        return 0, []
    n = 2 * k + 1
    c = 1
    edges: List[Tuple[int, int]] = []
    nxt = 2
    for _ in range(k):
        a, b = nxt, nxt + 1
        nxt += 2
        edges += [(c, a), (c, b), (a, b)]
    return n, edges


def ladder_graph(k: int) -> Tuple[int, List[Tuple[int, int]]]:
    # L_n = P_2 x P_n (two rails with n rungs)
    n1, E1 = path_graph(2)
    n2, E2 = path_graph(k)
    return cartesian_product(n1, E1, n2, E2)


def binomial_tree(k: int) -> Tuple[int, List[Tuple[int, int]]]:
    # Binomial tree B_k with n = 2^k vertices
    if k < 0:
        return 0, []
    def build(order: int, base: int) -> Tuple[int, int, List[Tuple[int, int]]]:
        # returns (root_index, last_index, edges)
        if order == 0:
            return base, base, []
        size_sub = 1 << (order - 1)
        left_root, left_last, E_left = build(order - 1, base)
        right_root, right_last, E_right = build(order - 1, base + size_sub)
        E_left.append((left_root, right_root))
        return left_root, right_last, E_left + E_right
    n = 1 << k
    if n == 0:
        return 0, []
    root, last, edges = build(k, 1)
    return n, edges


def _default_output_base() -> str:
    # Place outputs under repo_root/graph_gen/<cmd>/...
    here = os.path.dirname(__file__)  # .../src/graph_gen
    return here


def _sanitize(x: str) -> str:
    return ''.join(ch if ch.isalnum() or ch in ('-', '_') else '_' for ch in x)


def _compute_default_output(args: argparse.Namespace) -> str:
    base = _default_output_base()
    cmd = args.cmd
    if cmd == "path":
        name = f"{args.n}.txt"
    elif cmd == "cycle":
        name = f"{args.n}.txt"
    elif cmd == "grid":
        name = f"{args.rows}_{args.cols}.txt"
    elif cmd == "complete":
        name = f"{args.n}.txt"
    elif cmd == "star":
        name = f"{args.n}_c{args.center}.txt"
    elif cmd == "kbip":
        name = f"{args.n1}_{args.n2}.txt"
    elif cmd == "tree":
        if args.seed is None:
            name = f"{args.n}.txt"
        else:
            name = f"{args.n}_seed{args.seed}.txt"
    elif cmd == "gnp":
        pstr = _sanitize(str(args.p).replace('.', '_'))
        if args.seed is None:
            name = f"{args.n}_p{pstr}.txt"
        else:
            name = f"{args.n}_p{pstr}_seed{args.seed}.txt"
    elif cmd == "trisnake":
        name = f"{args.k}.txt"
    elif cmd == "cnsnake":
        name = f"{args.k}_n{args.n}.txt"
    elif cmd == "c4snake" or cmd == "c6snake":
        name = f"{args.k}.txt"
    elif cmd == "book":
        name = f"{args.k}.txt"
    elif cmd == "friendship":
        name = f"{args.k}.txt"
    elif cmd == "ladder":
        name = f"{args.k}.txt"
    elif cmd == "bintree":
        name = f"{args.k}.txt"
    else:
        name = "graph.txt"
    out_dir = os.path.join(base, cmd)
    return os.path.join(out_dir, name)

def main() -> None:
    parser = argparse.ArgumentParser(description="Graph generator -> input.txt format (1-indexed)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_path = sub.add_parser("path", help="Đường thẳng (path) với n đỉnh")
    p_path.add_argument("--n", type=int, required=True)
    p_path.add_argument("--output", nargs='?', const=None, default=None)
    p_path.set_defaults(func=lambda a: path_graph(a.n))

    p_cycle = sub.add_parser("cycle", help="Chu trình (cycle) với n đỉnh")
    p_cycle.add_argument("--n", type=int, required=True)
    p_cycle.add_argument("--output", nargs='?', const=None, default=None)
    p_cycle.set_defaults(func=lambda a: cycle_graph(a.n))

    p_comp = sub.add_parser("complete", help="Đồ thị đầy đủ K_n")
    p_comp.add_argument("--n", type=int, required=True)
    p_comp.add_argument("--output", nargs='?', const=None, default=None)
    p_comp.set_defaults(func=lambda a: complete_graph(a.n))

    p_star = sub.add_parser("star", help="Đồ thị sao với n đỉnh, tâm là 'center'")
    p_star.add_argument("--n", type=int, required=True)
    p_star.add_argument("--center", type=int, default=1)
    p_star.add_argument("--output", nargs='?', const=None, default=None)
    p_star.set_defaults(func=lambda a: star_graph(a.n, a.center))

    p_grid = sub.add_parser("grid", help="Lưới 2D 'rows' x 'cols' (kề 4 hướng)")
    p_grid.add_argument("--rows", type=int, required=True)
    p_grid.add_argument("--cols", type=int, required=True)
    p_grid.add_argument("--output", nargs='?', const=None, default=None)
    p_grid.set_defaults(func=lambda a: grid_graph(a.rows, a.cols))

    p_kmn = sub.add_parser("kbip", help="Song phương đầy đủ K_{n1,n2}")
    p_kmn.add_argument("--n1", type=int, required=True)
    p_kmn.add_argument("--n2", type=int, required=True)
    p_kmn.add_argument("--output", nargs='?', const=None, default=None)
    p_kmn.set_defaults(func=lambda a: complete_bipartite(a.n1, a.n2))

    p_tree = sub.add_parser("tree", help="Cây ngẫu nhiên với n đỉnh (Prüfer)")
    p_tree.add_argument("--n", type=int, required=True)
    p_tree.add_argument("--seed", type=int, default=None)
    p_tree.add_argument("--output", nargs='?', const=None, default=None)
    p_tree.set_defaults(func=lambda a: random_tree(a.n, a.seed))

    p_gnp = sub.add_parser("gnp", help="Erdos-Renyi G(n,p)")
    p_gnp.add_argument("--n", type=int, required=True)
    p_gnp.add_argument("--p", type=float, required=True)
    p_gnp.add_argument("--seed", type=int, default=None)
    p_gnp.add_argument("--output", nargs='?', const=None, default=None)
    p_gnp.set_defaults(func=lambda a: random_gnp(a.n, a.p, a.seed))

    p_tris = sub.add_parser("trisnake", help="k-triangular snake Δ_k")
    p_tris.add_argument("--k", type=int, required=True)
    p_tris.add_argument("--output", nargs='?', const=None, default=None)
    p_tris.set_defaults(func=lambda a: triangular_snake(a.k))

    p_cns = sub.add_parser("cnsnake", help="k·C_n-snake (chuỗi k chu trình n-đỉnh, kề nhau tại 1 đỉnh)")
    p_cns.add_argument("--k", type=int, required=True)
    p_cns.add_argument("--n", type=int, required=True)
    p_cns.add_argument("--output", nargs='?', const=None, default=None)
    p_cns.set_defaults(func=lambda a: cycle_snake(a.k, a.n))

    p_c4 = sub.add_parser("c4snake", help="k·C_4-snake")
    p_c4.add_argument("--k", type=int, required=True)
    p_c4.add_argument("--output", nargs='?', const=None, default=None)
    p_c4.set_defaults(func=lambda a: cycle_snake(a.k, 4))

    p_c6 = sub.add_parser("c6snake", help="k·C_6-snake")
    p_c6.add_argument("--k", type=int, required=True)
    p_c6.add_argument("--output", nargs='?', const=None, default=None)
    p_c6.set_defaults(func=lambda a: cycle_snake(a.k, 6))

    p_book = sub.add_parser("book", help="Stacked book B_{k+1,n} = S_(k+1) x P_n (mặc định n=2)")
    p_book.add_argument("--k", type=int, required=True)
    p_book.add_argument("--n", type=int, default=2)
    p_book.add_argument("--output", nargs='?', const=None, default=None)
    p_book.set_defaults(func=lambda a: stacked_book(a.k + 1, a.n))

    p_friend = sub.add_parser("friendship", help="Friendship F_k (windmill k tam giác)")
    p_friend.add_argument("--k", type=int, required=True)
    p_friend.add_argument("--output", nargs='?', const=None, default=None)
    p_friend.set_defaults(func=lambda a: friendship_graph(a.k))

    p_ladder = sub.add_parser("ladder", help="Ladder L_k = P_2 x P_(k+1) (hai ray, k+1 bậc)")
    p_ladder.add_argument("--k", type=int, required=True)
    p_ladder.add_argument("--output", nargs='?', const=None, default=None)
    p_ladder.set_defaults(func=lambda a: ladder_graph(a.k + 1))

    p_bint = sub.add_parser("bintree", help="Binomial tree B_k (n = 2^k)")
    p_bint.add_argument("--k", type=int, required=True)
    p_bint.add_argument("--output", nargs='?', const=None, default=None)
    p_bint.set_defaults(func=lambda a: binomial_tree(a.k))

    args = parser.parse_args()
    n, edges = args.func(args)
    out_path = args.output if getattr(args, 'output', None) else _compute_default_output(args)
    write_graph(n, edges, out_path)


if __name__ == "__main__":
    main()


