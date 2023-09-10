from dataclasses import dataclass, field
from itertools import count
from typing import Optional


@dataclass(order=False, frozen=True, slots=True)
class Knapsack:
    capacity: int = field(hash=False)
    identifier: int = field(default_factory=count().__next__, init=False)

    def __str__(self):
        return f'Knapsack {self.identifier} ({self.capacity})'

    def __hash__(self):
        return self.identifier


@dataclass(frozen=True, slots=True, order=False)
class Item:
    identifier: int = field(default_factory=count().__next__, init=False, hash=True)
    profit: int = field(hash=False)
    weight: int = field(hash=False)

    # if None, item can be placed in any knapsack, else only in knapsacks in the list
    restrictions: Optional[list[Knapsack]] = field(default=None, hash=False)

    def __hash__(self):
        return self.identifier

