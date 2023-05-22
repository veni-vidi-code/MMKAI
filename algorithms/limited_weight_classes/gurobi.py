from typing import Optional

import gurobipy as grb
from algorithms.models.knapsack import Knapsack, Item


def solve(knapsacks: list[Knapsack], items: list[Item],
          items_by_weight: Optional[dict[int, list[Item]]] = None) -> tuple[int, dict] | None:
    if len(knapsacks) == 0 or len(items) == 0:
        return 0, dict()

    model = grb.Model()

    # We will be maximizing
    model.modelSense = grb.GRB.MAXIMIZE

    # We will be highly symmetric
    model.setParam('Symmetry', 2)

    # create variables
    x = grb.tupledict()
    for item in items:
        for knapsack in (item.restrictions if item.restrictions is not None else knapsacks):
            x[item, knapsack] = model.addVar(vtype=grb.GRB.BINARY, name=f'x[{item.identifier},{knapsack.identifier}]',
                                             obj=item.profit)

    # add constraints
    model.addConstrs((x.sum(item, '*') <= 1 for item in items), name="item once")

    model.addConstrs(
        (grb.quicksum(x[item, knapsack] * item.weight for item in items) <= knapsack.capacity for knapsack in
         knapsacks), name="knapsack capacity")

    model.update()

    model.optimize()

    solution = dict()
    for item in items:
        for knapsack in knapsacks:
            if x[item, knapsack].X > 0.5:
                solution[item] = knapsack

    return model.objVal, solution
