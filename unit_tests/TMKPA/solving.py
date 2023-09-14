# Copyright (c) 2023 Tom Mucke
import unittest
import random

from src.TMKPA import *
import gurobipy as grb


def validate_solution(knapsacks, items, sol):
    with grb.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)  # surpress gurobis output
        env.start()
        with grb.Model(env=env) as model:
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
                 <= knapsack.capacity for knapsack in knapsacks))

            model.update()

            it = set(items)

            for k, j in sol.items():
                for i in j:
                    it.remove(i)
                    x[i, k].LB = 1

            for i in it:
                for k in i.restrictions:
                    x[i, k].UB = 0

            model.optimize()

            return model.objVal, model.status


class TestTMKPAsolve(unittest.TestCase):
    # this class will test using some harcoded values aswell as some random values
    def setUp(self) -> None:
        self.class_to_test = lambda weightclasses, knapsacks, items: TMKPA(weightclasses, knapsacks, items)

    def test_random_42(self):
        random.seed(42)
        knapsacks = [Knapsack(random.randint(1, 1000)) for _ in range(3)]
        weightclasses = [ItemClass(1, random.randint(1, 100)) for _ in range(3)]
        items = [random.choice(weightclasses).add_item(knapsacks) for _ in
                 range(100)]
        solver = self.class_to_test(weightclasses, knapsacks, items)
        val, sol = solver.solve()
        self.assertEqual(val, 23)  # calculated using gurobi

        # validate solution using gurobi
        gurobisol, gurobisolution = validate_solution(knapsacks, items, sol)
        self.assertEqual(gurobisolution, grb.GRB.Status.OPTIMAL)
        self.assertEqual(gurobisol, val)

    def test_random_pi(self):
        random.seed(3_1415926535)
        knapsacks = [Knapsack(random.randint(1, 1000)) for _ in range(2)]
        weightclasses = [ItemClass(1, random.randint(1, 100)) for _ in range(4)]
        items = [random.choice(weightclasses).add_item(knapsacks) for _ in
                 range(50)]
        solver = self.class_to_test(weightclasses, knapsacks, items)
        val, sol = solver.solve()
        self.assertEqual(val, 28)  # calculated using gurobi

        # validate solution using gurobi
        gurobisol, gurobisolution = validate_solution(knapsacks, items, sol)
        self.assertEqual(gurobisolution, grb.GRB.Status.OPTIMAL)
        self.assertEqual(gurobisol, val)

    def test_random_e(self):
        random.seed(2_7182818284)
        knapsacks = [Knapsack(random.randint(1000, 10000)) for _ in range(4)]
        weightclasses = [ItemClass(1, random.randint(100, 1000)) for _ in range(2)]
        items = [random.choice(weightclasses).add_item(knapsacks) for _ in
                 range(13)]
        solver = self.class_to_test(weightclasses, knapsacks, items)
        val, sol = solver.solve()
        self.assertEqual(val, 13)  # calculated using gurobi

        # validate solution using gurobi
        gurobisol, gurobisolution = validate_solution(knapsacks, items, sol)
        self.assertEqual(gurobisolution, grb.GRB.Status.OPTIMAL)
        self.assertEqual(gurobisol, val)

    def test_manual_0(self):
        knapsacks = [Knapsack(10), Knapsack(10)]
        weightclasses = [ItemClass(1, 1)]
        items = [weightclasses[0].add_item(set(knapsacks)) for _ in range(20)]
        solver = self.class_to_test(weightclasses, knapsacks, items)
        val, sol = solver.solve()
        self.assertEqual(val, 20)

    def test_manual_1(self):
        knapsacks = []
        weightclasses = []
        items = []
        solver = self.class_to_test(weightclasses, knapsacks, items)
        val, sol = solver.solve()
        self.assertEqual(val, 0)

    def test_manual_2(self):
        knapsacks = [Knapsack(10), Knapsack(10)]
        weightclasses = [ItemClass(1, 1)]
        items = []
        solver = self.class_to_test(weightclasses, knapsacks, items)
        val, sol = solver.solve()
        self.assertEqual(val, 0)

    def test_manual_3(self):
        knapsacks = [Knapsack(10), Knapsack(10)]
        weightclasses = []
        items = []
        solver = self.class_to_test(weightclasses, knapsacks, items)
        val, sol = solver.solve()
        self.assertEqual(val, 0)

    def test_manual_4(self):
        knapsacks = []
        weightclasses = [ItemClass(1, 1)]
        items = []
        solver = self.class_to_test(weightclasses, knapsacks, items)
        val, sol = solver.solve()
        self.assertEqual(val, 0)

    def test_manual_5(self):
        knapsacks = [Knapsack(10), Knapsack(1)]
        weightclasses = [ItemClass(2, 1)]
        self.assertRaises(Exception, self.class_to_test, weightclasses, knapsacks, [])

    def test_manual_6(self):
        knapsacks = [Knapsack(15), Knapsack(4)]
        weightclasses = [ItemClass(1, 1), ItemClass(1, 2)]
        items = [weightclasses[0].add_item({knapsacks[1]}) for _ in range(10)]
        items.extend([weightclasses[1].add_item(set(knapsacks)) for _ in range(10)])
        items.extend([weightclasses[0].add_item(set(knapsacks)) for _ in range(2)])
        solver = self.class_to_test(weightclasses, knapsacks, items)
        val, sol = solver.solve()
        self.assertEqual(val, 12)

        # validate solution using gurobi
        gurobisol, gurobisolution = validate_solution(knapsacks, items, sol)
        self.assertEqual(gurobisolution, grb.GRB.Status.OPTIMAL)
        self.assertEqual(gurobisol, val)
