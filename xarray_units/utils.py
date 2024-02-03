__all__ = [
    "UnitsError",
    "UnitsConversionError",
    "UnitsExistError",
    "UnitsNotFoundError",
    "UnitsNotValidError",
    "unitsof",
]


# standard library
from typing import Any, Literal, Optional, TypeVar, Union, overload


# dependencies
from astropy.units import Quantity, Unit, UnitBase
from typing_extensions import ParamSpec
from xarray import DataArray


# type hints
P = ParamSpec("P")
TDataArray = TypeVar("TDataArray", bound=DataArray)
UnitsLike = Union[UnitBase, str]


# constants
TESTER = 1
UNITS = "units"


class UnitsError(Exception):
    """Base exception for handling units."""

    pass


class UnitsConversionError(UnitsError):
    """Units conversion is not successful."""

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
def unitsof(
    obj: Any,
    /,
    *,
    format: None = None,
    strict: Literal[False] = False,
    **kwargs: Any,
) -> Optional[UnitBase]: ...


@overload
def unitsof(
    obj: Any,
    /,
    *,
    format: str,
    strict: Literal[False] = False,
    **kwargs: Any,
) -> Optional[str]: ...


@overload
def unitsof(
    obj: Any,
    /,
    *,
    format: None = None,
    strict: Literal[True] = True,
    **kwargs: Any,
) -> UnitBase: ...


@overload
def unitsof(
    obj: Any,
    /,
    *,
    format: str,
    strict: Literal[True] = True,
    **kwargs: Any,
) -> str: ...


def unitsof(
    obj: Any,
    /,
    *,
    format: Optional[str] = None,
    strict: bool = False,
    **kwargs: Any,
) -> Optional[UnitsLike]:
    """Return units of an object if they exist and are valid.

    Args:
        obj: Any object from which units are extracted.
        format: Format of units. If given, the return value
            will be ``string``. Otherwise, it will be ``UnitBase``.
        strict: Whether to allow ``None`` as the return value
            when units do not exist in the object.
        **kwargs: Keyword arguments of the formatting.

    Returns:
        Extracted units from the object.

    Raises:
        UnitsConversionError: Raised if ``format`` is given
            but units cannot be formatted to it.
        UnitsNotFoundError: Raised if ``strict`` is ``True``
            but units do not exist in the object.
        UnitsNotValidError: Raised if units exist in the object
            but they cannot be converted to ``UnitBase``.

    """

    if isinstance(obj, DataArray):
        units = obj.attrs.get(UNITS)
    elif isinstance(obj, Quantity):
        units = obj.unit
    else:
        units = None

    if units is None:
        if not strict:
            return None

        raise UnitsNotFoundError(repr(obj))

    try:
        units = Unit(units)  # type: ignore
    except Exception:
        raise UnitsNotValidError(repr(obj))

    if not isinstance(units, UnitBase):
        raise UnitsNotValidError(repr(obj))

    if format is None:
        return units

    try:
        return units.to_string(format, **kwargs)  # type: ignore
    except ValueError as error:
        raise UnitsConversionError(error)
