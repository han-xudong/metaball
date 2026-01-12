"""
Enable `metaball.__version__` to be imported.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("metaball")
except PackageNotFoundError:
    __version__ = "unknown"
