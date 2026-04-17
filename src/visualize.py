"""
SUDOS – Visualization Module
Generates graphs, route maps, and comparison charts using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random
import math
import os
from typing import Dict, List, Tuple, Optional

# Make plots reproducible
random.seed(42)


def _node_positions(n: int, special: Dict[int, Tuple[float, float]] = None) -> Dict[int, Tuple[float, float]]:
    """Generate circular layout positions for n nodes."""
    pos = {}
    for i in range(n):
        angle = 2 * math.pi * i / n
        pos[i] = (math.cos(angle) * 4, math.sin(angle) * 4)
    if special:
        pos.update(special)
    return pos


def plot_city_graph(graph, title="City Graph", save_path=None):
    """Draw the city graph with edge weights."""
    import sys; sys.path.insert(0, '/home/claude/SUDOS/src')
    n = graph.num_nodes
    pos = _node_positions(n)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor('#0f1117')
    fig.patch.set_facecolor('#0f1117')

    # Draw edges
    drawn = set()
    for u in range(n):
        for v, w in graph.neighbors(u):
            key = tuple(sorted((u, v)))
            if key in drawn:
                continue
            drawn.add(key)
            x = [pos[u][0], pos[v][0]]
            y = [pos[u][1], pos[v][1]]
            ax.plot(x, y, color='#4a9eff', linewidth=1.0, alpha=0.5, zorder=1)
            mx, my = (x[0]+x[1])/2, (y[0]+y[1])/2
            ax.text(mx, my, str(int(w)), fontsize=7, color='#aaaaaa',
                    ha='center', va='center', zorder=3)

    # Draw nodes
    for i, (x, y) in pos.items():
        circle = plt.Circle((x, y), 0.28, color='#1e90ff', zorder=4)
        ax.add_patch(circle)
        ax.text(x, y, str(i), fontsize=9, ha='center', va='center',
                color='white', fontweight='bold', zorder=5)

    ax.set_xlim(-5.5, 5.5)
    ax.set_ylim(-5.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=12)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#0f1117')
    plt.close()
    return fig


def plot_routes(graph, routes: Dict[int, Tuple[List[int], float]],
                depot: int, title="Agent Routes", save_path=None):
    """Visualize multi-agent routes on the city graph."""
    n = graph.num_nodes
    pos = _node_positions(n)

    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7']
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.set_facecolor('#0f1117')
    fig.patch.set_facecolor('#0f1117')

    # Draw all edges faintly
    drawn = set()
    for u in range(n):
        for v, _ in graph.neighbors(u):
            key = tuple(sorted((u, v)))
            if key not in drawn:
                drawn.add(key)
                ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                        color='#333344', linewidth=0.8, alpha=0.4, zorder=1)

    # Draw agent routes
    legend_patches = []
    for agent_id, (tour, cost) in routes.items():
        c = colors[(agent_id - 1) % len(colors)]
        for i in range(len(tour) - 1):
            u, v = tour[i], tour[i + 1]
            ax.annotate("", xy=pos[v], xytext=pos[u],
                        arrowprops=dict(arrowstyle="-|>", color=c,
                                        lw=2.5, mutation_scale=18), zorder=3)
        legend_patches.append(mpatches.Patch(color=c, label=f"Agent {agent_id} (cost={cost:.0f})"))

    # Draw all nodes
    for i, (x, y) in pos.items():
        if i == depot:
            circle = plt.Circle((x, y), 0.35, color='#ffd700', zorder=4)
            ax.add_patch(circle)
            ax.text(x, y, 'D', fontsize=10, ha='center', va='center',
                    color='black', fontweight='bold', zorder=5)
        else:
            circle = plt.Circle((x, y), 0.28, color='#2a2a4a', zorder=4,
                                 linewidth=1.5, linestyle='solid')
            ax.add_patch(circle)
            ax.text(x, y, str(i), fontsize=9, ha='center', va='center',
                    color='white', fontweight='bold', zorder=5)

    ax.set_xlim(-5.5, 5.5)
    ax.set_ylim(-5.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=12)
    ax.legend(handles=legend_patches, loc='lower right',
              facecolor='#1a1a2e', edgecolor='#4a9eff', labelcolor='white', fontsize=10)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#0f1117')
    plt.close()
    return fig


def plot_algorithm_comparison(results: Dict[str, Dict], save_path=None):
    """Bar chart comparing algorithm cost and runtime."""
    names = list(results.keys())
    costs = [results[n]['cost'] for n in names]
    times = [results[n]['time_ms'] for n in names]

    short_names = [n.split('(')[0].strip() for n in names]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('#0f1117')
    palette = ['#1e90ff', '#ff6b6b', '#4ecdc4', '#ffd700']

    for ax in (ax1, ax2):
        ax.set_facecolor('#1a1a2e')
        ax.spines['bottom'].set_color('#444466')
        ax.spines['left'].set_color('#444466')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors='#aaaacc')
        ax.yaxis.label.set_color('#aaaacc')
        ax.xaxis.label.set_color('#aaaacc')
        ax.title.set_color('white')

    bars1 = ax1.bar(short_names, costs, color=palette[:len(names)], edgecolor='none', width=0.5)
    ax1.set_title('Total Route Cost', fontweight='bold', fontsize=13)
    ax1.set_ylabel('Cost (units)')
    for b, v in zip(bars1, costs):
        ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 0.5, f'{v:.1f}',
                 ha='center', fontsize=10, color='white')

    bars2 = ax2.bar(short_names, times, color=palette[:len(names)], edgecolor='none', width=0.5)
    ax2.set_title('Execution Time', fontweight='bold', fontsize=13)
    ax2.set_ylabel('Time (ms)')
    for b, v in zip(bars2, times):
        ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 0.01, f'{v:.3f}',
                 ha='center', fontsize=10, color='white')

    plt.suptitle('SUDOS – Algorithm Performance Comparison',
                 color='white', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#0f1117')
    plt.close()
    return fig


def plot_scalability(save_path=None):
    """Plot theoretical time complexity curves."""
    import numpy as np
    ns = list(range(1, 21))

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#0f1117')
    ax.set_facecolor('#1a1a2e')
    ax.spines['bottom'].set_color('#444466')
    ax.spines['left'].set_color('#444466')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#aaaacc')

    ax.plot(ns, [n**2 for n in ns], label='Greedy O(N²)', color='#4ecdc4', linewidth=2.5)
    ax.plot(ns, [n**3 for n in ns], label='Floyd-Warshall O(N³)', color='#ffd700', linewidth=2.5)
    ax.plot(ns, [(2**n) * n**2 for n in ns], label='DP TSP O(2ᴺ·N²)', color='#ff6b6b', linewidth=2.5, linestyle='--')
    ax.plot(ns, [n**2 for n in ns], label='Nearest Insertion O(N²)', color='#1e90ff', linewidth=2.5, linestyle=':')

    ax.set_xlabel('Number of Delivery Nodes (N)', color='#aaaacc', fontsize=12)
    ax.set_ylabel('Relative Operations', color='#aaaacc', fontsize=12)
    ax.set_title('Scalability: Time Complexity Comparison', color='white', fontsize=14, fontweight='bold')
    ax.legend(facecolor='#1a1a2e', edgecolor='#4a9eff', labelcolor='white', fontsize=10)
    ax.set_yscale('log')
    ax.yaxis.grid(True, color='#2a2a3e', linewidth=0.7)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='#0f1117')
    plt.close()
    return fig


if __name__ == "__main__":
    import sys; sys.path.insert(0, '/home/claude/SUDOS/src')
    from sudos import CityGraph, benchmark, multi_agent_routing

    os.makedirs('/home/claude/SUDOS/outputs', exist_ok=True)

    city = CityGraph.sample_city()
    depot = 0
    deliveries = [3, 5, 7, 9, 11]

    os.makedirs('outputs', exist_ok=True)
    plot_city_graph(city, save_path='outputs/city_graph.png')
    print("Saved: city_graph.png")

    routes, _ = multi_agent_routing(city, depot, deliveries, 2, "greedy")
    plot_routes(city, routes, depot, save_path='outputs/agent_routes.png')
    print("Saved: agent_routes.png")

    bench = benchmark(city, depot, deliveries, 2)
    plot_algorithm_comparison(bench, save_path='outputs/algo_comparison.png')
    print("Saved: algo_comparison.png")

    plot_scalability(save_path='outputs/scalability.png')
    print("Saved: scalability.png")
    print("All plots generated!")
