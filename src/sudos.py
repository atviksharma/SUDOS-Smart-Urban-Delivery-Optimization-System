"""
SUDOS – Smart Urban Delivery Optimization System
================================================
Implements multiple DAA paradigms for urban delivery route optimization:
  1. Graph Construction (Adjacency Matrix + List)
  2. Greedy: Nearest Neighbor TSP
  3. Graph: Dijkstra's Shortest Path
  4. Graph: Floyd-Warshall All-Pairs Shortest Path
  5. DP: Bitmask TSP (exact, small inputs)
  6. Approximation: Nearest Insertion Heuristic
  7. Advanced: Max-Flow based Agent Assignment
"""

import heapq
import time
import math
import random
import itertools
from typing import List, Dict, Tuple, Optional


# ──────────────────────────────────────────────
# 1. GRAPH CONSTRUCTION
# ──────────────────────────────────────────────

class CityGraph:
    """Represents a city as a weighted undirected graph."""

    def __init__(self, num_nodes: int):
        self.num_nodes = num_nodes
        self.adj_list: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(num_nodes)}
        self.adj_matrix: List[List[float]] = [
            [float('inf')] * num_nodes for _ in range(num_nodes)
        ]
        for i in range(num_nodes):
            self.adj_matrix[i][i] = 0

    def add_edge(self, u: int, v: int, weight: float):
        """Add an undirected edge."""
        self.adj_list[u].append((v, weight))
        self.adj_list[v].append((u, weight))
        self.adj_matrix[u][v] = weight
        self.adj_matrix[v][u] = weight

    def node_count(self) -> int:
        return self.num_nodes

    def edge_count(self) -> int:
        return sum(len(neighbors) for neighbors in self.adj_list.values()) // 2

    def neighbors(self, node: int) -> List[Tuple[int, float]]:
        return self.adj_list[node]

    @staticmethod
    def generate_random(num_nodes: int, seed: int = 42) -> 'CityGraph':
        """Generate a random connected city graph."""
        random.seed(seed)
        g = CityGraph(num_nodes)
        # Ensure connectivity via a spanning chain
        nodes = list(range(num_nodes))
        random.shuffle(nodes)
        for i in range(len(nodes) - 1):
            w = random.randint(5, 50)
            g.add_edge(nodes[i], nodes[i + 1], w)
        # Add extra edges for density
        for _ in range(num_nodes * 2):
            u = random.randint(0, num_nodes - 1)
            v = random.randint(0, num_nodes - 1)
            if u != v:
                w = random.randint(5, 100)
                if g.adj_matrix[u][v] == float('inf'):
                    g.add_edge(u, v, w)
        return g

    @staticmethod
    def sample_city() -> 'CityGraph':
        """12-node sample city graph (manually crafted)."""
        g = CityGraph(12)
        edges = [
            (0, 1, 10), (0, 2, 15), (0, 3, 20),
            (1, 4, 12), (1, 5, 8),
            (2, 5, 6),  (2, 6, 18),
            (3, 6, 14), (3, 7, 9),
            (4, 8, 11), (4, 9, 16),
            (5, 9, 7),  (5, 10, 13),
            (6, 10, 10),(6, 11, 20),
            (7, 11, 15),(8, 9, 5),
            (9, 10, 8), (10, 11, 6),
        ]
        for u, v, w in edges:
            g.add_edge(u, v, w)
        return g


# ──────────────────────────────────────────────
# 2. DIJKSTRA'S ALGORITHM  O((V+E) log V)
# ──────────────────────────────────────────────

