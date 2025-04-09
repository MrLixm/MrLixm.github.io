from ._read import read_rst
from ._read import parse_metadata
from ._read import DocumentType

from . import _extensions

_extensions.register_extensions()
