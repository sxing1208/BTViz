from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QMessageBox
import qasync
import bleak
from .connect_widget import ConnectWidget
from .utils import calculate_window


class ScanWidget(QWidget):
    """
    A widget for scanning BLE devices.
    """
    def __init__(self):
        """
        Initializes the scan widget.
        """
        super().__init__()

        self.m_scanner = bleak.BleakScanner()
        self.m_client = None
        self.isDeviceDiscovered = False

        self.devicesDict = {}

        # UI elements
        self.scanButton = None
        self.connectButton = None
        self.devicesList = None

        self.scanServicesWindow = None

        self.initUI()

    def initUI(self):
        """
        Initializes the user interface for the scan widget.
        """
        self.setWindowTitle('BTViz')
        window_width, window_height, x_pos, y_pos = calculate_window(scale_width=0.2, scale_height=0.7)
        self.setGeometry(x_pos, y_pos, window_width, window_height)

        layout = QVBoxLayout(self)

        self.scanButton = QPushButton('Scan for Devices', self)
        self.scanButton.clicked.connect(self.scanDevices)

        self.connectButton = QPushButton('Connect to Device', self)
        self.connectButton.clicked.connect(self.scanServices)

        self.devicesList = QListWidget(self)

        layout.addWidget(self.scanButton)
        layout.addWidget(QLabel('Device List'))
        layout.addWidget(self.devicesList)
        layout.addWidget(self.connectButton)

    @qasync.asyncSlot()
    async def scanDevices(self):
        """
        Scans for BLE devices and updates the UI with the results.
        """
        self.scanButton.setEnabled(False)
        devices = await bleak.BleakScanner.discover()
        for device in devices:
            self.devicesList.addItem(device.name)
            self.devicesDict[device.name] = device

        self.isDeviceDiscovered = True
        self.scanButton.setText('Clear All')
        self.scanButton.disconnect()
        self.scanButton.clicked.connect(self.clearAll)

        self.scanButton.setEnabled(True)
        self.connectButton.setEnabled(True)

    def clearAll(self):
        """
        Clears all discovered devices and resets the UI.
        """

        self.devicesList.clear()

        self.devicesDict = {}

        self.scanButton.setText('Scan for Devices')
        self.scanButton.disconnect()
        self.scanButton.clicked.connect(self.scanDevices)

        self.connectButton.setEnabled(False)

    def scanServices(self):
        if self.devicesList.currentItem().text():
            device = self.devicesDict[self.devicesList.currentItem().text()]
            self.scanServicesWindow = ConnectWidget(device)
            self.scanServicesWindow.show()
        else:
            QMessageBox.warning(self, 'Warning', 'Select Valid Device')
