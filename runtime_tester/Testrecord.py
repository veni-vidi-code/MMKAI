from typing import TypedDict


class Testrecord(TypedDict):
    number_of_knapsacks: int
    number_of_items: int
    number_of_weightclasses: int
    min_weight: int
    max_weight: int
    min_capacity: int
    max_capacity: int
    knapsacks_per_item_min: int
    knapsacks_per_item_max: int
    seed: int
    required_time_MMKAI: float | None
    required_time_mtm_extended: float | None
    required_cpu_time_MMKAI: float | None
    required_cpu_time_mtm_extended: float | None
