# Copyright (c) 2023 Tom Mucke
import json
import os
import random
import sys
import time

from runtime_tester.Testrecord import Testrecord
from src.MTM_EXTENDED_iterative import MTM_EXTENDED_iterative
from src.TMKPA_iterative import TMKPA_iterative
from src.models.knapsack import Knapsack
from src.models.item_class import ItemClass

import timeit


def create_testinstance(number_of_knapsacks, number_of_items, number_of_weightclasses,
                        min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
                        knapsacks_per_item_max, seed=None):
    if seed is None:
        seed = random.randrange(sys.maxsize)
    random.seed(seed)

    knapsacks = [Knapsack(random.randint(min_capacity, max_capacity)) for _ in range(number_of_knapsacks)]

    max_weight = min(max_weight, max(knapsacks, key=lambda x: x.capacity).capacity)

    if max_weight < min_weight:
        min_weight = max_weight

    weightclasses = [ItemClass(1, random.randint(min_weight, max_weight)) for _ in range(number_of_weightclasses)]

    items_per_itemclass = [0] * number_of_weightclasses

    for _ in range(number_of_items):
        items_per_itemclass[random.randint(0, number_of_weightclasses - 1)] += 1

    items = []

    for number_of_items_for_weightclass, weightclass in zip(items_per_itemclass, weightclasses):
        fittable_knapsacks = list(filter(lambda x: x.capacity >= weightclass.weight, knapsacks))
        mi = min(knapsacks_per_item_min, len(fittable_knapsacks))
        ma = min(knapsacks_per_item_max, len(fittable_knapsacks))
        for _ in range(number_of_items_for_weightclass):
            k = random.randint(mi, ma)
            restrictions = random.sample(fittable_knapsacks, k)
            items.append(weightclass.add_item(restrictions))

    return knapsacks, items, weightclasses, seed


def performe_tests(number_of_knapsacks, number_of_items, number_of_weightclasses,
                   min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
                   knapsacks_per_item_max, seed):
    print(f"Number of knapsacks: {number_of_knapsacks}\nNumber of items: {number_of_items}\n"
          f"Number of weight classes: {number_of_weightclasses}")
    knapsacks_1, items_1, weightclasses_1, seed = create_testinstance(number_of_knapsacks, number_of_items,
                                                                      number_of_weightclasses,
                                                                      min_weight, max_weight, min_capacity,
                                                                      max_capacity, knapsacks_per_item_min,
                                                                      knapsacks_per_item_max, seed)
    knapsacks_2, items_2, weightclasses_2, _ = create_testinstance(number_of_knapsacks, number_of_items,
                                                                   number_of_weightclasses,
                                                                   min_weight, max_weight, min_capacity, max_capacity,
                                                                   knapsacks_per_item_min,
                                                                   knapsacks_per_item_max, seed)

    print(f"Seed: {seed}")

    tmkpa = TMKPA_iterative(weightclasses_1, knapsacks_1, items_1)
    mtm_extended = MTM_EXTENDED_iterative(items_2, knapsacks_2)
    tmkpa_time = None
    tmkpa_cpu_time = None
    mtm_extended_time = None
    mtm_extended_cpu_time = None

    try:
        tmkpa_time = timeit.timeit(lambda: tmkpa.solve(), number=1, timer=timeit.default_timer)
        tmkpa_cpu_time = timeit.timeit(lambda: tmkpa.solve(), number=1, timer=time.process_time)
        print(f"TMKPA: {tmkpa_time} seconds")
    except Exception as e:
        print(f"TMKPA: {e}")

    try:
        mtm_extended_time = timeit.timeit(lambda: mtm_extended.solve(), number=1, timer=timeit.default_timer)
        mtm_extended_cpu_time = timeit.timeit(lambda: mtm_extended.solve(), number=1, timer=time.process_time)
        print(f"MTM_EXTENDED: {mtm_extended_time} seconds")
    except Exception as e:
        print(f"MTM_EXTENDED: {e}")

    return Testrecord(number_of_knapsacks=number_of_knapsacks, number_of_items=number_of_items,
                      number_of_weightclasses=number_of_weightclasses, min_weight=min_weight, max_weight=max_weight,
                      min_capacity=min_capacity, max_capacity=max_capacity,
                      knapsacks_per_item_min=knapsacks_per_item_min,
                      knapsacks_per_item_max=knapsacks_per_item_max, seed=seed,
                      required_time_tmkpa=tmkpa_time, required_time_mtm_extended=mtm_extended_time,
                      required_cpu_time_tmkpa=tmkpa_cpu_time, required_cpu_time_mtm_extended=mtm_extended_cpu_time)


def performe_x_tests(number_of_knapsacks, number_of_items, number_of_weightclasses,
                     min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
                     knapsacks_per_item_max, x):
    return [performe_tests(number_of_knapsacks, number_of_items, number_of_weightclasses,
                           min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
                           knapsacks_per_item_max, None) for _ in range(x)]


def perform_multiple_tests_json(x, base_dir="./test_results"):
    filename = f"{base_dir}/test_results_{time.time()}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, "w+") as f:
            f.write("[")
            for number_of_weightclasses in range(1, 6):
                for number_of_knapsacks in range(1, 6):
                    for number_of_items_exp in range(6):
                        number_of_items = 10 ** number_of_items_exp
                        max_capacity = 100_000
                        min_capacity = 1
                        max_weight = 10_000
                        min_weight = 1
                        knapsacks_per_item_min = 1
                        knapsacks_per_item_max = number_of_knapsacks
                        print(f"Number of knapsacks: {number_of_knapsacks}\nNumber of items: {number_of_items:_}\n"
                              f"Number of weight classes: {number_of_weightclasses}")
                        results = performe_x_tests(number_of_knapsacks, number_of_items, number_of_weightclasses,
                                                   min_weight, max_weight, min_capacity, max_capacity,
                                                   knapsacks_per_item_min,
                                                   knapsacks_per_item_max, x)
                        json.dump(results, f)
                        f.write(",")

    finally:
        with open(filename, "rb+") as f:
            f.seek(-1, 2)
            f.truncate()

        with open(filename, "a") as f:
            f.write("]")


if __name__ == '__main__':
    perform_multiple_tests_json(10)
