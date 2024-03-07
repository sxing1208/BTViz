from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QPlainTextEdit, QMessageBox, QComboBox
from PyQt5.QtCore import QTimer
import qasync
import struct
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from .utils import calculate_window
from .plot_settings_widget import PlotSettingsWidget
from .config_loader import load_config
from .btviz_exceptions import *


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

        self.config = None

        self.m_client = client
        self.m_char = char

        self.dataframe = [deque(maxlen= 100)]

        self.isNotif = False
        self.isRead = False
        self.isFirstTransactions = True

        self.figList = []
        self.axList = []
        self.lineList = []

        self._line = None
        self._title = None
        self._xlabel = None
        self._ylabel = None
        self._canvas = None
        self.animateInterval = None
        self._animation = None
        self.isPlotting = False
        self._timer = None

        self.notifButton = None
        self.plotButton = None
        self.decodeMethodDropdown = None
        self.textfield = None
        self.readButton = None
        self.intervalDropdown = None
        self.settingsButton = None
        
        self.window = None

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
        self.config = load_config('config.json')
        for option in self.config['decodeOptions']:
            self.decodeMethodDropdown.addItem(option['name'])
        self.decodeMethodDropdown.addItem("String Literal")
        self.decodeMethodDropdown.addItem("Comma Delimited String Literal")

        self.setWindowTitle('Characteristic Reader')

        window_width, window_height, x_pos, y_pos = calculate_window(scale_width=0.5, scale_height=0.7)
        self.setGeometry(x_pos, y_pos, window_width, window_height)

        self.textfield = QPlainTextEdit()
        self.textfield.setReadOnly(True)

        self.readButton = QPushButton("Enable Timed Read")
        self.readButton.clicked.connect(self.enableTimedRead)

        self.intervalDropdown = QComboBox()
        self.intervalDropdown.addItem(".")
        self.intervalDropdown.addItem("100")
        self.intervalDropdown.addItem("200")
        self.intervalDropdown.addItem("500")
        self.intervalDropdown.addItem("1000")

        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self.notifButton)
        self._layout.addWidget(self.readButton)
        self._layout.addWidget(self.decodeMethodDropdown)
        self._layout.addWidget(self.intervalDropdown)
        self._layout.addWidget(self.textfield)
        self._layout.addWidget(self.plotButton)

        self.settingsButton = QPushButton("Plot Settings")
        self.settingsButton.clicked.connect(self.onSettings)

        self._layout.addWidget(self.settingsButton)

    @qasync.asyncSlot()
    async def onSettings(self):
        """
        Reveal plot settings scanServicesWindow
        """
        self.window = PlotSettingsWidget()
        self.window.gotPlotSetting.connect(self.onGotSettings)
        self.window.show()

    def onGotSettings(self, settings_str):
        """
        Update plot settings
        """
        str_list = settings_str.split(",")
        self._title = str_list[0]
        self._xlabel = str_list[1]
        self._ylabel = str_list[2]
        for valueQueue in self.dataframe:
            valueQueue = deque(maxlen=int(str_list[3]))
        for ax in self._axs:
            ax.set_title(self._title)
            ax.set_xlabel(self._xlabel)
            ax.set_ylabel(self._ylabel)

    @qasync.asyncSlot()
    async def enableNotif(self):
        """
        Enables notifications for the BLE characteristic.
        """
        self.notifButton.setEnabled(False)
        self.readButton.setEnabled(False)
        self.decodeMethodDropdown.setEnabled(False)
        self.intervalDropdown.setEnabled(False)

        try:
            await self.m_client.start_notify(self.m_char, self.decodeRoutine)
            self.decodeMethodDropdown.setEnabled(False)
            self.isNotif = True
        except Exception as e:
            raise NotificationError(f"Unable to start notification {str(e)}")
            # QMessageBox.information(self, 'Info', 'Unable to start notification')

    def decodeRoutine(self, char, value):
        """
        Routine that Handles decoding of the BLE characteristic.

        :param char: The characteristic that sent the notification.
        :param value: The value of the notification.
        """
        if (self.decodeMethodDropdown.currentText() != "String Literal" and
                self.decodeMethodDropdown.currentText() != "Comma Delimited String Literal"):
            option = self.config['decodeOptions'][self.decodeMethodDropdown.currentIndex()]
            format_str = option['format']

            if len(value) >= struct.calcsize(format_str):
                try:
                    decoded_value = struct.unpack(format_str, value)[0]
                except struct.error as e:
                    raise DataDecodingError(f"Error decoding data: {str(e)}")
                text = str(decoded_value) + '\n' + self.textfield.toPlainText()
                self.textfield.setPlainText(text)
                self.dataframe[0].append(decoded_value)
            else:
                QMessageBox.warning(self, 'Error', 'Received data does not match expected format.')
            if self.isFirstTransactions:
                self._fig, self._ax = plt.subplots()
                self._line, = self._ax.plot(self.dataframe[0])
                self._title = "ADC"
                self._xlabel = "Time (a.u.)"
                self._ylabel = "Value (a.u.)"
                self._canvas = FigureCanvas(self._fig)

                self._ax.set_title(self._title)
                self._ax.set_xlabel(self._xlabel)
                self._ax.set_ylabel(self._ylabel)

                self._lines = [self._line]
                self._axs = [self._ax]
                self.isFirstTransactions = False
                self.plotButton.setEnabled(True)

        elif self.decodeMethodDropdown.currentText() == "String Literal":
            decoded_value = value.decode("UTF-8")
            self.plotButton.setEnabled(False)
            text = str(decoded_value) + '\n' + self.textfield.toPlainText()
            self.textfield.setPlainText(text)

        else:
            try:
                decoded_value = value.decode("UTF-8")
                decoded_list = decoded_value.split(",")
            except:
                QMessageBox.warning(self,"Warning","Unable to decode")
                self.close()
            
            text = str(decoded_value) + '\n' + self.textfield.toPlainText()
            self.textfield.setPlainText(text)
            if(self.isFirstTransactions):
                self.dataframe = []
                self._lines = []
                for i in range(len(decoded_list)):
                    self.dataframe.append(deque(maxlen= 100))

                self.isFirstTransactions = False

                self._fig, self._axs = plt.subplots(len(self.dataframe),1)
                for i in range(len(self._axs)):
                    _ax = self._axs[i]
                    line, = _ax.plot(self.dataframe[i])
                    self._lines.append(line)
                    self._title = "ADC"
                    self._xlabel = "Time (a.u.)"
                    self._ylabel = "Value (a.u.)"

                    _ax.set_title(self._title)
                    _ax.set_xlabel(self._xlabel)
                    _ax.set_ylabel(self._ylabel)

                self._canvas = FigureCanvas(self._fig)
                self.plotButton.setEnabled(True)

            for i in range(len(decoded_list)):
                try:
                    item = float(decoded_list[i])
                except:
                    QMessageBox.warning(self,"Warning","Unable to decode")
                self.dataframe[i].append(item)

                    

    def plotUpdate(self, frame):
        """
        Updates the plot with new data.

        :param frame: The current frame of the animation (unused).
        """
        if self.isPlotting:
            for i in range(len(self.dataframe)):
                # Update plot data
                self._lines[i].set_xdata(range(len(self.dataframe[i])))  # Set x-data as the index of the data points
                self._lines[i].set_ydata(self.dataframe[i])  # Set y-data as the actual data values

                # Adjust plot limits and scaling
                self._axs[i].relim()
                self._axs[i].autoscale_view()

                # Set line color (optional)
                self._lines[i].set_color('r')

            # Return all line objects for animation update
            return [line for line in self.lineList]

    def _plot(self):
        """
        Starts plotting the BLE characteristic data in real-time.
        """
        self.plotButton.setEnabled(False)
        self._layout.addWidget(self._canvas)

        self._animation = FuncAnimation(self._fig, self.plotUpdate, interval=1, cache_frame_data=False)
        
        self.isPlotting = True
        self._canvas.draw_idle()

    def enableTimedRead(self):
        """
        Enables Timed Read of a BLE characteristic
        """
        try:
            self.animateInterval = int(self.intervalDropdown.currentText())
        except:
            QMessageBox.warning(self, "error", "select valid interval")
            return

        self.readButton.setEnabled(False)
        self.notifButton.setEnabled(False)
        self.decodeMethodDropdown.setEnabled(False)
        self.intervalDropdown.setEnabled(False)

        if self.decodeMethodDropdown.currentText() != "String Literal":
            self.plotButton.setEnabled(True)

        # TODO -change timer settings
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.timeoutHandler)
        self._timer.start(self.animateInterval)
        self.isRead = True

    @qasync.asyncSlot()
    async def timeoutHandler(self):
        """
        Handles characteristic reading timer timeouts
        """
        value = await self.m_client.read_gatt_char(self.m_char)
        self.decodeRoutine(self.m_char, value)

    @qasync.asyncClose
    async def closeEvent(self, event):
        """
        Routine that terminates characteristic operations prior to scanServicesWindow closure
        """
        if self.isNotif:
            await self.m_client.stop_notify(self.m_char)

        if self.isRead:
            self._timer.stop()
