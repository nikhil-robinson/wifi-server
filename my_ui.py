import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout,QGroupBox, QSplitter, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QButtonGroup, QHBoxLayout, QRadioButton
from PyQt6.QtCore import QProcess
import serial.tools.list_ports, sys, time, re
import threading
from PyQt6.QtCore import Qt, QMetaObject, pyqtSlot
from PyQt6.QtWidgets import QApplication, QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout
from PyQt6 import QtWidgets

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QButtonGroup, QHBoxLayout, QRadioButton,QStackedWidget
from PyQt6.QtCore import Qt, QProcess,QTimer

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

class QTextEditHandler(logging.Handler):
    def __init__(self, serial_console):
        super().__init__()
        self.server_console = serial_console

    def emit(self, record):
        msg = self.format(record)
        self.server_console.append(msg)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create the left side bar group box
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout for the main window
        self.main_layout = QHBoxLayout()

        # Create a group box for the left sidebar
        self.left_bar_group = QGroupBox("Tools")
        self.left_bar_group_layout = QVBoxLayout()
        self.left_bar_group.setLayout(self.left_bar_group_layout)
        self.left_bar_group.setFixedWidth(100)

        # Create buttons for the left sidebar
        self.server_button = QPushButton("Server")
        self.client_button = QPushButton("Client")
        self.serial_button = QPushButton("Serial")
        self.network_button = QPushButton("Network")
        self.security_button = QPushButton("Security")
        self.about_button = QPushButton("About")

        # Add buttons to the left sidebar group box
        self.left_bar_group_layout.addWidget(self.server_button)
        self.left_bar_group_layout.addWidget(self.client_button)
        self.left_bar_group_layout.addWidget(self.serial_button)
        self.left_bar_group_layout.addWidget(self.network_button)
        self.left_bar_group_layout.addWidget(self.security_button)
        self.left_bar_group_layout.addWidget(self.about_button)

        # Create a label for the right side text
        self.right_text = QLabel("This is the default text.")
        self.serverConf()
        self.serialConf()

        self.stacked_widget = QStackedWidget()

        # Create widgets to be displayed in the stacked widget
        self.server_widget = QLabel("Server Widget")
        self.client_widget = QLabel("Client Widget")
        self.serial_widget = QLabel("Serial Widget")
        self.network_widget = QLabel("Network Widget")
        self.security_widget = QLabel("Security Widget")
        self.about_widget = QLabel("About Widget")

        # Add widgets to the stacked widget
        self.stacked_widget.addWidget(self.server_form_widget)
        self.stacked_widget.addWidget(self.client_widget)
        self.stacked_widget.addWidget(self.serial_form_widget)
        self.stacked_widget.addWidget(self.network_widget)
        self.stacked_widget.addWidget(self.security_widget)
        self.stacked_widget.addWidget(self.about_widget)
        

        # Add the left sidebar and right text to the main layout
        self.main_layout.addWidget(self.left_bar_group)
        self.main_layout.addWidget(self.stacked_widget)


        # Set the main layout as the central widget
        self.central_widget.setLayout(self.main_layout)

        # Connect the buttons to their respective functions
        self.server_button.clicked.connect(self.on_serverButton_clicked)
        self.client_button.clicked.connect(self.on_clientButton_clicked)
        self.serial_button.clicked.connect(self.on_serialButton_clicked)
        
        # Set the window properties
        self.setWindowTitle("PyQt6 App")
        self.setGeometry(100, 100, 1000, 600)
        self.show()

    def serverConf(self):
        # Create the layout for the form
        self.server_form_widget = QWidget()
        self.server_form_layout = QFormLayout()
        self.server_form_widget.setLayout(self.server_form_layout)

        # Create the input fields for the form
        self.server_type_combo = QComboBox()
        self.server_type_combo.addItems(["HTTP", "UDP", "TCP"])
        self.server_type_combo.setCurrentIndex(0)
        # self.server_type_combo.currentIndexChanged.connect(self.handle_server_type_change)

        self.server_port_input = QLineEdit()
        self.server_port_input.setText("8080")

        self.server_local_host_radio = QRadioButton("Local Host")
        self.server_ngrok_radio = QRadioButton("Ngrok")

        # Create a button group for the Local Host and Ngrok buttons
        self.server_host_button_group = QButtonGroup()
        self.server_host_button_group.addButton(self.server_local_host_radio)
        self.server_host_button_group.addButton(self.server_ngrok_radio)
        self.server_local_host_radio.setChecked(True)

        self.create_server_button = QPushButton("Create Server")
        self.create_server_button.clicked.connect(self.create_server)

        # Add the input fields to the form layout
        self.server_form_layout.addRow(QLabel("Server Type:"), self.server_type_combo)
        self.server_form_layout.addRow(QLabel("Port:"), self.server_port_input)

        # Create a horizontal layout for the Local Host and Ngrok buttons
        self.server_host_button_layout = QHBoxLayout()
        self.server_host_button_layout.addWidget(self.server_local_host_radio)
        self.server_host_button_layout.addWidget(self.server_ngrok_radio)
        self.server_form_layout.addRow(QLabel("Server Host:"), self.server_host_button_layout)

        self.server_form_layout.addRow(QLabel(""), self.create_server_button)

        # Create the log window
        self.server_console = QTextEdit()
        self.server_console.setReadOnly(True)
        self.server_form_layout.addRow(QLabel(""), self.server_console)



        server_log_handler = QTextEditHandler(self.server_console)
        logging.getLogger().addHandler(server_log_handler)
        logging.getLogger().setLevel(logging.DEBUG)
        self.isSERVERstarted = False

    # def handle_server_type_change(self, index):
    #     # Retrieve the current selected server type
    #     self.server_type = self.server_type_combo.currentText()

    def start_http_server(self,serial_port):
        # Start HTTP server on serial_port 80
        
        self.http_process = QProcess(self)
        self.http_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.http_process.readyReadStandardOutput.connect(self.http_handle_output)
        self.http_process.finished.connect(self.http_process_finished)
        self.http_process.start("python3", ["-m", "http.server", serial_port])
        self.create_server_button.setText("Disconect")
        self.isSERVERstarted = True
        

        

    def http_handle_output(self):
        # Log http_output from HTTP server to serial_console
        http_output = bytes(self.http_process.readAllStandardOutput()).decode()
        logging.debug(http_output)

    def http_process_finished(self):
        # Destroy http_process and print message when finished
        self.http_process.terminate()
        self.http_process.waitForFinished()
        logging.debug("HTTP server stopped")
        self.isSERVERstarted = False

    def start_tcp_server(self):
        self.tcp_server = QTcpServer(self)
        self.tcp_server.listen(QHostAddress("127.0.0.1"), int(self.server_port_input.text()))  # Listen on localhost, port 5000
        self.tcp_server.newConnection.connect(self.handle_connection)



    def tcp_receive_data(self):
        tcp_client_socket = self.sender()
        tcp_message = tcp_client_socket.readAll().data().decode('utf-8')
        self.server_console.append(f'Received message: {tcp_message} from {tcp_client_socket.peerAddress().toString()}:{tcp_client_socket.peerPort()}')

    def tcp_client_disconnected(self):
        tcp_client_socket = self.sender()
        self.server_console.append(f'Client disconnected: {tcp_client_socket.peerAddress().toString()}:{tcp_client_socket.peerPort()}')
        tcp_client_socket.deleteLater()



    def handle_connection(self):
        while self.tcp_server.hasPendingConnections():
            tcp_client_socket = self.tcp_server.nextPendingConnection()
            tcp_client_socket.readyRead.connect(self.tcp_receive_data)
            tcp_client_socket.disconnected.connect(self.tcp_client_disconnected)

    def create_server(self):
        # TODO: Implement server creation logic
        if self.isSERVERstarted == False:
            http_server_host = "Local Host" if self.server_local_host_radio.isChecked() else "Ngrok"
            self.server_console.append(f"{self.server_type_combo.currentText()} Server created with {http_server_host} and serial_port {self.server_port_input.text()}!")
            if self.server_type_combo.currentText() == "HTTP" and http_server_host == "Local Host":
                print("Http")
                self.start_http_server(self.server_port_input.text())
                self.isSERVERstarted = True
                self.create_server_button.setText("Disconnect")
            elif self.server_type_combo.currentText() == "TCP" and http_server_host == "Local Host":
                print("TCP")
                self.start_tcp_server()
                self.isSERVERstarted = True
                self.create_server_button.setText("Disconnect")

        else:
            self.http_process.terminate()
            self.http_process.waitForFinished()
            self.create_server_button.setText("Connect")
            self.isSERVERstarted = False
            self.server_console.append(f"{self.server_type_combo.currentText()} Server Stoped!")

    
    def on_serverButton_clicked(self):
        #hellp
        self.stacked_widget.setCurrentWidget(self.server_form_widget)

        
    
    def on_clientButton_clicked(self):
        #self.main_right_text.setText("This is text for button 2.")
        self.stacked_widget.setCurrentWidget(self.client_widget)
    
    def on_serialButton_clicked(self):
        self.stacked_widget.setCurrentWidget(self.serial_form_widget)




    def serialConf(self):

        self.serial_form_widget = QWidget()
        self.serial_form_layout = QFormLayout()
        self.serial_form_widget.setLayout(self.serial_form_layout)
        self.serial_port_combo = QComboBox()
        serial_ports = [p.device for p in serial.tools.list_ports.comports()]
        self.serial_port_combo.addItems(serial_ports)
        self.serial_port_combo.setCurrentIndex(0)

        self.serial_baudrate_combo = QComboBox()
        self.serial_baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.serial_port_combo.setCurrentIndex(0)


        self.serial_connect_button = QPushButton("Connect")
        self.serial_connect_button.clicked.connect(self.connect_or_disconnect)

        self.serial_clear_button = QPushButton('Clear')
        self.serial_clear_button.clicked.connect(self.clear_console)

        self.serial_filter_button = QPushButton('Filter')
        self.serial_filter_button.clicked.connect(self.filter_console)

        # Create a QLineEdit widget for entering filter serial_pattern
        self.serial_filter_pattern = QLineEdit()
        self.serial_filter_pattern.setPlaceholderText('Enter filter serial_pattern')

        # self.filter_layout = QHBoxLayout()
        # self.filter_layout.addWidget(self.serial_filter_pattern)
        # self.filter_layout.addWidget(self.serial_filter_button)

        self.serial_console = QTextEdit()
        self.serial_console.setReadOnly(True)


        self.serial_send_input = QLineEdit()
        self.serial_send_input.returnPressed.connect(self.send)
        
        self.serial_send_button = QPushButton("Send")
        self.serial_send_button.clicked.connect(self.send)


        self.serial_form_layout.addRow(QLabel("Port:"), self.serial_port_combo)
        self.serial_form_layout.addRow(QLabel("Baudrate:"), self.serial_baudrate_combo)


        self.serial_form_layout.addRow(self.serial_clear_button, self.serial_connect_button)
        
        self.serial_form_layout.addRow(self.serial_filter_pattern, self.serial_filter_button)

        self.serial_form_layout.addRow(self.serial_console)


        self.serial_send_layout = QHBoxLayout()
        self.serial_send_layout.addWidget(self.serial_send_input)
        self.serial_send_layout.addWidget(self.serial_send_button)

        self.serial_form_layout.addRow(self.serial_send_layout)

        self.serial = None
        self.serial_connected = False

        self.serial_s_timer = QTimer()
        self.serial_s_timer.timeout.connect(self.read_serial)

        self.serial_p_timer =QTimer()
        self.serial_p_timer.timeout.connect(self.refresh_ports)
        self.serial_p_timer.start(1000)

    def refresh_ports(self):
        serial_ports = [p.device for p in serial.tools.list_ports.comports()]
        self.serial_port_combo.clear()
        self.serial_port_combo.addItems(serial_ports)
        # time.sleep(1)

    def connect_or_disconnect(self):
        if not self.serial_connected:
            self.serial_p_timer.stop()
            serial_port = self.serial_port_combo.currentText()
            baudrate = self.serial_baudrate_combo.currentText()
            self.serial = serial.Serial(serial_port, baudrate)
            self.serial_s_timer.start(100)
            self.serial_connect_button.setText("Disconnect")
            self.serial_connected = True

            # Start thread to read from serial
            # self.serial_thread = threading.Thread(target=self.read_serial, daemon=True)
            # self.serial_thread.start()


        else:
            self.serial_s_timer.stop()
            self.serial.close()
            self.serial=None
            self.serial_p_timer.start(1000)
            self.serial_connect_button.setText("Connect")
            self.serial_connected = False



    def send(self):
        if self.serial_connected:
            serial_data = self.serial_send_input.text()
            self.serial.write(serial_data.encode())
            self.serial_send_input.clear()

   

    def read_serial(self):
        try:
            if self.serial and self.serial.in_waiting > 0:
                # Read serial_data from serial serial_port
                serial_data = self.serial.readline().decode().strip()
                serial_pattern = r'\033\[[0-9;]*m'  # Pattern to remove escape sequences
                serial_data = re.sub(serial_pattern, '', serial_data)
                # Append serial_data to serial_console
                self.serial_console.append(serial_data)
        except Exception as e:
            self.serial_console.append(f"Error Occured {e}")
            self.serial_s_timer.stop()
            self.serial.close()
            self.serial=None
            self.serial_p_timer.start(1000)
            self.serial_connect_button.setText("Connect")
            self.serial_connected = False
            # self.connect_or_disconnect()

    def clear_console(self):
        self.serial_console.clear()
    
    def filter_console(self):
        # Filter serial_console based on entered serial_pattern
        serial_pattern = self.serial_filter_pattern.text()
        if serial_pattern:
            serial_pattern = f'.*{serial_pattern}.*'  # Add .* at the beginning and end to match anywhere in the line
            serial_filtered_text = self.serial_console.toPlainText()
            serial_filtered_lines = []
            for line in serial_filtered_text.split('\n'):
                if re.search(serial_pattern, line):
                    serial_filtered_lines.append(line)
            serial_filtered_text = '\n'.join(serial_filtered_lines)
            self.serial_console.setPlainText(serial_filtered_text)

    def closeEvent(self, event):
        # Terminate the process if the window is closed
        if self.http_process.state() != QProcess.ProcessState.NotRunning:
            self.http_process.terminate()
            self.http_process.waitForFinished()
        super().closeEvent(event)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
