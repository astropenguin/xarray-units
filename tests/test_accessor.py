# standard library
from typing import Any


# dependencies
from pytest import mark
from xarray.testing import assert_identical  # type: ignore
from xarray_units import operator, quantity
from xarray_units.accessor import DataArray, Units


data_aliases: list[tuple[Any, Any]] = [
    (
        getattr(Units, f"__{name}__").__wrapped__,
        getattr(operator, name),
    )
    for name in operator.__all__
    if name != "take"
]
data_operator: list[tuple[Any, Any]] = [
    (
        getattr(Units, name).__wrapped__,
        getattr(operator, name),
    )
    for name in operator.__all__
]
data_quantity: list[tuple[Any, Any]] = [
    (
        getattr(Units, name).__wrapped__,
        getattr(quantity, name),
    )
    for name in quantity.__all__
]


@mark.parametrize("method, expected", data_aliases)
def test_aliases(method: Any, expected: Any) -> None:
    assert method is expected


@mark.parametrize("method, expected", data_operator)
def test_operator(method: Any, expected: Any) -> None:
    assert method is expected


@mark.parametrize("method, expected", data_quantity)
def test_quantity(method: Any, expected: Any) -> None:
    assert method is expected


def test_chain() -> None:
    m = DataArray([1, 2, 3]).units.set("m")
    s = DataArray([1, 2, 3]).units.set("s")
    expected = (1 / DataArray([1, 2, 3])).units.set("m / s2")
    assert_identical(m.units(chain=2) / s / s, expected)
