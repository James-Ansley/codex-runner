from enum import Enum
from typing import Callable

from rapidfuzz import fuzz

FUZZY_CUTOFF = 90

TestCaseScoringStrategy = Callable[[str, str, ...], float]


class Options(str, Enum):
    # I have no idea why but Typer needs an enum + string type to work.
    exact = "exact"
    fuzzy_w_cutoff = "fuzzy_w_cutoff"
    fuzzy = "fuzzy"

    @property
    def strategy(self) -> TestCaseScoringStrategy:
        return {
            "exact": exact_match,
            "fuzzy_w_cutoff": fuzzy_match_with_cutoff,
            "fuzzy": fuzzy_ratio
        }[self.value]


def exact_match(expected: str, got: str):
    return expected.strip() == got.strip()


def fuzzy_match_with_cutoff(expected: str, got: str):
    ratio = fuzz.ratio(expected.strip(), got.strip())
    return ratio >= FUZZY_CUTOFF


def fuzzy_ratio(expected: str, got: str):
    return fuzz.ratio(expected.strip(), got.strip()) / 100
