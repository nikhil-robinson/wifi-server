import sys
import logging
import socket
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QIODevice, QRunnable, QThreadPool, QByteArray, QObject, pyqtSignal


class UdpServer(QObject):
    data_received = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('127.0.0.1', 9999))
        self.running = False

    def start(self):
        self.running = True
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                message = f"Received {data.decode()} from {addr[0]}:{addr[1]}"
                self.data_received.emit(message)
            except BlockingIOError:
                pass

    def stop(self):
        self.running = False
        self.socket.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up UI
        self.setWindowTitle("UDP Server")
        self.setMinimumSize(600, 400)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.setGeometry(10, 10, 80, 30)
        self.connect_button.clicked.connect(self.start_udp_server)

        self.console = QTextEdit(self)
        self.console.setGeometry(10, 50, 580, 340)
        self.console.setReadOnly(True)

        # Set up logging
        log_handler = QTextEditHandler(self.console)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.DEBUG)

        # Set up thread pool
        self.thread_pool = QThreadPool(self)
        self.thread_pool.setMaxThreadCount(1)

    def start_udp_server(self):
        self.connect_button.setDisabled(True)

        # Start UDP server in separate thread
        self.udp_server = UdpServer()
        self.udp_server_thread = QRunnableWrapper(self.udp_server.start)
        self.udp_server.data_received.connect(self.handle_output)
        self.thread_pool.start(self.udp_server_thread)

    def handle_output(self, message):
        # Log output from UDP server to console
        logging.debug(message)

    def closeEvent(self, event):
        # Stop UDP server when application is closed
        if hasattr(self, 'udp_server'):
            self.udp_server.stop()

    def enable_button(self):
        self.connect_button.setDisabled(False)


class QTextEditHandler(logging.Handler):
    def __init__(self, console):
        super().__init__()
        self.console = console

    def emit(self, record):
        msg = self.format(record)
        self.console.append(msg)


class QRunnableWrapper(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.function(*self.args, **self.kwargs)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
