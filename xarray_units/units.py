__all__ = ["set", "to"]


# standard library
from typing import Optional, TypeVar, Union


# dependencies
import xarray as xr
from astropy.units import Equivalency, Quantity, Unit, UnitConversionError
from .exceptions import UnitsExistError, UnitsNotConvertedError, UnitsNotFoundError


# type hints
TDataArray = TypeVar("TDataArray", bound=xr.DataArray)
UnitsLike = Union[Unit, str]


# constants
UNITS_ATTR = "units"


def get_units(da: xr.DataArray) -> Optional[UnitsLike]:
    """Return units of a DataArray."""
    if (units := da.attrs.get(UNITS_ATTR)) is None:
        return units

    if isinstance(units, UnitsLike):
        return units

    raise TypeError("Units must be Astropy units or string.")


def set(
    da: TDataArray,
    /,
    units: UnitsLike,
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
    if not overwrite and (da_units := get_units(da)) is not None:
        raise UnitsExistError(f"Units already exist ({da_units!r}).")

    return da.assign_attrs(units=str(units))


def to(
    da: TDataArray,
    /,
    units: UnitsLike,
    equivalencies: Optional[Equivalency] = None,
) -> TDataArray:
    """Convert units of a DataArray.

    Args:
        da: Input DataArray.
        units: Units to be converted from the current ones.
        equivalencies: Optional Astropy equivalencies.

    Returns:
        DataArray converted to given units.

    """
    if (da_units := get_units(da)) is None:
        raise UnitsNotFoundError("Units do not exist.")

    try:
        Quantity(0, da_units).to(units, equivalencies)  # type: ignore
    except UnitConversionError as error:
        raise UnitsNotConvertedError(error)

    def func(da: TDataArray) -> TDataArray:
        data = Quantity(da, da_units).to(units, equivalencies)  # type: ignore
        return da.copy(data=data)

    return set(xr.map_blocks(func, da), units, True)
