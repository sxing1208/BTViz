import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QMessageBox, QLineEdit, QLabel
from PyQt5.QtCore import pyqtSlot, pyqtSignal
import bleak
import qasync
import asyncio

class BluetoothWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

        self.m_scanner = bleak.BleakScanner()
        self.m_client = None

        self.devicesDict = {}
        self.servicesDict = {}
        self.charDict = {}

        self.isDeviceDiscovered = False
        self.isConnected = False
        self.isServiceDiscovered = False
        self.isCharDiscovered = False


    def initUI(self):
        self.setWindowTitle("Bluetooth Device Scanner")
        self.setGeometry(50, 50, 700, 1000)

        layout = QVBoxLayout(self)

        self.scanButton = QPushButton("Scan for Devices", self)
        self.scanButton.clicked.connect(self.scanDevices)

        self.connectButton = QPushButton("Connect to Sensor", self)
        self.connectButton.clicked.connect(self.scanServices)
        self.connectButton.setEnabled(False)

        self.serviceButton = QPushButton("Read Service", self)
        self.serviceButton.clicked.connect(self.scanChar)
        self.serviceButton.setEnabled(False)

        self.devicesList = QListWidget(self)

        self.servicesList = QListWidget(self)

        self.charList = QListWidget(self)


        layout.addWidget(self.scanButton)
        layout.addWidget(QLabel("Device List"))
        layout.addWidget(self.devicesList)
        layout.addWidget(self.connectButton)
        layout.addWidget(QLabel("Service List"))
        layout.addWidget(self.servicesList)
        layout.addWidget(self.serviceButton)
        layout.addWidget(QLabel("Characteristic List"))
        layout.addWidget(self.charList)
    
    @qasync.asyncSlot()
    async def scanDevices(self):
        self.scanButton.setEnabled(False)
        devices = await bleak.BleakScanner.discover()
        for device in devices:
            self.devicesList.addItem(device.name)
            self.devicesDict[device.name] = device
        
        self.isDeviceDiscovered = True
        self.scanButton.setText("Clear All")
        self.scanButton.disconnect()
        self.scanButton.clicked.connect(self.clearAll)

        self.scanButton.setEnabled(True)
        self.connectButton.setEnabled(True)

    def clearAll(self):
        if(self.isConnected):
            self.m_client.disconnect()
        
        self.devicesList.clear()
        self.servicesList.clear()
        self.charList.clear()

        self.devicesDict = {}
        self.servicesDict = {}
        self.charDict = {}

        self.scanButton.setText("Scan for Devices")
        self.scanButton.disconnect()
        self.scanButton.clicked.connect(self.scanDevices)

        self.connectButton.setText("Connect to Sensor")
        self.connectButton.disconnect()
        self.connectButton.clicked.connect(self.scanServices)
        self.connectButton.setEnabled(False)

        self.serviceButton.setText("Read Service")
        self.serviceButton.disconnect()
        self.serviceButton.clicked.connect(self.scanChar)
        self.serviceButton.setEnabled(False)

    @qasync.asyncSlot()
    async def disconnect(self):
        self.connectButton.setEnabled(False)
        if(self.m_client):
            await self.m_client.disconnect()
            self.connectButton.setText("Connect to Sensor")
            self.connectButton.disconnect()
            self.connectButton.clicked.connect(self.scanServices)

            self.servicesList.clear()
            self.charList.clear()

            self.servicesDict = {}
            self.charDict = {}

            self.connectButton.setEnabled(True)

        else:
            QMessageBox.warning(self,"Warning","No connected device, System Reset")
            self.clearAll()
        
        

    @qasync.asyncSlot()
    async def scanServices(self):
        self.connectButton.setEnabled(False)
        if(self.devicesList.currentItem()):
            self.m_client = bleak.BleakClient(self.devicesDict[self.devicesList.currentItem().text()])
            await self.m_client.connect()
            services = self.m_client.services
            for service in services:
                self.servicesList.addItem(str(service))
                self.servicesDict[str(service)] = service
                self.connectButton.setText("Disconnect")
                self.connectButton.disconnect()
                self.connectButton.clicked.connect(self.disconnect)
                self.connectButton.setEnabled(True)

                self.serviceButton.setEnabled(True)
        else:
            QMessageBox.warning(self,"warning","Please select a valid option")
        

    @qasync.asyncSlot()
    async def scanChar(self):
        self.serviceButton.setEnabled(False)
        if(self.servicesList.currentItem()):
            service = self.servicesDict[self.servicesList.currentItem().text()]
            chars = service.characteristics
            for char in chars:
                self.charList.addItem(str(char))
                self.charDict[str(char)] = char
        else:
            QMessageBox.warning(self,"warning","Please select a valid option")


def main():
    app = QApplication(sys.argv)
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    ex = BluetoothWidget()
    ex.show()
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())

if __name__ == '__main__':
    main()