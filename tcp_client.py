import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget
from PyQt6.QtCore import Qt, QIODevice, QByteArray
from PyQt6.QtNetwork import QTcpSocket, QAbstractSocket


class TcpClient(QMainWindow):
    def __init__(self):
        super().__init__()

        # UI setup
        self.setWindowTitle("TCP Client")
        self.setGeometry(100, 100, 400, 300)

        self.server_ip_input = QLineEdit()
        self.server_ip_input.setPlaceholderText("Enter Server IP Address")

        self.send_data_input = QTextEdit()
        self.send_data_input.setPlaceholderText("Enter Data to Send")

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_server)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_data)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        central_widget = QVBoxLayout()
        central_widget.addWidget(QLabel("Server IP:"))
        central_widget.addWidget(self.server_ip_input)
        central_widget.addWidget(QLabel("Data to Send:"))
        central_widget.addWidget(self.send_data_input)
        central_widget.addWidget(self.connect_button)
        central_widget.addWidget(self.send_button)
        central_widget.addWidget(QLabel("Log:"))
        central_widget.addWidget(self.log_output)

        main_widget = QWidget()
        main_widget.setLayout(central_widget)
        self.setCentralWidget(main_widget)

        # TCP socket setup
        self.tcp_socket = QTcpSocket()
        self.tcp_socket.readyRead.connect(self.receive_data)
        self.tcp_socket.errorOccurred.connect(self.display_error)

    def connect_to_server(self):
        if self.tcp_socket.state() == QAbstractSocket.SocketState.ConnectedState:
            self.tcp_socket.disconnectFromHost()

        server_ip = self.server_ip_input.text()
        if server_ip:
            self.tcp_socket.connectToHost(server_ip, 12345)

    def send_data(self):
        data = self.send_data_input.toPlainText().encode()
        self.tcp_socket.write(QByteArray(data))
        self.tcp_socket.flush()

    def receive_data(self):
        data = self.tcp_socket.readAll().data().decode()
        self.log_output.append(f"Received: {data}")

    def display_error(self, socket_error):
        if socket_error == QAbstractSocket.SocketError.ConnectionRefusedError:
            self.log_output.append("Error: Connection refused. Make sure the server is running.")
        elif socket_error == QAbstractSocket.SocketError.HostNotFoundError:
            self.log_output.append("Error: Host not found. Please check the server IP address.")
        elif socket_error == QAbstractSocket.SocketError.SocketTimeoutError:
            self.log_output.append("Error: Connection timed out.")
        else:
            self.log_output.append(f"Error: {self.tcp_socket.errorString()}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = TcpClient()
    client.show()
    sys.exit(app.exec())
