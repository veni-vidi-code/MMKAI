# Copyright (c) 2023 Tom Mucke
from src.TMKPA_iterative import TMKPA_iterative
from unit_tests.TMKPA_recursive.solving_recursive import TestTMKPA_solve_recursive


class TestMTM_Extended_solve_recursive(TestTMKPA_solve_recursive):
    def setUp(self) -> None:
        self.class_to_test = lambda weightclasses, knapsacks, items: TMKPA_iterative(weightclasses, knapsacks, items)
