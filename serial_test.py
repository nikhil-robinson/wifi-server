import serial.tools.list_ports, sys, time, re
import threading
from PyQt6.QtCore import Qt, QMetaObject, pyqtSlot
from PyQt6.QtWidgets import QApplication, QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout
from PyQt6 import QtWidgets

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QButtonGroup, QHBoxLayout, QRadioButton
from PyQt6.QtCore import Qt, QProcess,QTimer




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

        self.clear_button = QPushButton('Clear')
        self.clear_button.clicked.connect(self.clear_console)

        self.filter_button = QPushButton('Filter')
        self.filter_button.clicked.connect(self.filter_console)

        # Create a QLineEdit widget for entering filter pattern
        self.filter_pattern = QLineEdit()
        self.filter_pattern.setPlaceholderText('Enter filter pattern')

        # self.filter_layout = QHBoxLayout()
        # self.filter_layout.addWidget(self.filter_pattern)
        # self.filter_layout.addWidget(self.filter_button)

        self.console = QTextEdit()
        self.console.setReadOnly(True)


        self.send_input = QLineEdit()
        self.send_input.returnPressed.connect(self.send)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send)


        self.form_layout.addRow(QLabel("Port:"), self.port_combo)
        self.form_layout.addRow(QLabel("Baudrate:"), self.baudrate_combo)


        self.form_layout.addRow(self.clear_button, self.connect_button)
        
        self.form_layout.addRow(self.filter_pattern, self.filter_button)


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

        self.s_timer = QTimer()
        self.s_timer.timeout.connect(self.read_serial)

        self.p_timer =QTimer()
        self.p_timer.timeout.connect(self.refresh_ports)
        self.p_timer.start(1000)


    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        # time.sleep(1)

    def connect_or_disconnect(self):
        if not self.connected:
            self.p_timer.stop()
            port = self.port_combo.currentText()
            baudrate = self.baudrate_combo.currentText()
            self.serial = serial.Serial(port, baudrate)
            self.s_timer.start(100)
            self.connect_button.setText("Disconnect")
            self.connected = True

            # Start thread to read from serial
            # self.serial_thread = threading.Thread(target=self.read_serial, daemon=True)
            # self.serial_thread.start()


        else:
            self.s_timer.stop()
            self.serial.close()
            self.serial=None
            self.p_timer.start(1000)
            self.connect_button.setText("Connect")
            self.connected = False



    def send(self):
        if self.connected:
            data = self.send_input.text()
            self.serial.write(data.encode())
            self.send_input.clear()

   

    def read_serial(self):
        try:
            if self.serial and self.serial.in_waiting > 0:
                # Read data from serial port
                data = self.serial.readline().decode().strip()
                pattern = r'\033\[[0-9;]*m'  # Pattern to remove escape sequences
                data = re.sub(pattern, '', data)
                # Append data to console
                self.console.append(data)
        except Exception as e:
            self.console.append(f"Error Occured {e}")
            self.s_timer.stop()
            self.serial.close()
            self.serial=None
            self.p_timer.start(1000)
            self.connect_button.setText("Connect")
            self.connected = False
            # self.connect_or_disconnect()

    def clear_console(self):
        self.console.clear()
    
    def filter_console(self):
        # Filter console based on entered pattern
        pattern = self.filter_pattern.text()
        if pattern:
            pattern = f'.*{pattern}.*'  # Add .* at the beginning and end to match anywhere in the line
            filtered_text = self.console.toPlainText()
            filtered_lines = []
            for line in filtered_text.split('\n'):
                if re.search(pattern, line):
                    filtered_lines.append(line)
            filtered_text = '\n'.join(filtered_lines)
            self.console.setPlainText(filtered_text)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())