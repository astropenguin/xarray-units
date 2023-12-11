__all__ = []


# standard library
from typing import Literal


# type hints
Operator = Literal[
    "lt",  # <
    "le",  # <=
    "eq",  # ==
    "ne",  # !=
    "ge",  # >=
    "gt",  # >
    "add",  # +
    "sub",  # -
    "mul",  # *
    "pow",  # **
    "matmul",  # @
    "truediv",  # /
    "floordiv",  # //
    "mod",  # %
]
