__all__ = [
    "UnitsError",
    "UnitsApplicationError",
    "UnitsExistError",
    "UnitsNotFoundError",
    "UnitsNotValidError",
    "units_of",
]


# standard library
from typing import Any, Optional, TypeVar, Union, overload


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
def units_of(obj: Quantity) -> UnitBase:
    ...


@overload
def units_of(obj: Any) -> Optional[UnitBase]:
    ...


def units_of(obj: Any) -> Optional[UnitBase]:
    """Return units of an object if they exist and are valid."""
    if isinstance(obj, Quantity):
        if isinstance(units := obj.unit, UnitBase):
            return units
        else:
            raise UnitsNotValidError(repr(obj))

    if isinstance(obj, DataArray):
        if (units := obj.attrs.get(UNITS_ATTR)) is None:
            return None

        try:
            units = Unit(units)  # type: ignore
        except Exception:
            raise UnitsNotValidError(repr(obj))

        if isinstance(units, UnitBase):
            return units
        else:
            raise UnitsNotValidError(repr(obj))
