# xarray-units

[![Release](https://img.shields.io/pypi/v/xarray-units?label=Release&color=cornflowerblue&style=flat-square)](https://pypi.org/project/xarray-units/)
[![Python](https://img.shields.io/pypi/pyversions/xarray-units?label=Python&color=cornflowerblue&style=flat-square)](https://pypi.org/project/xarray-units/)
[![Downloads](https://img.shields.io/pypi/dm/xarray-units?label=Downloads&color=cornflowerblue&style=flat-square)](https://pepy.tech/project/xarray-units)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.10354517-cornflowerblue?style=flat-square)](https://doi.org/10.5281/zenodo.10354517)
[![Tests](https://img.shields.io/github/actions/workflow/status/astropenguin/xarray-units/tests.yaml?label=Tests&style=flat-square)](https://github.com/astropenguin/xarray-units/actions)

xarray extension for handling units

## Overview

xarray-units is an import-only package that provides a DataArray accessor `.units` for handling units such as converting units and numeric operations considering units. [Astropy](https://www.astropy.org) is used as a backend. Unlike similar implementations, xarray-units does not use a special data type to handle units, but uses the original data type in a DataArray. This allows to continue to use powerful features such as parallel and lazy processing with [Dask](https://www.dask.org) and/or user-defined DataArray subclasses.

## Installation

```shell
pip install xarray-units==0.3.0
```

## Basic usages

Suppose the following imports will be commonly used in the examples:

```python
import xarray as xr
import xarray_units
```

### Setting and unsetting units

xarray-units sets units in DataArray attributes (`.attrs`) with the name `"units"`:

```python
da_km = xr.DataArray([1, 2, 3]).units.set("km")
print(da_km)
```

```
<xarray.DataArray (dim_0: 3)>
array([1, 2, 3])
Dimensions without coordinates: dim_0
Attributes:
    units:    km
```

And the units can also be unset (deleted):

```python
da = da_km.units.unset()
print(da)
```

```
<xarray.DataArray (dim_0: 3)>
array([1, 2, 3])
Dimensions without coordinates: dim_0
```

These are equivalent to manually un/setting the units in the DataArray attributes, but the accessor also check that the units are valid when setting.

### Converting units to others

xarray-units converts a DataArray with units to other units:

```python
da_km = xr.DataArray([1, 2, 3]).units.set("km")
da_m = da_km.units.to("m")
print(da_m)
```

```
<xarray.DataArray (dim_0: 3)>
array([1000., 2000., 3000.])
Dimensions without coordinates: dim_0
Attributes:
    units:    m
```

Astropy [equivalencies](https://docs.astropy.org/en/stable/units/equivalencies.html) can also be used for equivalences between different units:

```python
from astropy.units import spectral

da_mm = xr.DataArray([1, 2, 3]).units.set("mm")
da_GHz = da_mm.units.to("GHz", spectral())
print(da_GHz)
```

```
<xarray.DataArray (dim_1: 3)>
array([299.792458  , 149.896229  ,  99.93081933])
Dimensions without coordinates: dim_0
Attributes:
    units:    GHz
```

### Numeric operations considering units

xarray-units performs numerical operations considering units when the accessor is attached to the DataArray on the left side of the operator:

```python
da_m = xr.DataArray([1000, 2000, 3000]).units.set("m")
da_km = xr.DataArray([1, 2, 3]).units.set("km")

da_sum_m = da_m.units + da_km
da_sum_km = da_km.units + da_m

print(da_sum_m)
print(da_sum_km)
```

```
<xarray.DataArray (dim_0: 3)>
array([2000., 4000., 6000.])
Dimensions without coordinates: dim_0
Attributes:
    units:    m

<xarray.DataArray (dim_0: 3)>
array([2., 4., 6.])
Dimensions without coordinates: dim_0
Attributes:
    units:    km
```

The units of the DataArray after the operation follows those of the DataArray with the accessor. Therefore, the resulting data values will be different depending on the order of the operation. They are, of course, identical when considering units:

```python
da_eq = da_sum_m.units == da_sum_km
print(da_eq)
```

```
<xarray.DataArray (dim_0: 3)>
array([ True,  True,  True])
Dimensions without coordinates: dim_0
```

### Formatting units

xarray-units converts units to [various string formats](https://docs.astropy.org/en/stable/units/format.html):

```python
da = xr.DataArray([1, 2, 3]).units.set("m / s^2")

da_console = da.units.format("console")
da_latex = da.units.format("latex")

print(da_console)
print(da_latex)
```

```
<xarray.DataArray (dim_0: 3)>
array([1, 2, 3])
Dimensions without coordinates: dim_0
Attributes:
    units:    m s^-2

<xarray.DataArray (dim_0: 3)>
array([1, 2, 3])
Dimensions without coordinates: dim_0
Attributes:
    units:    $\mathrm{\frac{m}{s^{2}}}$
```

This is useful, for example, when plotting a DataArray:

```python
da.units.format("latex").plot()
```

## Advanced usages

### Use with static type checking

xarray-units provides a special type hint `xarray_units.DataArray` that has the `units` accessor. By replacing `xarray.DataArray` with it at the beginning of the code, type checkers can statically handle the accessor and its methods:

```python
import xarray as xr
from xarray_units import DataArray

xr.DataArray = DataArray
```

Note that it will become exactly identical to `xarray.DataArray` at runtime, so the replacement is not a problem at all.

### Use without the units accessor

xarray-units provides a function `xarray_units.units` that returns the `units` accessor of a DataArray. The following two lines are therefore identical:

```python
import xarray as xr
from xarray_units import units

xr.DataArray([1, 2, 3]).units.set("km")
units(xr.DataArray([1, 2, 3])).set("km")
```
