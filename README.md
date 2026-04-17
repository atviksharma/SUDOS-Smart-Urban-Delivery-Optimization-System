# 🚀 SUDOS – Smart Urban Delivery Optimization System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![DAA Course Project](https://img.shields.io/badge/DAA-Course%20Project-orange.svg)]()

A comprehensive implementation of multiple **Design and Analysis of Algorithms (DAA)** paradigms applied to real-world urban delivery route optimization — inspired by platforms like Amazon, Swiggy, and Blinkit.

---

## 📌 Problem Statement

Modern delivery platforms must optimize:
- **Delivery routes** across a city modeled as a weighted graph
- **Agent assignment** using network flow algorithms
- **Trade-offs** between computational cost and route quality

---

## 🏗️ Project Structure

```
SUDOS/
├── src/
│   ├── sudos.py          # Core algorithms (Dijkstra, FW, TSP variants, MaxFlow)
│   └── visualize.py      # Matplotlib visualizations
├── tests/
│   └── test_sudos.py     # Comprehensive unit tests
├── dataset/
│   └── sample_graph.py   # Graph datasets (small, medium, random)
├── outputs/              # Generated plots and results
├── docs/                 # Report and presentation
├── requirements.txt
└── README.md
```

---

## ✨ Key Features

- Multiple algorithm paradigms in one system
- Real-world delivery optimization modeling
- Performance benchmarking and visualization
- Scalable design with fallback strategies

## 🧠 Algorithms Implemented

| Paradigm | Algorithm | Complexity | Use Case |
|----------|-----------|------------|----------|
| **Graph** | Dijkstra's SSSP | O((V+E) log V) | Shortest path from depot |
| **Graph** | Floyd-Warshall | O(V³) | All-pairs shortest paths |
| **Greedy** | Nearest Neighbor TSP | O(V²) | Fast route approximation |
| **DP** | Bitmask TSP (Held-Karp) | O(2ᴺ · N²) | Optimal route (small N) |
| **Approximation** | Nearest Insertion | O(V²) | Better heuristic routes |
| **Network Flow** | Ford-Fulkerson | O(V · E) | Multi-agent assignment |

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/atviksharma/SUDOS-Smart-Urban-Delivery-Optimization-System.git
cd SUDOS
pip install -r requirements.txt
```

### 2. Run the Demo
### ▶️ Running the Project

This will:
- Generate a sample city graph
- Compute shortest paths using Dijkstra
- Run TSP algorithms for route optimization
- Assign delivery agents using Max-Flow

```bash
python src/sudos.py
```

### 3. Generate Visualizations
```bash
python src/visualize.py
```
## 📷 Visual Outputs

### City Graph
outputs/city_graph.png

### Algorithm Comparison
outputs/algo_comparison.png

### Agent Routes
outputs/agent_routes.png

### Scalability
outputs/scalability.png

### 4. Run Tests
```bash
python -m pytest tests/ -v
```

---

## 📊 Sample Output

```
City Graph: 12 nodes, 19 edges
Depot: Node 0 | Deliveries: [3, 5, 7, 9, 11] | Agents: 2

--- Dijkstra Shortest Paths from Depot ---
  Node 0 → 5: dist=18.0, path=[0, 1, 5]
  Node 0 → 11: dist=37.0, path=[0, 1, 5, 10, 11]

--- Algorithm Benchmark ---
  Greedy TSP:        cost=83, time=0.013 ms
  Nearest Insertion: cost=83, time=0.024 ms
  DP TSP (Exact):    cost=83, time=0.195 ms

--- Multi-Agent Routing ---
  Agent 1: [0→3→5→7→0], cost=81
  Agent 2: [0→9→11→0],  cost=76
  Total: 157
```

---

## 📈 Algorithm Comparison

| Algorithm | Cost (6 nodes) | Time | Optimality |
|-----------|---------------|------|------------|
| Greedy NN | 83 | ~0.01 ms | Approximate |
| Nearest Insertion | 83 | ~0.02 ms | Approximate |
| DP Bitmask | 83 | ~0.2 ms | **Exact** |

---

## 🧩 Key Design Decisions

1. **Floyd-Warshall for pre-computation**: All-pairs shortest paths pre-computed once, then reused by TSP routines — amortizes the O(V³) cost.
2. **Max-Flow for fairness**: Ford-Fulkerson ensures each delivery zone is assigned to exactly one agent, respecting agent capacity constraints.
3. **DP TSP cap at N≤15**: Bitmask DP grows as O(2ᴺ), so we fall back to heuristics for larger inputs automatically.
4. **Modular design**: Each algorithm is a pure function — easy to benchmark and swap.

---

## 🔬 Complexity Analysis

```
Algorithm             | Time          | Space     | Optimal?
----------------------|---------------|-----------|----------
Dijkstra              | O((V+E)log V) | O(V)      | Yes (SSSP)
Floyd-Warshall        | O(V³)         | O(V²)     | Yes (APSP)
Greedy TSP            | O(N²)         | O(N)      | No
Nearest Insertion     | O(N²)         | O(N)      | No (~1.3× OPT)
DP Bitmask TSP        | O(2ᴺ · N²)   | O(2ᴺ · N) | Yes
Ford-Fulkerson        | O(V · E)      | O(V+E)    | Yes (flow)
```

---

## 📝 Code Documentation

- All algorithms are implemented with detailed docstrings
- Inline comments explain key steps like edge relaxation, DP transitions, and flow augmentation
- Modular functions ensure readability and maintainability

## 📚 Viva Preparation

**Q: Why is TSP NP-Hard?**  
A: No known polynomial algorithm exists. The search space of all tours is (N-1)!/2, which grows factorially. Bitmask DP reduces this to O(2ᴺ·N²) but is still exponential.

**Q: Why use Floyd-Warshall over repeated Dijkstra?**  
A: For dense graphs or when all-pairs are needed, FW's O(V³) is comparable to running Dijkstra V times: O(V·(V+E)logV). FW is also simpler to implement and handles the precomputation once.

**Q: How does Max-Flow help in assignment?**  
A: We model Source → Agents → Zones → Sink with capacitated edges. Max-flow finds a feasible assignment that maximizes coverage without overloading any agent.

---

## 👥 Team

| Member | Contribution |
|--------|-------------|
| Atvik Sharma (24BCT0025) | Graph modeling, Dijkstra’s algorithm, Floyd-Warshall implementation, and core system architecture |
| Rohan Kumar (24BDS0463) | TSP algorithms (Greedy, Nearest Insertion, DP Bitmask), benchmarking, and performance analysis |
| MD Rakhshan Saif (24BKT0164) | Max-Flow (Ford-Fulkerson) for agent assignment, visualization module, testing, and documentation |

---
