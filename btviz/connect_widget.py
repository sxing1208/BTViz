from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QMessageBox
import qasync
import bleak
from .display_widget import DisplayWidget
from .utils import calculate_window
from .btviz_exceptions import *


class ConnectWidget(QWidget):
    def __init__(self, device):
        super().__init__()

        self.device = device

        self.servicesDict = {}
        self.charDict = {}

        self.isDeviceDiscovered = False
        self.isConnected = False
        self.isServiceDiscovered = False
        self.isCharDiscovered = False

        self.m_client = None

        self.scanServices()

        self.serviceButton = None
        self.connectButton = None
        self.servicesList = None
        self.charList = None
        self.charMonitorWindow = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Device Connect")
        windowWidth, windowHeight, xPos, yPos = calculate_window(scale_width=0.5, scale_height=0.7)
        self.setGeometry(xPos, yPos, windowWidth, windowHeight)

        self.serviceButton = QPushButton('Read Service', self)
        self.serviceButton.clicked.connect(self.scanChar)
        self.serviceButton.setEnabled(False)

        self.connectButton = QPushButton('Disconnect', self)
        self.connectButton.clicked.connect(self.disconnect)
        self.connectButton.setEnabled(True)

        self.servicesList = QListWidget(self)

        self.charList = QListWidget(self)

        layout = QVBoxLayout(self)

        layout.addWidget(self.connectButton)
        layout.addWidget(QLabel('Service List'))
        layout.addWidget(self.servicesList)
        layout.addWidget(self.serviceButton)
        layout.addWidget(QLabel('Characteristic List'))
        layout.addWidget(self.charList)

    @qasync.asyncSlot()
    async def disconnect(self):
        """
        Disconnects from the currently connected BLE device.
        """
        self.connectButton.setEnabled(False)
        if self.m_client:
            await self.m_client.disconnect()
        self.close()

    @qasync.asyncSlot()
    async def scanServices(self):
        """
        Scans for services of the connected BLE device and updates the UI.
        """
        self.connectButton.setEnabled(False)
        if self.device:
            self.m_client = bleak.BleakClient(self.device)
            try:
                await self.m_client.connect()
            except Exception as e:
                raise DeviceConnectionError(f"Failed to connect to the BLE device: {str(e)}")
                # QMessageBox.warning(self, 'warning', 'Unable to connect')
                # self.close()
            services = self.m_client.services
            for service in services:
                self.servicesList.addItem(str(service))
                self.servicesDict[str(service)] = service
                self.connectButton.setText('Disconnect')
                self.connectButton.disconnect()
                self.connectButton.clicked.connect(self.disconnect)
                self.connectButton.setEnabled(True)

                self.serviceButton.setEnabled(True)

                self.charList.doubleClicked.connect(self.charMonitor)
        else:
            QMessageBox.warning(self, 'warning', 'Unable to connect')
            self.close()

    @qasync.asyncSlot()
    async def scanChar(self):
        """
        Scans for characteristics of the selected service and updates the UI.
        """
        self.serviceButton.setEnabled(False)
        if self.servicesList.currentItem():
            service = self.servicesDict[self.servicesList.currentItem().text()]
            chars = service.characteristics
            if not chars:
                raise CharacteristicNotFoundError("No characteristics found for the selected service.")
            for char in chars:
                self.charList.addItem(str(char))
                self.charDict[str(char)] = char
        else:
            QMessageBox.warning(self, 'warning', 'Please select a valid option')

    @qasync.asyncSlot()
    async def charMonitor(self):
        """
        Opens a display widget for the selected characteristic to monitor its data.
        """
        m_char = self.charDict[self.charList.currentItem().text()]
        self.charMonitorWindow = DisplayWidget(self.m_client,m_char)
        self.charMonitorWindow.show()

    @qasync.asyncClose
    async def closeEvent(self, event):
        if self.m_client:
            try:
                await self.m_client.disconnect()
            except:
                pass
            self.m_client = None
