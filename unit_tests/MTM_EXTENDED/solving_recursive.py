# Copyright (c) 2023 Tom Mucke
from src.MTM_EXTENDED_recursive import MTM_EXTENDED_recursive
from unit_tests.MMKAI_recursive.solving_recursive import TestMMKAI_solve_recursive


class TestMTM_Extended_solve_recursive(TestMMKAI_solve_recursive):
    def setUp(self) -> None:
        self.class_to_test = lambda weightclasses, knapsacks, items: MTM_EXTENDED_recursive(items=items,
                                                                                            knapsacks=knapsacks,
                                                                                            item_classes=weightclasses)

    def test_manual_5(self):
        ...

    # TODO add tests where p != 1
