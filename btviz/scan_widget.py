from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QMessageBox, QTextEdit
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
        window_width, window_height, x_pos, y_pos = calculate_window(scale_width=0.7, scale_height=0.7)
        self.setGeometry(x_pos, y_pos, window_width, window_height)
        self.setStyleSheet("background-color: #4B9CD3; color: white;")

        main_layout = QHBoxLayout(self)

        # Left Side
        left_layout = QVBoxLayout()

        self.scanButton = QPushButton('Scan for Devices', self)
        self.scanButton.clicked.connect(self.scanDevices)
        self.scanButton.setStyleSheet("""
        QPushButton {
            background-color: #4B9CD3; 
            color: white; 
            border: .5px solid white; 
            border-radius: 5px;
            font-size: 16px; 
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #13294B;
            color: white;
            border: .5px solid white;
            border-radius: 5px;
        }
        QPushButton:pressed {
            background-color: #13294B;
            color: white;
            border: .5px solid white;
            border-radius: 5px;
        }
        """)

        self.statusBox = QTextEdit(self)
        self.statusBox.setReadOnly(True)
        self.statusBox.setStyleSheet("background-color: #E7EBEB; color: black; border-radius: 5px; padding: 5px;")
        self.statusBox.append("Ready to scan...")
        left_layout.addWidget(self.statusBox)

        main_layout.addLayout(left_layout, 1)

        # Right Side Header (Title + Scan Button)
        right_header_layout = QHBoxLayout()
        device_list_label = QLabel('Device List')
        device_list_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_header_layout.addWidget(device_list_label)
        right_header_layout.addWidget(self.scanButton)

        right_layout = QVBoxLayout()
        right_layout.addLayout(right_header_layout)

        self.devicesList = QListWidget(self)
        self.devicesList.setStyleSheet("""
            QListWidget {
                background-color: #E7EBEB; 
                color: black; 
                padding: 2px;
                border-radius: 5px;
            }
            QListWidget::item {
                background-color: white;
                margin: 3px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #4B9CD3;
            }
            QListWidget::item:selected {
                background-color: #7BAFD4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #4B9CD3;
            }
        """)
        self.devicesList.itemSelectionChanged.connect(self.onDeviceSelected)
        right_layout.addWidget(self.devicesList)

        self.connectButton = QPushButton('Connect to Device', self)
        self.connectButton.clicked.connect(self.scanServices)
        self.connectButton.setStyleSheet("""
        QPushButton {
            background-color: #4B9CD3; 
            color: white; 
            border: .5px solid white; 
            border-radius: 5px;
            font-size: 16px; 
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #13294B;
            color: white;
            border: .5px solid white;
            border-radius: 5px;
        }
        QPushButton:pressed {
            background-color: #13294B;
            color: white;
            border: .5px solid white;
            border-radius: 5px;
        }
        """)
        right_layout.addWidget(self.connectButton)

        main_layout.addLayout(right_layout, 2)

    @qasync.asyncSlot()
    async def scanDevices(self):
        """
        Scans for BLE devices and updates the UI with the results.
        """
        self.statusBox.append("Scanning for devices...")
        self.scanButton.setEnabled(False)
        devices = await bleak.BleakScanner.discover()
        for device in devices:
            self.devicesList.addItem(device.name)
            self.devicesDict[device.name] = device

        self.statusBox.append(f"Found {len(devices)} devices. Select one to connect.")
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
        self.statusBox.append("Cleared device list. Ready to scan...")

    def onDeviceSelected(self):
        if self.devicesList.currentItem():
            device_name = self.devicesList.currentItem().text()
            self.statusBox.append(f"Selected: {device_name}")

    def scanServices(self):
        if self.devicesList.currentItem() and self.devicesList.currentItem().text():
            device_name = self.devicesList.currentItem().text()
            device = self.devicesDict[device_name]
            self.statusBox.append(f"Connecting to {device_name}...")
            self.scanServicesWindow = ConnectWidget(device)
            self.scanServicesWindow.show()
        else:
            QMessageBox.warning(self, 'Warning', 'Select Valid Device')
