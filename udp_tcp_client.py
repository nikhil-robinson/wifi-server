from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit, QFormLayout,QHBoxLayout
from PyQt6.QtCore import Qt, QIODevice, QByteArray
from PyQt6.QtNetwork import QUdpSocket, QTcpSocket, QAbstractSocket

class NetworkClientApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set up UI components
        self.protocol_combobox = QComboBox()
        self.protocol_combobox.addItem('UDP')
        self.protocol_combobox.addItem('TCP')

        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("IP Address")
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText("PORT")

        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connect_to_server)

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
        if self.socket is not None and self.socket.isOpen():
            self.socket.close()

        protocol = self.protocol_combobox.currentText()
        url = self.ip_edit.text()
        port = self.ip_edit.text()
        print(f'connectint to {url} : {port}')

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
