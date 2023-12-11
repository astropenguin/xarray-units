__all__ = ["like", "set", "to"]


# standard library
from typing import Any, Optional, TypeVar, Union, overload


# dependencies
from astropy.units import Equivalency, Quantity, Unit, UnitBase
from xarray import DataArray, map_blocks
from .exceptions import (
    UnitsConversionError,
    UnitsExistError,
    UnitsNotFoundError,
    UnitsNotValidError,
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
        UnitsNotValidError: Raised if units are not valid.

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
        UnitsNotValidError: Raised if units are not valid.

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
    """Convert a DataArray with units to other units.

    Args:
        da: Input DataArray with units.
        units: Units to which the input is converted.
        equivalencies: Optional Astropy equivalencies.

    Returns:
        DataArray with the converted units.

    Raises:
        UnitsConversionError: Raised if the unit conversion fails.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

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
    """Convert any data with units to other units."""
    try:
        data = Quantity(data, from_units)
        return data.to(to_units, equivalencies)
    except Exception:
        raise UnitsConversionError(f"{from_units!r} -> {to_units!r}")


@overload
def units_of(obj: Quantity) -> UnitBase:
    ...


@overload
def units_of(obj: DataArray) -> Optional[UnitBase]:
    ...


def units_of(obj: Any) -> Any:
    """Return units of an object if they exist and are valid."""
    if isinstance(obj, Quantity):
        if isinstance(units := obj.unit, UnitBase):
            return units

    if isinstance(obj, DataArray):
        if (units := obj.attrs.get(UNITS_ATTR)) is None:
            return None

        if isinstance(units := Unit(units), UnitBase):  # type: ignore
            return units

    raise UnitsNotValidError(repr(obj))
