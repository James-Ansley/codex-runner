import random
from enum import Enum
from itertools import starmap
from operator import mul
from statistics import mean
from typing import Callable

from rapidfuzz import fuzz


class TestingStrategy(str, Enum):
    exact = "exact"
    fuzzy_w_cutoff = "fuzzy_w_cutoff"
    fuzzy = "fuzzy"

    @property
    def callable(self) -> Callable[..., float]:
        return {
            "exact": self.exact_match,
            "fuzzy_w_cutoff": self.fuzzy_match_with_cutoff,
            "fuzzy": self.fuzzy_ratio
        }[self.value]

    @staticmethod
    def exact_match(expected, got):
        return expected.strip() == got.strip()

    @staticmethod
    def fuzzy_match_with_cutoff(expected, got, *, cutoff=90):
        ratio = fuzz.ratio(expected.strip(), got.strip())
        return ratio >= cutoff

    @staticmethod
    def fuzzy_ratio(expected, got):
        return fuzz.ratio(expected.strip(), got.strip()) / 100


class ScoringStrategy(str, Enum):
    basic = "basic"
    penalty = "penalty"

    @property
    def callable(self) -> Callable[..., float]:
        return {
            "basic": self.basic_score,
            "penalty": self.penalty_aggregation,
        }[self.value]

    @staticmethod
    def penalty_aggregation(completions, strategy):
        scores = [
            mean(r.score(strategy) for r in c.results) for c in completions
        ]
        penalties = [1.0, 1.0, 0.95, 0.9, 0.85, 0.8,
                     0.75, 0.7, 0.65, 0.6, 0.55, 0.5]

        def simulate_attempt(score_group):
            weighted = starmap(mul, zip(penalties, score_group))
            return next((m for m, s in zip(weighted, score_group) if s == 1), 0)

        results = []
        for _ in range(len(completions)):
            attempt = random.choices(scores, k=12)
            results.append(simulate_attempt(attempt))
        return results

    @staticmethod
    def basic_score(completions, strategy):
        return [mean(r.score(strategy) for r in c.results) for c in completions]
