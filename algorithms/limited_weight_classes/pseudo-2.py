from typing import Optional

from algorithms.limited_weight_classes.weight_dict import get_weight_dict
from algorithms.models.knapsack import Knapsack, Item

import networkx as nx


def solve(knapsacks: list[Knapsack], items: list[Item],
          items_by_weight: Optional[dict[int, list[Item]]] = None) -> tuple[int, dict] | None:
    """
    Solves the knapsack problem using the pseudo-polynomial algorithm by basically bruteforcing
    all possible distributions of items of each weight class into the knapsacks.
    :param knapsacks: list of knapsacks
    :param items: list of items
    """
    if len(knapsacks) == 0 or len(items) == 0:
        return 0, dict()

    if items_by_weight is None:
        items_by_weight = get_weight_dict(items)

    weights = list(items_by_weight.keys())
    weights.sort()

    m = len(knapsacks)

    possibilities = []
    for weight_index, weight in enumerate(weights):
        items_used = items_by_weight[weight]
        n = len(items_used)

        g = nx.DiGraph({i: {k: {"weight": 0, "capacity": 1} for k in
                            (i.restrictions if i.restrictions is not None else knapsacks)}
                        for i in items_used})

        # ensure all knapsacks are in the graph
        for k in knapsacks:
            g.add_node(k)

        g.add_node("source")
        for i in items_used:
            g.add_edge("source", i, weight=-1, capacity=1)

        adjusted_knapsacks_capacities_by_pos = []
        for possibility in possibilities:
            adjusted_knapsacks_capacities = [k.capacity for k in knapsacks]
            for p_w_index, p_w in enumerate(possibility):
                for k in range(len(knapsacks)):
                    adjusted_knapsacks_capacities[k] -= p_w[p_w_index]

            adjusted_knapsacks_capacities_by_pos.append(adjusted_knapsacks_capacities)

        res = list()

        highest_possible_sum = min(sum(k.capacity // weight for k in knapsacks), n)

        for i in range(highest_possible_sum, 0, -1):
            if weight_index == 0:
                adjusted_knapsacks_capacities = [k.capacity for k in knapsacks]
                komma_pos = [0] * (m - 1)
                komma_pos.append(i)
                while True:
                    # transform komma_pos to pos
                    pos = [0] * m
                    pos[0] = komma_pos[0]
                    for j in range(1, m):
                        pos[j] = komma_pos[j] - komma_pos[j - 1]

                    # test the pos
                    s = 0
                    for a, b in enumerate(pos):
                        s += b
                        g.nodes[knapsacks[a]]["demand"] = b
                    g.nodes["source"]["demand"] = -s
                    try:
                        x = nx.min_cost_flow_cost(g)
                        res.append([pos])
                    except nx.NetworkXUnfeasible:
                        ...

                    # find next komma_pos
                    for k in range(m - 1, 0, -1):
                        diff_to_cap = adjusted_knapsacks_capacities[k] // weight + komma_pos[k] - komma_pos[k - 1]
                        if diff_to_cap < 0:
                            komma_pos[k - 1] -= diff_to_cap

                    diff_to_cap = adjusted_knapsacks_capacities[0] // weight - komma_pos[0]
                    if diff_to_cap < 0:
                        break

                    for j in range(m - 2, -1, -1):
                        komma_pos[j] += 1
                        if komma_pos[j] <= i:
                            for x in range(j + 1, m - 1):
                                komma_pos[x] = komma_pos[j]
                            break
                    else:
                        break

            for possibility_index, possibility in enumerate(possibilities):
                adjusted_knapsacks_capacities = adjusted_knapsacks_capacities_by_pos[possibility_index]
                adjusted_highest_possible_sum = min(sum(k // weight for k in adjusted_knapsacks_capacities), n)
                if adjusted_highest_possible_sum < i:
                    continue

                komma_pos = [0] * (m - 1)
                komma_pos.append(i)
                while True:
                    # transform komma_pos to pos
                    pos = [0] * m
                    pos[0] = komma_pos[0]
                    for j in range(1, m):
                        pos[j] = komma_pos[j] - komma_pos[j - 1]

                    # test the pos
                    s = 0
                    for a, b in enumerate(pos):
                        s += b
                        g.nodes[knapsacks[a]]["demand"] = b
                    g.nodes["source"]["demand"] = -s
                    try:
                        x = nx.min_cost_flow_cost(g)
                        assert sum(_ for _ in pos) == i
                        res.append([*possibility, pos])
                    except nx.NetworkXUnfeasible:
                        ...

                    # find next komma_pos
                    for k in range(m - 1, 0, -1):
                        diff_to_cap = adjusted_knapsacks_capacities[k] // weight + komma_pos[k] - komma_pos[k - 1]
                        if diff_to_cap < 0:
                            komma_pos[k - 1] -= diff_to_cap

                    diff_to_cap = adjusted_knapsacks_capacities[0] // weight - komma_pos[0]
                    if diff_to_cap < 0:
                        break

                    for j in range(m - 2, -1, -1):
                        komma_pos[j] += 1
                        if komma_pos[j] <= i:
                            for x in range(j + 1, m - 1):
                                komma_pos[x] = komma_pos[j]
                            break
                    else:
                        break

            if len(res) > 0:
                break

        possibilities = res

    first_posssibility = possibilities[0]

    # turn the best distribution into a solution
    solution = dict()
    optimal_value = 0
    for weightindex, weight in enumerate(weights):
        distribution = first_posssibility[weightindex]
        g = nx.DiGraph({i: {k: {"weight": 0, "capacity": 1} for k in
                            (i.restrictions if i.restrictions is not None else knapsacks)}
                        for i in items_by_weight[weight]})
        for k in knapsacks:
            g.add_node(k)
        g.add_node("source")
        for i in items_by_weight[weight]:
            g.add_edge("source", i, weight=-1, capacity=1)

        s = 0
        for a, b in enumerate(distribution):
            s += b
            g.nodes[knapsacks[a]]["demand"] = b
        g.nodes["source"]["demand"] = -s
        flow = nx.min_cost_flow(g)
        for item in items_by_weight[weight]:
            solution[item] = None
            for knapsack in item.restrictions if item.restrictions is not None else knapsacks:
                if flow[item][knapsack] == 1:
                    solution[item] = knapsack
                    optimal_value += 1
                    break

    return optimal_value, solution


if __name__ == '__main__':
    import random
    import time

    topend = 50

    numer_of_knapsacks = 5
    print(f"Number of knapsacks: {numer_of_knapsacks}")

    knapsacks = [Knapsack(random.randint(1, topend)) for _ in range(numer_of_knapsacks)]

    biggest_knapsack_kapacity = max(k.capacity for k in knapsacks)

    number_of_weightclasses = 3
    print(f"Number of weight classes: {number_of_weightclasses}")

    weightclasses = [random.randint(1, biggest_knapsack_kapacity) for _ in range(number_of_weightclasses)]

    number_of_items = topend
    print(f"Number of items: {number_of_items}")

    items = [Item(random.randint(1, topend), random.choice(weightclasses), None)
             # random.choices(knapsacks, k=random.randint(1, biggest_knapsack_kapacity)))
             for _ in range(number_of_items)]

    print("Solving...")
    start = time.time()
    value, solution = solve(knapsacks, items)
    end = time.time()
    print(f"Value: {value}")
    print(f"Time: {end - start}")
