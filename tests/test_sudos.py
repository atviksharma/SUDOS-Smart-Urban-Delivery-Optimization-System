"""
SUDOS – Unit Tests
Run: python -m pytest tests/test_sudos.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from sudos import (
    CityGraph, dijkstra, floyd_warshall,
    greedy_tsp, dp_tsp, nearest_insertion_tsp,
    MaxFlowAssignment, multi_agent_routing, reconstruct_path
)


@pytest.fixture
def small_graph():
    g = CityGraph(4)
    g.add_edge(0, 1, 10)
    g.add_edge(1, 2, 5)
    g.add_edge(2, 3, 8)
    g.add_edge(0, 3, 20)
    g.add_edge(0, 2, 18)
    return g


@pytest.fixture
def city():
    return CityGraph.sample_city()


# ── Graph Construction ──────────────────────────────

def test_graph_nodes(small_graph):
    assert small_graph.node_count() == 4

def test_graph_edges(small_graph):
    assert small_graph.edge_count() == 5

def test_adj_matrix_symmetric(small_graph):
    m = small_graph.adj_matrix
    for i in range(4):
        for j in range(4):
            assert m[i][j] == m[j][i]

def test_random_graph():
    g = CityGraph.generate_random(10, seed=0)
    assert g.node_count() == 10
    assert g.edge_count() > 0


# ── Dijkstra ────────────────────────────────────────

def test_dijkstra_simple(small_graph):
    dist, _ = dijkstra(small_graph, 0)
    assert dist[1] == 10
    assert dist[2] == 15    # 0→1→2
    assert dist[3] == 20

def test_dijkstra_self_distance(small_graph):
    dist, _ = dijkstra(small_graph, 0)
    assert dist[0] == 0

def test_dijkstra_path_reconstruction(small_graph):
    dist, prev = dijkstra(small_graph, 0)
    path = reconstruct_path(prev, 2)
    assert path[0] == 0
    assert path[-1] == 2

def test_dijkstra_city(city):
    dist, _ = dijkstra(city, 0)
    assert all(d < float('inf') for d in dist.values()), "City must be connected"


# ── Floyd-Warshall ───────────────────────────────────

def test_floyd_matches_dijkstra(small_graph):
    fw = floyd_warshall(small_graph)
    for src in range(4):
        dijk, _ = dijkstra(small_graph, src)
        for dst in range(4):
            assert abs(fw[src][dst] - dijk[dst]) < 1e-6, \
                f"Mismatch at {src}->{dst}: fw={fw[src][dst]}, dijk={dijk[dst]}"

def test_floyd_diagonal_zero(small_graph):
    fw = floyd_warshall(small_graph)
    for i in range(4):
        assert fw[i][i] == 0

def test_floyd_symmetric(small_graph):
    fw = floyd_warshall(small_graph)
    for i in range(4):
        for j in range(4):
            assert abs(fw[i][j] - fw[j][i]) < 1e-6


# ── TSP Algorithms ───────────────────────────────────

@pytest.fixture
def dist4():
    g = CityGraph(4)
    g.add_edge(0, 1, 10)
    g.add_edge(1, 2, 15)
    g.add_edge(2, 3, 20)
    g.add_edge(3, 0, 25)
    g.add_edge(0, 2, 35)
    g.add_edge(1, 3, 30)
    return floyd_warshall(g)

def test_greedy_tsp_visits_all(dist4):
    nodes = [0, 1, 2, 3]
    tour, cost = greedy_tsp(dist4, nodes, 0)
    assert set(tour[:-1]) == set(nodes)
    assert tour[0] == tour[-1] == 0
    assert cost > 0

def test_dp_tsp_optimal(dist4):
    nodes = [0, 1, 2, 3]
    tour, cost = dp_tsp(dist4, nodes)
    greedy_tour, greedy_cost = greedy_tsp(dist4, nodes, 0)
    # DP must be at most greedy cost (it's exact)
    assert cost <= greedy_cost + 1e-6, "DP TSP must be at least as good as greedy"

def test_dp_tsp_tour_valid(dist4):
    nodes = [0, 1, 2, 3]
    tour, cost = dp_tsp(dist4, nodes)
    assert set(tour[:-1]) == set(nodes)
    assert tour[0] == tour[-1]

def test_nearest_insertion_valid(dist4):
    nodes = [0, 1, 2, 3]
    tour, cost = nearest_insertion_tsp(dist4, nodes)
    assert set(tour[:-1]) == set(nodes)
    assert tour[0] == tour[-1]
    assert cost > 0


# ── Max-Flow Assignment ──────────────────────────────

def test_max_flow_all_assigned():
    mf = MaxFlowAssignment(agents=2, zones=4)
    flow, assign = mf.max_flow()
    assert flow == 4

def test_max_flow_no_overlap():
    mf = MaxFlowAssignment(agents=3, zones=6)
    flow, assign = mf.max_flow()
    all_zones = []
    for zones in assign.values():
        all_zones.extend(zones)
    assert len(all_zones) == len(set(all_zones)), "Each zone assigned to exactly one agent"

def test_max_flow_capacity_respected():
    cap = 2
    mf = MaxFlowAssignment(agents=3, zones=5, capacity_per_agent=cap)
    flow, assign = mf.max_flow()
    for agent, zones in assign.items():
        assert len(zones) <= cap, f"Agent {agent} exceeded capacity"


# ── Multi-Agent Routing ──────────────────────────────

def test_multi_agent_returns_all_agents(city):
    routes, total = multi_agent_routing(city, 0, [3, 5, 7, 9, 11], 2, "greedy")
    assert len(routes) == 2
    assert total >= 0

def test_multi_agent_insertion(city):
    routes, total = multi_agent_routing(city, 0, [3, 5, 9], 2, "insertion")
    assert len(routes) == 2

def test_multi_agent_dp(city):
    routes, total = multi_agent_routing(city, 0, [3, 5], 2, "dp")
    assert total >= 0
