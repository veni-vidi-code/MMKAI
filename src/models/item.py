from __future__ import annotations

from itertools import count

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.knapsack import Knapsack
    from src.models.item_class import ItemClass


class Item:
    __slots__ = ['_identifier', '_profit', '_weight', '_restrictions', '_item_class']
    _counter = count()

    def __init__(self, profit: int, weight: int, restrictions: set[Knapsack], item_class: ItemClass):
        self._identifier = next(self._counter)
        self._profit = profit
        assert weight > 0
        assert profit > 0
        self._weight = weight
        self._restrictions = restrictions
        self._item_class = item_class
        self._item_class.items.add(self)
        for knapsack in restrictions:
            knapsack.eligible_items.add(self)

    def __str__(self):
        return f'Item {self._identifier} ({self.profit}, {self.weight})'

    def __repr__(self):
        return f'Item {self._identifier} ({self.profit}, {self.weight})'

    def __hash__(self):
        return self._identifier

    def __eq__(self, other):
        if isinstance(other, Item):
            return self._identifier == other._identifier
        return False

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

    @property
    def item_class(self):
        return self._item_class
