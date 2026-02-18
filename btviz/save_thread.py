from PyQt5.QtCore import QObject, pyqtSignal
import os
import datetime

class SaveThread(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, filename, content):
        super().__init__()
        self.filename = filename
        self.content = content

    def saveData(self):
        try:
            date_str = str(datetime.datetime.now())[:10]
            file_folder_str = './output/' + date_str
            full_path = './output/' + date_str + '/' + self.filename
            
            if not os.path.exists("./output"):
                os.makedirs("./output")
            if not os.path.exists(file_folder_str):
                os.makedirs(file_folder_str)
                
            with open(full_path, 'w') as f:
                f.write(self.content)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))