"""
Elliot Fitting: Exciton Binding Energy Analysis Package
"""

from .fsum2d import fsum2d
from .fitter import ElliotFitter
from .utils import fit_absorption_spectrum

__version__ = "0.1.0"
__all__ = ['fsum2d', 'ElliotFitter', 'fit_absorption_spectrum']

