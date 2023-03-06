"""Quick helper functions for the project."""

import typing

if typing.TYPE_CHECKING:
    from collections.abc import Iterator


def nth_element(my_iter: Iterator, n: int) -> int:
    """Return the nth element of an iterator."""
    for _ in range(n):
        next(my_iter)
    return next(my_iter)
