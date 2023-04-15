import sys
import socket
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

class UdpClientApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the UI
        self.setWindowTitle("UDP Client")
        self.setGeometry(100, 100, 300, 200)

        # Widgets
        self.label_server_address = QLabel("Server Address:")
        self.edit_server_address = QLineEdit()
        self.label_server_port = QLabel("Server Port:")
        self.edit_server_port = QLineEdit()
        self.label_message = QLabel("Message:")
        self.edit_message = QLineEdit()
        self.btn_send = QPushButton("Send")
        self.btn_send.clicked.connect(self.send_message)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_server_address)
        layout.addWidget(self.edit_server_address)
        layout.addWidget(self.label_server_port)
        layout.addWidget(self.edit_server_port)
        layout.addWidget(self.label_message)
        layout.addWidget(self.edit_message)
        layout.addWidget(self.btn_send)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def send_message(self):
        # Get server address, port, and message from input fields
        server_address = self.edit_server_address.text()
        server_port = int(self.edit_server_port.text())
        message = self.edit_message.text()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UdpClientApp()
    window.show()
    sys.exit(app.exec())
