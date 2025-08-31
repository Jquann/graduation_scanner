"""
GUI Package for Graduation Scanner
Contains all GUI components and interfaces
"""

from .main_window import GraduationScannerApp
from .registration_tab import RegistrationTab
from .scanning_tab import ScanningTab
from .management_tab import ManagementTab
from .certificate_display import CertificateDisplay, CertificateIntegration

__all__ = [
    'GraduationScannerApp',
    'RegistrationTab', 
    'ScanningTab',
    'ManagementTab',
    'CertificateDisplay',
    'CertificateIntegration'
]

__version__ = '1.0.0'