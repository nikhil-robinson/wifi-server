from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit, QFormLayout,QHBoxLayout
from PyQt6.QtCore import Qt, QIODevice, QByteArray
from PyQt6.QtNetwork import QUdpSocket, QTcpSocket, QAbstractSocket
import socket

class NetworkClientApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set up UI components
        self.protocol_combobox = QComboBox()
        self.protocol_combobox.addItem('UDP')
        self.protocol_combobox.addItem('TCP')
        self.protocol_combobox.activated.connect(self.on_combo_box_activated)


        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("IP Address")
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText("PORT")

        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connect_to_server)
        self.connect_button.setDisabled(True)

        self.send_edit = QLineEdit()

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_data)

        self.console = QTextEdit()
        self.console.setReadOnly(True)

        self.link_layout = QHBoxLayout()
        self.link_layout.addWidget(self.protocol_combobox)
        # self.link_layout.addWidget(QLabel("IP :"))
        self.link_layout.addWidget(self.ip_edit)
        self.link_layout.addWidget(QLabel(":"))
        self.link_layout.addWidget(self.port_edit)
        self.link_layout.addWidget(self.connect_button)

        # Set up layout
        self.layout = QFormLayout()

        # self.layout.addRow('Protocol:', self.protocol_combobox)
        self.layout.addRow(self.link_layout)
        # self.layout.addRow(self.connect_button)
        self.layout.addRow('Send Data:', self.send_edit)
        self.layout.addRow(self.send_button)
        self.layout.addRow(self.console)

        self.setLayout(self.layout)

        self.socket = None

    def connect_to_server(self):
        protocol = self.protocol_combobox.currentText()
        url = self.ip_edit.text()
        port = int(self.port_edit.text())
        print(f'connectint to {url} : {port}')

        if protocol == 'UDP':
            # self.socket = QUdpSocket()
            # self.socket.readyRead.connect(self.receive_udp_data)
            # self.socket.errorOccurred.connect(self.handle_socket_error)
            return
        elif protocol == 'TCP':
            self.tcp_socket = QTcpSocket()
            self.tcp_socket.readyRead.connect(self.receive_tcp_data)
            self.tcp_socket.errorOccurred.connect(self.socket_display_error)
            self.tcp_socket.connectToHost(url, port)

    def send_data(self):
        if self.protocol_combobox.currentText() == 'UDP':
            if self.udp_socket is None or not self.udp_socket.isOpen():
                self.log_message('Error: Socket is not connected.')
                return
            server_address = self.ip_edit.text()
            server_port = int(self.ip_edit.text())
            message = self.send_edit.text()

            # Create a UDP socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Send message to the server
            client_socket.sendto(message.encode(), (server_address, server_port))

            # Receive response from the server
            response, server_address = client_socket.recvfrom(1024)

            # Process the response (e.g. display it on the UI)
            # ...

            # Close the socket
            client_socket.close()
        elif self.protocol_combobox.currentText() == 'TCP':
            if self.tcp_socket is None or not self.tcp_socket.isOpen():
                self.log_message('Error: Socket is not connected.')
                return
            message = self.send_edit.text().encode()
            self.tcp_socket.write(QByteArray(message))
            self.tcp_socket.flush()

    def receive_udp_data(self):
        while self.socket.hasPendingDatagrams():
            data, host, port = self.socket.readDatagram(self.socket.pendingDatagramSize())
            self.log_message(f'Received UDP data from {host.toString()}:{port}: {data.decode()}')

    def receive_tcp_data(self):
        data = self.tcp_socket.readAll().data().decode()
        self.log_message(f'Received TCP data: {data}')

    def handle_socket_error(self, socket_error):
        self.log_message(f'Socket error occurred: {self.socket.errorString()}')

    def log_message(self, message):
        self.console.append(message)
    

    def on_combo_box_activated(self, index):
        combo_box = self.sender()  # Get the sender of the signal
        selected_option = combo_box.itemText(index)  # Get the text of the selected item
        print(f"Activated: {selected_option}")
        if selected_option == "UDP":
            self.connect_button.setDisabled(True)
        elif selected_option == "TCP":
            self.connect_button.setDisabled(False)
    
    def socket_display_error(self, socket_error):
        if socket_error == QAbstractSocket.SocketError.ConnectionRefusedError:
            self.console.append("Error: Connection refused. Make sure the server is running.")
        elif socket_error == QAbstractSocket.SocketError.HostNotFoundError:
            self.console.append("Error: Host not found. Please check the server IP address.")
        elif socket_error == QAbstractSocket.SocketError.SocketTimeoutError:
            self.console.append("Error: Connection timed out.")
        else:
            self.console.append(f"Error: {self.tcp_socket.errorString()}")



if __name__ == '__main__':
    app = QApplication([])
    window = NetworkClientApp()
    window.show()
    app.exec()
