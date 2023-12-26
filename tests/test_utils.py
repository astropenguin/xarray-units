# standard library
from typing import Any


# dependencies
from astropy.units import Unit
from pytest import mark, raises
from xarray import DataArray
from xarray_units.utils import (
    UnitsConversionError,
    UnitsNotFoundError,
    UnitsNotValidError,
    units_of,
)


# test data
data_units_of: list[tuple[Any, Any, Any, Any]] = [
    (1, False, False, None),
    (1, "generic", False, None),
    (1, "invalid", False, None),
    (1, False, True, UnitsNotFoundError),
    (1, "generic", True, UnitsNotFoundError),
    (1, "invalid", True, UnitsNotFoundError),
    #
    (Unit("m"), False, False, None),
    (Unit("m"), "generic", False, None),
    (Unit("m"), "invalid", False, None),
    (Unit("m"), False, True, UnitsNotFoundError),
    (Unit("m"), "generic", True, UnitsNotFoundError),
    (Unit("m"), "invalid", True, UnitsNotFoundError),
    #
    (1 * Unit("m"), False, False, Unit("m")),
    (1 * Unit("m"), "generic", False, "m"),
    (1 * Unit("m"), "invalid", False, UnitsConversionError),
    (1 * Unit("m"), False, True, Unit("m")),
    (1 * Unit("m"), "generic", True, "m"),
    (1 * Unit("m"), "invalid", True, UnitsConversionError),
    #
    (DataArray(1), False, False, None),
    (DataArray(1), "generic", False, None),
    (DataArray(1), "invalid", False, None),
    (DataArray(1), False, True, UnitsNotFoundError),
    (DataArray(1), "generic", True, UnitsNotFoundError),
    (DataArray(1), "invalid", True, UnitsNotFoundError),
    #
    (DataArray(1, attrs={"units": "m"}), False, False, Unit("m")),
    (DataArray(1, attrs={"units": "m"}), "generic", False, "m"),
    (DataArray(1, attrs={"units": "m"}), "invalid", False, UnitsConversionError),
    (DataArray(1, attrs={"units": "m"}), False, True, Unit("m")),
    (DataArray(1, attrs={"units": "m"}), "generic", True, "m"),
    (DataArray(1, attrs={"units": "m"}), "invalid", True, UnitsConversionError),
    #
    (DataArray(1, attrs={"units": "m, s"}), False, False, UnitsNotValidError),
    (DataArray(1, attrs={"units": "m, s"}), "generic", False, UnitsNotValidError),
    (DataArray(1, attrs={"units": "m, s"}), "invalid", False, UnitsNotValidError),
    (DataArray(1, attrs={"units": "m, s"}), False, True, UnitsNotValidError),
    (DataArray(1, attrs={"units": "m, s"}), "generic", True, UnitsNotValidError),
    (DataArray(1, attrs={"units": "m, s"}), "invalid", True, UnitsNotValidError),
    #
    (DataArray(1, attrs={"units": "invalid"}), False, False, UnitsNotValidError),
    (DataArray(1, attrs={"units": "invalid"}), "generic", False, UnitsNotValidError),
    (DataArray(1, attrs={"units": "invalid"}), "invalid", False, UnitsNotValidError),
    (DataArray(1, attrs={"units": "invalid"}), False, True, UnitsNotValidError),
    (DataArray(1, attrs={"units": "invalid"}), "generic", True, UnitsNotValidError),
    (DataArray(1, attrs={"units": "invalid"}), "invalid", True, UnitsNotValidError),
]


@mark.parametrize("obj, format, strict, expected", data_units_of)
def test_units_of(obj: Any, format: Any, strict: Any, expected: Any) -> None:
    if isinstance(expected, type) and issubclass(expected, Exception):
        with raises(expected):
            assert units_of(obj, format=format, strict=strict)
    else:
        assert units_of(obj) == expected
