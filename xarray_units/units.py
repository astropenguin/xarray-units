__all__ = ["like", "set", "to"]


# standard library
from typing import Any, Optional, TypeVar, Union


# dependencies
from astropy.units import Equivalency, Quantity, UnitBase
from xarray import DataArray, map_blocks
from .exceptions import (
    UnitsConversionError,
    UnitsExistError,
    UnitsNotFoundError,
)


# type hints
TDataArray = TypeVar("TDataArray", bound=DataArray)
Equivalencies = Optional[Equivalency]
UnitsLike = Union[UnitBase, str]


# constants
UNITS_ATTR = "units"


def like(
    da: TDataArray,
    other: DataArray,
    /,
    equivalencies: Equivalencies = None,
) -> TDataArray:
    """Convert a DataArray with units to those of the other.

    Args:
        da: Input DataArray with units.
        other: DataArray with units to which the input is converted.
        equivalencies: Optional Astropy equivalencies.

    Returns:
        DataArray with the converted units.

    Raises:
        UnitsConversionError: Raised if the unit conversion fails.
        UnitsNotFoundError: Raised if units are not found.

    """
    if (units := units_of(other)) is None:
        raise UnitsNotFoundError(repr(other))

    return to(da, units, equivalencies)


def set(
    da: TDataArray,
    units: UnitsLike,
    /,
    overwrite: bool = False,
) -> TDataArray:
    """Set units to a DataArray.

    Args:
        da: Input DataArray.
        units: Units to be set to the input.
        overwrite: Whether to overwrite existing units.

    Returns:
        DataArray with given units in ``attrs["units"]``.

    Raises:
        UnitsExistError: Raised if units already exist.
            Not raised when ``overwrite`` is ``True``.

    """
    if not overwrite and units_of(da) is not None:
        raise UnitsExistError(repr(da))

    return da.assign_attrs(units=units)


def to(
    da: TDataArray,
    units: UnitsLike,
    /,
    equivalencies: Equivalencies = None,
) -> TDataArray:
    """Convert a DataArray with units to given units.

    Args:
        da: Input DataArray with units.
        units: Units to which the input is converted.
        equivalencies: Optional Astropy equivalencies.

    Returns:
        DataArray with the converted units.

    Raises:
        UnitsConversionError: Raised if the unit conversion fails.
        UnitsNotFoundError: Raised if units are not found.

    """
    if (da_units := units_of(da)) is None:
        raise UnitsNotFoundError(repr(da))

    # test units conversion
    convert(1, da_units, units, equivalencies)

    def to(da: TDataArray) -> TDataArray:
        data = convert(da, da_units, units, equivalencies)
        return da.copy(data=data)

    return set(map_blocks(to, da), units, True)


# helper functions
def convert(
    data: Any,
    from_units: UnitsLike,
    to_units: UnitsLike,
    /,
    equivalencies: Equivalencies = None,
) -> Quantity:
    """Convert data with units to other units."""
    try:
        data = Quantity(data, from_units)
        return data.to(to_units, equivalencies)
    except Exception:
        raise UnitsConversionError(f"{from_units!r} -> {to_units!r}")


def units_of(obj: Any) -> Optional[str]:
    """Return units in an object if they exist."""
    if isinstance(obj, DataArray):
        if (units := obj.attrs.get(UNITS_ATTR)) is None:
            return units
        else:
            return str(units)

    if isinstance(obj, Quantity):
        return str(obj.unit)
