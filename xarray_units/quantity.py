__all__ = ["apply", "decompose", "like", "set", "to", "unset"]


# standard library
from types import MethodType, MethodWrapperType
from typing import Any


# dependencies
from astropy.units import Quantity
from xarray import DataArray
from .utils import (
    TESTER,
    UNITS_ATTR,
    Equivalencies,
    TDataArray,
    UnitsApplicationError,
    UnitsExistError,
    UnitsLike,
    units_of,
)


def apply(
    da: TDataArray,
    method: str,
    /,
    *args: Any,
    **kwargs: Any,
) -> TDataArray:
    """Apply a method of Astropy Quantity to a DataArray.

    Args:
        da: Input DataArray with units.
        method: Method (or property) name of Astropy Quantity.
        *args: Positional arguments of the method.
        *kwargs: Keyword arguments of the method.

    Returns:
        DataArray with the method (or property) applied.

    Raises:
        UnitsApplicationError: Raised if the application fails.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    """
    units = units_of(da, strict=True)

    def per_block(block: TDataArray) -> TDataArray:
        data = apply_any(block, units, method, *args, **kwargs)
        return block.copy(data=data)

    try:
        test = apply_any(TESTER, units, method, *args, **kwargs)
    except Exception as error:
        raise UnitsApplicationError(error)

    try:
        result = da.map_blocks(per_block)
    except Exception as error:
        raise UnitsApplicationError(error)

    return set(result, units_of(test, strict=True), overwrite=True)


def apply_any(
    data: Any,
    units: UnitsLike,
    method: str,
    /,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Apply a method of Astropy Quantity to any data."""
    attr = getattr(Quantity(data, units), method)

    if isinstance(attr, (MethodType, MethodWrapperType)):
        return attr(*args, **kwargs)
    else:
        return attr


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
    return apply(da, "to", units_of(other, strict=True), equivalencies)


def set(
    da: TDataArray,
    units: UnitsLike,
    /,
    *,
    overwrite: bool = False,
) -> TDataArray:
    """Set units to a DataArray.

    Args:
        da: Input DataArray.
        units: Units to be set to the input.

    Keyword Args:
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

    return da.assign_attrs({UNITS_ATTR: units})


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


def unset(da: TDataArray, /) -> TDataArray:
    """Remove units from a DataArray.

    Args:
        da: Input DataArray.

    Returns:
        DataArray with units removed.

    """
    da = da.copy(data=da.data)
    da.attrs.pop(UNITS_ATTR, None)
    return da
