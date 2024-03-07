import sys
import asyncio
from PyQt5.QtWidgets import QApplication
import qasync
from btviz.scan_widget import ScanWidget
from btviz.error_handler import show_error_message


def main():
    """
    Main function to execute the application.
    """
    app = QApplication(sys.argv)
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    try:
        ex = ScanWidget()
        ex.show()
    except Exception as e:
        show_error_message(e)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())


if __name__ == '__main__':
    main()
