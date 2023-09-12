from new_version.src.models.knapsack import Knapsack, Item
import gurobipy as grb


class MTM_EXTENDED:
    def __init__(self, items: list[Item], knapsacks: list[Knapsack]):
        self.best_solution_value = -1
        self.best_solution = {}
        self.items = items
        self.knapsacks = knapsacks
        self.knapsacks.sort(key=lambda x: x.capacity)
        self.items.sort(key=lambda x: x.profit / x.weight, reverse=True)
        self.current_value = 0
        self.current_solution = {k: set() for k in knapsacks}
        self.solved = False

    def _solve_single_kp(self, capacity, items: list[Item]) -> (int, set[Item]):
        model = grb.Model()

        # We will be maximizing
        model.modelSense = grb.GRB.MAXIMIZE

        # create variables
        x = grb.tupledict()
        for item in items:
            x[item] = model.addVar(vtype=grb.GRB.BINARY,
                                   name=f'x[{item.identifier}]',
                                   obj=item.profit)

        model.addConstr(grb.quicksum(x[item] * item.weight for item in items) <= capacity, name="knapsack capacity")

        model.update()
        model.optimize()

        return model.objVal, {item for item in items if x[item].X > 0.5}

    def _upper_bound(self, current_knapsack) -> int:
        # Surrogate Relaxation
        if current_knapsack == -1:
            z, _ = self._solve_single_kp(sum((k.capacity for k in self.knapsacks)), self.items)
            return z + self.current_value
        z, _ = self._solve_single_kp(sum((k.capacity for k in self.knapsacks[current_knapsack:])), self.items)
        return z + self.current_value

    def _lower_bound(self, current_knapsack) -> (int, dict[Knapsack, list[Item]]):
        L = self.current_value
        heuristic_solution = {k: [] for k in self.knapsacks}
        heuristik_items = self.items.copy()
        for knapsack in self.knapsacks[current_knapsack:]:
            k = knapsack.remaining_capacity
            items = [item for item in heuristik_items if item.weight <= k and item in knapsack.eligible_items]
            z, x = self._solve_single_kp(k, items)
            L += z
            heuristic_solution[knapsack] = sorted(list(x), key=lambda x: x.profit / x.weight, reverse=True)

            heuristik_items = [item for item in heuristik_items if item not in x]
        return L, heuristic_solution

    def _solve(self, current_knapsack=0):
        # calculate upper bound
        U = self._upper_bound(current_knapsack)

        # calculate lower bound
        L, heuristic_solution = self._lower_bound(current_knapsack)

        if L > self.best_solution_value:
            self.best_solution_value = L
            self.best_solution = {k: set(v).union(self.current_solution[k]) for k, v in heuristic_solution.items()}

        if U > self.best_solution_value:
            # branch
            while not heuristic_solution[self.knapsacks[current_knapsack]]:
                current_knapsack += 1
                if current_knapsack >= len(self.knapsacks) - 1:
                    return
            item = heuristic_solution[self.knapsacks[current_knapsack]].pop(0)
            self.knapsacks[current_knapsack].eligible_items.remove(item)

            # add item to knapsack
            self.current_solution[self.knapsacks[current_knapsack]].add(item)
            self.current_value += item.profit
            self.knapsacks[current_knapsack].remaining_capacity -= item.weight
            self.items.remove(item)
            self._solve(current_knapsack)

            # remove item from knapsack
            self.current_solution[self.knapsacks[current_knapsack]].remove(item)
            self.current_value -= item.profit
            self.knapsacks[current_knapsack].remaining_capacity += item.weight
            self.items.append(item)
            self._solve(current_knapsack)

            # unbranch
            self.knapsacks[current_knapsack].eligible_items.add(item)

    def solve(self) -> (int, dict[Knapsack, set[Item]]):
        if not self.solved:
            self._solve(0)
            self.solved = True
        return self.best_solution_value, self.best_solution
