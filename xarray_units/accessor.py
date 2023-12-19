__all__ = ["Units"]


# standard library
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Generic


# dependencies
from typing_extensions import Concatenate, ParamSpec
from .utils import TDataArray


# type hints
P = ParamSpec("P")


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


@dataclass
class Units(Generic[TDataArray]):
    """DataArray accessor for handling units."""

    accessed: TDataArray
    """DataArray to be accessed."""
