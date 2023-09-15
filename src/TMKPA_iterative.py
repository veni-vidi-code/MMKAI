import collections

from src.TMKPA_recursive import *


class TMKPA_iterative(TMKPA_recursive):
    def _branch(self, current_itemclass: int, current_knapsack: int, heuristic_solution: list[MatchingSave]):
        cval_change = 0
        if current_knapsack >= len(self.knapsacks) - 1:
            current_itemclass += 1
            current_knapsack = 0
            if current_itemclass >= len(self.item_classes) - 1:
                return
            cval_change = sum(heuristic_solution[current_itemclass].match_vec) \
                          * self.item_classes[current_itemclass].profit
            self.current_value += cval_change
        else:
            current_knapsack += 1

        current_val = heuristic_solution[current_itemclass].match_vec[current_knapsack]
        available_spaces = heuristic_solution[current_itemclass].remaining_capacity[current_knapsack] // \
                           self.item_classes[current_itemclass].weight
        m = deepcopy(heuristic_solution)
        for i in range(current_val, available_spaces + 1):
            if not self._bound(current_itemclass, current_knapsack, i, m):
                break
        if current_val > 0:  # deepcopy is expensive
            m = deepcopy(heuristic_solution)
            for i in range(current_val - 1, -1, -1):
                if not self._bound(current_itemclass, current_knapsack, i, m):
                    break
        self.current_value -= cval_change

    def _bound(self, current_itemclass: int, current_knapsack: int, fixed_to: int,
               previous_matchings: list[MatchingSave]):
        # calculate upper bound
        U = self._upper_bound(current_itemclass, current_knapsack, fixed_to, previous_matchings)

        if U == -1:
            return False

        # calculate lower bound
        L, heuristic_solution = self._lower_bound(current_itemclass, current_knapsack, fixed_to, previous_matchings)

        if L != sum(sum(i.match_vec) for i in heuristic_solution) and L != -1:
            raise Exception("Lower bound is incorrect, it should be "
                            + str(sum(sum(i.match_vec) for i in heuristic_solution))
                            + " but is " + str(L) + ". The number of matchings is "
                            + str([sum(i.match_vec) for i in heuristic_solution]) + str(
                [len(i.matching) for i in heuristic_solution]))

        if L == -1:
            return False

        if L > self.best_solution_value:
            self.best_solution_value = L
            self.best_solution = deepcopy(heuristic_solution)

        if U > self.best_solution_value:
            self._branch(current_itemclass, current_knapsack, heuristic_solution)
        return True

    def _solve(self):
        remaining_capacity = [k.capacity for k in self.knapsacks]
        matchings = []
        L = 0
        for item_class in self.item_classes:
            graph = copy_graph(item_class._graph)
            graph.remove_nodes_from(list((i, j) for i in range(len(self.knapsacks))
                                         for j in range(remaining_capacity[i] // item_class.weight,
                                                        item_class._available_spaces[i])))
            matching = nx.algorithms.bipartite.hopcroft_karp_matching(graph, item_class.items)
            match_vec = [0 for _ in self.knapsacks]
            for i, knapsack in enumerate(self.knapsacks):
                for j in range(min(remaining_capacity[i] // item_class.weight, item_class._available_spaces[i])):
                    if (i, j) in matching:
                        match_vec[i] += 1
            matchings.append(MatchingSave(matching, graph, remaining_capacity, match_vec, item_class))
            L += item_class.profit * sum(match_vec)
            remaining_capacity = [remaining_capacity[i] - match_vec[i] * item_class.weight for i in
                                  range(len(self.knapsacks))]
        self.best_solution_value = L
        self.best_solution = deepcopy(matchings)

        stack: collections.deque[tuple[int, int, int, list, bool, int]] = collections.deque()
        current_itemclass, current_knapsack, heuristic_solution = -1, len(self.knapsacks), matchings

        while stack:

            cval_change = 0
            if current_knapsack >= len(self.knapsacks) - 1:
                current_itemclass += 1
                current_knapsack = 0
                if current_itemclass >= len(self.item_classes) - 1:
                    return
                cval_change = sum(heuristic_solution[current_itemclass].match_vec) \
                              * self.item_classes[current_itemclass].profit
                self.current_value += cval_change
            else:
                current_knapsack += 1

            current_val = heuristic_solution[current_itemclass].match_vec[current_knapsack]
            available_spaces: int = heuristic_solution[current_itemclass].remaining_capacity[current_knapsack] // \
                                    self.item_classes[current_itemclass].weight

            if current_val > 0:  # deepcopy is expensive
                m = deepcopy(heuristic_solution)
                stack.append((current_itemclass, current_knapsack, current_val - 1, m, False, cval_change))
            m = deepcopy(heuristic_solution)
            stack.append((current_itemclass, current_knapsack, current_val, m, True, available_spaces))
            self.current_value -= cval_change

            while stack:
                current_itemclass, current_knapsack, fixed_to, previous_matchings, increase, additional = stack.pop()

                U = self._upper_bound(current_itemclass, current_knapsack, fixed_to, previous_matchings)

                if U == -1:
                    continue

                # calculate lower bound
                L, heuristic_solution = self._lower_bound(current_itemclass, current_knapsack, fixed_to,
                                                          previous_matchings)

                assert L == sum(sum(i.match_vec) for i in heuristic_solution) or L == -1, \
                    f"Lower bound is incorrect, it should be {sum(sum(i.match_vec) for i in heuristic_solution)} " \
                    f"but is {L}. The number of matchings is {[sum(i.match_vec) for i in heuristic_solution]} " \
                    f"{[len(i.matching) for i in heuristic_solution]}"

                if L == -1:
                    continue
                if L > self.best_solution_value:
                    self.best_solution_value = L
                    self.best_solution = deepcopy(heuristic_solution)

                if U > self.best_solution_value:
                    if increase and fixed_to < additional:
                        stack.append((current_itemclass, current_knapsack, fixed_to + 1, heuristic_solution, increase,
                                      additional))
                    elif not increase:
                        if fixed_to > 0:
                            stack.append((current_itemclass, current_knapsack, fixed_to - 1, heuristic_solution,
                                          increase, additional))
                        else:
                            self.current_value -= additional
                    break
                else:
                    if not increase:
                        self.current_value -= additional

    def solve(self) -> (int, dict[Knapsack, set[Item]]):
        if not self.solved:
            self._solve()
            self.solved = True

            self.transformed_best_solution = {i: [] for i in self.knapsacks}
            for matching_save in self.best_solution:
                for a, b in matching_save.matching.items():
                    if isinstance(a, Item):
                        self.transformed_best_solution[self.knapsacks[b[0]]].append(a)

        return self.best_solution_value, self.transformed_best_solution
