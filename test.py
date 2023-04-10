import sys
import serial
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QPushButton, QDockWidget, QWidget, QFormLayout
from PyQt6.QtCore import QTimer, Qt

class SerialTerminal(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a QTextEdit widget to serve as the console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.setCentralWidget(self.console)

        # Create start and stop buttons
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_serial)
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_serial)

        # Create a QFormLayout for buttons
        button_layout = QFormLayout()
        button_layout.addRow('Start:', self.start_button)
        button_layout.addRow('Stop:', self.stop_button)

        # Create a QWidget to hold the buttons
        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        # Create a QDockWidget to hold the button widget
        dock_widget = QDockWidget()
        dock_widget.setWidget(button_widget)

        # Add the dock widget to the bottom dock
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock_widget)

        # Open serial port
        self.ser = None

        # Create a QTimer to periodically read data from serial port
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)

    def start_serial(self):
        # Open serial port if not already open
        if not self.ser:
            self.ser = serial.Serial('/dev/ttyACM0', 9600)  # Replace with your desired baud rate
            self.timer.start(100)  # Adjust the interval (in milliseconds) based on your needs

    def stop_serial(self):
        # Close serial port if open
        if self.ser:
            self.ser.close()
            self.ser = None
            self.timer.stop()

    def read_serial(self):
        if self.ser and self.ser.in_waiting > 0:
            # Read data from serial port
            data = self.ser.readline().decode().strip()
            # Append data to console
            self.console.append(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SerialTerminal()
    window.show()
    sys.exit(app.exec())
