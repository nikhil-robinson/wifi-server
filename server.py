import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QButtonGroup, QHBoxLayout, QRadioButton
from PyQt6.QtCore import Qt, QProcess


class QTextEditHandler(logging.Handler):
    def __init__(self, console):
        super().__init__()
        self.console = console

    def emit(self, record):
        msg = self.format(record)
        self.console.append(msg)




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the layout for the form
        self.form_layout = QFormLayout()

        # Create the input fields for the form
        self.server_type_combo = QComboBox()
        self.server_type_combo.addItems(["HTTP", "FTP", "SSH"])
        self.server_type_combo.setCurrentIndex(0)
        # self.server_type_combo.currentIndexChanged.connect(self.handle_server_type_change)

        self.port_input = QLineEdit()
        self.port_input.setText("8080")

        self.local_host_radio = QRadioButton("Local Host")
        self.ngrok_radio = QRadioButton("Ngrok")

        # Create a button group for the Local Host and Ngrok buttons
        self.host_button_group = QButtonGroup()
        self.host_button_group.addButton(self.local_host_radio)
        self.host_button_group.addButton(self.ngrok_radio)
        self.local_host_radio.setChecked(True)

        self.create_server_button = QPushButton("Create Server")
        self.create_server_button.clicked.connect(self.create_server)

        # Add the input fields to the form layout
        self.form_layout.addRow(QLabel("Server Type:"), self.server_type_combo)
        self.form_layout.addRow(QLabel("Port:"), self.port_input)

        # Create a horizontal layout for the Local Host and Ngrok buttons
        self.host_button_layout = QHBoxLayout()
        self.host_button_layout.addWidget(self.local_host_radio)
        self.host_button_layout.addWidget(self.ngrok_radio)
        self.form_layout.addRow(QLabel("Server Host:"), self.host_button_layout)

        self.form_layout.addRow(QLabel(""), self.create_server_button)

        # Create the log window
        self.console = QTextEdit()
        self.console.setReadOnly(True)

        # Create the main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addWidget(self.console)

        # Set the main layout as the central widget
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        # Set the window properties
        self.setWindowTitle("PyQt6 App")
        self.setGeometry(100, 100, 400, 300)
        self.show()

        log_handler = QTextEditHandler(self.console)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.DEBUG)

    # def handle_server_type_change(self, index):
    #     # Retrieve the current selected server type
    #     self.server_type = self.server_type_combo.currentText()

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

    def create_server(self):
        # TODO: Implement server creation logic
        server_host = "Local Host" if self.local_host_radio.isChecked() else "Ngrok"
        self.console.append(f"{self.server_type_combo.currentText()} Server created with {server_host} and port {self.port_input.text()}!")
        if self.server_type_combo.currentText() == "HTTP" and server_host == "Local Host":
            print("HI")
            self.start_http_server()
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
