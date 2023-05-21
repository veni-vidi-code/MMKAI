from itertools import repeat
from typing import Optional, Generator

from algorithms.limited_weight_classes.weight_dict import get_weight_dict
from algorithms.models.knapsack import Knapsack, Item

from multiprocessing import Pool

import networkx as nx


def generate_poss_recurs(free_n, current_entry: list, knapsacks: list[Knapsack],
                         weight, x: int = None, m: int = None) -> list[list[int]]:
    """
    Generates all possible arrays of items to be placed in the knapsacks. 
    This is recursive and will generate all at once. 
    Does not look at the restrictions.
    """
    if x is None:
        x = len(current_entry)
    if m is None:
        m = len(knapsacks)
    if x == m:
        return [current_entry]
    k = knapsacks[x]
    i = 0
    pos = list()
    while i * weight <= k.capacity and i <= free_n:
        new_entry = current_entry.copy()
        new_entry.append(i)
        pos += generate_poss_recurs(free_n - i, new_entry, knapsacks, weight, x + 1, m)
        i += 1
    return pos


def generate_poss_non_recurs(knapsacks: list[Knapsack], weight, n: int, m: int = None) \
        -> Generator[list[int], None, None]:
    """
    Generates all possible arrays of items to be placed in the knapsacks. Does not look at the restrictions.
    This is non-recursive and works as a generator (yields one at a time).
    """
    if m is None:
        m = len(knapsacks)
    pos = [0] * m
    current_sum = 0
    while True:
        yield pos.copy()
        for i in range(m - 1, -1, -1):
            pos[i] += 1
            if pos[i] * weight <= knapsacks[i].capacity and current_sum < n:
                current_sum += 1
                break
            elif i != 0:
                current_sum -= pos[i] - 1
                pos[i] = 0
        else:
            break


def generate_and_filter_possible_arrays(weight: int, items: list[Item], knapsacks: list[Knapsack]):
    n = len(items)
    m = len(knapsacks)

    possibilities = generate_poss_non_recurs(knapsacks, weight, n, m)

    g = nx.DiGraph({i: {k: {"weight": 0, "capacity": 1} for k in
                        (i.restrictions if i.restrictions is not None else knapsacks)}
                    for i in items})
    g.add_node("source")
    for i in items:
        g.add_edge("source", i, weight=-i.profit, capacity=1)

    res = list()

    for distribution in possibilities:
        # TODO: implement without networkx algos
        s = 0
        for a, b in enumerate(distribution):
            s += b
            g.nodes[knapsacks[a]]["demand"] = b
        g.nodes["source"]["demand"] = -s
        try:
            x = nx.min_cost_flow_cost(g)
            res.append((distribution, -x))
        except nx.NetworkXUnfeasible:
            continue

    return weight, res


def solve(knapsacks: list[Knapsack], items: list[Item],
          items_by_weight: Optional[dict[int, list[Item]]] = None) -> tuple[int, dict] | None:
    """
    Solves the knapsack problem using the pseudo-polynomial algorithm.
    :param knapsacks: list of knapsacks
    :param items: list of items
    :return: None
    """
    if len(knapsacks) == 0 or len(items) == 0:
        return

    if items_by_weight is None:
        items_by_weight = get_weight_dict(items)

    weights = list(items_by_weight.keys())

    # find all possible distributions
    with Pool() as pool:
        possibilities_by_weight = dict(pool.starmap(generate_and_filter_possible_arrays,
                                                    zip(items_by_weight.keys(), items_by_weight.values(),
                                                        repeat(knapsacks))))
    possibilities = [possibilities_by_weight[w] for w in weights]

    # find the best distribution combination
    current_max = -1
    max_pos = None
    current_pos = [0] * len(weights)
    while True:
        # check if current_pos is valid and what the value is
        for i, k in enumerate(knapsacks):
            kapsum = 0
            for j, w in enumerate(weights):
                kapsum += possibilities[j][current_pos[j]][0][i] * w
            if kapsum > k.capacity:
                print("invalid")
                break
        else:
            value = 0
            for j in range(len(weights)):
                value += possibilities[j][current_pos[j]][1]

            if value > current_max:
                current_max = value
                max_pos = current_pos.copy()

        # increment current_pos
        for i in range(len(weights) - 1, -1, -1):
            current_pos[i] += 1
            if current_pos[i] < len(possibilities[i]):
                break
            else:
                current_pos[i] = 0
        else:
            break  # all possibilities have been checked

    # turn the best distribution into a solution
    solution = dict()
    for weightindex, weight in enumerate(weights):
        distribution = possibilities[weightindex][max_pos[weightindex]][0]
        g = nx.DiGraph({i: {k: {"weight": 0, "capacity": 1} for k in
                            (i.restrictions if i.restrictions is not None else knapsacks)}
                        for i in items_by_weight[weight]})
        g.add_node("source")
        for i in items_by_weight[weight]:
            g.add_edge("source", i, weight=-i.profit, capacity=1)

        s = 0
        for a, b in enumerate(distribution):
            s += b
            g.nodes[knapsacks[a]]["demand"] = b
        g.nodes["source"]["demand"] = -s
        flow = nx.min_cost_flow(g)
        for item in items_by_weight[weight]:
            solution[item] = None
            for knapsack in knapsacks:
                if flow[item][knapsack] == 1:
                    solution[item] = knapsack
                    break

    return current_max, solution
