__all__ = [
    # submodules
    "accessor",
    "operator",
    "quantity",
    "utils",
    # aliases
    "DataArray",
    "units",
    "unitsof",
]
__version__ = "0.5.0"


# submodules
from . import accessor
from . import operator
from . import quantity
from . import utils


# aliases
from .accessor import DataArray, units
from .utils import unitsof
