import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QProcess


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up UI
        self.setWindowTitle("HTTP Server")
        self.setMinimumSize(600, 400)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.setGeometry(10, 10, 80, 30)
        self.connect_button.clicked.connect(self.start_http_server)

        self.console = QTextEdit(self)
        self.console.setGeometry(10, 50, 580, 340)
        self.console.setReadOnly(True)

        # Set up logging
        log_handler = QTextEditHandler(self.console)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.DEBUG)

    def start_http_server(self):
        # Start HTTP server on port 80
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.finished.connect(self.process_finished)
        self.process.start("python3", ["-m", "http.server", "1111"])

    def handle_output(self):
        # Log output from HTTP server to console
        output = bytes(self.process.readAllStandardOutput()).decode()
        logging.debug(output)

    def process_finished(self):
        # Destroy process and print message when finished
        self.process.destroy()
        logging.debug("HTTP server stopped")


class QTextEditHandler(logging.Handler):
    def __init__(self, console):
        super().__init__()
        self.console = console

    def emit(self, record):
        msg = self.format(record)
        self.console.append(msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
