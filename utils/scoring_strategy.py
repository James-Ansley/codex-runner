from collections.abc import Iterable
from enum import Enum
from statistics import mean
from typing import Callable

from utils.question import Completion
from utils.testing_strategy import TestCaseScoringStrategy

QuestionScoringStrategy = Callable[
    [Iterable[Completion], TestCaseScoringStrategy],
    list[float]
]

_PENALTIES = [1.0, 1.0, 0.95, 0.9, 0.85, 0.8,
              0.75, 0.7, 0.65, 0.6, 0.55, 0.5]


class Options(str, Enum):
    # I have no idea why but Typer needs an enum + string type to work.
    basic = "basic"
    expected = "expected"
    finite_expected = "finite-expected"
    all_or_nothing = "all-or-nothing"

    @property
    def strategy(self) -> QuestionScoringStrategy:
        return {
            "basic": basic_score,
            "expected": expected_score,
            "finite-expected": expected_finite_attempts,
            "all-or-nothing": all_or_nothing,
        }[self.value]


def basic_score(completions, test_case_scoring_strategy):
    """
    Returns the mean testcases scores using the given scoring strategy to
    grade individual testcase scores.
    """
    return [
        mean(r.score(test_case_scoring_strategy) for r in c.results)
        for c in completions
    ]


def all_or_nothing(completions, test_case_scoring_strategy):
    """
    Equivalent to the floor of the basic scoring strategy.
    """
    scores = [
        int(all(r.score(test_case_scoring_strategy) == 1 for r in c.results))
        for c in completions
    ]
    return scores


def expected_score(completions, test_case_scoring_strategy):
    """
    Approximate expected score using all-or-nothing grading with UoA
    Moodle-Coderunner penalty schemes
    """
    scores = all_or_nothing(completions, test_case_scoring_strategy)
    probability = sum(scores) / len(scores)
    not_probability = 1 - probability

    result = 0
    for i in range(len(scores) * 10):
        penalty = _PENALTIES[min(i, len(_PENALTIES) - 1)]
        probability_penalty = (not_probability ** i) * probability * penalty
        result += probability_penalty
    return [result]


def expected_finite_attempts(completions, test_case_scoring_strategy):
    """
    Approximate expected score using all-or-nothing grading with UoA
    Moodle-Coderunner penalty schemes limited to 12 attempts
    """
    scores = all_or_nothing(completions, test_case_scoring_strategy)
    probability = sum(scores) / len(scores)
    not_probability = 1 - probability

    result = 0
    for i in range(12):
        penalty = _PENALTIES[i]
        probability_penalty = (not_probability ** i) * probability * penalty
        result += probability_penalty
    return [result]
