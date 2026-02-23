from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QMessageBox, QTextEdit
import qasync
import bleak
from .display_widget import DisplayWidget
from .utils import calculate_window


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
        windowWidth, windowHeight, xPos, yPos = calculate_window(scale_width=0.7, scale_height=0.7)
        self.setGeometry(xPos, yPos, windowWidth, windowHeight)
        self.setStyleSheet("background-color: #4B9CD3; color: white;")

        main_layout = QHBoxLayout(self)

        # Left Side (Status and Disconnect)
        left_layout = QVBoxLayout()
        
        self.connectButton = QPushButton('Disconnect', self)
        self.connectButton.clicked.connect(self.disconnect)
        self.connectButton.setStyleSheet("""
        QPushButton {
            background-color: #4B9CD3; 
            color: white; 
            border: .5px solid white; 
            border-radius: 5px;
            font-size: 14px; 
            font-weight: bold;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #C0392B;
        }
        """)
        left_layout.addWidget(self.connectButton)

        self.statusBox = QTextEdit(self)
        self.statusBox.setReadOnly(True)
        self.statusBox.setStyleSheet("background-color: #E7EBEB; color: black; border-radius: 5px; padding: 5px;")
        self.statusBox.append(f"Connecting to {self.device.name}...")
        left_layout.addWidget(self.statusBox)

        main_layout.addLayout(left_layout, 1)

        # Right Side (Lists and Actions)
        right_layout = QVBoxLayout()

        service_list_label = QLabel('Service List')
        service_list_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_layout.addWidget(service_list_label)

        self.servicesList = QListWidget(self)
        self.servicesList.setStyleSheet("""
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
        right_layout.addWidget(self.servicesList)

        self.serviceButton = QPushButton('Read Service', self)
        self.serviceButton.clicked.connect(self.scanChar)
        self.serviceButton.setStyleSheet("""
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
        }
        """)
        self.serviceButton.setEnabled(False)
        right_layout.addWidget(self.serviceButton)

        char_list_label = QLabel('Characteristic List')
        char_list_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_layout.addWidget(char_list_label)

        self.charList = QListWidget(self)
        self.charList.setStyleSheet("""
            QListWidget {
                background-color: #E7EBEB; 
                color: black; 
                padding: 2px;
                border-radius: 5px;
                font-size: 14px; 
                font-weight: bold;
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
        right_layout.addWidget(self.charList)

        main_layout.addLayout(right_layout, 2)

    @qasync.asyncSlot()
    async def disconnect(self):
        """
        Disconnects from the currently connected BLE device.
        """
        self.statusBox.append("Disconnecting...")
        self.connectButton.setEnabled(False)
        if self.m_client:
            await self.m_client.disconnect()
        self.close()

    @qasync.asyncSlot()
    async def scanServices(self):
        """
        Scans for services of the connected BLE device and updates the UI.
        """
        try:
            self.connectButton.setEnabled(False)
            if self.device:
                self.m_client = bleak.BleakClient(self.device)
                try:
                    await self.m_client.connect()
                    self.statusBox.append(f"Successfully connected to {self.device.name}!")
                except Exception as e:
                    import traceback; traceback.print_exc()
                    self.statusBox.append(f"Failed to connect: {str(e)}")
                    QMessageBox.warning(self, 'warning', 'Unable to connect')
                    self.close()
                    return
                
                self.statusBox.append("Discovering services...")
                i=0
                
                services = self.m_client.services
                for service in services:
                    i+=1
                    self.servicesList.addItem(str(service))
                    self.servicesDict[str(service)] = service

                self.statusBox.append(f"Found {i} services. Select one to read.")

                self.connectButton.setText('Disconnect')
                self.connectButton.disconnect()
                self.connectButton.clicked.connect(self.disconnect)
                self.connectButton.setEnabled(True)

                self.serviceButton.setEnabled(True)

                self.charList.doubleClicked.connect(self.charMonitor)
            else:
                QMessageBox.warning(self, 'warning', 'Unable to connect')
                self.close()
        except Exception as e:
            import traceback; traceback.print_exc()
            self.statusBox.append(f"Error in scanServices: {str(e)}")

    @qasync.asyncSlot()
    async def scanChar(self):
        """
        Scans for characteristics of the selected service and updates the UI.
        """
        try:
            self.serviceButton.setEnabled(False)
            if self.servicesList.currentItem():
                service_name = self.servicesList.currentItem().text()
                self.statusBox.append(f"Reading characteristics for {service_name}...")
                service = self.servicesDict[service_name]
                chars = service.characteristics
                self.charList.clear()
                for char in chars:
                    self.charList.addItem(str(char))
                    self.charDict[str(char)] = char
                self.statusBox.append(f"Found {len(chars)} characteristics.")
            else:
                QMessageBox.warning(self,'warning','Please select a valid option')
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.statusBox.append(f"Error in scanChar: {str(e)}")
        finally:
            self.serviceButton.setEnabled(True)

    @qasync.asyncSlot()
    async def charMonitor(self):
        """
        Opens a display widget for the selected characteristic to monitor its data.
        """
        char_name = self.charList.currentItem().text()
        self.statusBox.append(f"Monitoring characteristic: {char_name}")
        m_char = self.charDict[char_name]
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
