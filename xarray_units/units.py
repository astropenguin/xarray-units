__all__ = ["set", "to"]


# standard library
from typing import Any, Optional, TypeVar, Union


# dependencies
import xarray as xr
from astropy.units import Equivalency, Quantity, Unit
from .exceptions import (
    UnitsConversionError,
    UnitsExistError,
    UnitsNotFoundError,
    UnitsNotValidError,
)


# type hints
TDataArray = TypeVar("TDataArray", bound=xr.DataArray)
UnitsLike = Union[Unit, str]


# constants
UNITS_ATTR = "units"


def set(
    da: TDataArray,
    units: Union[UnitsLike, xr.DataArray],
    /,
    overwrite: bool = False,
) -> TDataArray:
    """Set units to a DataArray.

    Args:
        da: Input DataArray.
        units: Units to be set to the input DataArray.
        overwrite: Whether to overwrite existing units.

    Returns:
        DataArray with given units in ``attrs["units"]``.

    Raises:
        UnitsExistError: Raised if ``overwrite=False``
            and units already exist in the input DataArray.

    """
    if not overwrite and infer(da) is not None:
        raise UnitsExistError(da)

    return da.assign_attrs(units=infer(units))


def to(
    da: TDataArray,
    units: Union[UnitsLike, xr.DataArray],
    /,
    equivalencies: Optional[Equivalency] = None,
) -> TDataArray:
    """Convert units of a DataArray.

    Args:
        da: Input DataArray with units.
        units: Units to be converted from the current ones.
        equivalencies: Optional Astropy equivalencies.

    Returns:
        DataArray converted to given units.

    Raises:
        UnitsConversionError: Raised if the unit conversion fails.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    """
    if (units_from := infer(da)) is None:
        raise UnitsNotFoundError(repr(da))

    if (units_to := infer(units)) is None:
        raise UnitsNotValidError(repr(units))

    # test units conversion
    convert(1, units_from, units_to, equivalencies)

    def to(da: TDataArray) -> TDataArray:
        data = convert(da, units_from, units_to, equivalencies)
        return da.copy(data=data)

    return set(xr.map_blocks(to, da), units_to, True)


# helper functions
def convert(
    data: Any,
    from_: UnitsLike,
    to: UnitsLike,
    /,
    equivalencies: Optional[Equivalency] = None,
) -> Any:
    """Convert units of any data."""
    try:
        data = Quantity(data, from_)
        return data.to(to, equivalencies).value
    except Exception:
        raise UnitsConversionError(f"{from_!r} -> {to!r}")


def infer(obj: Optional[Any], /) -> Optional[UnitsLike]:
    """Infer units from an object."""
    if isinstance(obj, xr.DataArray):
        return infer(obj.attrs.get(UNITS_ATTR))

    if isinstance(obj, Unit) or (obj is None):
        return obj

    elif isinstance(obj, str):
        try:
            Unit(obj)  # type: ignore
            return obj
        except Exception:
            pass

    raise UnitsNotValidError(repr(obj))
