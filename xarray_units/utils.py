__all__ = [
    "UnitsError",
    "UnitsConversionError",
    "UnitsExistError",
    "UnitsNotFoundError",
    "UnitsNotValidError",
    "units_of",
]


# standard library
from typing import Any, Literal, Optional, TypeVar, Union, overload


# dependencies
from astropy.units import Equivalency, Quantity, Unit, UnitBase
from typing_extensions import ParamSpec
from xarray import DataArray


# type hints
P = ParamSpec("P")
TDataArray = TypeVar("TDataArray", bound=DataArray)
Equivalencies = Optional[Equivalency]
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
def units_of(
    obj: Any,
    /,
    *,
    format: None = None,
    strict: Literal[False] = False,
) -> Optional[UnitBase]:
    ...


@overload
def units_of(
    obj: Any,
    /,
    *,
    format: str,
    strict: Literal[False] = False,
) -> Optional[str]:
    ...


@overload
def units_of(
    obj: Any,
    /,
    *,
    format: None = None,
    strict: Literal[True] = True,
) -> UnitBase:
    ...


@overload
def units_of(
    obj: Any,
    /,
    *,
    format: str,
    strict: Literal[True] = True,
) -> str:
    ...


def units_of(
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

    Keyword Args:
        format: Format of units. If given, the return value
            will be ``string``. Otherwise, it will be ``UnitBase``.
        strict: Whether to allow ``None`` as the return value
            when units do not exist in the object.

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

    if isinstance(obj, Quantity):
        if not isinstance(units := obj.unit, UnitBase):
            raise UnitsNotValidError(repr(obj))

        if format is None:
            return units

        try:
            return units.to_string(format, **kwargs)  # type: ignore
        except ValueError as error:
            raise UnitsConversionError(error)

    if isinstance(obj, DataArray):
        if (units := obj.attrs.get(UNITS)) is not None:
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

    if strict:
        raise UnitsNotFoundError(repr(obj))
