__all__ = ["set"]


# standard library
from typing import TypeVar, Union


# dependencies
import xarray as xr
from astropy.units import Unit  # type: ignore


# type hints
TDataArray = TypeVar("TDataArray", bound=xr.DataArray)
UnitsLike = Union[Unit, str]


# constants
UNITS_ATTR = "units"


class UnitsExistError(Exception):
    """Exception used when units already exist."""

    pass


class UnitsNotFoundError(Exception):
    """Exception used when units do not exist."""

    pass


def set(
    da: TDataArray,
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
    if not overwrite and UNITS_ATTR in da.attrs:
        raise UnitsExistError("Units already exist.")

    return da.assign_attrs(units=str(units))
