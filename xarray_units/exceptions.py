__all__ = [
    "UnitsError",
    "UnitsApplicationError",
    "UnitsExistError",
    "UnitsNotFoundError",
    "UnitsNotValidError",
]


class UnitsError(Exception):
    """Base exception for handling units."""

    pass


class UnitsApplicationError(UnitsError):
    """Units application is not successful."""

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
