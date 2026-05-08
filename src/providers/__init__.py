"""Cross-cutting provider for random number generation."""

import random


class RandomProvider:
    """Provides random number generation services."""

    def choice(self, sequence: list) -> any:
        """Select a random element from a non-empty sequence."""
        return random.choice(sequence)

    def choices(self, population: list, weights: list, k: int = 1) -> list:
        """Select k random elements from population with replacement."""
        return random.choices(population, weights=weights, k=k)

    def randint(self, a: int, b: int) -> int:
        """Return a random integer between a and b (inclusive)."""
        return random.randint(a, b)
