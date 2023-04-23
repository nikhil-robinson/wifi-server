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

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt6.QtNetwork import QUdpSocket

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit, QFormLayout,QHBoxLayout
from PyQt6.QtCore import Qt, QRegularExpression, QRegularExpressionMatch, QByteArray
from PyQt6.QtNetwork import QUdpSocket, QTcpSocket, QAbstractSocket,QHostAddress
from PyQt6.QtGui import QRegularExpressionValidator

import http.server
import socketserver
import os

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
        try:
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
            self.client_conf()

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
            self.stacked_widget.addWidget(self.client_form_widget)
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
            self.setWindowTitle("MBOX V1.0 Beta")
            self.setGeometry(100, 100, 1000, 600)
            self.show()
        except Exception as e:
            fh.exception(e)

    def serverConf(self):
        try:
            # Create the layout for the form
            self.server_form_widget = QWidget()
            self.server_form_layout = QFormLayout()
            self.server_form_widget.setLayout(self.server_form_layout)

            # Create the input fields for the form
            self.server_type_combo = QComboBox()
            self.server_type_combo.addItems(["--Select Server--","HTTP", "UDP", "TCP","MQTT"])
            self.server_type_combo.setCurrentIndex(0)
            self.server_type_combo.currentIndexChanged.connect(self.server_combo_box_changed)
            # self.server_type_combo.currentIndexChanged.connect(self.handle_server_type_change)

            self.server_port_input = QLineEdit()
            self.server_port_input.setPlaceholderText("Enter Port Number")

            self.server_ip_label =QLabel("IP :")
            self.server_port_label =QLabel("Port :")

            self.server_ip_input = QLineEdit()
            self.server_ip_input.setPlaceholderText("Enter ip address")
            self.server_ip_input.setText("127.0.0.1")

            self.server_address_bar = QHBoxLayout()
            self.server_address_bar.addWidget(self.server_ip_label)
            self.server_address_bar.addWidget(self.server_ip_input)
            self.server_address_bar.addWidget(self.server_port_label)
            self.server_address_bar.addWidget(self.server_port_input)


            self.server_send_data = QLineEdit()
            self.server_send_data.setPlaceholderText("Enter server response")


            server_port_regex = QRegularExpression("^[0-9]{1,5}$")
            server_ip_regex = QRegularExpression("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")

            server_port_validator = QRegularExpressionValidator(server_port_regex, self.server_port_input)
            self.server_port_input.setValidator(server_port_validator)

            server_ip_validator = QRegularExpressionValidator(server_ip_regex, self.server_ip_input)
            self.server_ip_input.setValidator(server_ip_validator)


            self.create_server_button = QPushButton("Start Server")
            self.create_server_button.clicked.connect(self.create_server)

            # Add the input fields to the form layout
            self.server_form_layout.addRow(self.server_type_combo)
            self.server_form_layout.addRow(self.server_address_bar)
            self.server_form_layout.addRow(self.server_send_data)
            self.server_form_layout.addRow(self.create_server_button)

            self.server_ip_input.setEnabled(False)
            self.server_port_input.setEnabled(False)
            self.server_send_data.setEnabled(False)
            self.create_server_button.setEnabled(False)
            # Create the log window
            self.server_console = QTextEdit()
            self.server_console.setReadOnly(True)
            self.server_form_layout.addRow(self.server_console)



            server_log_handler = QTextEditHandler(self.server_console)
            logging.getLogger().addHandler(server_log_handler)
            logging.getLogger().setLevel(logging.DEBUG)
            self.server_http_process = None
            self.server_udp_socket =None
            self.isSERVERstarted = False
        except Exception as e:
            fh.exception(e)

    def server_combo_box_changed(self):
        try:
            selected_option = self.server_type_combo.currentText()
            if selected_option == "MQTT":
                self.server_ip_input.setEnabled(True)
                self.server_port_input.setEnabled(True)
                self.server_send_data.setEnabled(True)
                self.create_server_button.setEnabled(True)
                self.server_send_data.setPlaceholderText("Enter topic and data seprated by ':' eg: topic:data")
            elif selected_option == "HTTP":
                self.server_ip_input.setEnabled(True)
                self.server_port_input.setEnabled(True)
                self.server_send_data.setEnabled(True)
                self.create_server_button.setEnabled(True)
                self.server_send_data.setPlaceholderText("Enter path for files (.html,.js)")
            elif selected_option == "UDP" or selected_option == "TCP":
                self.server_ip_input.setEnabled(True)
                self.server_port_input.setEnabled(True)
                self.server_send_data.setEnabled(True)
                self.create_server_button.setEnabled(True)
                self.server_send_data.setPlaceholderText("Enter server response")
            else:
                self.server_ip_input.setEnabled(False)
                self.server_port_input.setEnabled(False)
                self.server_send_data.setEnabled(False)
                self.create_server_button.setEnabled(False)
        except Exception as e:
            fh.exception(e)

    def start_http_server(self):
        try:
        # Start HTTP server on serial_port 80
            self.cwd = None
            if os.path.exists(self.server_send_data.text()) and self.server_send_data.text() !="":
                self.cwd =os.getcwd()
                os.chdir(self.server_send_data.text())
                logging.debug(f"Linking dir {self.server_send_data.text()}")

            self.server_http_process = QProcess(self)
            self.server_http_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
            self.server_http_process.readyReadStandardOutput.connect(self.http_handle_output)
            self.server_http_process.finished.connect(self.http_process_finished)
            self.server_http_process.start("python3", [ "-m", "http.server", self.server_port_input.text(), "--bind", self.server_ip_input.text()])
            self.create_server_button.setText("Stop Server")
            self.isSERVERstarted = True
        except Exception as e:
            fh.exception(e)
        
    def http_handle_output(self):
        try:
            # Log http_output from HTTP server to serial_console
            http_output = bytes(self.server_http_process.readAllStandardOutput()).decode()
            logging.debug(http_output)
        except Exception as e:
            fh.exception(e)

    def http_process_finished(self):
        try:
            # Destroy server_http_process and print message when finished
            self.server_http_process.terminate()
            self.server_http_process.waitForFinished()
            # logging.debug("HTTP server stopped")
            self.isSERVERstarted = False
            os.chdir(self.cwd)
        except Exception as e:
            fh.exception(e)

    def start_tcp_server(self):
        try:
            self.tcp_server = QTcpServer(self)
            self.tcp_server.listen(QHostAddress("127.0.0.1"), int(self.server_port_input.text()))  # Listen on localhost, port 5000
            self.tcp_server.newConnection.connect(self.tcp_server_handle_connection)
        except Exception as e:
            fh.exception(e)



    def tcp_receive_data(self):
        try:
            tcp_client_socket = self.sender()
            tcp_message = tcp_client_socket.readAll().data().decode('utf-8')
            self.server_console.append(f'Received message: {tcp_message} from {tcp_client_socket.peerAddress().toString()}:{tcp_client_socket.peerPort()}')
            tcp_client_socket.write(self.server_send_data.text().encode())
        except Exception as e:
            fh.exception(e)

    def tcp_client_disconnected(self):
        try:
            tcp_client_socket = self.sender()
            self.server_console.append(f'Client disconnected: {tcp_client_socket.peerAddress().toString()}:{tcp_client_socket.peerPort()}')
            tcp_client_socket.deleteLater()
        except Exception as e:
            fh.exception(e)

    def start_udp_server(self):
        try:
            self.server_udp_socket = QUdpSocket(self)
            self.server_udp_socket.bind(QHostAddress(self.server_ip_input.text()),int(self.server_port_input.text()))  # Bind to port
            self.server_udp_socket.readyRead.connect(self.udp_receive_data)
        except Exception as e:
            fh.exception(e)
    
    def udp_receive_data(self):
        try:
            while self.server_udp_socket.hasPendingDatagrams():
                server_udp_datagram, server_udp_host, server_udp_port = self.server_udp_socket.readDatagram(self.server_udp_socket.pendingDatagramSize())
                server_udp_message = bytes(server_udp_datagram).decode('utf-8')
                self.server_console.append(f'Received message: {server_udp_message} from {server_udp_host.toString()}:{server_udp_port}')
            self.server_udp_socket.writeDatagram(self.server_send_data.text().encode(), QHostAddress(server_udp_host), int(server_udp_port))
        except Exception as e:
            fh.exception(e)

    def tcp_server_handle_connection(self):
        try:
            while self.tcp_server.hasPendingConnections():
                tcp_server_client_socket = self.tcp_server.nextPendingConnection()
                self.server_console.append(f'Client Connected: {tcp_server_client_socket.peerAddress().toString()}:{tcp_server_client_socket.peerPort()}')
                tcp_server_client_socket.readyRead.connect(self.tcp_receive_data)
                tcp_server_client_socket.disconnected.connect(self.tcp_client_disconnected)
        except Exception as e:
            fh.exception(e)

    def create_server(self):
        try:
            if self.isSERVERstarted == False:
                if self.server_type_combo.currentText() == "--Select Server--" or self.server_ip_input.text() =="" or self.server_port_input.text() =="":
                    self.server_console.append("Please check your configuration")
                    return
                if self.server_type_combo.currentText() == "HTTP":
                    print("Http")
                    self.start_http_server()
                    self.isSERVERstarted = True
                    self.create_server_button.setText("Stop Server")
                    if self.server_http_process:
                        self.server_type_combo.setDisabled(True)
                        self.server_ip_input.setDisabled(True)
                        self.server_port_input.setDisabled(True)
                        self.server_send_data.setDisabled(True)
                    self.server_console.append(f"{self.server_type_combo.currentText()} Server created on {self.server_ip_input.text()}:{self.server_port_input.text()}")
                elif self.server_type_combo.currentText() == "TCP":
                    print("TCP")
                    self.start_tcp_server()
                    self.isSERVERstarted = True
                    self.create_server_button.setText("Stop Server")
                    if self.tcp_server:
                        self.server_type_combo.setDisabled(True)
                        self.server_ip_input.setDisabled(True)
                        self.server_port_input.setDisabled(True)
                    self.server_console.append(f"{self.server_type_combo.currentText()} Server created on {self.server_ip_input.text()}:{self.server_port_input.text()}")
                    
                elif self.server_type_combo.currentText() == "UDP":
                    print("UDP")
                    self.start_udp_server()
                    self.isSERVERstarted = True
                    self.create_server_button.setText("Stop Server")
                    if self.server_udp_socket:
                        self.server_type_combo.setDisabled(True)
                        self.server_ip_input.setDisabled(True)
                        self.server_port_input.setDisabled(True)
                    self.server_console.append(f"{self.server_type_combo.currentText()} Server created on {self.server_ip_input.text()}:{self.server_port_input.text()}")
                else:
                    self.server_console.append("Please select a server type")

            else:
                if self.server_http_process:
                    self.server_http_process.terminate()
                    self.server_http_process.waitForFinished()
                elif self.server_udp_socket:
                    self.server_udp_socket.deleteLater()
                elif self.tcp_server:
                    self.tcp_server.deleteLater()
                self.create_server_button.setText("Sart Server")
                self.isSERVERstarted = False
                self.server_type_combo.setDisabled(False)
                self.server_ip_input.setDisabled(False)
                self.server_port_input.setDisabled(False)
                self.server_send_data.setDisabled(False)
                self.server_console.append(f"{self.server_type_combo.currentText()} Server Stoped!")

        except Exception as e:
            fh.exception(e)

    
    def on_serverButton_clicked(self):
        #hellp
        try:
            self.stacked_widget.setCurrentWidget(self.server_form_widget)
        except Exception as e:
            fh.exception(e)

        
    
    def on_clientButton_clicked(self):
        try:
            self.stacked_widget.setCurrentWidget(self.client_form_widget)
        except Exception as e:
            fh.exception(e)
    
    def on_serialButton_clicked(self):
        try:
            self.stacked_widget.setCurrentWidget(self.serial_form_widget)
        except Exception as e:
            fh.exception(e)




    def serialConf(self):
        try:

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
        except Exception as e:
            fh.exception(e)

    def refresh_ports(self):
        try:
            serial_ports = [p.device for p in serial.tools.list_ports.comports()]
            self.serial_port_combo.clear()
            self.serial_port_combo.addItems(serial_ports)
            # time.sleep(1)
        except Exception as e:
            fh.exception(e)

    def connect_or_disconnect(self):
        try:
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
        except Exception as e:
            fh.exception(e)



    def send(self):
        try:
            if self.serial_connected:
                serial_data = self.serial_send_input.text()
                self.serial.write(serial_data.encode())
                self.serial_send_input.clear()
        except Exception as e:
            fh.exception(e)

   

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
            fh.exception(e)
            # self.connect_or_disconnect()

    def clear_console(self):
        try:
            self.serial_console.clear()
        except Exception as e:
            fh.exception(e)
    
    def filter_console(self):
        try:
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
        except Exception as e:
            fh.exception(e)





    def client_conf(self):
        try:

            self.client_protocol_combobox = QComboBox()
            self.client_protocol_combobox.addItem('UDP')
            self.client_protocol_combobox.addItem('TCP')
            self.client_protocol_combobox.activated.connect(self.on_client_combo_box_activated)


            self.client_ip_edit = QLineEdit()
            self.client_ip_edit.setPlaceholderText("IP Address")
            self.client_port_edit = QLineEdit()
            self.client_port_edit.setPlaceholderText("PORT")

            client_ip_regex = QRegularExpression("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
            client_port_regex = QRegularExpression("^[0-9]{1,5}$")

            client_ip_validator = QRegularExpressionValidator(client_ip_regex, self.client_ip_edit)
            self.client_ip_edit.setValidator(client_ip_validator)

            client_port_validator = QRegularExpressionValidator(client_port_regex, self.client_port_edit)
            self.client_port_edit.setValidator(client_port_validator)

            self.client_connect_button = QPushButton('Connect')
            self.client_connect_button.clicked.connect(self.client_connect_to_server)

            self.client_send_edit = QLineEdit()
            self.client_send_edit.setDisabled(True)

            self.client_send_button = QPushButton('Send')
            self.client_send_button.clicked.connect(self.client_send_data)
            self.client_send_button.setDisabled(True)

            self.client_console = QTextEdit()
            self.client_console.setReadOnly(True)

            self.client_link_layout = QHBoxLayout()
            self.client_link_layout.addWidget(self.client_protocol_combobox)
            # self.client_link_layout.addWidget(QLabel("IP :"))
            self.client_link_layout.addWidget(self.client_ip_edit)
            self.client_link_layout.addWidget(QLabel(":"))
            self.client_link_layout.addWidget(self.client_port_edit)
            self.client_link_layout.addWidget(self.client_connect_button)

            # Set up client_layout
            self.client_layout = QFormLayout()

            self.client_form_widget = QWidget()
            self.client_form_widget.setLayout(self.client_layout)

            # self.client_layout.addRow('Protocol:', self.client_protocol_combobox)
            self.client_layout.addRow(self.client_link_layout)
            # self.client_layout.addRow(self.client_connect_button)
            self.client_layout.addRow('Send Data:', self.client_send_edit)
            self.client_layout.addRow(self.client_send_button)
            self.client_layout.addRow(self.client_console)
            self.client_socket = None
        except Exception as e:
            fh.exception(e)

    def client_connect_to_server(self):
        try:
            client_protocol = self.client_protocol_combobox.currentText()
            if self.client_ip_edit.text() != "" and self.client_port_edit.text() != "":
                self.client_url = self.client_ip_edit.text()
                self.client_port = int(self.client_port_edit.text())

            else:
                self.log_message('Error: Check your IP and PORT number.')
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                return

            if self.client_socket is not None: 
                if self.client_socket.isOpen():
                    self.client_socket.close()
                self.client_socket = None
                self.client_connect_button.setText("Connect")
                self.client_protocol_combobox.setDisabled(False)
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)

            elif client_protocol == 'UDP':
                self.client_socket = QUdpSocket(self)
                self.client_socket.readyRead.connect(self.client_receive_data)
                self.client_socket.errorOccurred.connect(self.client_socket_display_error)
                if self.client_socket is not None:
                    self.client_send_edit.setDisabled(False)
                    self.client_send_button.setDisabled(False)
                    self.client_protocol_combobox.setDisabled(True)
                    self.client_connect_button.setText("Disconnect")
                else:
                    self.log_message('Error: Creating the socket.')
                    self.client_send_edit.setDisabled(True)
                    self.client_send_button.setDisabled(True)
                    self.client_socket =None
                    return

            elif client_protocol == 'TCP':
                self.client_socket = QTcpSocket()
                self.client_socket.readyRead.connect(self.client_receive_data)
                self.client_socket.errorOccurred.connect(self.client_socket_display_error)
                self.client_socket.connectToHost(self.client_url, self.client_port)
                if self.client_socket is not None and self.client_socket.isOpen():
                    self.client_send_edit.setDisabled(False)
                    self.client_send_button.setDisabled(False)
                    self.client_protocol_combobox.setDisabled(True)
                    self.client_connect_button.setText("Disconnect")
                else:
                    self.log_message('Error: Creating the socket.')
                    self.client_send_edit.setDisabled(True)
                    self.client_send_button.setDisabled(True)
                    self.client_socket =None
                    return
        except Exception as e:
            fh.exception(e)

    def client_send_data(self):
        try:
            if self.client_protocol_combobox.currentText() == 'UDP':
                print("UDP")
                client_message = self.client_send_edit.text().encode()
                self.client_socket.writeDatagram(client_message, QHostAddress(self.client_url), self.client_port)

            elif self.client_protocol_combobox.currentText() == 'TCP':
                if self.client_socket is None or not self.client_socket.isOpen():
                    self.log_message('Error: Socket is not connected.')
                    return
                client_message = self.client_send_edit.text().encode()
                self.client_socket.write(QByteArray(client_message))
                self.client_socket.flush()
        except Exception as e:
            fh.exception(e)


    def client_receive_data(self):
        try:
            if self.client_protocol_combobox.currentText() == 'UDP':
                while self.client_socket.hasPendingDatagrams():
                    client_udp_datagram, client_udp_host, client_udp_port = self.client_socket.readDatagram(self.client_socket.pendingDatagramSize())
                    client_udp_message = QByteArray(client_udp_datagram).data().decode()
                    self.log_message(f'Received UDP data: {client_udp_message}')

            elif self.client_protocol_combobox.currentText() == 'TCP':
                client_tcp_data = self.client_socket.readAll().data().decode()
                self.log_message(f'Received TCP data: {client_tcp_data}')
        except Exception as e:
                fh.exception(e)


    def log_message(self, client_message):
        try:
            self.client_console.append(client_message)
        except Exception as e:
                fh.exception(e)
    

    def on_client_combo_box_activated(self, index):
        try:
            combo_box = self.sender()  # Get the sender of the signal
            client_selected_option = combo_box.itemText(index)  # Get the text of the selected item
            print(f"Activated: {client_selected_option}")
            self.client_send_edit.setDisabled(True)
            self.client_send_button.setDisabled(True)
        except Exception as e:
                fh.exception(e)
    
    def client_socket_display_error(self, client_socket_error):
        try:
            if client_socket_error == QAbstractSocket.SocketError.ConnectionRefusedError:
                self.client_console.append("Error: Connection refused. Make sure the server is running.")
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                
            elif client_socket_error == QAbstractSocket.SocketError.HostNotFoundError:
                self.client_console.append("Error: Host not found. Please check the server IP address.")
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                
            elif client_socket_error == QAbstractSocket.SocketError.SocketTimeoutError:
                self.client_console.append("Error: Connection timed out.")
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
                
            else:
                self.client_console.append(f"Error: {self.client_socket.errorString()}")
                self.client_send_edit.setDisabled(True)
                self.client_send_button.setDisabled(True)
        except Exception as e:
                fh.exception(e)
            


    def closeEvent(self, event):
        try:
            # Terminate the process if the window is closed
            if self.server_http_process:
                if self.server_http_process.state() != QProcess.ProcessState.NotRunning:
                    self.server_http_process.terminate()
                    self.server_http_process.waitForFinished()
            super().closeEvent(event)
        except Exception as e:
            fh.exception(e)



if __name__ == "__main__":
    fh = logging.FileHandler("mbox.log")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logging.getLogger().addHandler(fh)
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
