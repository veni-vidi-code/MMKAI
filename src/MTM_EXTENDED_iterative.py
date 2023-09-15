"""
Copyrigth (c) 2023 Tom Mucke

The Idea of this algorithm is based on the MTM Algorithm from
    Martello, Silvano; Toth, Paolo (1981):
    A Bound and Bound algorithm for the zero-one multiple knapsack problem.
    In: Discrete Applied Mathematics 3 (4), S. 275–288. DOI: 10.1016/0166-218X(81)90005-6.
which was extended to allow for multiple knapsacks
"""
import collections

from src.MTM_EXTENDED_recursive import MTM_EXTENDED_recursive
from src.models.knapsack import Knapsack
from src.models.item import Item
import gurobipy as grb


class MTM_EXTENDED_iterative(MTM_EXTENDED_recursive):
    def _solve(self, current_knapsack=0):
        stack: collections.deque[tuple[int, Item, bool]] = collections.deque()

        U = self._upper_bound(current_knapsack)

        L, heuristic_solution = self._lower_bound(current_knapsack)

        if L > self.best_solution_value:
            self.best_solution_value = L
            self.best_solution = {k: set(v).union(self.current_solution[k]) for k, v in heuristic_solution.items()}

        while U > self.best_solution_value:
            while True:
                backtrack = False
                while not heuristic_solution[self.knapsacks[current_knapsack]]:
                    current_knapsack += 1
                    if current_knapsack >= len(self.knapsacks) - 1:
                        backtrack = True
                        break
                if backtrack:
                    break
                item = heuristic_solution[self.knapsacks[current_knapsack]].pop(0)
                self.knapsacks[current_knapsack].eligible_items.remove(item)

                # add item to knapsack
                self.current_solution[self.knapsacks[current_knapsack]].add(item)
                self.current_value += item.profit
                self.knapsacks[current_knapsack].remaining_capacity -= item.weight
                self.items.remove(item)
                stack.append((current_knapsack, item, True))

                U = self._upper_bound(current_knapsack)

            while stack:
                # unbranch
                current_knapsack, item, one = stack.pop()

                if one:
                    self.current_solution[self.knapsacks[current_knapsack]].remove(item)
                    self.current_value -= item.profit
                    self.knapsacks[current_knapsack].remaining_capacity += item.weight
                    self.items.append(item)
                    break
                else:
                    self.knapsacks[current_knapsack].eligible_items.add(item)
            else:
                break

            L, heuristic_solution = self._lower_bound(current_knapsack)

            if L > self.best_solution_value:
                self.best_solution_value = L
                self.best_solution = {k: set(v).union(self.current_solution[k]) for k, v in heuristic_solution.items()}
