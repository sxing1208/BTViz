from PyQt5.QtWidgets import QWidget, QPushButton, QTextEdit, QLabel, QFormLayout
from PyQt5.QtCore import pyqtSignal


class PlotSettingsWidget(QWidget):
    """
    A widget for setting plot titles and axis
    """
    gotPlotSetting = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.titleText = QTextEdit()
        self.xAxisText = QTextEdit()
        self.yAxisText = QTextEdit()
        self.windowText = QTextEdit()
        self.saveButton = QPushButton("save settings")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Plot Settings")

        self.titleText.setPlainText("Characteristic Value")
        self.xAxisText.setPlainText("Time (a.u.)")
        self.yAxisText.setPlainText("Value (a.u.)")
        self.windowText.setPlainText("50")
        self.saveButton.clicked.connect(self.on_save)

        layout = QFormLayout(self)

        layout.addWidget(QLabel("Title Text"))
        layout.addWidget(self.titleText)
        layout.addWidget(QLabel("x Axis Text"))
        layout.addWidget(self.xAxisText)
        layout.addWidget(QLabel("y Axis Text"))
        layout.addWidget(self.yAxisText)
        layout.addWidget(QLabel("Animation Window Length"))
        layout.addWidget(self.windowText)
        layout.addWidget(self.saveButton)

    def on_save(self):
        ret_str = self.titleText.toPlainText() + ',' \
                  + self.xAxisText.toPlainText() + ',' \
                  + self.yAxisText.toPlainText() + ',' \
                  + self.windowText.toPlainText()
        self.gotPlotSetting.emit(ret_str)
        self.close()
