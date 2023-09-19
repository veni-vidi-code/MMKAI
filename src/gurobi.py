# Copyright (c) 2023 Tom Mucke
from typing import Optional

import gurobipy as grb
from src.models.knapsack import Knapsack
from src.models.item import Item


def solve(knapsacks: list[Knapsack], items: list[Item],
          items_by_weight: Optional[dict[int, list[Item]]] = None, *, threads=0,
          timelimit: None | int = None) -> tuple[int, dict] | None:
    if len(knapsacks) == 0 or len(items) == 0:
        return 0, dict()

    model = grb.Model()
    model.setParam('OutputFlag', 0)
    model.setParam('Threads', threads)

    if timelimit is not None:
        model.setParam('TimeLimit', timelimit)

    # We will be maximizing
    model.modelSense = grb.GRB.MAXIMIZE

    # create variables
    x = grb.tupledict()
    for item in items:
        for knapsack in item.restrictions:
            x[item, knapsack] = model.addVar(vtype=grb.GRB.BINARY, name=f'x[{item.identifier},{knapsack.identifier}]',
                                             obj=item.profit)

    # add constraints
    model.addConstrs((x.sum(item, '*') <= 1 for item in items))

    model.addConstrs(
        (grb.quicksum(x[item, knapsack] * item.weight
                      for item in items if knapsack in item.restrictions)
         <= knapsack.capacity for knapsack in knapsacks), name="knapsack capacity")

    model.update()
    print("Model created")
    model.optimize()

    solution = dict()
    for item in items:
        for knapsack in item.restrictions:
            if x[item, knapsack].X > 0.5:
                solution[item] = knapsack

    if timelimit is not None and model.status == grb.GRB.TIME_LIMIT:
        return -1, solution

    return model.objVal, solution


if __name__ == '__main__':
    import random
    import time

    topend = 5000

    numer_of_knapsacks = 30
    print(f"Number of knapsacks: {numer_of_knapsacks}")

    knapsacks = [Knapsack(random.randint(1, topend)) for _ in range(numer_of_knapsacks)]

    number_of_weightclasses = 20
    print(f"Number of weight classes: {number_of_weightclasses}")

    weightclasses = [random.randint(1, topend) for _ in range(number_of_weightclasses)]

    number_of_items = topend
    print(f"Number of items: {number_of_items}")

    items = [Item(random.randint(1, topend), random.choice(weightclasses),
                  random.choices(knapsacks, k=random.randint(1, topend))) for _ in range(number_of_items)]

    print("Solving...")
    start = time.time()
    value, solution = solve(knapsacks, items)
    end = time.time()
    print(f"Value: {value}")
    print(f"Time: {end - start}")
