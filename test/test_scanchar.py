import sys
import asyncio
import qasync
from PyQt5.QtWidgets import QApplication
from btviz.connect_widget import ConnectWidget

class MockChar:
    def __init__(self, n):
        self.n = n
    def __str__(self):
        return f"MockChar {self.n}"

class MockService:
    def __init__(self, n):
        self.n = n
        self.characteristics = [MockChar(1), MockChar(2)]
    def __str__(self):
        return f"MockService {self.n}"

class MockDevice:
    name = "MockDevice"
    address = "00:11:22:33:44:55"

app = QApplication(sys.argv)
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)

def sim():
    print("Simulating ConnectWidget...")
    cw = ConnectWidget(MockDevice())
    # Bypass scanServices connection logic
    cw.m_client = type("MockClient", (), {"services": [MockService(1), MockService(2)]})()
    
    # Manually populate
    for s in cw.m_client.services:
        cw.servicesList.addItem(str(s))
        cw.servicesDict[str(s)] = s
    
    cw.servicesList.setCurrentRow(0)
    
    print("Clicking read service button!")
    cw.serviceButton.setEnabled(True)
    cw.serviceButton.clicked.emit()
    
    # Allow event loop to process
    async def wait():
        await asyncio.sleep(1)
        print("Done!")
        loop.stop()
    
    asyncio.ensure_future(wait())

asyncio.ensure_future(asyncio.sleep(0.1)).add_done_callback(lambda _: sim())
loop.run_forever()
