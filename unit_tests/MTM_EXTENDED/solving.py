# Copyright (c) 2023 Tom Mucke
from src.MTM_EXTENDED import MTM_EXTENDED
from unit_tests.TMKPA.solving import TestTMKPAsolve


class TestMTM_Extende_solve(TestTMKPAsolve):
    def setUp(self) -> None:
        self.class_to_test = lambda weightclasses, knapsacks, items: MTM_EXTENDED(items, knapsacks)

    def test_manual_5(self):
        ...

    # TODO add tests where p != 1

