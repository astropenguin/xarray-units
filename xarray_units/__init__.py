__all__ = [
    # submodules
    "accessor",
    "operator",
    "quantity",
    "utils",
    # aliases
    "DataArray",
    "units",
]
__version__ = "0.4.0"


# submodules
from . import accessor
from . import operator
from . import quantity
from . import utils


# aliases
from .accessor import DataArray, units
