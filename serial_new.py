import sys
from PyQt6 import QtCore, QtWidgets, QtSerialPort

class SerialMonitor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the UI
        self.setWindowTitle("Serial Monitor")
        self.setGeometry(100, 100, 640, 480)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Set up the serial port
        self.serial_port = QtSerialPort.QSerialPort()
        self.serial_port.setPortName("/dev/ttyACM0")
        self.serial_port.setBaudRate(115200)
        self.serial_port.setDataBits(QtSerialPort.QSerialPort.DataBits.Data8)
        self.serial_port.setParity(QtSerialPort.QSerialPort.Parity.NoParity)
        self.serial_port.setStopBits(QtSerialPort.QSerialPort.StopBits.OneStop)

        # Set up the serial port signals
        self.serial_port.readyRead.connect(self.handle_ready_read)
        self.serial_port.errorOccurred.connect(self.handle_error)

        # Set up the input/output widgets
        self.input_widget = QtWidgets.QLineEdit()
        self.input_widget.returnPressed.connect(self.send_data)
        self.layout.addWidget(self.input_widget)
        self.output_widget = QtWidgets.QTextEdit()
        self.layout.addWidget(self.output_widget)

        # Open the serial port
        if not self.serial_port.open(QtCore.QIODevice.OpenModeFlag.ReadWrite):
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not open serial port {self.serial_port.portName()}")
            sys.exit(1)

        # Show the window
        self.show()

    def handle_ready_read(self):
        data = self.serial_port.readAll().data().decode()
        self.output_widget.insertPlainText(data)

    def handle_error(self, error):
        if error == QtSerialPort.QSerialPortError.NoError:
            return
        QtWidgets.QMessageBox.critical(self, "Error", f"Serial port error: {self.serial_port.errorString()}")

    def send_data(self):
        data = self.input_widget.text() + "\n"
        self.serial_port.write(data.encode())
        self.input_widget.clear()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    monitor = SerialMonitor()
    sys.exit(app.exec())
