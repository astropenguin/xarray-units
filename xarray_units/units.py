__all__ = ["like", "set", "to"]


# standard library
from typing import Any, Optional, TypeVar, Union


# dependencies
import xarray as xr
from astropy.units import Equivalency, Quantity, Unit
from .exceptions import (
    UnitsConversionError,
    UnitsExistError,
    UnitsNotFoundError,
)


# type hints
TDataArray = TypeVar("TDataArray", bound=xr.DataArray)
Equivalencies = Optional[Equivalency]
UnitsLike = Union[Unit, str]


# constants
UNITS_ATTR = "units"


def like(
    da: TDataArray,
    other: xr.DataArray,
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

    return set(xr.map_blocks(to, da), units, True)


# helper functions
def convert(
    data: Any,
    units_from: UnitsLike,
    units_to: UnitsLike,
    /,
    equivalencies: Equivalencies = None,
) -> Any:
    """Convert units of any data."""
    try:
        data = Quantity(data, units_from)
        return data.to(units_to, equivalencies).value
    except Exception:
        raise UnitsConversionError(f"{units_from!r} -> {units_to!r}")


def units_of(da: xr.DataArray) -> Optional[UnitsLike]:
    """Return units of a DataArray if it exists."""
    return da.attrs.get(UNITS_ATTR)
