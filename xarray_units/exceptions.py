__all__ = [
    "UnitsError",
    "UnitsExistError",
    "UnitsNotConvertedError",
    "UnitsNotFoundError",
]


class UnitsError(Exception):
    """Base exception for handling units."""

    pass


class UnitsExistError(UnitsError):
    """Units already exist in a DataArray."""

    pass


class UnitsNotConvertedError(UnitsError):
    """Units cannot be converted to others."""

    pass


class UnitsNotFoundError(UnitsError):
    """Units do not exist in a DataArray."""

    pass
