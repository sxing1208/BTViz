import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QMessageBox, QPlainTextEdit, QLabel
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
import bleak
import qasync
import asyncio
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class DisplayWidget(QWidget):

    def __init__(self, client, char):
        super().__init__()
        self.m_client = client
        self.m_char = char  
        
        self.valueList = []
        self.valueQueue = deque(maxlen = 50)

        self._animation = None 

        self.isPlotting = False

        self.initUI()

    def initUI(self):
        self.notifButton = QPushButton("Enable Notifications")
        self.notifButton.clicked.connect(self.enableNotif)

        self.plotButton = QPushButton("Plot")
        self.plotButton.clicked.connect(self._plot)
        self.plotButton.setEnabled(False)

        self.setWindowTitle("Characteristic Reader")
        self.setGeometry(200, 200, 1000, 1000)

        self.textfield = QPlainTextEdit()
        self.textfield.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.notifButton)
        layout.addWidget(self.plotButton)
        layout.addWidget(self.textfield)

        self._fig, self._ax = plt.subplots()
        self._line, = self._ax.plot(self.valueQueue)
        self._ax.set_title('ADC')
        self._ax.set_xlabel('Time (s)')
        self._ax.set_ylabel('ADC (a. u.)')
        self._canvas = FigureCanvas(self._fig)

        layout.addWidget(self._canvas)
        
    @qasync.asyncSlot()
    async def enableNotif(self):
        self.notifButton.setEnabled(False)
        try:
            await self.m_client.start_notify(self.m_char, self.notifHandler)
            self.plotButton.setEnabled(True)
        except:
            QMessageBox.information(self,"info","unable to start notification")

    def notifHandler(self, char, value):
        value = int(str(value[::-1].hex()),16)
        text = self.textfield.toPlainText() + "\n" + str(value)
        self.valueList.append(value)
        self.textfield.setPlainText(text)
        self.valueQueue.append(value)

    def plotUpdate(self, frame):
        if self.isPlotting:
            # Update plot data
            self._line.set_xdata(range(len(self.valueQueue)))
            self._line.set_ydata(self.valueQueue)
            self._ax.relim()
            self._ax.autoscale_view()
            
            # Set line color
            self._line.set_color('r')
            return self._line,

    def _plot(self):
        self.plotButton.setEnabled(False)
        self._animation = FuncAnimation(self._fig, self.plotUpdate, interval=1, cache_frame_data=False)
        self.isPlotting = True
        self._canvas.draw_idle()

class ScanWidget(QWidget):

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
        self.setWindowTitle("Bluetooth scanner")
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

                self.charList.doubleClicked.connect(self.charMonitor)
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

    @qasync.asyncSlot()
    async def charMonitor(self):
        m_char = self.charDict[self.charList.currentItem().text()]
        self.window = DisplayWidget(self.m_client,m_char)
        self.window.show()
        
def main():
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