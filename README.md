# Bài toán tô màu radio-k

Dự án nghiên cứu và so sánh các phương pháp giải Bài toán tô màu radio-k trên đồ thị.

## Mục lục

- [Hướng dẫn cài đặt](#hướng-dẫn-cài-đặt)
- [Cách chạy code](#cách-chạy-code)
- [Các phương pháp có sẵn](#các-phương-pháp-có-sẵn)
- [Cấu trúc dự án](#cấu-trúc-dự-án)

## Hướng dẫn cài đặt

### Yêu cầu hệ thống

- Python 3.10
- Pipenv (để quản lý môi trường ảo và dependencies)

### Bước 1: Cài đặt Pipenv

```bash
pip install pipenv
```

### Bước 2: Cài đặt dependencies

```bash
pipenv install
```

Các package sẽ được cài đặt:

- `python-sat` - SAT solver
- `pypblib` - PB constraint encoding
- `prettytable` - Hiển thị bảng đẹp
- `pandas` - Xử lý dữ liệu
- `z3-solver` - SMT solver
- `igraph` - Thư viện đồ thị
- `gurobipy==13.0.0` - Gurobi optimizer

### Bước 3: Cài đặt CPLEX (tùy chọn)

Để sử dụng CPLEX MIP solver:

1. Tải CPLEX từ IBM Academic Initiative
   - Phiên bản sử dụng: v22.1.1
   - Link: <https://www.ibm.com/academic/technology/data-science>

2. Cài đặt CPLEX Python API.

### Bước 4: Cài đặt Gurobi (tùy chọn)

Để sử dụng Gurobi MIP solver:

1. Tải Gurobi từ trang chủ
   - Phiên bản sử dụng: v13.0.0
   - Link: <https://www.gurobi.com/downloads/>

2. Kích hoạt license (academic license miễn phí):

```bash
grbgetkey <your-license-key>
```

### Bước 5: Kích hoạt môi trường

```bash
pipenv shell
```

## Cách chạy code

### 1. Sinh đồ thị test

Sử dụng Makefile để sinh các loại đồ thị khác nhau:

#### Sinh một đồ thị cụ thể

```bash
# Đường đi (path) với n đỉnh
make path n=10 out=./graph_gen/path/10.txt

# Chu trình (cycle) với n đỉnh
make cycle n=10 out=./graph_gen/cycle/10.txt

# Thang (ladder) với k bậc
make ladder k=5 out=./graph_gen/ladder/5.txt

# Sách (book) với k trang
make book k=5 out=./graph_gen/book/5.txt

# Friendship graph với k tam giác
make friendship k=5 out=./graph_gen/friendship/5.txt

# Triangle snake với k tam giác
make trisnake k=5 out=./graph_gen/trisnake/5.txt

# C4 snake với k chu trình C4
make c4snake k=5 out=./graph_gen/c4snake/5.txt

# C6 snake với k chu trình C6
make c6snake k=5 out=./graph_gen/c6snake/5.txt

# Binomial tree với độ sâu k
make bintree k=3 out=./graph_gen/bintree/3.txt
```

#### Sinh toàn bộ đồ thị test

```bash
bash scripts/graph_gen.sh
```

Script này sẽ sinh:

- Path graphs: n = 1..25
- Cycle graphs: n = 3..25
- Ladder graphs: k = 1..15
- Book graphs: k = 1..15
- Friendship graphs: k = 1..15
- Triangle snake: k = 1..15
- C4 snake: k = 1..15
- C6 snake: k = 1..15
- Binomial trees: k = 0..7

### 2. Chạy thuật toán

#### Chạy trực tiếp với Makefile

```bash
make label algo=<algorithm> input=<graph_file> delta=<delta>
```

Ví dụ:

```bash
make label algo=sat_pysat input=./graph_gen/path/10.txt delta=0
```

#### Chạy trực tiếp với Python

```bash
python3 src/graph_k_labeling.py --algo <algorithm> --input <graph_file> --delta <delta>
```

Ví dụ:

```bash
python3 src/graph_k_labeling.py --algo sat_pysat --input ./graph_gen/path/10.txt --delta=0
```

#### Tham số

- `--algo`: Tên thuật toán (xem danh sách bên dưới)
- `--input`: Đường dẫn đến file đồ thị
- `--delta`: Hiệu số giữa k và đường kính đồ thị (k = diameter + delta)
  - `delta=0`: k = diameter
  - `delta=-1`: k = diameter - 1
  - `delta=1`: k = diameter + 1

### 3. Chạy benchmark với scripts

Các script có sẵn trong thư mục `scripts/` để chạy benchmark trên nhiều đồ thị:

#### SAT solver (Glucose 3)

```bash
# Delta = 0
bash scripts/sat_pysat/delta_0.sh

# Delta = -1
bash scripts/sat_pysat/delta_neg1.sh

# Delta = 1
bash scripts/sat_pysat/delta_1.sh
```

#### SMT solver (Z3)

```bash
bash scripts/smt_z3/delta_0.sh
bash scripts/smt_z3/delta_neg1.sh
bash scripts/smt_z3/delta_1.sh
```

#### Gurobi MIP

```bash
bash scripts/gurobi_mip/delta_0.sh
bash scripts/gurobi_mip/delta_neg1.sh
bash scripts/gurobi_mip/delta_1.sh
```

#### CPLEX MIP

```bash
bash scripts/cplex_mip/delta_0.sh
bash scripts/cplex_mip/delta_neg1.sh
bash scripts/cplex_mip/delta_1.sh
```

#### Upper bounds

```bash
# Upper bound 2019
bash scripts/ub_2019/delta_0.sh
bash scripts/ub_2019/delta_neg1.sh
bash scripts/ub_2019/delta_1.sh

# Upper bound 2020
bash scripts/ub_2020/delta_0.sh
```

### 4. Xem kết quả

- **Logs**: Kết quả chi tiết được lưu trong thư mục `logs/`
  - `sat_pysat.log`
  - `smt_z3.log`
  - `gurobi_mip.log`
  - `cplex_mip.log`

- **Reports**: Kết quả tổng hợp dạng CSV trong thư mục `reports/`
  - `sat_pysat.csv` và `sat_pysat_final.csv`
  - `smt_z3.csv` và `smt_z3_final.csv`
  - `gurobi_mip.csv`
  - `cplex_mip.csv`

## Các phương pháp có sẵn

Dự án cài đặt các phương pháp giải Bài toán tô màu radio-k:

### 1. SAT Solver - Glucose 3 (`sat_pysat`)

- **Mô tả**: Giải bằng SAT solver với binary search trên span
- **File**: `src/algorithms/sat_pysat.py`
- **Ưu điểm**: Tìm được nghiệm tối ưu, hiệu quả với đồ thị có tính đối xứng cao
- **Sử dụng**: orbit vertices để giảm không gian tìm kiếm

**Cách chạy**:

```bash
make label algo=sat_pysat input=./graph_gen/path/10.txt delta=0
```

### 2. SMT Solver - Z3 (`smt_z3`)

- **Mô tả**: Giải bằng SMT solver với binary search trên span
- **File**: `src/algorithms/smt_z3.py`
- **Ưu điểm**: Linh hoạt, dễ mô hình hóa ràng buộc
- **Sử dụng**: orbit vertices để giảm không gian tìm kiếm

**Cách chạy**:

```bash
make label algo=smt_z3 input=./graph_gen/path/10.txt delta=0
```

### 3. Gurobi MIP (`gurobi_mip`)

- **Mô tả**: Giải bằng Mixed Integer Programming với Gurobi
- **File**: `src/algorithms/gurobi_mip.py`
- **Yêu cầu**: Gurobi v13.0.0 và license
- **Ưu điểm**: Solver thương mại mạnh mẽ, tối ưu hóa tốt

**Cách chạy**:

```bash
make label algo=gurobi_mip input=./graph_gen/path/10.txt delta=0
```

### 4. CPLEX MIP (`cplex_mip`)

- **Mô tả**: Giải bằng Mixed Integer Programming với CPLEX
- **File**: `src/algorithms/cplex_mip.py`
- **Yêu cầu**: IBM CPLEX v22.1.1 (IBM Academic Initiative)
- **Ưu điểm**: Solver IBM mạnh mẽ cho bài toán tối ưu

**Cách chạy**:

```bash
make label algo=cplex_mip input=./graph_gen/path/10.txt delta=0
```

### 5. Upper Bound 2019 (`ub_2019`)

- **Mô tả**: 2 thuật toán heuristic tìm upper bound (năm 2019)
- **File**: `src/algorithms/ub_2019.py`
- **Ưu điểm**: Nhanh, không cần solver
- **Hạn chế**: Không đảm bảo tối ưu

**Cách chạy**:

```bash
make label algo=ub_2019 input=./graph_gen/path/10.txt delta=0
```

### 6. Upper Bound 2020 (`ub_2020`)

- **Mô tả**: Thuật toán heuristic tìm upper bound (năm 2020)
- **File**: `src/algorithms/ub_2020.py`
- **Ưu điểm**: Nhanh, không cần solver
- **Hạn chế**: Không đảm bảo tối ưu; chỉ áp dụng được với `delta = 0`.

**Cách chạy**:

```bash
make label algo=ub_2020 input=./graph_gen/path/10.txt
```

## Cấu trúc dự án

``` text
.
├── README.md
├── Makefile                   ## Makefile để sinh đồ thị và chạy thuật toán
├── Pipfile                    ## Dependencies
├── Pipfile.lock               
├── graph_gen/                 ## Thư mục chứa đồ thị test
│   ├── gen.py                 # Script sinh đồ thị
│   ├── path/                  # Đường đi
│   ├── cycle/                 # Chu trình
│   ├── ladder/                # Thang
│   ├── book/                  # Sách
│   ├── friendship/            # Friendship
│   ├── trisnake/              # Triangle snake
│   ├── c4snake/               # C4 snake
│   ├── c6snake/               # C6 snake
│   └── bintree/               # Binomial tree
├── src/
│   ├── graph_k_labeling.py    # Core
│   └── algorithms/            ## Các thuật toán
│       ├── sat_pysat.py       # SAT solver
│       ├── smt_z3.py          # SMT solver
│       ├── gurobi_mip.py      # Gurobi MIP
│       ├── cplex_mip.py       # CPLEX MIP
│       ├── ub_2019.py         # Upper bound 2019
│       └── ub_2020.py         # Upper bound 2020
├── scripts/                   ## Scripts chạy benchmark
│   ├── graph_gen.sh           # Sinh toàn bộ đồ thị
│   ├── sat_pysat/
│   ├── smt_z3/
│   ├── gurobi_mip/
│   ├── cplex_mip/
│   ├── ub_2019/
│   └── ub_2020/
├── logs/                       # Ghi lại log được in ra trong quá trình chạy
└── reports/                    # Kết quả tổng hợp (CSV)
```

## License

Academic use only.

## Tham khảo

- CPLEX: v22.1.1 (IBM Academic Initiative)
- Gurobi: v13.0.0
