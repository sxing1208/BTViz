import sys
from PyQt5.QtWidgets import QApplication
from btviz.display_widget import DisplayWidget
import traceback

class MockClient:
    pass

class MockChar:
    pass

app = QApplication(sys.argv)

print("Starting test DisplayWidget...")
dw = DisplayWidget(MockClient(), MockChar())
dw.show()

try:
    print("Testing onGotSettings before plotting...")
    dw.onGotSettings("Test Title,Test X,Test Y,100")
    print("onGotSettings passed!")

    print("Testing _plot with 1 item in dataframe...")
    dw.isFirstTransactions = False
    dw.decodeMethodDropdown.setCurrentText("Comma Delimited String Literal")
    dw.dataframe = [[0,1,2]]
    dw.isFirstPlot = True

    dw._plot()
    print("_plot initialization passed!")
    print(f"Subplots instantiated. _axs len: {len(dw._axs)}")

except Exception as e:
    traceback.print_exc()
    sys.exit(1)

print("All tests passed.")
