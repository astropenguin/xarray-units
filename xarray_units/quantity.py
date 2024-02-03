__all__ = [
    "apply",
    "decompose",
    "format",
    "like",
    "set",
    "to",
    "unset",
]


# standard library
from types import MethodType, MethodWrapperType
from typing import Any, Optional


# dependencies
from astropy.units import Equivalency, Quantity
from xarray import DataArray
from .utils import (
    TESTER,
    UNITS,
    TDataArray,
    UnitsConversionError,
    UnitsExistError,
    UnitsLike,
    unitsof,
)


def apply(
    da: TDataArray,
    method: str,
    /,
    *args: Any,
    **kwargs: Any,
) -> TDataArray:
    """Apply a method of Astropy Quantity to a DataArray.

    When called from an accessor, it runs ``apply(accessed, method, ...)``.

    Args:
        da: Input DataArray with units.
        method: Method (or property) name of Astropy Quantity.
        *args: Positional arguments of the method.
        *kwargs: Keyword arguments of the method.

    Returns:
        DataArray with the method (or property) applied.

    Raises:
        UnitsConversionError: Raised if units cannot be converted.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    See Also:
        https://docs.astropy.org/en/stable/units/quantity.html

    """
    units = unitsof(da, strict=True)

    def per_block(block: TDataArray) -> TDataArray:
        data = apply_any(block, units, method, *args, **kwargs)
        return block.copy(data=data)

    try:
        test = apply_any(TESTER, units, method, *args, **kwargs)
    except Exception as error:
        raise UnitsConversionError(error)

    try:
        result = da.map_blocks(per_block)
    except Exception as error:
        raise UnitsConversionError(error)

    return set(result, unitsof(test, strict=True), overwrite=True)


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

    When called from an accessor, it runs ``decompose(accessed)``.

    Args:
        da: Input DataArray with units.

    Returns:
        DataArray with the decomposed units.

    Raises:
        UnitsConversionError: Raised if units cannot be converted.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    See Also:
        https://docs.astropy.org/en/stable/units/decomposing_and_composing.html

    """
    return apply(da, "decompose")


def format(
    da: TDataArray,
    format: str,
    /,
    coords: bool = True,
    **kwargs: Any,
) -> TDataArray:
    """Format units of a DataArray.

    When called from an accessor, it runs ``format(accessed, format, ...)``.

    Args:
        da: Input DataArray with units.
        format: Format of units (e.g. ``"console"``, ``"latex"``).
        coords: Whether to also format the units of the coordinates.
        **kwargs: Keyword arguments of the formatting.

    Returns:
        DataArray with formatted units.

    Raises:
        UnitsConversionError: Raised if units cannot be converted.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    See Also:
        https://docs.astropy.org/en/stable/units/format.html

    """
    units = unitsof(da, format=format, strict=True, **kwargs)
    da = set(da, units, overwrite=True)

    if not coords:
        return da

    for name, coord in da.coords.items():  # type: ignore
        if (units := unitsof(coord, format=format, **kwargs)) is None:
            continue

        coord = set(coord, units, overwrite=True)  # type: ignore
        da = da.assign_coords({name: coord})  # type: ignore

    return da


def like(
    da: TDataArray,
    other: DataArray,
    /,
    equivalencies: Optional[Equivalency] = None,
) -> TDataArray:
    """Convert a DataArray with units to those of the other.

    When called from an accessor, it runs ``like(accessed, other, ...)``.

    Args:
        da: Input DataArray with units.
        other: DataArray with units to which the input is converted.
        equivalencies: Optional Astropy equivalencies.

    Returns:
        DataArray with the converted units.

    Raises:
        UnitsConversionError: Raised if units cannot be converted.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    See Also:
        https://docs.astropy.org/en/stable/units/quantity.html

    """
    units = unitsof(other, strict=True)
    return apply(da, "to", units, equivalencies)


def set(
    da: TDataArray,
    units: UnitsLike,
    /,
    *,
    overwrite: bool = False,
) -> TDataArray:
    """Set units to a DataArray.

    When called from an accessor, it runs ``set(accessed, units, ...)``.

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
    if not overwrite and unitsof(da) is not None:
        raise UnitsExistError(repr(da))

    return da.assign_attrs({UNITS: units})


def to(
    da: TDataArray,
    units: UnitsLike,
    /,
    equivalencies: Optional[Equivalency] = None,
) -> TDataArray:
    """Convert a DataArray with units to other units.

    When called from an accessor, it runs ``to(accessed, units, ...)``.

    Args:
        da: Input DataArray with units.
        units: Units to which the input is converted.
        equivalencies: Optional Astropy equivalencies.

    Returns:
        DataArray with the converted units.

    Raises:
        UnitsConversionError: Raised if units cannot be converted.
        UnitsNotFoundError: Raised if units are not found.
        UnitsNotValidError: Raised if units are not valid.

    See Also:
        https://docs.astropy.org/en/stable/units/quantity.html

    """
    return apply(da, "to", units, equivalencies)


def unset(da: TDataArray, /) -> TDataArray:
    """Remove units from a DataArray.

    When called from an accessor, it runs ``unset(accessed)``.

    Args:
        da: Input DataArray.

    Returns:
        DataArray with units removed.

    """
    da = da.copy(data=da.data)
    da.attrs.pop(UNITS, None)
    return da
