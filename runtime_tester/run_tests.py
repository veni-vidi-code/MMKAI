# Copyright (c) 2023 Tom Mucke

# Always run with -OO flag to improve performance
import json
import multiprocessing
import os
import random
import sys
import time

from runtime_tester.Testrecord import Testrecord
from src import gurobi
from src.MTM_EXTENDED_iterative import MTM_EXTENDED_iterative
from src.MMKAI_recursive import MMKAI_recursive
from src.models.knapsack import Knapsack
from src.models.item_class import ItemClass

import timeit


class Dummy_Value:
    def __init__(self):
        self.value = -1


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


def timeit_wrapper(instance, cpu_time: bool, result_value, number_of_knapsacks, number_of_items,
                   number_of_weightclasses,
                   min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
                   knapsacks_per_item_max, seed):
    knapsacks, items, item_classes, seed = create_testinstance(number_of_knapsacks, number_of_items,
                                                               number_of_weightclasses,
                                                               min_weight, max_weight, min_capacity,
                                                               max_capacity, knapsacks_per_item_min,
                                                               knapsacks_per_item_max, seed)

    instance = instance(knapsacks=knapsacks, items=items, item_classes=item_classes)

    try:
        if cpu_time:
            result_value.value = timeit.timeit(instance.solve, number=1, timer=time.process_time)
        else:
            result_value.value = timeit.timeit(instance.solve, number=1, timer=timeit.default_timer)
    except SystemExit:
        pass  # timeouts are handled by the main process
    except Exception as e:
        print(f"{e}")
    print(f"Finished {instance.__class__.__name__}")


def performe_tests(number_of_knapsacks, number_of_items, number_of_weightclasses,
                   min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
                   knapsacks_per_item_max, seed, max_time=60 * 3):
    if seed is None:
        seed = random.randrange(sys.maxsize)

    print(f"Number of knapsacks: {number_of_knapsacks}\nNumber of items: {number_of_items}\n"
          f"Number of weight classes: {number_of_weightclasses}")

    required_create_time = timeit.timeit(lambda: create_testinstance(number_of_knapsacks, number_of_items,
                                                                     number_of_weightclasses,
                                                                     min_weight, max_weight, min_capacity,
                                                                     max_capacity, knapsacks_per_item_min,
                                                                     knapsacks_per_item_max, seed), number=1)
    print(f"Required time to create test instance: {required_create_time}")
    max_time += required_create_time * 2

    print(f"Seed: {seed}")

    times = [multiprocessing.Value("d", -1) for _ in range(4)]

    p = []

    for i, instance in enumerate([(MMKAI_recursive, False), (MMKAI_recursive, True),
                                  (MTM_EXTENDED_iterative, False), (MTM_EXTENDED_iterative, True)]):
        p.append(multiprocessing.Process(target=timeit_wrapper, args=(
            instance[0], instance[1], times[i], number_of_knapsacks, number_of_items, number_of_weightclasses,
            min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
            knapsacks_per_item_max, seed)))

    for x in p:
        x.start()

    start_time = timeit.default_timer()
    p[0].join(max_time)
    while any(x.is_alive() for x in p) and timeit.default_timer() - start_time < max_time:
        time.sleep(1)

    for i, x in enumerate(p):
        if x.is_alive():
            x.terminate()
            times[i] = Dummy_Value()
            # The following is colored for better readability
            print("\033[94m" + f"Process {i} timed out" + "\033[0m")

    for i, x in enumerate(p):
        x.join()

    MMKAI_time = times[0].value
    MMKAI_cpu_time = times[1].value
    mtm_extended_time = times[2].value
    mtm_extended_cpu_time = times[3].value

    print(f"Required time to solve MMKAI: {MMKAI_time}")
    print(f"Required time to solve MMKAI (CPU time): {MMKAI_cpu_time}")
    print(f"Required time to solve MTM_EXTENDED: {mtm_extended_time}")
    print(f"Required time to solve MTM_EXTENDED (CPU time): {mtm_extended_cpu_time}")

    return Testrecord(number_of_knapsacks=number_of_knapsacks, number_of_items=number_of_items,
                      number_of_weightclasses=number_of_weightclasses, min_weight=min_weight, max_weight=max_weight,
                      min_capacity=min_capacity, max_capacity=max_capacity,
                      knapsacks_per_item_min=knapsacks_per_item_min,
                      knapsacks_per_item_max=knapsacks_per_item_max, seed=seed,
                      required_time_MMKAI=MMKAI_time, required_time_mtm_extended=mtm_extended_time,
                      required_cpu_time_MMKAI=MMKAI_cpu_time, required_cpu_time_mtm_extended=mtm_extended_cpu_time)


def performe_x_tests(number_of_knapsacks, number_of_items, number_of_weightclasses,
                     min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
                     knapsacks_per_item_max, x):
    return [performe_tests(number_of_knapsacks, number_of_items, number_of_weightclasses,
                           min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
                           knapsacks_per_item_max, None) for _ in range(x)]


