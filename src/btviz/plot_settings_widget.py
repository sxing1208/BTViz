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
        self.setStyleSheet("background-color: #4B9CD3; color: white;")

        text_style = "background-color: #E7EBEB; color: black; border-radius: 5px; padding: 5px;"
        label_style = "font-size: 14px; font-weight: bold; color: white;"
        button_style = """
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
            background-color: #13294B;
        }
        """

        self.titleText.setPlainText("Characteristic Value")
        self.titleText.setStyleSheet(text_style)
        self.xAxisText.setPlainText("Time (a.u.)")
        self.xAxisText.setStyleSheet(text_style)
        self.yAxisText.setPlainText("Value (a.u.)")
        self.yAxisText.setStyleSheet(text_style)
        self.windowText.setPlainText("50")
        self.windowText.setStyleSheet(text_style)
        
        self.saveButton.setStyleSheet(button_style)
        self.saveButton.clicked.connect(self.on_save)

        layout = QFormLayout(self)

        title_label = QLabel("Title Text")
        title_label.setStyleSheet(label_style)
        layout.addWidget(title_label)
        layout.addWidget(self.titleText)
        
        x_label = QLabel("x Axis Text")
        x_label.setStyleSheet(label_style)
        layout.addWidget(x_label)
        layout.addWidget(self.xAxisText)
        
        y_label = QLabel("y Axis Text")
        y_label.setStyleSheet(label_style)
        layout.addWidget(y_label)
        layout.addWidget(self.yAxisText)
        
        window_label = QLabel("Animation Window Length")
        window_label.setStyleSheet(label_style)
        layout.addWidget(window_label)
        layout.addWidget(self.windowText)
        
        layout.addWidget(self.saveButton)

    def on_save(self):
        ret_str = self.titleText.toPlainText() + ',' \
                  + self.xAxisText.toPlainText() + ',' \
                  + self.yAxisText.toPlainText() + ',' \
                  + self.windowText.toPlainText()
        self.gotPlotSetting.emit(ret_str)
        self.close()
