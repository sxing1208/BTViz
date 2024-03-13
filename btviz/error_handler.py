# error_handler.py
# import logging

from PyQt5.QtWidgets import QMessageBox
from .btviz_exceptions import *


def show_error_message(error):
    if isinstance(error, DeviceNotFoundError):
        QMessageBox.warning(None, "Error", str(error))
    elif isinstance(error, DeviceConnectionError):
        QMessageBox.warning(None, "Error", str(error))
    elif isinstance(error, CharacteristicNotFoundError):
        QMessageBox.warning(None, "Error", str(error))
    elif isinstance(error, NotificationError):
        QMessageBox.warning(None, "Error", str(error))
    elif isinstance(error, DataDecodingError):
        QMessageBox.warning(None, "Error", str(error))
    elif isinstance(error, ConfigurationError):
        QMessageBox.warning(None, "Error", str(error))
    elif isinstance(error, BTVizException):
        QMessageBox.warning(None, "BTViz Error", str(error))
    else:
        QMessageBox.critical(None, "Error", "An unexpected error occurred.")


def handle_exception():
    ...

