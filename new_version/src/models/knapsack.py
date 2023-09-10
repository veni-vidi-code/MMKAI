from itertools import count
from typing import TYPE_CHECKING
import networkx as nx

if TYPE_CHECKING:
    from __future__ import annotations


class Knapsack:
    __slots__ = ['_capacity', 'eligible_items', 'identifier', 'remaining_capacity']
    _counter = count()

    def __init__(self, capacity: int):
        self._capacity = capacity
        self.eligible_items = set()
        self.identifier = next(self._counter)
        self.remaining_capacity = capacity

    def __str__(self):
        return f'Knapsack {self.identifier} ({self.capacity})'

    def __hash__(self):
        return self.identifier

    @property
    def capacity(self):
        return self._capacity


class Item:
    __slots__ = ['_identifier', '_profit', '_weight', '_restrictions', '_weight_class']
    _counter = count()

    def __init__(self, profit: int, weight: int, restrictions: set[Knapsack], item_class: ItemClass):
        self._identifier = next(self._counter)
        self._profit = profit
        self._weight = weight
        self._restrictions = restrictions
        self._weight_class = item_class
        self._weight_class.items.add(self)
        for knapsack in restrictions:
            knapsack.eligible_items.add(self)

    def __str__(self):
        return f'Item {self.identifier} ({self.profit}, {self.weight})'

    def __hash__(self):
        return self.identifier

    @property
    def identifier(self):
        return self._identifier

    @property
    def profit(self):
        return self._profit

    @property
    def weight(self):
        return self._weight

    @property
    def restrictions(self):
        return self._restrictions


class ItemClass(object):
    __slots__ = ['_items', '_profit', '_weight', '_sorted_items', '_available_spaces', '_graph']
    lookup = dict()

    def __new__(cls, profit: int, weight: int):
        if (profit, weight) in cls.lookup:
            return cls.lookup[(profit, weight)]
        else:
            instance = super(ItemClass, cls).__new__(cls)
            cls.lookup[(profit, weight)] = instance
            return instance

    def __init__(self, profit: int, weight: int):
        self._items = set()
        self._profit = profit
        self._weight = weight

    def __str__(self):
        return f'ItemClass ({self.profit}, {self.weight})'

    def __hash__(self):
        return hash((self.profit, self.weight))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def items(self):
        return self._items

    @property
    def profit(self):
        return self._profit

    @property
    def weight(self):
        return self._weight

    def add_item(self, restrictions: set[Knapsack]):
        item = Item(self.profit, self.weight, restrictions, self)
        return item

    def prepare(self, knapsacks: list[Knapsack]):
        self._sorted_items = sorted(self.items, key=lambda x: x.profit / x.weight, reverse=True)
        self._available_spaces = [min(k.capacity // self._weight, len(self.items)) for k in knapsacks]
        self._graph = nx.Graph(
            {i: ((knapsack, j) for i, knapsack in enumerate(knapsacks) for j in range(self._available_spaces[i])) for i
             in self._sorted_items})
