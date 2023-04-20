import sys
import serial
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt, QIODevice, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo


class SerialPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Plotter")
        self.setGeometry(100, 100, 800, 600)
        
        self.serial_port = QSerialPort()
        self.serial_port.readyRead.connect(self.handle_serial_data)
        
        self.plot_data = []
        self.plot_time = []
        self.start_time = time.time()
        
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        
        self.port_label = QLabel("COM Port")
        self.port_combo = QComboBox()
        for port_info in QSerialPortInfo.availablePorts():
            self.port_combo.addItem(port_info.portName())
        self.layout.addWidget(self.port_label)
        self.layout.addWidget(self.port_combo)
        
        self.baud_label = QLabel("Baud Rate")
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.layout.addWidget(self.baud_label)
        self.layout.addWidget(self.baud_combo)
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_serial)
        self.layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_serial)
        self.layout.addWidget(self.stop_button)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)
        
        self.show()
        
    def handle_serial_data(self):
        while self.serial_port.canReadLine():
            line = self.serial_port.readLine().decode().strip()
            if line.startswith("PLOTX:"):
                value = int(line.split(":")[1])
                self.plot_data.append(value)
                self.plot_time.append(time.time() - self.start_time)
                
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor(0, 0, 255), 1))
        
        x_scale = self.width() / 10
        y_scale = self.height() / 1024
        
        for i in range(len(self.plot_data)-1):
            x1 = (self.plot_time[i] % 10) * x_scale
            x2 = (self.plot_time[i+1] % 10) * x_scale
            y1 = self.height() - (self.plot_data[i] * y_scale)
            y2 = self.height() - (self.plot_data[i+1] * y_scale)
            painter.drawLine(x1, y1, x2, y2)
        
    def start_serial(self):
        port_name = self.port_combo.currentText()
        baud_rate = int(self.baud_combo.currentText())
        self.serial_port.setPortName(port_name)
        self.serial_port.setBaudRate(baud_rate)
        if self.serial_port.open(QIODevice.OpenModeFlag.ReadOnly):
            self.statusBar().showMessage(f"Connected to {port_name}")
        else:
            self.statusBar().showMessage(f"Failed to connect to {port_name}")
            
    def stop_serial(self):
        self.serial_port.close()
        self.plot_data = []
        self.plot_time = []
        self.start_time = time.time()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    serial_plotter = SerialPlotter()
    sys.exit(app.exec())
