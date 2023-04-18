from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit, QFormLayout,QHBoxLayout
from PyQt6.QtCore import Qt, QRegularExpression, QRegularExpressionMatch, QByteArray
from PyQt6.QtNetwork import QUdpSocket, QTcpSocket, QAbstractSocket,QHostAddress
from PyQt6.QtGui import QRegularExpressionValidator

class NetworkClientApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set up UI components
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

        # self.client_layout.addRow('Protocol:', self.client_protocol_combobox)
        self.client_layout.addRow(self.client_link_layout)
        # self.client_layout.addRow(self.client_connect_button)
        self.client_layout.addRow('Send Data:', self.client_send_edit)
        self.client_layout.addRow(self.client_send_button)
        self.client_layout.addRow(self.client_console)

        self.setLayout(self.client_layout)
        self.client_socket = None


    def client_connect_to_server(self):
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

    def client_send_data(self):
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


    def client_receive_data(self):
        if self.client_protocol_combobox.currentText() == 'UDP':
            while self.client_socket.hasPendingDatagrams():
                client_udp_datagram, client_udp_host, client_udp_port = self.client_socket.readDatagram(self.client_socket.pendingDatagramSize())
                client_udp_message = QByteArray(client_udp_datagram).data().decode()
                self.log_message(f'Received UDP data: {client_udp_message}')

        elif self.client_protocol_combobox.currentText() == 'TCP':
            client_tcp_data = self.client_socket.readAll().data().decode()
            self.log_message(f'Received TCP data: {client_tcp_data}')


    def log_message(self, client_message):
        self.client_console.append(client_message)
    

    def on_client_combo_box_activated(self, index):
        combo_box = self.sender()  # Get the sender of the signal
        client_selected_option = combo_box.itemText(index)  # Get the text of the selected item
        print(f"Activated: {client_selected_option}")
        self.client_send_edit.setDisabled(True)
        self.client_send_button.setDisabled(True)
    
    def client_socket_display_error(self, client_socket_error):
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
            



if __name__ == '__main__':
    app = QApplication([])
    window = NetworkClientApp()
    window.show()
    app.exec()
