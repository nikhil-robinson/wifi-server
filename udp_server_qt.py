import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt6.QtNetwork import QUdpSocket

class UDPServer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.socket = QUdpSocket(self)
        self.socket.bind(5000)  # Bind to port 5000

        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)

        self.socket.readyRead.connect(self.receive_data)

    def receive_data(self):
        while self.socket.hasPendingDatagrams():
            datagram, host, port = self.socket.readDatagram(self.socket.pendingDatagramSize())
            message = bytes(datagram).decode('utf-8')
            self.text_edit.append(f'Received message: {message} from {host.toString()}:{port}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UDPServer()
    window.show()
    sys.exit(app.exec())
