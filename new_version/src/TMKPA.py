import collections

import networkx as nx
from gurobipy import quicksum

from new_version.src.models.knapsack import Knapsack, Item, ItemClass
import gurobipy as grb

from copy import deepcopy


class MatchingSave:
    def __init__(self, matching: dict, graph: nx.Graph, remaining_capacity: list[int], match_vec: list[int],
                 item_class: ItemClass):
        self.matching = matching
        self.graph = graph
        self.remaining_capacity = remaining_capacity.copy()
        self.match_vec = match_vec
        self.item_class = item_class

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        return MatchingSave(self.matching.copy(), self.graph.copy(),
                            self.remaining_capacity.copy(), self.match_vec.copy(), self.item_class)

    def __str__(self):
        return f"MatchingSave(matching={self.matching}, graph={self.graph}, " \
               f"remaining_capacity={self.remaining_capacity}, " \
               f"match_vec={self.match_vec}, item_class={self.item_class})"

    def __repr__(self):
        return str(self)


class TMKPA:
    # ONLY FOR MKPA with identical profits
    def __init__(self, item_classes: list[ItemClass], knapsacks: list[Knapsack], items: list[Item]):
        self.knapsacks = knapsacks
        self.item_classes = item_classes
        self.item_classes.sort(key=lambda x: x.weight)

        self.items = items
        self.items.sort(key=lambda x: x.weight)
        self.knapsacks.sort(key=lambda x: x.capacity)

        for item_class in self.item_classes:
            item_class.prepare(knapsacks)
            assert item_class.profit == 1

        self.best_solution_value = -1
        self.best_solution: list[MatchingSave] = []

        self.current_value = 0

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

        model.addConstrs(
            (grb.quicksum(x[item] * item.weight
                          for item in items)
             <= capacity), name="knapsack capacity")

        model.update()
        model.optimize()

        return model.objVal, {item for item in items if x[item].X > 0.5}

    def _upper_bound(self, current_fixed_itemclass, current_fixed_knapsack, fixed_to, previous_matchings) -> int:
        model = grb.Model()

        # We will be maximizing
        model.modelSense = grb.GRB.MAXIMIZE

        # create variables
        x = grb.tupledict()
        for item in self.item_classes[current_fixed_itemclass].items:
            for knapsack in range(len(self.knapsacks)):
                x[item, knapsack] = model.addVar(vtype=grb.GRB.BINARY,
                                                 name=f'x[{item.identifier}, {knapsack}]',
                                                 obj=item.profit)

        y = grb.tupledict()
        for itemclass in self.item_classes[current_fixed_itemclass + 1:]:
            for item in itemclass.items:
                for knapsack in range(len(self.knapsacks)):
                    y[item, knapsack] = model.addVar(vtype=grb.GRB.BINARY,
                                                     name=f'y[{item.identifier}, {knapsack}]',
                                                     obj=item.profit)

        z = grb.tupledict()
        for knapsack in range(current_fixed_knapsack + 1):
            z[knapsack] = model.addVar(vtype=grb.GRB.INTEGER,
                                       name=f'z[{knapsack}]',
                                       obj=0)

        model.addConstrs(
            z[knapsack] == quicksum(x[item, knapsack] for item in self.item_classes[current_fixed_itemclass].items) for
            knapsack in range(current_fixed_knapsack + 1))

        model.addConstr(z[current_fixed_knapsack] == fixed_to)
        model.addConstrs(z[knapsack] == previous_matchings[current_fixed_itemclass].match_vec[knapsack] for knapsack in
                         range(current_fixed_knapsack))

        model.addConstrs(
            quicksum(x[item, knapsack] for knapsack in range(len(self.knapsacks))) <= 1 for item in
            self.item_classes[current_fixed_itemclass].items)

        model.addConstrs(
            quicksum(y[item, knapsack] for knapsack in range(len(self.knapsacks))) <= 1 for itemclass in
            self.item_classes[current_fixed_itemclass + 1:] for item in itemclass.items)

        model.addConstrs(
            quicksum(x[item, knapsack] for item in self.item_classes[current_fixed_itemclass].items) *
            self.item_classes[current_fixed_itemclass].weight +
            quicksum(y[item, knapsack] * item.weight for item in itemclass.items) <= self.knapsacks[knapsack].capacity
            for itemclass in
            self.item_classes[current_fixed_itemclass + 1:] for knapsack in
            range(len(self.knapsacks)))  # TODO asjust to remaining capacity

        model.update()
        model.optimize()

        if model.status == grb.GRB.Status.OPTIMAL:
            return model.objVal
        else:
            # calculate IIS solution
            # model.computeIIS()
            # model.write("model.ilp")

            return -1

    def _reduce_matching_by_one(self, current_itemclass: int,
                                knapsack_to_reduce_index: int,
                                matching: dict, graph: nx.Graph, remaining_capacity: list) -> bool:
        """
        Attempts to reduce matching at given index by one without changing matching count in higher knapsacks
        or decreasing total matching count
        """
        # DFS
        checked = set()
        stack: list[tuple[tuple[int, int] | int, tuple | bool]] = \
            [(i, False) for i in matching if isinstance(i, tuple) and i[0] == knapsack_to_reduce_index]
        checked.update(i[0] for i in stack)
        while stack:
            x = stack.pop()
            vertex = x[0]
            if isinstance(vertex, int):
                # vertex is an item
                # get all neighbouring knapsacks
                knapsacks = [(i, x) for i in graph.neighbors(vertex) if i not in checked]
                if vertex in matching:
                    knapsacks.remove((matching[vertex], x))
                stack.extend(knapsacks)
                checked.update((knapsack[0] for knapsack in knapsacks))
            else:
                # vertex is a knapsack
                if vertex in matching:
                    if matching[vertex] not in checked:
                        stack.append((matching[vertex], x))
                        checked.add(matching[vertex])
                elif vertex[0] > current_itemclass:
                    # we can reduce the matching
                    # construct the path
                    path = [vertex]
                    while x:
                        path.append(x[0])
                        x = x[1]
                    # reduce the matching
                    for i in range(0, len(path), 2):
                        matching[path[i]] = path[i + 1]
                        matching[path[i + 1]] = path[i]
                    matching.pop(path[-1])
                    remaining_capacity[knapsack_to_reduce_index] += self.item_classes[current_itemclass].weight
                    remaining_capacity[vertex[0]] -= self.item_classes[current_itemclass].weight
                    return True

        return False

    def _increase_matching_by_one(self, current_itemclass, knapsack_to_increase_index: int, matching: dict,
                                  graph: nx.Graph, remaining_capacity: list[int]) -> bool:
        """
        Attempts to increase matching at given index by one without changing matching count in higher knapsacks
        or changing total matching count
        """
        # DFS
        checked = set()
        stack: list[tuple[tuple[int, int] | int, tuple | bool]] = \
            [(i, False) for i in graph.nodes if isinstance(i, tuple)
             and i[0] == knapsack_to_increase_index and i not in matching]
        checked.update(i[0] for i in stack)
        while stack:
            x = stack.pop()  # TODO compare to dfs
            vertex = x[0]
            if isinstance(vertex, int):
                # vertex is an item
                assert vertex not in matching
                if matching[vertex] not in checked:
                    stack.append((matching[vertex], x))
                    checked.add(matching[vertex])
            else:
                # vertex is a knapsack
                if vertex[0] <= current_itemclass:
                    # get all neighbouring items
                    items = {i for i in graph.neighbors(vertex) if i not in checked}
                    checked.update(items)
                    stack.extend([(i, x) for i in items])
                else:
                    # we can increase the matching
                    # construct the path
                    path = [vertex]
                    while x:
                        path.append(x[0])
                        x = x[1]
                    # increase the matching
                    for i in range(1, len(path), 2):
                        matching[path[i]] = path[i + 1]
                        matching[path[i + 1]] = path[i]
                    matching.pop(vertex)
                    remaining_capacity[knapsack_to_increase_index] -= self.item_classes[current_itemclass].weight
                    remaining_capacity[vertex[0]] += self.item_classes[current_itemclass].weight
                    return True
        return False

    def _improve_matching(self, matching, graph, itemclass: ItemClass, match_vec, remaining_capacity):
        """
        Bases on Hopcroft-Karp algorithm and its implementation in networkx

        Aric A. Hagberg, Daniel A. Schult and Pieter J. Swart,
        “Exploring network structure, dynamics, and function using NetworkX”,
        in Proceedings of the 7th Python in Science Conference (SciPy2008),
        Gäel Varoquaux, Travis Vaught, and Jarrod Millman (Eds), (Pasadena, CA USA), pp. 11–15, Aug 2008

        John E. Hopcroft and Richard M. Karp. “An n^{5 / 2} Algorithm for Maximum Matchings in Bipartite Graphs”
        In: SIAM Journal of Computing 2.4 (1973), pp. 225–231.
        https://doi.org/10.1137/0202019
        """
        items = itemclass.items
        distances = {}
        queue = collections.deque()

        def breadth_first_search():
            for v in items:
                if matching.get(v, None) is None:
                    distances[v] = 0
                    queue.append(v)
                else:
                    distances[v] = -1
            distances[None] = -1
            while queue:
                v = queue.popleft()
                if distances[v] < distances[None]:
                    for u in graph[v]:
                        if distances[matching.get(u, None)] == -1:
                            distances[matching.get(u, None)] = distances[v] + 1
                            queue.append(matching.get(u, None))
            return distances[None] != -1

        def depth_first_search(v):
            if v is not None:
                for u in graph[v]:
                    if distances[matching[u]] == distances[v] + 1:
                        if depth_first_search(matching[u]):
                            if u not in matching:
                                match_vec[u[0]] += 1
                                remaining_capacity[u[0]] -= itemclass.weight
                            matching[u] = v
                            matching[v] = u
                            return True
                distances[v] = -1
                return False
            return True

        num_matched_pairs = 0
        while breadth_first_search():
            for v in items:
                if matching.get(v, None) is None:
                    if depth_first_search(v):
                        num_matched_pairs += 1

    def _adjust_matching(self, matching_save: MatchingSave, remaining_capacity: list[int]):
        """
        Adjusts matching to current remaining capacity
        by either increasing or decreasing matching until
        a feasible maximum matching is found
        """
        matching_save.remaining_capacity = remaining_capacity.copy()
        item_class = matching_save.item_class
        matching = matching_save.matching
        graph = matching_save.graph
        match_vec = matching_save.match_vec
        for i in range(len(self.knapsacks)):
            remaining_capacity[i] = remaining_capacity[i] - match_vec[i] * item_class.weight
        # remove all nodes with to little remaining capacity
        for node in list(graph.nodes):
            if isinstance(node, tuple) and remaining_capacity[node[0]] != 0\
                    and node[1] > remaining_capacity[node[0]] // item_class.weight:
                graph.remove_node(node)
                if node in matching:
                    x = matching.pop(node)
                    matching.pop(x)
                    match_vec[node[0]] -= 1
                    # find one of the other nodes for this knapsack that will remain and is not yet matched
                    for i in range(remaining_capacity[node[0]] // item_class.weight):
                        if (node[0], i) not in matching:
                            matching[x] = (node[0], i)
                            matching[(node[0], i)] = x
                            break

        # if there are increasing capacities, add nodes and edges
        for i in range(len(self.knapsacks)):
            if remaining_capacity[i] > 0:
                for j in range(remaining_capacity[i] // item_class.weight):
                    if (i, j) not in matching:
                        graph.add_node((i, j))
                        for item in item_class.items:
                            if self.knapsacks[i] in item.restrictions:
                                graph.add_edge((i, j), item)

        # maximize matching by searching for augmenting paths
        self._improve_matching(matching, graph, item_class, match_vec, remaining_capacity)

    def _lower_bound(self, current_fixed_itemclass: int, current_fixed_knapsack: int, fixed_to: int,
                     previous_matchings: list[MatchingSave]) -> (
            int, list[MatchingSave]):
        # ensure that the matching follows fixed_to
        current_save = previous_matchings[current_fixed_itemclass]
        remaining_capacity = previous_matchings[current_fixed_itemclass + 1].remaining_capacity.copy()
        if current_save.match_vec[current_fixed_knapsack] < fixed_to:
            x = self._increase_matching_by_one(current_fixed_itemclass, current_fixed_knapsack,
                                               current_save.matching, current_save.graph, remaining_capacity)
            if not x:
                return -1, previous_matchings

        elif current_save.match_vec[current_fixed_knapsack] > fixed_to:
            x = self._reduce_matching_by_one(current_fixed_itemclass, current_fixed_knapsack,
                                             current_save.matching, current_save.graph, remaining_capacity)
            if not x:
                return -1, previous_matchings

        bound = sum(current_save.match_vec[current_fixed_knapsack + 1:]) * self.item_classes[
            current_fixed_itemclass].profit + self.current_value

        # ensure all following matchings are valid and maximal
        for i in range(current_fixed_itemclass + 1, len(self.item_classes)):
            self._adjust_matching(previous_matchings[i], remaining_capacity)
            bound += sum(previous_matchings[i].match_vec) * self.item_classes[i].profit

        return bound, previous_matchings

    def _branch(self, current_itemclass: int, current_knapsack: int, heuristic_solution: list[MatchingSave]):
        if current_knapsack >= len(self.knapsacks) - 1:
            current_itemclass += 1
            current_knapsack = 0
        else:
            current_knapsack += 1

        current_val = heuristic_solution[current_itemclass].match_vec[current_knapsack]
        available_spaces = heuristic_solution[current_itemclass].remaining_capacity[current_knapsack] // \
                           self.item_classes[current_itemclass].weight
        m = deepcopy(heuristic_solution)
        c_val = self.current_value
        for i in range(current_val, available_spaces):
            self.current_value = c_val + i * self.item_classes[current_itemclass].profit
            if not self._bound(current_itemclass, current_knapsack, i, m):
                break
        m = deepcopy(heuristic_solution)
        for i in range(current_val - 1, -1, -1):
            self.current_value = c_val + i * self.item_classes[current_itemclass].profit
            if not self._bound(current_itemclass, current_knapsack, i, m):
                break

    def _bound(self, current_itemclass: int, current_knapsack: int, fixed_to: int,
               previous_matchings: list[MatchingSave]):
        # calculate upper bound
        U = self._upper_bound(current_itemclass, current_knapsack, fixed_to, previous_matchings)

        if U == -1:
            return False

        # calculate lower bound
        L, heuristic_solution = self._lower_bound(current_itemclass, current_knapsack, fixed_to, previous_matchings)

        if L != sum(sum(heuristic_solution[itemclass].match_vec) for itemclass in range(len(self.item_classes))) and L!= -1:
            raise Exception("Lower bound is incorrect")


        if L == -1:
            return False

        if L > self.best_solution_value:
            self.best_solution_value = L
            self.best_solution = deepcopy(heuristic_solution)

        if U > self.best_solution_value:
            self._branch(current_itemclass, current_knapsack, heuristic_solution)
        return True

    def solve(self) -> (int, dict[Knapsack, set[Item]]):
        if not self.solved:
            remaining_capacity = [k.capacity for k in self.knapsacks]
            matchings = []
            L = 0
            for item_class in self.item_classes:
                graph = item_class._graph.copy()
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

            self._branch(0, -1, matchings)
            self.solved = True

            self.transformed_best_solution = {i: [] for i in self.knapsacks}
            for matching_save in self.best_solution:
                for a, b in matching_save.matching.items():
                    if isinstance(a, Item):
                        self.transformed_best_solution[self.knapsacks[b[0]]].append(a)

        return self.best_solution_value, self.transformed_best_solution
