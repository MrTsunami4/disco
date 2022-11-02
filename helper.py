from typing import Iterator


def nth_element(my_iter: Iterator, n: int) -> int:
    for _ in range(n):
        next(my_iter)
    return next(my_iter)
