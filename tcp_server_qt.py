import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

class TCPServer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tcp_server = QTcpServer(self)
        self.tcp_server.listen(QHostAddress("127.0.0.1"), 5000)  # Listen on localhost, port 5000

        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)

        self.tcp_server.newConnection.connect(self.handle_connection)

    def handle_connection(self):
        while self.tcp_server.hasPendingConnections():
            tcp_client_socket = self.tcp_server.nextPendingConnection()
            tcp_client_socket.readyRead.connect(self.tcp_receive_data)
            tcp_client_socket.disconnected.connect(self.tcp_client_disconnected)

    def tcp_receive_data(self):
        tcp_client_socket = self.sender()
        message = tcp_client_socket.readAll().data().decode('utf-8')
        self.text_edit.append(f'Received message: {message} from {tcp_client_socket.peerAddress().toString()}:{tcp_client_socket.peerPort()}')

    def tcp_client_disconnected(self):
        tcp_client_socket = self.sender()
        self.text_edit.append(f'Client disconnected: {tcp_client_socket.peerAddress().toString()}:{tcp_client_socket.peerPort()}')
        tcp_client_socket.deleteLater()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TCPServer()
    window.show()
    sys.exit(app.exec())
