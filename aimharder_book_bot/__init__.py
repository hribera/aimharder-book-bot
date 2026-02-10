#
# AimHarder Booking Bot
# Author: Helena Ribera <heleribera@gmail.com>
# Website: www.hriberaponsa.com
#
"""AimHarder Booking Bot."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["__version__"]
