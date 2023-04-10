import sys
from PyQt6 import QtWidgets, QtGui, QtCore
import serial.tools.list_ports, re

class SerialTerminal(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Initialize serial connection
        self.serial = None

        # Create GUI elements
        self.port_combo = QtWidgets.QComboBox()
        self.baud_combo = QtWidgets.QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200", "Custom"])
        self.baud_combo.currentIndexChanged.connect(self.handle_baud_change)
        self.custom_baud_box = QtWidgets.QSpinBox()
        self.custom_baud_box.setRange(1, 1000000)
        self.custom_baud_box.setValue(9600)
        self.custom_baud_box.setEnabled(False)
        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect)
        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.clicked.connect(self.send_data)
        self.input_box = QtWidgets.QLineEdit()
        self.console = QtWidgets.QTextEdit()
        self.console.setReadOnly(True)

        # Add elements to layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.port_combo)
        layout.addWidget(self.baud_combo)
        layout.addWidget(self.custom_baud_box)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.input_box)
        layout.addWidget(self.send_button)
        layout.addWidget(self.console)
        self.setLayout(layout)

        # Populate port dropdown with available ports
        self.refresh_ports()

        # Create timer to read incoming serial data
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.read_data)

    def refresh_ports(self):
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)

    def handle_baud_change(self, index):
        if self.baud_combo.currentText() == "Custom":
            self.custom_baud_box.setEnabled(True)
        else:
            self.custom_baud_box.setEnabled(False)

    def connect(self):
        # Disconnect any existing connection
        self.disconnect()

        # Get selected port and baud rate
        port = self.port_combo.currentText()
        if self.baud_combo.currentText() == "Custom":
            baud = self.custom_baud_box.value()
        else:
            baud = int(self.baud_combo.currentText())

        # Open serial connection
        self.serial = serial.Serial(port=port, baudrate=baud)

        # Start timer to read incoming data
        self.timer.start(100)

    def disconnect(self):
        if self.serial is not None and self.serial.is_open:
            self.serial.close()
            self.timer.stop()

    def send_data(self):
        if self.serial is not None and self.serial.is_open:
            data = self.input_box.text() + "\r\n"
            self.serial.write(data.encode())
            self.input_box.clear()

    def read_data(self):
        if self.serial is not None and self.serial.is_open:
            data = self.serial.read_all().decode()

            # Strip out ANSI escape codes
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            data = ansi_escape.sub('', data)

            self.console.insertPlainText(data)
            self.console.ensureCursorVisible()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SerialTerminal()
    window.show()
    sys.exit(app.exec())
