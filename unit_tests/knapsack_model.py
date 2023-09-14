import unittest

from src.models.knapsack import Knapsack


class TestKnapsackModel(unittest.TestCase):
    def setUp(self):
        self.knapsack_1 = Knapsack(10)
        self.knapsack_2 = Knapsack(20)
        self.knapsack_3 = Knapsack(30)

    def test_capacity(self):
        self.assertEqual(self.knapsack_1.capacity, 10)
        self.assertEqual(self.knapsack_2.capacity, 20)
        self.assertEqual(self.knapsack_3.capacity, 30)
        with self.assertRaises(AssertionError):
            Knapsack(0)

    def test_capacity_editing(self):
        # capacity should not be editable
        with self.assertRaises(AttributeError):
            self.knapsack_1.capacity = 20

    def test_str(self):
        self.assertEqual(str(self.knapsack_1), f"Knapsack {self.knapsack_1.identifier} (10)")
        self.assertEqual(str(self.knapsack_2), f"Knapsack {self.knapsack_2.identifier} (20)")
        self.assertEqual(str(self.knapsack_3), f"Knapsack {self.knapsack_3.identifier} (30)")

    def test_repr(self):
        self.assertEqual(repr(self.knapsack_1), str(self.knapsack_1))
        self.assertEqual(repr(self.knapsack_2), str(self.knapsack_2))
        self.assertEqual(repr(self.knapsack_3), str(self.knapsack_3))

    def test_hash(self):
        self.assertLess(hash(self.knapsack_1), hash(self.knapsack_2))
        self.assertLess(hash(self.knapsack_2), hash(self.knapsack_3))
        self.assertLess(hash(self.knapsack_1), hash(self.knapsack_3))

    def test_eq(self):
        self.assertNotEqual(self.knapsack_1, self.knapsack_2)
        self.assertNotEqual(self.knapsack_2, self.knapsack_3)
        self.assertNotEqual(self.knapsack_1, self.knapsack_3)
        self.assertEqual(self.knapsack_1, self.knapsack_1)
        self.assertEqual(self.knapsack_2, self.knapsack_2)
        self.assertEqual(self.knapsack_3, self.knapsack_3)

    def test_remaining_capacity(self):
        self.assertEqual(self.knapsack_1.remaining_capacity, 10)
        self.assertEqual(self.knapsack_2.remaining_capacity, 20)
        self.assertEqual(self.knapsack_3.remaining_capacity, 30)
        self.knapsack_1.remaining_capacity = 5
        self.assertEqual(self.knapsack_1.remaining_capacity, 5)