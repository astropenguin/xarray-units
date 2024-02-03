# xarray-units

[![Release](https://img.shields.io/pypi/v/xarray-units?label=Release&color=cornflowerblue&style=flat-square)](https://pypi.org/project/xarray-units/)
[![Python](https://img.shields.io/pypi/pyversions/xarray-units?label=Python&color=cornflowerblue&style=flat-square)](https://pypi.org/project/xarray-units/)
[![Downloads](https://img.shields.io/pypi/dm/xarray-units?label=Downloads&color=cornflowerblue&style=flat-square)](https://pepy.tech/project/xarray-units)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.10354517-cornflowerblue?style=flat-square)](https://doi.org/10.5281/zenodo.10354517)
[![Tests](https://img.shields.io/github/actions/workflow/status/astropenguin/xarray-units/tests.yaml?label=Tests&style=flat-square)](https://github.com/astropenguin/xarray-units/actions)

xarray extension for handling units

## Overview

xarray-units is an import-only package that provides a DataArray accessor `.units` for handling units such as converting units and numeric operations considering units.
[Astropy](https://www.astropy.org) is used as a backend.
Unlike similar implementations, xarray-units does not use a special data type to handle units, but uses the original data type in a DataArray.
This allows to continue to use powerful features such as parallel and lazy processing with [Dask](https://www.dask.org) and/or user-defined DataArray subclasses.

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

These are equivalent to manually un/setting the units in the DataArray attributes, but the `units ` accessor also check that the units are valid when setting.

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

xarray-units performs numerical operations considering units when the `units` accessor is attached to the DataArray on the left side of the operator:

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

The units of the DataArray after the operation follows those of the DataArray with the `units` accessor.
The resulting data values will be therefore different depending on the order of the operation.
They are, of course, equal when considering units:

```python
da_eq = (da_sum_m.units == da_sum_km)
print(da_eq)
```

```
<xarray.DataArray (dim_0: 3)>
array([ True,  True,  True])
Dimensions without coordinates: dim_0
```

> [!IMPORTANT]
> Because this feature is accessor-based, units are only considered for the operation right after the `units` accessor.
> See [method and operation chains](#method-and-operation-chains) for performing multiple operations at once.

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

### Method and operation chains

The `units` accessor has an option for chaining methods or operations while considering units:

```python
da_m = xr.DataArray([1, 2, 3]).units.set("m")
da_s = xr.DataArray([1, 2, 3]).units.set("s")
da_a = da_m.units(chain=2) / da_s / da_s
print(da_a)
```

```
<xarray.DataArray (dim_0: 3)>
array([1.        , 0.5       , 0.33333333])
Dimensions without coordinates: dim_0
Attributes:
    units:    m / s2
```

where `chain` is the number of chained methods or operations.
This is equivalent to nesting the `units` accessors:

```python
(da_m.units / da_s).units / da_s
```

### Use with static type checking

xarray-units provides a special type hint `xarray_units.DataArray` with which type checkers can statically handle the `units ` accessor and its methods:

```python
from xarray_units import DataArray

da: DataArray = xr.DataArray([1, 2, 3]).units.set("km")
```

> [!TIP]
> `xarray_units.DataArray` will be replaced by `xarray.DataArray` at runtime, so it can also be used for creating and subclassing `DataArray`.

### Use without the units accessor

xarray-units provides a function `xarray_units.units` that returns the `units` accessor of a DataArray.
The following two codes are therefore equivalent:

```python
xr.DataArray([1, 2, 3]).units.set("km")
```

```python
from xarray_units import units

units(xr.DataArray([1, 2, 3])).set("km")
```
