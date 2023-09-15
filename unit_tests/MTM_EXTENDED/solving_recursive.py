# Copyright (c) 2023 Tom Mucke
from src.MTM_EXTENDED_recursive import MTM_EXTENDED_recursive
from unit_tests.TMKPA_recursive.solving_recursive import TestTMKPA_solve_recursive


class TestMTM_Extended_solve_recursive(TestTMKPA_solve_recursive):
    def setUp(self) -> None:
        self.class_to_test = lambda weightclasses, knapsacks, items: MTM_EXTENDED_recursive(items, knapsacks)

    def test_manual_5(self):
        ...

    # TODO add tests where p != 1

