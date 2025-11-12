#!/usr/bin/env bash
set -euo pipefail

# Move to repo root where the Makefile lives
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Generating graphs with Makefile targets..."

# path: n = 1..25
echo "- Generating path graphs (n=1..25)"
for n in $(seq 1 25); do
  make -s path n="$n"
done

# cycle: n = 3..25 (n<=2 degenerates to path per implementation)
echo "- Generating cycle graphs (n=3..25)"
for n in $(seq 3 25); do
  make -s cycle n="$n"
done

# bintree: k = 0..11
echo "- Generating binomial trees (bintree k=0..11)"
for k in $(seq 0 11); do
  make -s bintree k="$k"
done

# trisnake: k = 1..15
echo "- Generating trisnake (k=1..15)"
for k in $(seq 1 15); do
  make -s trisnake k="$k"
done

# c4snake: k = 1..15
echo "- Generating c4snake (k=1..15)"
for k in $(seq 1 15); do
  make -s c4snake k="$k"
done

# c6snake: k = 1..15
echo "- Generating c6snake (k=1..15)"
for k in $(seq 1 15); do
  make -s c6snake k="$k"
done

# book: k = 1..15 (Makefile uses default n=2)
echo "- Generating book graphs (k=1..15)"
for k in $(seq 1 15); do
  make -s book k="$k"
done

# friendship: k = 1..15
echo "- Generating friendship graphs (k=1..15)"
for k in $(seq 1 15); do
  make -s friendship k="$k"
done

# ladder: k = 1..15
echo "- Generating ladder graphs (k=1..15)"
for k in $(seq 1 15); do
  make -s ladder k="$k"
done

echo "Done. Outputs are under graph_gen/<type>/*.txt"
