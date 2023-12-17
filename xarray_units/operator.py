__all__ = [
    "take",
    # any-units operators
    "mul",  # *
    "pow",  # **
    "matmul",  # @
    "truediv",  # /
    # same-units operators
    "add",  # +
    "sub",  # -
    "floordiv",  # //
    "mod",  # %
    "lt",  # <
    "le",  # <=
    "eq",  # ==
    "ne",  # !=
    "ge",  # >=
    "gt",  # >
]


# standard library
import operator as opr
from typing import Any, Literal, Union, get_args


# dependencies
from astropy.units import Quantity
from xarray import DataArray
from xarray_units.quantity import apply_any, set, to, unset
from .utils import TESTER, TDataArray, UnitsApplicationError, units_of


# type hints
AnyUnitsOperator = Literal[
    "mul",  # *
    "pow",  # **
    "matmul",  # @
    "truediv",  # /
]
SameUnitsOperator = Literal[
    "add",  # +
    "sub",  # -
    "floordiv",  # //
    "mod",  # %
    "lt",  # <
    "le",  # <=
    "eq",  # ==
    "ne",  # !=
    "ge",  # >=
    "gt",  # >
]
Operator = Union[AnyUnitsOperator, SameUnitsOperator]


def take(left: TDataArray, operator: Operator, right: Any, /) -> TDataArray:
    """Perform an operation between a DataArray and any data with units.

    Args:
        left: DataArray with units on the left side of the operator.
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
    left_units = units_of(left, strict=True)
    right_units = units_of(right)

    if operator == "pow":
        method = f"__{operator}__"
        args = (Quantity(right, right_units),)
    elif operator == "matmul":
        method = "__mul__"
        args = (Quantity(TESTER, right_units),)
    elif operator == "eq" or operator == "ne":
        method = "__lt__"
        args = (Quantity(TESTER, right_units),)
    else:
        method = f"__{operator}__"
        args = (Quantity(TESTER, right_units),)

    try:
        test = apply_any(TESTER, left_units, method, *args)
    except Exception as error:
        raise UnitsApplicationError(error)

    if operator in get_args(SameUnitsOperator):
        if isinstance(right, Quantity):
            right = right.to(left_units).value  # type: ignore

        if isinstance(right, DataArray):
            right = to(right, left_units)

    try:
        result = getattr(opr, operator)(left, right)
    except Exception as error:
        raise UnitsApplicationError(error)

    if (units := units_of(test)) is None:
        return unset(result)
    else:
        return set(result, units, overwrite=True)


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


def add(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) + (right)`` with units."""
    return take(left, "add", right)


def sub(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) - (right)`` with units."""
    return take(left, "sub", right)


def floordiv(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) // (right)`` with units."""
    return take(left, "floordiv", right)


def mod(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) % (right)`` with units."""
    return take(left, "mod", right)


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
