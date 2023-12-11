__all__ = ["apply", "decompose", "like", "set", "to"]


# standard library
from types import MethodType
from typing import Any, Optional, TypeVar, Union, overload


# dependencies
from astropy.units import Equivalency, Quantity, Unit, UnitBase
from xarray import DataArray, map_blocks
from .exceptions import (
    UnitsApplicationError,
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


def apply(da: TDataArray, name: str, /, *args: Any, **kwargs: Any) -> TDataArray:
    """Apply a method of Astropy Quantity to a DataArray.

    Args:
        da: Input DataArray with units.
        name: Method (or property) name of Astropy Quantity.
        *args: Positional arguments of the method.
        *kwargs: Keyword arguments of the method.

    Returns:
        DataArray with the method (or property) applied.

    Raises:
        UnitsApplicationError: Raised if the application fails.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    """
    if (da_units := units_of(da)) is None:
        raise UnitsNotFoundError(repr(da))

    # test application
    try:
        test = apply_any(1, da_units, name, *args, **kwargs)
    except Exception as error:
        raise UnitsApplicationError(error)

    def per_block(block: TDataArray) -> TDataArray:
        data = apply_any(block, da_units, name, *args, **kwargs)
        return block.copy(data=data)

    return set(map_blocks(per_block, da), units_of(test), True)


def decompose(da: TDataArray, /) -> TDataArray:
    """Convert a DataArray with units to decomposed ones.

    Args:
        da: Input DataArray with units.

    Returns:
        DataArray with the decomposed units.

    Raises:
        UnitsApplicationError: Raised if the application fails.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    """
    return apply(da, "decompose")


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
        UnitsApplicationError: Raised if the application fails.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    """
    if (units := units_of(other)) is None:
        raise UnitsNotFoundError(repr(other))

    return apply(da, "to", units, equivalencies)


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
        UnitsApplicationError: Raised if the application fails.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    """
    return apply(da, "to", units, equivalencies)


# helper functions
def apply_any(
    data: Any,
    units: UnitsLike,
    name: str,
    /,
    *args: Any,
    **kwargs: Any,
) -> Quantity:
    """Apply a method of Astropy Quantity to any data."""
    data = Quantity(data, units)

    if isinstance(attr := getattr(data, name), MethodType):
        return ensure_consistency(data, attr(*args, **kwargs))
    else:
        return ensure_consistency(data, attr)


def ensure_consistency(data_in: Any, data_out: Any, /) -> Quantity:
    """Ensure consistency between input and output data."""
    if not isinstance(data_in, Quantity):
        raise TypeError("Input must be Astropy Quantity.")

    if not isinstance(data_out, Quantity):
        raise TypeError("Output must be Astropy Quantity.")

    if data_out.shape != data_in.shape:
        raise ValueError("Input and output shapes must be same.")

    return data_out


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
