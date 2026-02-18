from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
import os, datetime

class SaveThread(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self._buf = []
        self._fh = None
        self._timer = None

    @pyqtSlot()
    def open(self):
        try:
            date_str = str(datetime.datetime.now())[:10]
            folder = os.path.join(".", "output", date_str)
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, self.filename)

            self._fh = open(path, "a", buffering=1)  # line-buffered

            # flush every 0.5s (reduces disk churn)
            self._timer = QTimer()
            self._timer.timeout.connect(self.flush)
            self._timer.start(500)

        except Exception as e:
            self.error.emit(str(e))

    @pyqtSlot(str)
    def enqueue(self, line: str):
        # cheap: just buffer
        self._buf.append(line)

    @pyqtSlot()
    def flush(self):
        if not self._fh or not self._buf:
            return
        try:
            self._fh.write("\n".join(self._buf) + "\n")
            self._buf.clear()
        except Exception as e:
            self.error.emit(str(e))

    @pyqtSlot()
    def close(self):
        try:
            if self._timer:
                self._timer.stop()
            self.flush()
            if self._fh:
                self._fh.close()
        finally:
            self.finished.emit()
