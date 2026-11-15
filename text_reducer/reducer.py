"""Core delta-debugging reduction logic."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ReductionResult:
    """The reduced text and the number of checker invocations."""

    text: str
    tests: int


class InputDoesNotFail(ValueError):
    """Raised when the checker accepts the original input."""


def reduce_text(text: str, checker: Callable[[str], bool]) -> ReductionResult:
    """Minimize text while ``checker`` continues to report failure.

    The checker must return True when the candidate still exhibits the
    failure. It is called once for the original input before reduction.
    """

    tests = 0

    def still_fails(candidate: str) -> bool:
        nonlocal tests
        tests += 1
        return checker(candidate)

    # A reduction is meaningful only if the starting input already fails.
    if not still_fails(text):
        raise InputDoesNotFail("the original input does not fail the checker")

    current = text
    granularity = 2
    while len(current) >= 2:
        # Larger granularity tries smaller chunks; failed passes increase it.
        chunk_size = max(1, (len(current) + granularity - 1) // granularity)
        changed = False

        for start in range(0, len(current), chunk_size):
            candidate = current[:start] + current[start + chunk_size :]
            if still_fails(candidate):
                current = candidate
                # After a successful removal, try again with a coarser split.
                granularity = max(granularity - 1, 2)
                changed = True
                break

        if changed:
            continue
        if granularity >= len(current):
            break
        granularity = min(len(current), granularity * 2)

    return ReductionResult(current, tests)
