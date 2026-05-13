def mean_absolute_error(actual: list[float], predicted: list[float]) -> float:
    total = 0.0
    for truth, estimate in zip(actual, predicted):
        total += abs(truth - estimate)
    return total / max(1, len(actual))


def mean_absolute_percentage_error(actual: list[float], predicted: list[float]) -> float:
    total = 0.0
    for truth, estimate in zip(actual, predicted):
        denominator = truth if truth else 1e-6
        total += abs((truth - estimate) / denominator)
    return total / max(1, len(actual))


def root_mean_squared_error(actual: list[float], predicted: list[float]) -> float:
    squared_error = [(truth - estimate) ** 2 for truth, estimate in zip(actual, predicted)]
    return (sum(squared_error) / max(1, len(squared_error))) ** 0.5
