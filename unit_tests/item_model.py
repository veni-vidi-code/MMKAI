import unittest

import networkx as nx

from src.models.item import Item
from src.models.item_class import ItemClass
from src.models.knapsack import Knapsack


class TestItemClassModel(unittest.TestCase):
    def setUp(self):
        self.knapsack_1 = Knapsack(10)
        self.knapsack_2 = Knapsack(20)

        self.item_class_1 = ItemClass(1, 1)
        self.item_class_2 = ItemClass(2, 2)
        self.item_class_3 = ItemClass(1, 3)

    def test_profit(self):
        self.assertEqual(self.item_class_1.profit, 1)
        self.assertEqual(self.item_class_2.profit, 2)
        self.assertEqual(self.item_class_3.profit, 1)

    def test_weight(self):
        self.assertEqual(self.item_class_1.weight, 1)
        self.assertEqual(self.item_class_2.weight, 2)
        self.assertEqual(self.item_class_3.weight, 3)

    def test_new(self):
        self.assertIs(self.item_class_1, ItemClass(1, 1))
        self.assertIs(self.item_class_2, ItemClass(2, 2))
        self.assertIs(self.item_class_3, ItemClass(1, 3))

    def test_eq(self):
        self.assertEqual(self.item_class_1, ItemClass(1, 1))
        self.assertEqual(self.item_class_2, ItemClass(2, 2))
        self.assertEqual(self.item_class_3, ItemClass(1, 3))
        self.assertNotEqual(self.item_class_1, self.item_class_2)
        self.assertNotEqual(self.item_class_1, self.item_class_3)
        self.assertNotEqual(self.item_class_2, self.item_class_3)

    def test_hash(self):
        self.assertEqual(hash(self.item_class_1), hash((self.item_class_1.profit, self.item_class_1.weight)))
        self.assertEqual(hash(self.item_class_2), hash((self.item_class_2.profit, self.item_class_2.weight)))
        self.assertEqual(hash(self.item_class_3), hash((self.item_class_3.profit, self.item_class_3.weight)))

    def test_assert(self):
        self.assertRaises(AssertionError, ItemClass, 0, 1)
        self.assertRaises(AssertionError, ItemClass, 1, 0)
        self.assertRaises(AssertionError, ItemClass, 0, 0)
        self.assertRaises(AssertionError, ItemClass, -1, 1)
        self.assertRaises(AssertionError, ItemClass, 1, -1)

    def test_add_item(self):
        self.assertEqual(self.item_class_1.items, set())
        self.assertEqual(self.item_class_2.items, set())
        self.assertEqual(self.item_class_3.items, set())

        items = [None] * 7  # type: ignore
        corresponding_classes = [self.item_class_1, self.item_class_2, self.item_class_3, self.item_class_1,
                                 self.item_class_2, self.item_class_3, self.item_class_1]

        items[0] = corresponding_classes[0].add_item({self.knapsack_1})
        self.assertEqual(self.item_class_1.items, {items[0]})
        self.assertEqual(self.item_class_2.items, set())
        self.assertEqual(self.item_class_3.items, set())
        items[1] = corresponding_classes[1].add_item({self.knapsack_1})
        self.assertEqual(self.item_class_1.items, {items[0]})
        self.assertEqual(self.item_class_2.items, {items[1]})
        self.assertEqual(self.item_class_3.items, set())
        items[2] = corresponding_classes[2].add_item({self.knapsack_1})
        self.assertEqual(self.item_class_1.items, {items[0]})
        self.assertEqual(self.item_class_2.items, {items[1]})
        self.assertEqual(self.item_class_3.items, {items[2]})
        items[3] = corresponding_classes[3].add_item({self.knapsack_2})
        self.assertEqual(self.item_class_1.items, {items[0], items[3]})
        self.assertEqual(self.item_class_2.items, {items[1]})
        self.assertEqual(self.item_class_3.items, {items[2]})
        items[4] = corresponding_classes[4].add_item({self.knapsack_2})
        self.assertEqual(self.item_class_1.items, {items[0], items[3]})
        self.assertEqual(self.item_class_2.items, {items[1], items[4]})
        self.assertEqual(self.item_class_3.items, {items[2]})
        items[5] = corresponding_classes[5].add_item({self.knapsack_2})
        self.assertEqual(self.item_class_1.items, {items[0], items[3]})
        self.assertEqual(self.item_class_2.items, {items[1], items[4]})
        self.assertEqual(self.item_class_3.items, {items[2], items[5]})
        items[6] = corresponding_classes[6].add_item({self.knapsack_1, self.knapsack_2})
        self.assertEqual(self.item_class_1.items, {items[0], items[3], items[6]})
        self.assertEqual(self.item_class_2.items, {items[1], items[4]})
        self.assertEqual(self.item_class_3.items, {items[2], items[5]})

        for item in items:
            self.assertIsInstance(item, Item)

        items: list[Item]

        self.assertEqual(items[0].restrictions, {self.knapsack_1})
        self.assertEqual(items[1].restrictions, {self.knapsack_1})
        self.assertEqual(items[2].restrictions, {self.knapsack_1})
        self.assertEqual(items[3].restrictions, {self.knapsack_2})
        self.assertEqual(items[4].restrictions, {self.knapsack_2})
        self.assertEqual(items[5].restrictions, {self.knapsack_2})
        self.assertEqual(items[6].restrictions, {self.knapsack_1, self.knapsack_2})

        self.assertEqual(self.knapsack_1.eligible_items, {items[0], items[1], items[2], items[6]})
        self.assertEqual(self.knapsack_2.eligible_items, {items[3], items[4], items[5], items[6]})

        for i, item in enumerate(items):
            self.assertEqual(item.item_class, corresponding_classes[i])
            self.assertEqual(item.profit, corresponding_classes[i].profit)
            self.assertEqual(item.weight, corresponding_classes[i].weight)

    def test_prepare(self):
        self.assertEqual(self.item_class_1._graph, None)
        self.assertEqual(self.item_class_2._graph, None)
        self.assertEqual(self.item_class_3._graph, None)
        self.assertEqual(self.item_class_1._available_spaces, None)
        self.assertEqual(self.item_class_2._available_spaces, None)
        self.assertEqual(self.item_class_3._available_spaces, None)

        k = [self.knapsack_1, self.knapsack_2]
        self.item_class_1.prepare(k)
        self.assertEqual(k, [self.knapsack_1, self.knapsack_2])
        self.assertIsInstance(self.item_class_1._graph, nx.Graph)
        self.assertEqual(self.item_class_1._graph.number_of_nodes(), 0)
        self.assertEqual(self.item_class_1._available_spaces, [0, 0])

        i_1 = self.item_class_2.add_item({self.knapsack_1})
        i_2 = self.item_class_2.add_item({self.knapsack_2})
        self.item_class_2.prepare(k)
        self.assertIsInstance(self.item_class_2._graph, nx.Graph)
        self.assertEqual(self.item_class_2._available_spaces, [2, 2])
        self.assertEqual(self.item_class_2._graph.number_of_nodes(), 6)
        self.assertEqual(self.item_class_2._graph.number_of_edges(), 4)
        self.assertEqual(len(self.item_class_2._graph[i_1]), 2)

        items = [self.item_class_3.add_item({self.knapsack_1}) for _ in range(100)]
        self.item_class_3.prepare(k)
        self.assertIsInstance(self.item_class_3._graph, nx.Graph)
        self.assertEqual(self.item_class_3._available_spaces, [3, 6])
        self.assertEqual(self.item_class_3._graph.number_of_nodes(), 109)
        self.assertEqual(self.item_class_3._graph.number_of_edges(), 300)
        self.assertEqual(len(self.item_class_3._graph[items[0]]), 3)
        self.assertEqual(len(self.item_class_3._graph[(1, 0)]), 0)
        self.assertEqual(len(self.item_class_3._graph[(1, 1)]), 0)
        self.assertEqual(len(self.item_class_3._graph[(1, 2)]), 0)

        self.assertTrue(nx.is_bipartite(self.item_class_1._graph))
        self.assertTrue(nx.is_bipartite(self.item_class_2._graph))
        self.assertTrue(nx.is_bipartite(self.item_class_3._graph))

        self.assertEqual(k, [self.knapsack_1, self.knapsack_2])





