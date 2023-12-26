# standard library
from typing import Any


# dependencies
from astropy.units import Quantity
from pytest import mark, raises
from xarray import DataArray
from xarray.testing import assert_identical  # type: ignore
from xarray_units import operator as opr
from xarray_units.operator import Operator, take
from xarray_units.quantity import set
from xarray_units.utils import UnitsConversionError


# test data
km = set(DataArray([1, 2, 3]), "km")
mm = set(DataArray([1, 2, 3]) * 1e6, "mm")
sc_1 = 2
sc_2 = Quantity(2000, "m")


data_take: list[tuple[DataArray, Operator, Any, Any]] = [
    (km, "mul", sc_1, set(DataArray([2, 4, 6]), "km")),
    (km, "mul", sc_2, set(DataArray([2, 4, 6]) * 1e3, "km m")),
    (km, "mul", mm, set(DataArray([1, 4, 9]) * 1e6, "km mm")),
    (mm, "mul", km, set(DataArray([1, 4, 9]) * 1e6, "km mm")),
    #
    (km, "pow", sc_1, set(DataArray([1, 4, 9]), "km2")),
    (km, "pow", sc_2, UnitsConversionError),
    (km, "pow", mm, UnitsConversionError),
    (mm, "pow", km, UnitsConversionError),
    #
    (km, "matmul", sc_1, UnitsConversionError),
    (km, "matmul", sc_2, UnitsConversionError),
    (km, "matmul", mm, set(DataArray(14) * 1e6, "km mm")),
    (mm, "matmul", km, set(DataArray(14) * 1e6, "km mm")),
    #
    (km, "truediv", sc_1, set(DataArray([0.5, 1, 1.5]), "km")),
    (km, "truediv", sc_2, set(DataArray([0.5, 1.0, 1.5]) * 1e-3, "km m-1")),
    (km, "truediv", mm, set(DataArray([1, 1, 1]) * 1e-6, "km mm-1")),
    (mm, "truediv", km, set(DataArray([1, 1, 1]) * 1e6, "mm km-1")),
    #
    (km, "add", sc_1, UnitsConversionError),
    (km, "add", sc_2, set(DataArray([3, 4, 5]), "km")),
    (km, "add", mm, set(DataArray([2, 4, 6]), "km")),
    (mm, "add", km, set(DataArray([2, 4, 6]) * 1e6, "mm")),
    #
    (km, "sub", sc_1, UnitsConversionError),
    (km, "sub", sc_2, set(DataArray([-1, 0, 1]), "km")),
    (km, "sub", mm, set(DataArray([0, 0, 0]), "km")),
    (mm, "sub", km, set(DataArray([0, 0, 0]), "mm")),
    #
    (km, "floordiv", sc_1, UnitsConversionError),
    (km, "floordiv", sc_2, set(DataArray([0, 1, 1]), "1")),
    (km, "floordiv", mm, set(DataArray([1, 1, 1]), "1")),
    (mm, "floordiv", km, set(DataArray([1, 1, 1]), "1")),
    #
    (km, "mod", sc_1, UnitsConversionError),
    (km, "mod", sc_2, set(DataArray([1, 0, 1]), "km")),
    (km, "mod", mm, set(DataArray([0, 0, 0]), "km")),
    (mm, "mod", km, set(DataArray([0, 0, 0]), "mm")),
    #
    (km, "lt", sc_1, UnitsConversionError),
    (km, "lt", sc_2, DataArray([True, False, False])),
    (km, "lt", mm, DataArray([False, False, False])),
    (mm, "lt", km, DataArray([False, False, False])),
    #
    (km, "le", sc_1, UnitsConversionError),
    (km, "le", sc_2, DataArray([True, True, False])),
    (km, "le", mm, DataArray([True, True, True])),
    (mm, "le", km, DataArray([True, True, True])),
    #
    (km, "eq", sc_1, UnitsConversionError),
    (km, "eq", sc_2, DataArray([False, True, False])),
    (km, "eq", mm, DataArray([True, True, True])),
    (mm, "eq", km, DataArray([True, True, True])),
    #
    (km, "ne", sc_1, UnitsConversionError),
    (km, "ne", sc_2, DataArray([True, False, True])),
    (km, "ne", mm, DataArray([False, False, False])),
    (mm, "ne", km, DataArray([False, False, False])),
    #
    (km, "ge", sc_1, UnitsConversionError),
    (km, "ge", sc_2, DataArray([False, True, True])),
    (km, "ge", mm, DataArray([True, True, True])),
    (mm, "ge", km, DataArray([True, True, True])),
    #
    (km, "gt", sc_1, UnitsConversionError),
    (km, "gt", sc_2, DataArray([False, False, True])),
    (km, "gt", mm, DataArray([False, False, False])),
    (mm, "gt", km, DataArray([False, False, False])),
]


@mark.parametrize("left, operator, right, expected", data_take)
def test_take(
    left: DataArray,
    operator: Operator,
    right: Any,
    expected: Any,
) -> None:
    if expected is UnitsConversionError:
        with raises(expected):
            take(left, operator, right)
    else:
        assert_identical(take(left, operator, right), expected)


@mark.parametrize("left, operator, right, expected", data_take)
def test_take_alias(
    left: DataArray,
    operator: Operator,
    right: Any,
    expected: DataArray,
) -> None:
    if expected is UnitsConversionError:
        with raises(expected):
            getattr(opr, operator)(left, right)
    else:
        assert_identical(getattr(opr, operator)(left, right), expected)
