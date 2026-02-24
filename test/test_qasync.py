import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget
import qasync
import asyncio

class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.btn = QPushButton("Test", self)
        self.btn.clicked.connect(self.my_slot)
        
    @qasync.asyncSlot()
    async def my_slot(self):
        print("Success! Slot executed without arguments.")
        asyncio.get_event_loop().stop()

app = QApplication(sys.argv)
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)

w = TestWidget()
w.show()

# Simulate a click programmatically which pushes args.
# clicked() emits `bool checked = false`
import threading

def sim_click():
    import time
    time.sleep(1)
    print("Clicking...")
    w.btn.clicked.emit()
    w.btn.clicked.emit(False)

t = threading.Thread(target=sim_click)
t.start()

loop.run_forever()
