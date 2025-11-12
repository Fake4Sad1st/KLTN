#!/usr/bin/env bash
set -euo pipefail

# Resolve repo root (this script is under scripts)
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

for k in $(seq 1 25); do
  python3 ./src/graph_k_labeling.py --algo smt_z3 --input ./graph_gen/path/$k.txt --delta -1
done

for k in $(seq 3 25); do
  python3 ./src/graph_k_labeling.py --algo smt_z3 --input ./graph_gen/cycle/$k.txt --delta -1
done

for k in $(seq 1 15); do
  python3 ./src/graph_k_labeling.py --algo smt_z3 --input ./graph_gen/book/$k.txt --delta -1
done

for k in $(seq 1 15); do
  python3 ./src/graph_k_labeling.py --algo smt_z3 --input ./graph_gen/ladder/$k.txt --delta -1
done

for k in $(seq 1 15); do
  python3 ./src/graph_k_labeling.py --algo smt_z3 --input ./graph_gen/friendship/$k.txt --delta -1
done

for k in $(seq 1 15); do
  python3 ./src/graph_k_labeling.py --algo smt_z3 --input ./graph_gen/trisnake/$k.txt --delta -1
done

for k in $(seq 1 15); do
  python3 ./src/graph_k_labeling.py --algo smt_z3 --input ./graph_gen/c4snake/$k.txt --delta -1
done

for k in $(seq 1 15); do
  python3 ./src/graph_k_labeling.py --algo smt_z3 --input ./graph_gen/c6snake/$k.txt --delta -1
done

for k in $(seq 0 7); do
  python3 ./src/graph_k_labeling.py --algo smt_z3 --input ./graph_gen/bintree/$k.txt --delta -1
done