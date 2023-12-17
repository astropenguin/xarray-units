# standard library
from typing import Any


# dependencies
from astropy.units import Unit
from pytest import mark, raises
from xarray import DataArray
from xarray_units.utils import UnitsNotValidError, units_of


# test data
data_units_of: list[tuple[Any, Any]] = [
    (1, None),
    (Unit("m"), None),
    (1 * Unit("m"), Unit("m")),
    (DataArray(1), None),
    (DataArray(1, attrs={"units": "m"}), Unit("m")),
    (DataArray(1, attrs={"units": "m, s"}), UnitsNotValidError),
    (DataArray(1, attrs={"units": "spam"}), UnitsNotValidError),
]


@mark.parametrize("obj, expected", data_units_of)
def test_units_of(obj: Any, expected: Any) -> None:
    if expected is UnitsNotValidError:
        with raises(expected):
            assert units_of(obj)
    else:
        assert units_of(obj) == expected
