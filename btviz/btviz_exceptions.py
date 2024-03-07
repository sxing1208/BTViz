# btviz_exceptions.py

class BTVizException(Exception):
    """Base exception class for BTViz application."""
    pass


class DeviceConnectionError(BTVizException):
    """Raised when there is an error connecting to a BLE device."""
    pass


class DeviceNotFoundError(BTVizException):
    """Raised when no BLE devices are found during the scan."""
    pass


class CharacteristicNotFoundError(BTVizException):
    """Raised when no characteristics are found for a given BLE service."""
    pass


class NotificationError(BTVizException):
    """Raised when there is an error enabling notifications for a BLE characteristic."""
    pass


class DataDecodingError(BTVizException):
    """Raised when there is an error decoding the data received from a BLE characteristic."""
    pass


class ConfigurationError(BTVizException):
    """Raised when there is an error loading or parsing the configuration file."""
    pass
