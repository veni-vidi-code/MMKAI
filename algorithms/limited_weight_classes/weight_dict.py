from algorithms.models.knapsack import Item


def get_weight_dict(items: list[Item]):
    weight_dict = dict()
    for item in items:
        if item.weight not in weight_dict:
            weight_dict[item.weight] = list()
        weight_dict[item.weight].append(item)
    return weight_dict
