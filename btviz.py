import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QMessageBox, QPlainTextEdit, QLabel, QComboBox
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
import bleak
import qasync
import asyncio
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import struct
import json

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
config = load_config('config.json')

class DisplayWidget(QWidget):
    """
    A widget for displaying BLE characteristic data and plotting it in real-time.
    """
    def __init__(self, client, char):
        """
        Initializes the display widget.

        :param client: A BleakClient connected to the BLE device.
        :param char: The characteristic to monitor and display.
        """
        super().__init__()
        self.m_client = client
        self.m_char = char  
        
        self.valueList = []
        self.valueQueue = deque(maxlen = 50)

        self._animation = None 
        self.isPlotting = False

        self.initUI()

    def initUI(self):
        """
        Initializes the user interface for the display widget.
        """
        self.notifButton = QPushButton('Enable Notifications')
        self.notifButton.clicked.connect(self.enableNotif)

        self.plotButton = QPushButton('Plot')
        self.plotButton.clicked.connect(self._plot)
        self.plotButton.setEnabled(False)

        # Dropdown for selecting data decoding method
        self.decodeMethodDropdown = QComboBox()
        self.decodeMethodDropdown.setEnabled(False)
        for option in config['decodeOptions']:
            self.decodeMethodDropdown.addItem(option['name'])

        self.setWindowTitle('Characteristic Reader')
        self.setGeometry(200, 200, 1000, 1000)

        self.textfield = QPlainTextEdit()
        self.textfield.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.notifButton)
        layout.addWidget(self.plotButton)
        layout.addWidget(self.decodeMethodDropdown)
        layout.addWidget(self.textfield)

        self._fig, self._ax = plt.subplots()
        self._line, = self._ax.plot(self.valueQueue)
        self._ax.set_title('Temperature') # TODO: make the title and labels easy to change
        self._ax.set_xlabel('Time') # TODO  
        self._ax.set_ylabel('Value') # TODO
        self._canvas = FigureCanvas(self._fig)

        layout.addWidget(self._canvas)
        
    @qasync.asyncSlot()
    async def enableNotif(self):
        """
        Enables notifications for the BLE characteristic.
        """
        self.notifButton.setEnabled(False)
        try:
            await self.m_client.start_notify(self.m_char, self.notifHandler)
            self.plotButton.setEnabled(True)
            self.decodeMethodDropdown.setEnabled(True)
        except:
            QMessageBox.information(self, 'Info', 'Unable to start notification')

    def notifHandler(self, char, value):
        """
        Handles notifications from the BLE characteristic.

        :param char: The characteristic that sent the notification.
        :param value: The value of the notification.
        """
        option = config['decodeOptions'][self.decodeMethodDropdown.currentIndex()]
        format_str = option['format']
        
        if len(value) >= struct.calcsize(format_str):
            decoded_value = struct.unpack(format_str, value)[0]
            text = self.textfield.toPlainText() + '\n' + str(decoded_value)
            self.textfield.setPlainText(text)
            self.valueQueue.append(decoded_value)
            self.valueList.append(decoded_value)
        else:
            QMessageBox.warning(self, 'Error', 'Received data does not match expected format.')

        # value = int(str(value[::-1].hex()), 16)
        # text = self.textfield.toPlainText() + '\n' + str(value)
        # self.valueList.append(value)
        # self.textfield.setPlainText(text)
        # self.valueQueue.append(value)

    def plotUpdate(self, frame):
        """
        Updates the plot with new data.

        :param frame: The current frame of the animation (unused).
        """
        if self.isPlotting:
            # Update plot data
            self._line.set_xdata(range(len(self.valueQueue))) # TODO: this should be related to real-time 
            self._line.set_ydata(self.valueQueue)
            self._ax.relim()
            self._ax.autoscale_view()
            
            # Set line color
            self._line.set_color('r')
            return self._line,

    def _plot(self):
        """
        Starts plotting the BLE characteristic data in real-time.
        """
        self.plotButton.setEnabled(False)
        self._animation = FuncAnimation(self._fig, self.plotUpdate, interval=1, cache_frame_data=False)
        self.isPlotting = True
        self._canvas.draw_idle()

