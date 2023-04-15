from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QIODevice, QByteArray
from PyQt6.QtNetwork import QUdpSocket, QTcpSocket, QAbstractSocket

class NetworkClientApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set up UI components
        self.protocol_label = QLabel('Protocol:')
        self.protocol_combobox = QComboBox()
        self.protocol_combobox.addItem('UDP')
        self.protocol_combobox.addItem('TCP')

        self.url_label = QLabel('Server Link:')
        self.url_edit = QLineEdit()

        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connect_to_server)

        self.send_label = QLabel('Send Data:')
        self.send_edit = QLineEdit()

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_data)

        self.console = QTextEdit()
        self.console.setReadOnly(True)

        # Set up layout
        self.layout = QVBoxLayout()

        protocol_layout = QHBoxLayout()
        protocol_layout.addWidget(self.protocol_label)
        protocol_layout.addWidget(self.protocol_combobox)

        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_edit)

        send_layout = QHBoxLayout()
        send_layout.addWidget(self.send_label)
        send_layout.addWidget(self.send_edit)
        send_layout.addWidget(self.send_button)

        self.layout.addLayout(protocol_layout)
        self.layout.addLayout(url_layout)
        self.layout.addWidget(self.connect_button)
        self.layout.addLayout(send_layout)
        self.layout.addWidget(self.console)

        self.setLayout(self.layout)

        self.socket = None

    def connect_to_server(self):
        if self.socket is not None and self.socket.isOpen():
            self.socket.close()

        protocol = self.protocol_combobox.currentText()
        url = self.url_edit.text()
        port = int(url.split(':')[-1])

        if protocol == 'UDP':
            self.socket = QUdpSocket()
            self.socket.readyRead.connect(self.receive_udp_data)
            self.socket.errorOccurred.connect(self.handle_socket_error)
        elif protocol == 'TCP':
            self.socket = QTcpSocket()
            self.socket.readyRead.connect(self.receive_tcp_data)
            self.socket.errorOccurred.connect(self.handle_socket_error)

        self.socket.connectToHost(url, port)

    def send_data(self):
        if self.socket is None or not self.socket.isOpen():
            self.log_message('Error: Socket is not connected.')
            return

        data = self.send_edit.text()
        if self.protocol_combobox.currentText() == 'UDP':
            self.socket.writeDatagram(data.encode(), self.socket.peerAddress(), self.socket.peerPort())
        elif self.protocol_combobox.currentText() == 'TCP':
            self.socket.write(data.encode())

    def receive_udp_data(self):
        while self.socket.hasPendingDatagrams():
            data, host, port = self.socket.readDatagram(self.socket.pendingDatagramSize())
            self.log_message(f'Received UDP data from {host.toString()}:{port}: {data.decode()}')

    def receive_tcp_data(self):
        data = self.socket.readAll().data().decode()
        self.log_message(f'Received TCP data: {data}')

    def handle_socket_error(self, socket_error):
        self.log_message(f'Socket error occurred: {self.socket.errorString()}')

    def log_message(self, message):
        self.console.append(message)

if __name__ == '__main__':
    app = QApplication([])
    window = NetworkClientApp()
    window.show()
    app.exec()
