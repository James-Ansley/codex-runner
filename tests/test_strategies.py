from utils.question import Completion, TestResult, Testcase
from utils.scoring_strategy import basic_score, all_or_nothing, expected_score, \
    expected_finite_attempts
from utils.testing_strategy import exact_match

RIGHT = [TestResult(Testcase("", "", "Hello"), "Hello")]
WRONG = [TestResult(Testcase("", "", "Hello"), "Goodbye")]


def test_basic():
    assert basic_score([Completion("...", RIGHT * 4)], exact_match) == [1.0]
    assert basic_score([Completion("...", WRONG * 4)], exact_match) == [0.0]
    assert basic_score(
        [Completion("...", RIGHT * 2 + WRONG * 2)], exact_match
    ) == [0.5]
    assert basic_score(
        [Completion("...", RIGHT * 1 + WRONG * 3)], exact_match
    ) == [0.25]


def test_all_or_nothing():
    assert all_or_nothing([Completion("...", RIGHT * 4)], exact_match) == [1.0]
    assert all_or_nothing([Completion("...", WRONG * 4)], exact_match) == [0.0]
    assert all_or_nothing(
        [Completion("...", RIGHT * 2 + WRONG * 2)], exact_match
    ) == [0.0]
    assert all_or_nothing(
        [Completion("...", RIGHT * 1 + WRONG * 3)], exact_match
    ) == [0.0]


def test_expected():
    assert expected_score(
        [
            Completion("...", RIGHT),
            Completion("...", RIGHT),
            Completion("...", RIGHT),
        ],
        exact_match
    ) == [1.0]
    assert expected_score(
        [
            Completion("...", WRONG * 4),
            Completion("...", WRONG * 4),
            Completion("...", WRONG * 4),
        ],
        exact_match
    ) == [0.0]
    half = expected_score(
        [
            Completion("...", RIGHT),
            Completion("...", WRONG),
        ],
        exact_match
    )[0]
    assert f"{half:.2f}" == "0.98"


def test_expected_finite_attempts():
    assert expected_finite_attempts(
        [
            Completion("...", RIGHT),
            Completion("...", RIGHT),
            Completion("...", RIGHT),
        ],
        exact_match
    ) == [1.0]
    assert expected_finite_attempts(
        [
            Completion("...", WRONG * 4),
            Completion("...", WRONG * 4),
            Completion("...", WRONG * 4),
        ],
        exact_match
    ) == [0.0]
    half = expected_finite_attempts(
        [
            Completion("...", RIGHT),
            Completion("...", WRONG),
        ],
        exact_match
    )[0]
    assert f"{half:.2f}" == "0.97"
