import serial.tools.list_ports, sys, time
import threading
from PyQt6.QtCore import Qt, QMetaObject, pyqtSlot
from PyQt6.QtWidgets import QApplication, QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout
from PyQt6 import QtWidgets

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QButtonGroup, QHBoxLayout, QRadioButton
from PyQt6.QtCore import Qt, QProcess




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.form_layout = QFormLayout()


        # UI widgets
        self.port_combo = QComboBox()
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)
        self.port_combo.setCurrentIndex(0)

        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.port_combo.setCurrentIndex(0)


        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_or_disconnect)

        self.console = QTextEdit()
        self.console.setReadOnly(True)


        self.send_input = QLineEdit()
        self.send_input.returnPressed.connect(self.send)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send)


        self.form_layout.addRow(QLabel("Port:"), self.port_combo)
        self.form_layout.addRow(QLabel("Baudrate:"), self.baudrate_combo)


        self.form_layout.addRow(QLabel(), self.connect_button)


        self.send_layout = QHBoxLayout()
        self.send_layout.addWidget(self.send_input)
        self.send_layout.addWidget(self.send_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addWidget(self.console)
        self.main_layout.addLayout(self.send_layout)

        # self.setLayout(self.main_layout)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.setWindowTitle("Serial Terminal")
        self.setGeometry(100, 100, 400, 300)
        self.show()


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
            baudrate = self.baudrate_combo.currentText()
            self.serial = serial.Serial(port, baudrate,timeout=1)
            self.connect_button.setText("Disconnect")
            self.connected = True

            # Start thread to read from serial
            self.serial_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.serial_thread.start()


        else:
            self.connected = False
            self.serial_thread.join()
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
                self.console.append(data.decode().strip())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())