def dijkstra(graph: CityGraph, source: int) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
    """
    Single-source shortest paths using a min-heap.
    Returns (dist, prev) dicts.
    """
    dist = {i: float('inf') for i in range(graph.num_nodes)}
    prev: Dict[int, Optional[int]] = {i: None for i in range(graph.num_nodes)}
    dist[source] = 0
    pq = [(0.0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph.neighbors(u):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    return dist, prev


def reconstruct_path(prev: Dict[int, Optional[int]], target: int) -> List[int]:
    """Trace back the shortest path from prev dict."""
    path = []
    node: Optional[int] = target
    while node is not None:
        path.append(node)
        node = prev[node]
    return path[::-1]


# ──────────────────────────────────────────────
# 3. FLOYD-WARSHALL  O(V³)
# ──────────────────────────────────────────────

def floyd_warshall(graph: CityGraph) -> List[List[float]]:
    """
    All-pairs shortest paths.
    Returns distance matrix.
    """
    n = graph.num_nodes
    dist = [row[:] for row in graph.adj_matrix]   # deep copy

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist


# ──────────────────────────────────────────────
# 4. GREEDY TSP  –  Nearest Neighbor  O(V²)
# ──────────────────────────────────────────────

def greedy_tsp(dist_matrix: List[List[float]], nodes: List[int], start: int) -> Tuple[List[int], float]:
    """
    Nearest-neighbor greedy TSP.
    nodes: subset of node indices to visit.
    Returns (tour, total_cost).
    """
    unvisited = set(nodes) - {start}
    tour = [start]
    cost = 0.0
    current = start

    while unvisited:
        best = min(unvisited, key=lambda n: dist_matrix[current][n])
        cost += dist_matrix[current][best]
        tour.append(best)
        unvisited.remove(best)
        current = best

    # Return to start
    cost += dist_matrix[current][start]
    tour.append(start)
    return tour, cost


# ──────────────────────────────────────────────
# 5. DP BITMASK TSP  –  Exact  O(2^N · N²)
# ──────────────────────────────────────────────

def dp_tsp(dist_matrix: List[List[float]], nodes: List[int]) -> Tuple[List[int], float]:
    """
    Exact TSP via bitmask DP (Held-Karp).
    nodes: subset of node indices (keep len ≤ 20 for practical runtime).
    """
    n = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    INF = float('inf')

    # dp[mask][i] = min cost to visit nodes in mask, ending at node i
    dp = [[INF] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]

    dp[1][0] = 0   # start at nodes[0], mask = 0001

    for mask in range(1 << n):
        for u in range(n):
            if not (mask & (1 << u)):
                continue
            if dp[mask][u] == INF:
                continue
            for v in range(n):
                if mask & (1 << v):
                    continue
                nmask = mask | (1 << v)
                d = dist_matrix[nodes[u]][nodes[v]]
                if dp[mask][u] + d < dp[nmask][v]:
                    dp[nmask][v] = dp[mask][u] + d
                    parent[nmask][v] = u

    full_mask = (1 << n) - 1
    last = min(range(n), key=lambda i: dp[full_mask][i] + dist_matrix[nodes[i]][nodes[0]])
    cost = dp[full_mask][last] + dist_matrix[nodes[last]][nodes[0]]

    # Reconstruct
    tour_idx = []
    mask = full_mask
    cur = last
    while cur != -1:
        tour_idx.append(cur)
        prev = parent[mask][cur]
        mask ^= (1 << cur)
        cur = prev
    tour_idx.reverse()
    tour = [nodes[i] for i in tour_idx] + [nodes[0]]
    return tour, cost


# ──────────────────────────────────────────────
# 6. NEAREST INSERTION HEURISTIC  O(V²)
# ──────────────────────────────────────────────

def nearest_insertion_tsp(dist_matrix: List[List[float]], nodes: List[int]) -> Tuple[List[int], float]:
    """
    Approximation: Nearest Insertion.
    Repeatedly inserts the nearest un-visited node into the cheapest position.
    """
    n = len(nodes)
    if n == 1:
        return nodes + [nodes[0]], 0.0

    start = nodes[0]
    tour = [start]
    remaining = set(nodes[1:])

    while remaining:
        # Find node nearest to any node in tour
        best_new = min(remaining, key=lambda r: min(dist_matrix[t][r] for t in tour))
        # Find cheapest insertion position
        best_cost = float('inf')
        best_pos = 1
        for i in range(len(tour)):
            j = (i + 1) % len(tour)
            c = (dist_matrix[tour[i]][best_new] +
                 dist_matrix[best_new][tour[j]] -
                 dist_matrix[tour[i]][tour[j]])
            if c < best_cost:
                best_cost = c
                best_pos = i + 1
        tour.insert(best_pos, best_new)
        remaining.remove(best_new)

    # Compute total cost
    cost = sum(dist_matrix[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))
    cost += dist_matrix[tour[-1]][tour[0]]
    tour.append(tour[0])
    return tour, cost


# ──────────────────────────────────────────────
# 7. MAX-FLOW AGENT ASSIGNMENT  O(V·E)
# ──────────────────────────────────────────────

class MaxFlowAssignment:
    """
    Assign delivery locations to agents using Ford-Fulkerson max-flow.
    Models: Source → Agents → Delivery Zones → Sink
    """

    def __init__(self, agents: int, zones: int, capacity_per_agent: int = 3):
        self.agents = agents
        self.zones = zones
        self.cap = capacity_per_agent
        # Nodes: 0=source, 1..agents=agents, agents+1..agents+zones=zones, agents+zones+1=sink
        self.n = agents + zones + 2
        self.source = 0
        self.sink = self.n - 1
        self.graph: Dict[int, Dict[int, int]] = {i: {} for i in range(self.n)}
        self._build()

    def _add_edge(self, u, v, cap):
        self.graph[u][v] = self.graph[u].get(v, 0) + cap
        self.graph[v].setdefault(u, 0)

    def _build(self):
        for a in range(1, self.agents + 1):
            self._add_edge(self.source, a, self.cap)
        for z in range(1, self.zones + 1):
            znode = self.agents + z
            self._add_edge(znode, self.sink, 1)
            for a in range(1, self.agents + 1):
                self._add_edge(a, znode, 1)

    def _bfs(self, parent):
        visited = {self.source}
        queue = [self.source]
        while queue:
            u = queue.pop(0)
            for v, cap in self.graph[u].items():
                if v not in visited and cap > 0:
                    visited.add(v)
                    parent[v] = u
                    if v == self.sink:
                        return True
                    queue.append(v)
        return False

    def max_flow(self) -> Tuple[int, Dict[int, List[int]]]:
        """Run Ford-Fulkerson; return (total_flow, assignment dict)."""
        parent: Dict[int, int] = {}
        flow = 0
        while self._bfs(parent):
            # Find min capacity along path
            path_flow = float('inf')
            s = self.sink
            while s != self.source:
                u = parent[s]
                path_flow = min(path_flow, self.graph[u][s])
                s = parent[s]
            # Update capacities
            v = self.sink
            while v != self.source:
                u = parent[v]
                self.graph[u][v] -= path_flow
                self.graph[v][u] = self.graph[v].get(u, 0) + path_flow
                v = parent[v]
            flow += path_flow
            parent = {}

        # Read assignment: which zones each agent covers
        assignment: Dict[int, List[int]] = {a: [] for a in range(1, self.agents + 1)}
        for a in range(1, self.agents + 1):
            for z in range(1, self.zones + 1):
                znode = self.agents + z
                # Edge a->znode was used if residual capacity from znode back to a > 0
                if self.graph[znode].get(a, 0) > 0:
                    assignment[a].append(z - 1)   # 0-indexed zone

        return flow, assignment


# ──────────────────────────────────────────────
# 8. MULTI-AGENT ROUTING
# ──────────────────────────────────────────────

def multi_agent_routing(
    graph: CityGraph,
    depot: int,
    deliveries: List[int],
    num_agents: int,
    algorithm: str = "greedy"
) -> Tuple[Dict[int, Tuple[List[int], float]], float]:
    """
    Assign deliveries to agents and compute routes.
    algorithm: 'greedy' | 'dp' | 'insertion'
    Returns (routes_per_agent, total_cost).
    """
    # Pre-compute all-pairs shortest paths via Floyd-Warshall
    dist_matrix = floyd_warshall(graph)

    # Agent assignment via max-flow
    mf = MaxFlowAssignment(num_agents, len(deliveries))
    _, assignment = mf.max_flow()

    routes: Dict[int, Tuple[List[int], float]] = {}
    total_cost = 0.0

    for agent_id in range(1, num_agents + 1):
        zone_indices = assignment.get(agent_id, [])
        agent_deliveries = [depot] + [deliveries[z] for z in zone_indices if z < len(deliveries)]

        if len(agent_deliveries) == 1:
            routes[agent_id] = ([depot, depot], 0.0)
            continue

        nodes_to_visit = agent_deliveries

        if algorithm == "dp" and len(nodes_to_visit) <= 12:
            tour, cost = dp_tsp(dist_matrix, nodes_to_visit)
        elif algorithm == "insertion":
            tour, cost = nearest_insertion_tsp(dist_matrix, nodes_to_visit)
        else:
            tour, cost = greedy_tsp(dist_matrix, nodes_to_visit, depot)

        routes[agent_id] = (tour, cost)
        total_cost += cost

    return routes, total_cost


# ──────────────────────────────────────────────
# 9. BENCHMARKING UTILITY
# ──────────────────────────────────────────────

def benchmark(graph: CityGraph, depot: int, deliveries: List[int], num_agents: int):
    """Run all algorithms and return timing + cost metrics."""
    dist_matrix = floyd_warshall(graph)
    nodes = [depot] + deliveries
    results = {}

    algos = {
        "Greedy (Nearest Neighbor)": lambda: greedy_tsp(dist_matrix, nodes, depot),
        "Nearest Insertion":         lambda: nearest_insertion_tsp(dist_matrix, nodes),
    }
    if len(nodes) <= 15:
        algos["DP Bitmask (Exact)"] = lambda: dp_tsp(dist_matrix, nodes)

    for name, fn in algos.items():
        t0 = time.perf_counter()
        tour, cost = fn()
        elapsed = (time.perf_counter() - t0) * 1000
        results[name] = {"tour": tour, "cost": round(cost, 2), "time_ms": round(elapsed, 4)}

    return results


# ──────────────────────────────────────────────
# 10. DEMO RUNNER
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  SUDOS – Smart Urban Delivery Optimization System")
    print("=" * 60)

    # Build sample graph
    city = CityGraph.sample_city()
    print(f"\nCity Graph: {city.node_count()} nodes, {city.edge_count()} edges")

    depot = 0
    deliveries = [3, 5, 7, 9, 11]
    num_agents = 2

    print(f"Depot: Node {depot}")
    print(f"Deliveries: {deliveries}")
    print(f"Agents: {num_agents}")

    # Dijkstra from depot
    print("\n--- Dijkstra Shortest Paths from Depot ---")
    dist, prev = dijkstra(city, depot)
    for d in deliveries:
        path = reconstruct_path(prev, d)
        print(f"  Node 0 → {d}: dist={dist[d]}, path={path}")

    # Floyd-Warshall
    print("\n--- Floyd-Warshall All-Pairs (sample) ---")
    fw = floyd_warshall(city)
    print(f"  Dist[0][11] = {fw[0][11]}")
    print(f"  Dist[3][9]  = {fw[3][9]}")

    # Benchmark single-agent TSP
    print("\n--- Single-Agent TSP Benchmark ---")
    bench = benchmark(city, depot, deliveries, num_agents)
    for name, r in bench.items():
        print(f"  [{name}]")
        print(f"    Tour: {r['tour']}")
        print(f"    Cost: {r['cost']}  |  Time: {r['time_ms']} ms")

    # Multi-agent routing
    print("\n--- Multi-Agent Routing (Greedy) ---")
    routes, total = multi_agent_routing(city, depot, deliveries, num_agents, "greedy")
    for agent, (tour, cost) in routes.items():
        print(f"  Agent {agent}: tour={tour}, cost={cost:.1f}")
    print(f"  Total cost: {total:.1f}")

    # Max-flow assignment
    print("\n--- Max-Flow Assignment ---")
    mf = MaxFlowAssignment(agents=num_agents, zones=len(deliveries))
    flow, assign = mf.max_flow()
    print(f"  Total flow (deliveries assigned): {flow}")
    for a, zones in assign.items():
        nodes_assigned = [deliveries[z] for z in zones if z < len(deliveries)]
        print(f"  Agent {a}: delivery nodes = {nodes_assigned}")

    print("\n" + "=" * 60)
    print("  All algorithms executed successfully!")
    print("=" * 60)