def perform_multiple_tests_json(x, base_dir=os.path.join(os.path.dirname(__file__), "test_results")):
    filename = f"{base_dir}/test_results_{time.time()}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, "w+") as f:
            f.write("[")
            for number_of_weightclasses in [1, 2, 5, 10, 20, 40, 60, 100]:
                for number_of_knapsacks in [2, 3, 4, 5, 10, 31, 50, 100, 183]:
                    for number_of_items_exp in range(3, 6):
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


def _test_MMKAI_wrapper(result_value, number_of_knapsacks, number_of_items,
                        number_of_weightclasses,
                        min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
                        knapsacks_per_item_max, seed):
    knapsacks, items, item_classes, seed = create_testinstance(number_of_knapsacks, number_of_items,
                                                               number_of_weightclasses,
                                                               min_weight, max_weight, min_capacity,
                                                               max_capacity, knapsacks_per_item_min,
                                                               knapsacks_per_item_max, seed)
    instance = MMKAI_recursive(knapsacks=knapsacks, items=items, item_classes=item_classes)
    result_value.value = timeit.timeit(instance.solve, number=1, timer=timeit.default_timer)
    print(f"Finished {instance.__class__.__name__}")  # this will print to stdout, even with it overwritten due to
    # beeing called through multiprocessing


class Dummy_Buffer:
    def write(self, *args, **kwargs):
        pass

    def flush(self, *args, **kwargs):
        pass


def run_against_gurobi(number_of_knapsacks, number_of_items, number_of_weightclasses,
                       min_weight=1, max_weight=10_000, min_capacity=1, max_capacity=100_000, knapsacks_per_item_min=1,
                       knapsacks_per_item_max: int | None = None, x=5, timeout=60 * 5):
    if knapsacks_per_item_max is None:
        knapsacks_per_item_max = number_of_knapsacks
    gurobi_wins = 0
    MMKAI_wins = 0
    print(f"Number of knapsacks: {number_of_knapsacks}\nNumber of items: {number_of_items:_}\n"
          f"Number of weight classes: {number_of_weightclasses}")
    for i in range(x):
        seed = random.randrange(sys.maxsize)
        print(f"Seed: {seed}")

        required_create_time = timeit.timeit(lambda: create_testinstance(number_of_knapsacks, number_of_items,
                                                                         number_of_weightclasses,
                                                                         min_weight, max_weight, min_capacity,
                                                                         max_capacity, knapsacks_per_item_min,
                                                                         knapsacks_per_item_max, seed), number=1)

        print(f"Required time to create test instance: {required_create_time}")

        result_value = multiprocessing.Value("d", -1)
        p = multiprocessing.Process(target=_test_MMKAI_wrapper, args=(
            result_value, number_of_knapsacks, number_of_items, number_of_weightclasses,
            min_weight, max_weight, min_capacity, max_capacity, knapsacks_per_item_min,
            knapsacks_per_item_max, seed))
        p.start()
        p.join(timeout + required_create_time * 2)
        if p.is_alive():
            p.terminate()
            result_value.value = -1
            print("Timeout")

        print(f"Required time to solve MMKAI: {result_value.value}")

        knapsacks, items, item_classes, seed = create_testinstance(number_of_knapsacks, number_of_items,
                                                                   number_of_weightclasses,
                                                                   min_weight, max_weight, min_capacity,
                                                                   max_capacity, knapsacks_per_item_min,
                                                                   knapsacks_per_item_max, seed)
        old_stdout = sys.stdout  # Gurobi sometimes prints to stdout, even with output flag set to 0
        sys.stdout = Dummy_Buffer()

        start = timeit.default_timer()
        x, _ = gurobi.solve(knapsacks, items, timelimit=timeout)
        end = timeit.default_timer()
        if x == -1:
            gurobi_time = -1
        else:
            gurobi_time = end - start

        sys.stdout = old_stdout

        print(f"Required time to solve Gurobi: {gurobi_time}")

        if result_value.value == -1 and gurobi_time == -1:
            print("Both timed out")
        elif result_value.value == -1:
            print("MMKAI timed out")
            gurobi_wins += 1
        elif gurobi_time == -1:
            print("Gurobi timed out")
            MMKAI_wins += 1
        elif result_value.value < gurobi_time:
            print("MMKAI won")
            MMKAI_wins += 1
        elif result_value.value > gurobi_time:
            print("Gurobi won")
            gurobi_wins += 1
        else:
            print("Draw")

    print(f"MMKAI won {MMKAI_wins} times")
    print(f"Gurobi won {gurobi_wins} times")


if __name__ == '__main__':
    perform_multiple_tests_json(10)
    with open("./gurobi_run_output.txt", 'w') as sys.stdout:
        run_against_gurobi(5, 100_000, 5, x=10)
