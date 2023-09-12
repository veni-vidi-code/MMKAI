import pickle
import random
import time

from algorithms.limited_weight_classes.gurobi import solve
from new_version.src.MTM_EXTENDED import MTM_EXTENDED
from new_version.src.TMKPA import TMKPA
from new_version.src.models.knapsack import Knapsack, Item, ItemClass

import gurobipy as grb

random.seed(42)

topend = 100

numer_of_knapsacks = 2
print(f"Number of knapsacks: {numer_of_knapsacks}")

knapsacks = [Knapsack(random.randint(1, topend * 10)) for _ in range(numer_of_knapsacks)]

number_of_weightclasses = 3
print(f"Number of weight classes: {number_of_weightclasses}")

weightclasses = [ItemClass(1, random.randint(1, topend // 2)) for _ in range(number_of_weightclasses)]

number_of_items = topend
print(f"Number of items: {number_of_items}")

items = [random.choice(weightclasses).add_item(knapsacks) for _ in
         range(number_of_items)]



if __name__ == '__main__':
    print("Solving...")

    class_to_use = input("Class to use (1) TMKPA, (2) MTM_EXTENDED: ")
    if "1" in class_to_use or "TMKPA" in class_to_use:
        solver = TMKPA(weightclasses, knapsacks, items)
    elif "2" in class_to_use or "MTM_EXTENDED" in class_to_use:
        solver = MTM_EXTENDED(items, knapsacks)
    else:
        raise Exception("Wrong class")
    start = time.time()
    val, sol = solver.solve()
    end = time.time()

    start_gurobi = time.time()
    gurobisol, _ = solve(knapsacks, items)
    end_gurobi = time.time()

    print(f"\033[92mValue: {val}")
    print(f"Time: {end - start}")
    print(f"Solution: {sol}")


    print(f"Gurobi Value: {gurobisol}")
    print(f"Gurobi Time: {end_gurobi - start_gurobi}\033[0m")

    from pprint import pprint
    #pprint(_)
    model = grb.Model()

    # We will be maximizing
    model.modelSense = grb.GRB.MAXIMIZE

    # create variables
    x = grb.tupledict()
    for item in items:
        for knapsack in (item.restrictions if item.restrictions is not None else knapsacks):
            x[item, knapsack] = model.addVar(vtype=grb.GRB.BINARY,
                                             name=f'x[{item.identifier},{knapsack.identifier}]',
                                             obj=item.profit)

    # add constraints
    model.addConstrs((x.sum(item, '*') <= 1 for item in items))

    model.addConstrs(
        (grb.quicksum(x[item, knapsack] * item.weight
                      for item in items if item.restrictions is None or knapsack in item.restrictions)
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


