__all__ = [
    "UnitsError",
    "UnitsConversionError",
    "UnitsExistError",
    "UnitsNotFoundError",
    "UnitsNotValidError",
]


class UnitsError(Exception):
    """Base exception for handling units."""

    pass


class UnitsExistError(UnitsError):
    """Units already exist in a DataArray."""

    pass


class UnitsConversionError(UnitsError):
    """Units cannot be converted to others."""

    pass


class UnitsNotFoundError(UnitsError):
    """Units do not exist in a DataArray."""

    pass


class UnitsNotValidError(UnitsError):
    """Units are not valid for handling."""

    pass