class ScanWidget(QWidget):
    """
    A widget for scanning BLE devices and their services and characteristics.
    """
    def __init__(self):
        """
        Initializes the scan widget.
        """
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
        """
        Initializes the user interface for the scan widget.
        """
        self.setWindowTitle('BTViz')
        self.setGeometry(50, 50, 700, 1000)

        layout = QVBoxLayout(self)

        self.scanButton = QPushButton('Scan for Devices', self)
        self.scanButton.clicked.connect(self.scanDevices)

        self.connectButton = QPushButton('Connect to Device', self)
        self.connectButton.clicked.connect(self.scanServices)
        self.connectButton.setEnabled(False)

        self.serviceButton = QPushButton('Read Service', self)
        self.serviceButton.clicked.connect(self.scanChar)
        self.serviceButton.setEnabled(False)

        self.devicesList = QListWidget(self)

        self.servicesList = QListWidget(self)

        self.charList = QListWidget(self)

        layout.addWidget(self.scanButton)
        layout.addWidget(QLabel('Device List'))
        layout.addWidget(self.devicesList)
        layout.addWidget(self.connectButton)
        layout.addWidget(QLabel('Service List'))
        layout.addWidget(self.servicesList)
        layout.addWidget(self.serviceButton)
        layout.addWidget(QLabel('Characteristic List'))
        layout.addWidget(self.charList)
    
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
        if(self.isConnected):
            self.m_client.disconnect()
        
        self.devicesList.clear()
        self.servicesList.clear()
        self.charList.clear()

        self.devicesDict = {}
        self.servicesDict = {}
        self.charDict = {}

        self.scanButton.setText('Scan for Devices')
        self.scanButton.disconnect()
        self.scanButton.clicked.connect(self.scanDevices)

        self.connectButton.setText('Connect to Sensor')
        self.connectButton.disconnect()
        self.connectButton.clicked.connect(self.scanServices)
        self.connectButton.setEnabled(False)

        self.serviceButton.setText('Read Service')
        self.serviceButton.disconnect()
        self.serviceButton.clicked.connect(self.scanChar)
        self.serviceButton.setEnabled(False)

    @qasync.asyncSlot()
    async def disconnect(self):
        """
        Disconnects from the currently connected BLE device.
        """
        self.connectButton.setEnabled(False)
        if(self.m_client):
            await self.m_client.disconnect()
            self.connectButton.setText('Connect to Sensor')
            self.connectButton.disconnect()
            self.connectButton.clicked.connect(self.scanServices)

            self.servicesList.clear()
            self.charList.clear()

            self.servicesDict = {}
            self.charDict = {}

            self.connectButton.setEnabled(True)

        else:
            QMessageBox.warning(self,'Warning','No connected device, System Reset')
            self.clearAll()

    @qasync.asyncSlot()
    async def scanServices(self):
        """
        Scans for services of the connected BLE device and updates the UI.
        """
        self.connectButton.setEnabled(False)
        if(self.devicesList.currentItem()):
            self.m_client = bleak.BleakClient(self.devicesDict[self.devicesList.currentItem().text()])
            await self.m_client.connect()
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
            QMessageBox.warning(self,'warning','Please select a valid option')
        
    @qasync.asyncSlot()
    async def scanChar(self):
        """
        Scans for characteristics of the selected service and updates the UI.
        """
        self.serviceButton.setEnabled(False)
        if(self.servicesList.currentItem()):
            service = self.servicesDict[self.servicesList.currentItem().text()]
            chars = service.characteristics
            for char in chars:
                self.charList.addItem(str(char))
                self.charDict[str(char)] = char
        else:
            QMessageBox.warning(self,'warning','Please select a valid option')

    @qasync.asyncSlot()
    async def charMonitor(self):
        """
        Opens a display widget for the selected characteristic to monitor its data.
        """
        m_char = self.charDict[self.charList.currentItem().text()]
        self.window = DisplayWidget(self.m_client,m_char)
        self.window.show()
        
def main():
    """
    Main function to execute the application.
    """
    app = QApplication(sys.argv)
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    ex = ScanWidget()
    ex.show()
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())

if __name__ == '__main__':
    main()