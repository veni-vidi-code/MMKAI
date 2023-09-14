# Copyright (c) 2023 Tom Mucke
from itertools import count

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.item import Item


class Knapsack:
    __slots__ = ['_capacity', 'eligible_items', 'identifier', 'remaining_capacity']
    _counter = count()

    def __init__(self, capacity: int):
        assert capacity > 0
        self._capacity = capacity
        self.eligible_items: set[Item] = set()
        self.identifier = next(self._counter)
        self.remaining_capacity = capacity

    def __str__(self):
        return f'Knapsack {self.identifier} ({self.capacity})'

    def __repr__(self):
        return f'Knapsack {self.identifier} ({self.capacity})'

    def __hash__(self):
        return self.identifier

    def __eq__(self, other):
        return self.identifier == other.identifier

    @property
    def capacity(self):
        return self._capacity
