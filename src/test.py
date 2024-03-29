# Copyright (c) 2023 Tom Mucke
import random
import sys
import time

from gurobi import solve
from MTM_EXTENDED_recursive import MTM_EXTENDED_recursive
from MMKAI_recursive import MMKAI_recursive
from src.MTM_EXTENDED_iterative import MTM_EXTENDED_iterative
from src.models.knapsack import Knapsack
from src.models.item_class import ItemClass

import gurobipy as grb

seed = random.randrange(sys.maxsize)
# seed = 42
random.seed(seed)
print(f"Seed: {seed}")

topend = 10_000

numer_of_knapsacks = 5
print(f"Number of knapsacks: {numer_of_knapsacks}")

knapsacks = [Knapsack(random.randint(1, topend * 10)) for _ in range(numer_of_knapsacks)]

number_of_weightclasses = 2
print(f"Number of weight classes: {number_of_weightclasses}")

weightclasses = [ItemClass(1, random.randint(1, topend // 2)) for _ in range(number_of_weightclasses)]

number_of_items = topend
print(f"Number of items: {number_of_items}")

items = [random.choice(weightclasses).add_item(knapsacks) for _ in
         range(number_of_items)]

if __name__ == '__main__':
    from pprint import pprint
    print("Solving...")

    class_to_use = input("Class to use (1) MMKAI, (2) MTM_EXTENDED: ")

    if "1" in class_to_use or "MMKAI" in class_to_use:
        solver = MMKAI_recursive(weightclasses, knapsacks, items)
    elif "2" in class_to_use or "MTM_EXTENDED" in class_to_use:
        iterative = input("Iterative? (y/n): ")
        if iterative in ["y", "Y", "j", "J", "yes", "Yes", "YES", "1", "Ja", "ja", "JA"] or bool(iterative):
            solver = MTM_EXTENDED_iterative(items=items, knapsacks=knapsacks, item_classes=None)
        else:
            solver = MTM_EXTENDED_recursive(items=items, knapsacks=knapsacks, item_classes=None)
    else:
        raise Exception("Wrong class")

    start = time.time()
    val, sol = solver.solve()
    end = time.time()

    print("Solved")

    start_gurobi = time.time()
    gurobisol, gurobisolution = solve(knapsacks, items, threads=1)
    end_gurobi = time.time()

    print(f"\033[92mValue: {val}")
    print(f"Time: {end - start}")
    print(f"Solution: {sol}")

    pprint(solver.best_solution)

    print(f"Gurobi Value: {gurobisol}")
    print(f"Gurobi Time: {end_gurobi - start_gurobi}\033[0m")

    # transform gurobisol to a match_vec
    match_vec = {i: [0 for _ in range(len(knapsacks))] for i in weightclasses}
    for item, knapsack in gurobisolution.items():
        match_vec[item.item_class][knapsacks.index(knapsack)] += 1

    pprint(match_vec)

    from pprint import pprint

    # pprint(_)
    model = grb.Model()

    # We will be maximizing
    model.modelSense = grb.GRB.MAXIMIZE

    # create variables
    x = grb.tupledict()
    for item in items:
        for knapsack in item.restrictions:
            x[item, knapsack] = model.addVar(vtype=grb.GRB.BINARY,
                                             name=f'x[{item.identifier},{knapsack.identifier}]',
                                             obj=item.profit)

    # add constraints
    model.addConstrs((x.sum(item, '*') <= 1 for item in items))

    model.addConstrs(
        (grb.quicksum(x[item, knapsack] * item.weight
                      for item in items if knapsack in item.restrictions)
         <= knapsack.capacity for knapsack in knapsacks), name="knapsack capacity")

    model.update()
    print("\033[94mModel created\033[0m")

    it = set(items)

    for k, j in sol.items():
        for i in j:
            it.remove(i)
            x[i, k].LB = 1

    for i in it:
        for k in knapsacks:
            x[i, k].UB = 0

    model.optimize()

    if model.status == grb.GRB.Status.OPTIMAL:
        if abs(model.objVal - val) > 0.1:
            raise Exception("Wrong solution value")

        if abs(gurobisol - val) > 0.1:
            raise Exception("Wrong solution")

    elif model.status == grb.GRB.Status.INFEASIBLE:
        model.computeIIS()
        model.write("model.ilp")
        raise Exception("Non feasible solution")
