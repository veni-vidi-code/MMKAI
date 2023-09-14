# Copyright (c) 2023 Tom Mucke
from __future__ import annotations

import networkx as nx

from src.models.item import Item
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.knapsack import Knapsack


class ItemClass(object):
    __slots__ = ['_items', '_profit', '_weight', '_available_spaces', '_graph']
    lookup = dict()

    def __new__(cls, profit: int, weight: int):
        if (profit, weight) in cls.lookup:
            return cls.lookup[(profit, weight)]
        else:
            instance = super(ItemClass, cls).__new__(cls)
            cls.lookup[(profit, weight)] = instance
            return instance

    def __init__(self, profit: int, weight: int):
        assert weight > 0
        assert profit > 0
        self._items = set()
        self._profit = profit
        self._weight = weight
        self._graph = None
        self._available_spaces = None

    def __str__(self):
        return f'ItemClass ({self.profit}, {self.weight})'

    def __repr__(self):
        return f'ItemClass ({self.profit}, {self.weight})'

    def __hash__(self):
        return hash((self.profit, self.weight))

    def __eq__(self, other):
        return (self.profit, self.weight) == (other.profit, other.weight)

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
        item = Item(self.profit, self.weight, set(restrictions), self)
        return item

    def prepare(self, knapsacks: list[Knapsack]):
        self._available_spaces = [min(k.capacity // self._weight, len(self.items)) for k in knapsacks]
        self._graph = nx.Graph(
            {(i, j): tuple(item for item in self._items if knapsack in item.restrictions)
             for i, knapsack in enumerate(knapsacks) for j in range(self._available_spaces[i])})
