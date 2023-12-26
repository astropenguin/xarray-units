__all__ = ["DataArray", "Units", "units"]


# standard library
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, Callable, Generic


# dependencies
from typing_extensions import Concatenate, Self
from xarray import DataArray, register_dataarray_accessor  # type: ignore
from . import operator, quantity
from .utils import UNITS, P, TDataArray


# type hints
if TYPE_CHECKING:

    class DataArray(DataArray):
        units: "Units[Self]"


def to_method(
    func: Callable[Concatenate[TDataArray, P], TDataArray]
) -> Callable[Concatenate["Units[TDataArray]", P], TDataArray]:
    """Convert an operator or quantity function to a method."""

    @wraps(func)
    def wrapper(
        units: "Units[TDataArray]",
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> TDataArray:
        return func(units.accessed, *args, **kwargs)

    return wrapper


def units(accessed: TDataArray, /) -> "Units[TDataArray]":
    """Return a units accessor of a DataArray.

    Args:
        da: DataArray to be accessed.

    Returns:
        Units accessor of the DataArray.

    """
    return Units(accessed)


@register_dataarray_accessor(UNITS)
@dataclass
class Units(Generic[TDataArray]):
    """DataArray accessor for handling units.

    Args:
        accessed: DataArray to be accessed.

    """

    accessed: TDataArray
    """DataArray to be accessed."""

    # quantity
    apply = to_method(quantity.apply)
    decompose = to_method(quantity.decompose)
    format = to_method(quantity.format)
    like = to_method(quantity.like)
    set = to_method(quantity.set)
    to = to_method(quantity.to)
    unset = to_method(quantity.unset)

    # operator
    take = to_method(operator.take)
    mul = to_method(operator.mul)
    pow = to_method(operator.pow)
    matmul = to_method(operator.matmul)
    truediv = to_method(operator.truediv)
    add = to_method(operator.add)
    sub = to_method(operator.sub)
    floordiv = to_method(operator.floordiv)
    mod = to_method(operator.mod)
    lt = to_method(operator.lt)
    le = to_method(operator.le)
    eq = to_method(operator.eq)
    ne = to_method(operator.ne)
    ge = to_method(operator.ge)
    gt = to_method(operator.gt)

    # aliases
    __mul__ = mul
    __pow__ = pow
    __matmul__ = matmul
    __truediv__ = truediv
    __add__ = add
    __sub__ = sub
    __floordiv__ = floordiv
    __mod__ = mod
    __lt__ = lt
    __le__ = le
    __eq__ = eq  # type: ignore
    __ne__ = ne  # type: ignore
    __ge__ = ge
    __gt__ = gt
