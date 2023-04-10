import serial.tools.list_ports, sys, time
import threading
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QTabWidget
from PyQt6 import QtWidgets


class SerialTerminal(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Terminal")

        # UI widgets
        self.port_combo = QComboBox()
        self.baudrate_combo = QComboBox()
        self.custom_baudrate_input = QLineEdit()
        self.connect_button = QPushButton("Connect")
        self.console = QTextEdit()
        self.send_input = QLineEdit()
        self.send_button = QPushButton("Send")

        # Populate port combo with available ports
        self.refresh_ports()

        # Populate baudrate combo with standard baudrates
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Port:"), self.port_combo)
        form_layout.addRow(QLabel("Baudrate:"), self.baudrate_combo)
        form_layout.addRow(QLabel("Custom baudrate:"), self.custom_baudrate_input)
        self.custom_baudrate_input.setEnabled(False)
        form_layout.addRow(QLabel(), self.connect_button)
        form_layout.addRow(QLabel("Console:"), self.console)

        send_layout = QHBoxLayout()
        send_layout.addWidget(self.send_input)
        send_layout.addWidget(self.send_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(send_layout)
        self.setLayout(main_layout)

        # Signals
        self.connect_button.clicked.connect(self.connect_or_disconnect)
        self.send_input.returnPressed.connect(self.send)
        self.send_button.clicked.connect(self.send)
        self.custom_baudrate_input.textChanged.connect(self.custom_baudrate_changed)

        # Serial connection
        self.serial = None
        self.connected = False

        # Start thread to check for new ports
        self.ports_thread = threading.Thread(target=self.update_ports_thread, daemon=True)
        self.ports_thread.start()

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo.clear()
        self.port_combo.addItems(ports)

    def connect_or_disconnect(self):
        if not self.connected:
            port = self.port_combo.currentText()
            baudrate = int(self.custom_baudrate_input.text() or self.baudrate_combo.currentText())
            self.serial = serial.Serial(port, baudrate)
            self.connect_button.setText("Disconnect")
            self.connected = True

            # Start thread to read from serial
            self.serial_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.serial_thread.start()

        else:
            self.serial.close()
            self.connect_button.setText("Connect")
            self.connected = False

    def send(self):
        if self.connected:
            data = self.send_input.text()
            self.serial.write(data.encode())
            self.send_input.clear()

    def custom_baudrate_changed(self, text):
        self.baudrate_combo.setEnabled(not bool(text))
        self.custom_baudrate_input.setEnabled(bool(text))

    def update_ports_thread(self):
        while True:
            # Check for new ports
            current_ports = set(self.port_combo.itemText(i) for i in range(self.port_combo.count()))
            new_ports = set(p.device for p in serial.tools.list_ports.comports()) - current_ports

            # Add new ports to dropdown
            if new_ports:
                self.port_combo.addItems(new_ports)

            # Remove disconnected ports from dropdown
            disconnected_ports = current_ports - set(p.device for p in serial.tools.list_ports.comports())
            for port in disconnected_ports:
                index = self.port_combo.findText(port)
                self.port_combo.removeItem(index)

            # Sleep for 1 second
            time.sleep(1)
    def read_serial(self):
        while self.connected:
            data = self.serial.readline()
            if data is not None:
                self.console.append(data.decode('utf-8'))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SerialTerminal()
    window.show()
    sys.exit(app.exec())