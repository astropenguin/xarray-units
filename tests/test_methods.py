# dependencies
import xarray as xr
from astropy.constants import c  # type: ignore
from astropy.units import spectral  # type: ignore
from xarray.testing import assert_identical  # type: ignore
from xarray_units.methods import apply, decompose, like, set, to


# test datasets
da = xr.DataArray([1, 2, 3])
km = xr.DataArray([1, 2, 3], attrs={"units": "km"})
mm = xr.DataArray([1, 2, 3], attrs={"units": "mm"})


# test functions
def test_apply() -> None:
    expected = (1e3 * km).assign_attrs(units="m")
    assert_identical(apply(km, "si"), expected)


def test_decompose() -> None:
    expected = (1e3 * km).assign_attrs(units="m")
    assert_identical(decompose(km), expected)


def test_like() -> None:
    expected = (1e6 * km).assign_attrs(units="mm")
    assert_identical(like(km, mm), expected)


def test_set() -> None:
    assert_identical(set(da, "km"), km)


def test_to() -> None:
    expected = (1e6 * km).assign_attrs(units="mm")
    assert_identical(to(km, "mm"), expected)


def test_to_equivalencies() -> None:
    expected = (c / (1e3 * km)).assign_attrs(units="Hz")  # type: ignore
    assert_identical(to(km, "Hz", spectral()), expected)  # type: ignore
