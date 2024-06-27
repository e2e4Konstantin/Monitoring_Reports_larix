import numpy as np
def calculate_abbe_criterion(signal):
    """Вычисляет Abbe criterion для последовательности значений."""
    if len(signal) <= 3:
        return 0
    differences = np.diff(signal) ** 2
    squared_differences = np.sum(differences)
    return np.sqrt(squared_differences / (len(signal) - 1))
