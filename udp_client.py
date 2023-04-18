import sys
from PyQt6.QtCore import QByteArray
from PyQt6.QtGui import QTextCursor, QTextDocument
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton

from PyQt6.QtNetwork import QUdpSocket, QHostAddress

class UDPClient(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up window properties
        self.setWindowTitle("UDP Client")
        self.setFixedSize(500, 400)

        # Create widgets
        self.message_history = QTextEdit()
        self.message_history.setReadOnly(True)
        self.message_entry = QLineEdit()
        self.send_button = QPushButton("Send")

        # Set up layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        message_label = QLabel("Message history:")
        layout.addWidget(message_label)
        layout.addWidget(self.message_history)

        entry_layout = QHBoxLayout()
        entry_label = QLabel("Enter message:")
        entry_layout.addWidget(entry_label)
        entry_layout.addWidget(self.message_entry)
        entry_layout.addWidget(self.send_button)
        layout.addLayout(entry_layout)

        # Set up UDP socket
        self.udp_socket = QUdpSocket(self)
        self.udp_socket.readyRead.connect(self.receive_message)
        self.send_button.clicked.connect(self.send_message)

    def send_message(self):
        message = self.message_entry.text().encode()
        self.udp_socket.writeDatagram(message, QHostAddress("127.0.0.1"), 12345)

        # Clear the message entry and move cursor to end of message history
        self.message_entry.clear()
        self.message_entry.setFocus()
        self.message_history.moveCursor(QTextCursor.MoveOperation.End)

        # Append message to message history
        self.message_history.append(f">>> {message.decode()}")

    def receive_message(self):
        while self.udp_socket.hasPendingDatagrams():
            datagram, host, port = self.udp_socket.readDatagram(self.udp_socket.pendingDatagramSize())
            message = QByteArray(datagram).data().decode()
            self.message_history.append(f"<<< {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UDPClient()
    window.show()
    sys.exit(app.exec())
