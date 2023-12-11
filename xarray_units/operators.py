__all__ = [
    "take",
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


# standard library
import operator as opr
from typing import Any, Literal, Union


# dependencies
from astropy.units import Quantity
from numpy import bool_
from numpy.typing import NDArray
from xarray import map_blocks
from .methods import set
from .utils import (
    UNITS_ONE,
    TDataArray,
    UnitsApplicationError,
    UnitsLike,
    UnitsNotFoundError,
    units_of,
)


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


def take(left: TDataArray, operator: Operator, right: Any, /) -> TDataArray:
    """Perform an operation between a DataArray and any data with units.

    Args:
        left: DataArray with units on the left side of the operator..
        operator: Name of the operator (e.g. ``"add"``, ``"gt"``).
        right: Any data on the right side of the operator.

    Returns:
        DataArray of the result of the operation. Units are
        the same as ``left`` in a numerical operation (e.g. ``"add"``)
        or nothing in a relational operation (e.g. ``"gt"``).

    Raises:
        UnitsApplicationError: Raised if the application fails.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    """
    if (left_units := units_of(left)) is None:
        raise UnitsNotFoundError(repr(left))

    if (right_units := units_of(right)) is None:
        right_units = UNITS_ONE

    try:
        if operator == "pow":
            test = take_any(1, left_units, operator, right, right_units)
        else:
            test = take_any(1, left_units, operator, 1, right_units)
    except Exception as error:
        raise UnitsApplicationError(error)

    def per_block(left_: TDataArray, right_: Any) -> TDataArray:
        data = take_any(left_, left_units, operator, right_, right_units)
        return left.copy(data=data)

    if (units := units_of(test)) is None:
        return map_blocks(per_block, left, (right,))
    else:
        return set(map_blocks(per_block, left, (right,)), units, True)


def take_any(
    left: Any,
    left_units: UnitsLike,
    operator: Operator,
    right: Any,
    right_units: UnitsLike,
    /,
) -> Union[Quantity, NDArray[bool_], bool_]:
    """Perform an operation between two any datasets."""
    left = Quantity(left, left_units)
    right = Quantity(right, right_units)
    return getattr(opr, operator)(left, right)


def lt(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) < (right)`` with units."""
    return take(left, "lt", right)


def le(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) <= (right)`` with units."""
    return take(left, "le", right)


def eq(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) == (right)`` with units."""
    return take(left, "eq", right)


def ne(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) != (right)`` with units."""
    return take(left, "ne", right)


def ge(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) >= (right)`` with units."""
    return take(left, "ge", right)


def gt(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) > (right)`` with units."""
    return take(left, "gt", right)


def add(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) + (right)`` with units."""
    return take(left, "add", right)


def sub(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) - (right)`` with units."""
    return take(left, "sub", right)


def mul(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) * (right)`` with units."""
    return take(left, "mul", right)


def pow(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) ** (right)`` with units."""
    return take(left, "pow", right)


def matmul(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) @ (right)`` with units."""
    return take(left, "matmul", right)


def truediv(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) / (right)`` with units."""
    return take(left, "truediv", right)


def floordiv(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) // (right)`` with units."""
    return take(left, "floordiv", right)


def mod(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) % (right)`` with units."""
    return take(left, "mod", right)
