__all__ = ["DataArray", "Units", "units"]


# standard library
from collections.abc import Hashable, Sequence
from dataclasses import dataclass, replace
from functools import wraps
from typing import TYPE_CHECKING, Callable, Generic, Union


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
        if (of := units.of) is None:
            da = func(units.accessed, *args, **kwargs)
        else:
            da = units.accessed
            coords: dict[Hashable, DataArray]

            if isinstance(of, Hashable):
                coords = {of: da.coords[of]}  # type: ignore
            else:
                coords = {name: da.coords[name] for name in of}  # type: ignore

            for name, coord in coords.items():
                coord = func(coord, *args, **kwargs)  # type: ignore
                da = da.assign_coords({name: coord})  # type: ignore

        if (chain := units.chain) > 1:
            return Units(da, chain=chain - 1, of=of)  # type: ignore

        return da

    return wrapper


def units(
    accessed: TDataArray,
    /,
    *,
    chain: int = 1,
    of: Union[Sequence[Hashable], Hashable] = None,
) -> "Units[TDataArray]":
    """Return a units accessor of a DataArray.

    Args:
        accessed: DataArray to be accessed.
        chain: Length of method chain. If it is greater than 1,
            each accessor method (or operation) will return not the resulting
            DataArray but an accessor of it with the length of ``chain - 1``.
            Note that, while this simplifies the method chain notation,
            static type checking may not work correctly in the middle of it.
        of: Coordinate(s) of the DataArray to be accessed. If specified,
            each accessor method will be applied not to the DataArray itself
            but to the selected coordinates, and return the DataArray with
            the updated coordinates.

    Returns:
        Units accessor of the DataArray.

    Raises:
        TypeError: Raised if options of the accessor are not valid.

    """
    return Units(accessed, chain=chain, of=of)


@register_dataarray_accessor(UNITS)
@dataclass
class Units(Generic[TDataArray]):
    """DataArray accessor for handling units.

    Args:
        accessed: DataArray to be accessed.
        chain: Length of method chain. If it is greater than 1,
            each accessor method (or operation) will return not the resulting
            DataArray but an accessor of it with the length of ``chain - 1``.
            Note that, while this simplifies the method chain notation,
            static type checking may not work correctly in the middle of it.
        of: Coordinate(s) of the DataArray to be accessed. If specified,
            each accessor method will be applied not to the DataArray itself
            but to the selected coordinates, and return the DataArray with
            the updated coordinates.

        Raises:
            TypeError: Raised if options of the accessor are not valid.

    """

    accessed: TDataArray
    """DataArray to be accessed."""

    chain: int = 1
    """Length of method chain."""

    of: Union[Sequence[Hashable], Hashable] = None
    """Coordinate(s) of the DataArray to be accessed."""

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

    def __call__(
        self,
        /,
        *,
        chain: int = 1,
        of: Union[Sequence[Hashable], Hashable] = None,
    ) -> Self:
        """Update the options of the accessor.

        Args:
            accessed: DataArray to be accessed.
            chain: Length of method chain. If it is greater than 1,
                each accessor method (or operation) will return not the resulting
                DataArray but an accessor of it with the length of ``chain - 1``.
                Note that, while this simplifies the method chain notation,
                static type checking may not work correctly in the middle of it.
            of: Coordinate(s) of the DataArray to be accessed. If specified,
                each accessor method will be applied not to the DataArray itself
                but to the selected coordinates, and return the DataArray with
                the updated coordinates.

        Returns:
            Unit accessor with the updated options.

        Raises:
            TypeError: Raised if options of the accessor are not valid.

        """
        return replace(self, chain=chain, of=of)

    def __post_init__(self) -> None:
        """Validate the options of the accessor."""
        if not (isinstance(self.chain, int) and self.chain > 0):
            raise TypeError("Chain must be a positive integer.")

        if not isinstance(self.of, (Hashable, Sequence)):
            raise TypeError("Of must be a (sequence of) hashable.")
