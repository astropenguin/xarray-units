__all__ = [
    "take",
    # any-units operators
    "mul",  # *
    "pow",  # **
    "matmul",  # @
    "truediv",  # /
    "mod",  # %
    # same-units operators
    "add",  # +
    "sub",  # -
    "floordiv",  # //
    "lt",  # <
    "le",  # <=
    "eq",  # ==
    "ne",  # !=
    "ge",  # >=
    "gt",  # >
]


# standard library
import operator as opr
from typing import Any, Literal, Optional, Union, get_args


# dependencies
from astropy.units import Quantity
from xarray import DataArray
from xarray_units.quantity import set, to, unset
from .utils import TDataArray, UnitsApplicationError, UnitsLike, units_of


# type hints
AnyUnitsOperator = Literal[
    "mul",  # *
    "pow",  # **
    "matmul",  # @
    "truediv",  # /
    "mod",  # %
]
SameUnitsOperator = Literal[
    "add",  # +
    "sub",  # -
    "floordiv",  # //
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

    try:
        if operator == "pow":
            tested = take_any(1, left_units, operator, right, right_units)
        else:
            tested = take_any(1, left_units, operator, 1, right_units)
    except Exception as error:
        raise UnitsApplicationError(error)

    if operator in get_args(SameUnitsOperator):
        if isinstance(right, DataArray):
            right = to(right, left_units)
        elif isinstance(right, Quantity):
            right = right.to(left_units)  # type: ignore

    result = getattr(opr, operator)(left, right)

    if (units := units_of(tested)) is None:
        return unset(result)
    else:
        return set(result, units, True)


def take_any(
    left: Any,
    left_units: UnitsLike,
    operator: Operator,
    right: Any,
    right_units: Optional[UnitsLike],
    /,
) -> Any:
    """Perform an operation between two any datasets."""
    left = Quantity(left, left_units)
    right = Quantity(right, right_units)

    return getattr(opr, operator)(left, right)


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


def mod(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) % (right)`` with units."""
    return take(left, "mod", right)


def add(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) + (right)`` with units."""
    return take(left, "add", right)


def sub(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) - (right)`` with units."""
    return take(left, "sub", right)


def floordiv(left: TDataArray, right: Any) -> TDataArray:
    """Perform ``(left) // (right)`` with units."""
    return take(left, "floordiv", right)


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
