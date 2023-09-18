# Copyright (c) 2023 Tom Mucke
from src.MTM_EXTENDED_iterative import MTM_EXTENDED_iterative
from unit_tests.MTM_EXTENDED.solving_recursive import TestMTM_Extended_solve_recursive


class TestMTM_Extendes_solve_iterative(TestMTM_Extended_solve_recursive):
    def setUp(self) -> None:
        self.class_to_test = lambda weightclasses, knapsacks, items: MTM_EXTENDED_iterative(item_classes=weightclasses,
                                                                                           knapsacks=knapsacks,
                                                                                           items=items)
