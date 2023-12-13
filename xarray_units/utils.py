__all__ = [
    "UnitsError",
    "UnitsApplicationError",
    "UnitsExistError",
    "UnitsNotFoundError",
    "UnitsNotValidError",
    "units_of",
]


# standard library
from typing import Any, Literal, Optional, TypeVar, Union, overload


# dependencies
from astropy.units import Equivalency, Quantity, Unit, UnitBase
from xarray import DataArray


# type hints
TDataArray = TypeVar("TDataArray", bound=DataArray)
Equivalencies = Optional[Equivalency]
UnitsLike = Union[UnitBase, str]


# constants
UNITS_ATTR = "units"
UNITS_ONE = "1"


class UnitsError(Exception):
    """Base exception for handling units."""

    pass


class UnitsApplicationError(UnitsError):
    """Units application is not successful."""

    pass


class UnitsExistError(UnitsError):
    """Units already exist in a DataArray."""

    pass


class UnitsNotFoundError(UnitsError):
    """Units do not exist in a DataArray."""

    pass


class UnitsNotValidError(UnitsError):
    """Units are not valid for a DataArray."""

    pass


@overload
def units_of(obj: Quantity, /, strict: Literal[False] = False) -> UnitBase:
    ...


@overload
def units_of(obj: Quantity, /, strict: Literal[True] = True) -> UnitBase:
    ...


@overload
def units_of(obj: Any, /, strict: Literal[False] = False) -> Optional[UnitBase]:
    ...


@overload
def units_of(obj: Any, /, strict: Literal[True] = True) -> UnitBase:
    ...


def units_of(obj: Any, /, strict: bool = False) -> Optional[UnitBase]:
    """Return units of an object if they exist and are valid."""
    if isinstance(obj, Quantity):
        if isinstance(units := obj.unit, UnitBase):
            return units
        else:
            raise UnitsNotValidError(repr(obj))

    if isinstance(obj, DataArray):
        if (units := obj.attrs.get(UNITS_ATTR)) is not None:
            try:
                units = Unit(units)  # type: ignore
            except Exception:
                raise UnitsNotValidError(repr(obj))

            if isinstance(units, UnitBase):
                return units
            else:
                raise UnitsNotValidError(repr(obj))

    if strict:
        raise UnitsNotFoundError(repr(obj))
