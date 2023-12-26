__all__ = [
    # submodules
    "accessor",
    "operator",
    "quantity",
    "utils",
    # aliases
    "DataArray",
    "Units",
    "units",
]
__version__ = "0.2.0"


# submodules
from . import accessor
from . import operator
from . import quantity
from . import utils


# aliases
from .accessor import DataArray, Units, units
