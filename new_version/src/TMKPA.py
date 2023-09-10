import networkx as nx

from new_version.src.models.knapsack import Knapsack, Item, ItemClass
import gurobipy as grb


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

        self.best_solution_value = -1
        self.best_solution = {}

        self.current_value = 0
        self.current_solution = {k: set() for k in knapsacks}

        self.matching_vector = [[0 for _ in knapsacks] for weight_class in self.item_classes]
        self.matchings = []

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

    def _upper_bound(self, current_knapsack) -> int:

    def _lower_bound(self, current_itemclass, previous_matchings, fixed) -> (int, dict[Knapsack, list[Item]]):
        # fixed: last fixed knapsack, number of items
        L = self.current_value

        matchings = {}

        if previous_matchings is None:
            remaining_capacity = [k.remaining_capacity for k in self.knapsacks]
            for item_class in self.item_classes[current_itemclass:]:
                graph = item_class._graph.copy()
                graph.remove_edges_from(((knapsack, j) for i, knapsack in enumerate(self.knapsacks)
                                         for j in range(remaining_capacity[i] // item_class.weight,
                                                        item_class._available_spaces[i])))
                matching = nx.algorithms.bipartite.hopcroft_karp_matching(graph, item_class.items)
                match_vec = [0 for _ in self.knapsacks]
                for i, knapsack in enumerate(self.knapsacks):
                    for j in range(remaining_capacity[i] // item_class.weight, item_class._available_spaces[i]):
                        if (knapsack, j) in matching:
                            match_vec[i] += 1
                matchings[item_class] = (matching, graph, str(remaining_capacity), match_vec)
                L += item_class.profit * sum(match_vec)
                remaining_capacity = [remaining_capacity[i] - match_vec[i] * item_class.weight for i in
                                      range(len(self.knapsacks))]

        else:
            remaining_capacity = [k.remaining_capacity for k in self.knapsacks]

            item_class = self.item_classes[current_itemclass]
            prev_match = previous_matchings[item_class]
            if prev_match[2] != str(remaining_capacity):
                # matching needs to be recalculated
                # TODO
                pass
            # ensure that the matching satisfies fixed in this class
            if prev_match[3][fixed[0]] < fixed[1]:
                graph = prev_match[1].copy()
                # find one augmenting path from the fixed knapsack that are matched to one of the next knapsacks
                todolist = [((self.knapsacks[fixed[0]], j), False, []) for j in
                            range(remaining_capacity[fixed[0]] // item_class.weight,
                                  item_class._available_spaces[fixed[0]]) if
                            (self.knapsacks[fixed[0]], j) not in prev_match[0]]
                checked_nodes = {node[0] for node in todolist}.union({prev_match[0][node[0]] for node in todolist})
                while todolist:
                    node = todolist.pop()
                    if node[1]:
                        # Knapsack
                        if node[0] in prev_match[0]:
                            path = node[2]
                            path.append(node[0])
                            todolist.append((prev_match[0][node[0]], False, path))
                        elif self.knapsacks.index(node[0][0]) > fixed[0]:
                            # found augmenting path
                            matching = prev_match[0].copy()
                            path = node[2]
                            path.append(node[0])
                            match_vec = prev_match[3].copy()
                            match_vec[fixed[0]] += 1
                            match_vec[self.knapsacks.index(node[0][0])] -= 1
                            for i in range(len(path) - 1, 0, -2):
                                matching[path[i]] = path[i - 1]
                                matching[path[i - 1]] = path[i]
                            matchings[item_class] = (matching, graph, str(remaining_capacity), match_vec)
                            L += item_class.profit * sum(match_vec)
                            remaining_capacity = [remaining_capacity[i] - match_vec[i] * item_class.weight for i in
                                                  range(len(self.knapsacks))]
                            break

                    else:
                        # Item
                        for neighbor in graph.neighbors(node[0]):
                            if neighbor not in checked_nodes and neighbor[0] != prev_match[0][node[0]]:
                                path = node[2]
                                path.append(node[0])
                                todolist.append((neighbor, True, path))
                                checked_nodes.add(neighbor)
                else:
                    # no augmenting path found
                    return False

            elif prev_match[3][fixed[0]] < fixed[1]:
                graph = prev_match[1].copy()
                # find one augmenting path from the fixed knapsack that are matched to one of the next knapsacks
                todolist = [(prev_match[(self.knapsacks[fixed[0]], j)], False, [(self.knapsacks[fixed[0]], j)]) for j in
                            range(remaining_capacity[fixed[0]] // item_class.weight,
                                  item_class._available_spaces[fixed[0]]) if
                            (self.knapsacks[fixed[0]], j) in prev_match[0]]
                checked_nodes = {node[0] for node in todolist}.union({prev_match[0][node[0]] for node in todolist})
                while todolist:
                    node = todolist.pop()
                    if node[1]:
                        # Knapsack
                        if node[0] in prev_match[0]:
                            path = node[2]
                            path.append(node[0])
                            todolist.append((prev_match[0][node[0]], False, path))
                        elif self.knapsacks.index(node[0][0]) > fixed[0]:
                            # found augmenting path
                            matching = prev_match[0].copy()
                            path = node[2]
                            path.append(node[0])
                            match_vec = prev_match[3].copy()
                            match_vec[fixed[0]] += 1
                            match_vec[self.knapsacks.index(node[0][0])] -= 1
                            for i in range(len(path) - 1, 0, -2):
                                matching[path[i]] = path[i - 1]
                                matching[path[i - 1]] = path[i]
                            matchings[item_class] = (matching, graph, str(remaining_capacity), match_vec)
                            L += item_class.profit * sum(match_vec)
                            remaining_capacity = [remaining_capacity[i] - match_vec[i] * item_class.weight for i in
                                                  range(len(self.knapsacks))]
                            break

                    else:
                        # Item
                        for neighbor in graph.neighbors(node[0]):
                            if neighbor not in checked_nodes and neighbor[0] != prev_match[0][node[0]]:
                                path = node[2]
                                path.append(node[0])
                                todolist.append((neighbor, True, path))
                                checked_nodes.add(neighbor)
                else:
                    # no augmenting path found
                    return False

            for item_class in self.item_classes[current_itemclass + 1:]:
                prev_match = previous_matchings[item_class]

    def _solve(self, current_itemclass=0, previous_matchings=None):
        # calculate upper bound
        U = self._upper_bound(current_itemclass)

        # calculate lower bound
        L, heuristic_solution = self._lower_bound(current_itemclass, previous_matchings)

        if L > self.best_solution_value:
            self.best_solution_value = L
            self.best_solution = {k: set(v).union(self.current_solution[k]) for k, v in heuristic_solution.items()}

        if U > self.best_solution_value:

    def solve(self) -> (int, dict[Knapsack, set[Item]]):
        if not self.solved:
            self._solve(0)
            self.solved = True
        return self.best_solution_value, self.best_solution
