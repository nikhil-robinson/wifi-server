import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QButtonGroup, QHBoxLayout, QRadioButton
from PyQt6.QtCore import Qt, QProcess,QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator


class QTextEditHandler(logging.Handler):
    def __init__(self, server_console):
        super().__init__()
        self.server_console = server_console

    def emit(self, record):
        msg = self.format(record)
        self.server_console.append(msg)





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the layout for the form
        self.server_form_widget = QWidget()
        self.server_form_layout = QFormLayout()
        self.server_form_widget.setLayout(self.server_form_layout)

        # Create the input fields for the form
        self.server_type_combo = QComboBox()
        self.server_type_combo.addItems(["--Select Server--","HTTP", "UDP", "TCP","MQTT"])
        self.server_type_combo.setCurrentIndex(0)
        self.server_type_combo.currentIndexChanged.connect(self.server_combo_box_changed)
        # self.server_type_combo.currentIndexChanged.connect(self.handle_server_type_change)

        self.server_port_input = QLineEdit()
        self.server_port_input.setPlaceholderText("Enter Port Number")

        self.server_ip_label =QLabel("IP :")
        self.server_port_label =QLabel("Port :")

        self.server_ip_input = QLineEdit()
        self.server_ip_input.setPlaceholderText("Enter ip address")
        self.server_ip_input.setText("127.0.0.1")

        self.server_address_bar = QHBoxLayout()
        self.server_address_bar.addWidget(self.server_ip_label)
        self.server_address_bar.addWidget(self.server_ip_input)
        self.server_address_bar.addWidget(self.server_port_label)
        self.server_address_bar.addWidget(self.server_port_input)


        self.server_send_data = QLineEdit()
        self.server_send_data.setPlaceholderText("Enter server response")


        server_port_regex = QRegularExpression("^[0-9]{1,5}$")
        server_ip_regex = QRegularExpression("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")

        server_port_validator = QRegularExpressionValidator(server_port_regex, self.server_port_input)
        self.server_port_input.setValidator(server_port_validator)

        server_ip_validator = QRegularExpressionValidator(server_ip_regex, self.server_ip_input)
        self.server_ip_input.setValidator(server_ip_validator)


        self.create_server_button = QPushButton("Start Server")
        self.create_server_button.clicked.connect(self.create_server)

        # Add the input fields to the form layout
        self.server_form_layout.addRow(self.server_type_combo)
        self.server_form_layout.addRow(self.server_address_bar)
        self.server_form_layout.addRow(self.server_send_data)
        self.server_form_layout.addRow(self.create_server_button)
        # Create the log window
        self.server_console = QTextEdit()
        self.server_console.setReadOnly(True)
        self.server_form_layout.addRow(self.server_console)

        # Create the main layout
        # self.main_layout = QVBoxLayout()
        # self.main_layout.addLayout(self.server_form_layout)
        # self.main_layout.addWidget(self.server_console)

        # Set the main layout as the central widget
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.server_form_layout)
        self.setCentralWidget(self.central_widget)

        # Set the window properties
        self.setWindowTitle("PyQt6 App")
        self.setGeometry(100, 100, 400, 300)
        self.show()

        log_handler = QTextEditHandler(self.server_console)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.DEBUG)

    # def handle_server_type_change(self, index):
    #     # Retrieve the current selected server type
    #     self.server_type = self.server_type_combo.currentText()

    def server_combo_box_changed(self):
        selected_option = self.server_type_combo.currentText()
        if selected_option == "MQTT":
            self.server_send_data.setPlaceholderText("Enter topic and data seprated by : [topic:data]")
        elif selected_option == "HTTP":
            self.server_send_data.setPlaceholderText("Enter path for files (.html,.js)")
        elif selected_option == "UDP" or selected_option == "TCP":
            self.server_send_data.setPlaceholderText("Enter server response")

    def start_http_server(self):
        # Start HTTP server on port 80
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.finished.connect(self.process_finished)
        self.process.start("python3", ["-m", "http.server", "1111"])

    def handle_output(self):
        # Log output from HTTP server to server_console
        output = bytes(self.process.readAllStandardOutput()).decode()
        logging.debug(output)

    def process_finished(self):
        # Destroy process and print message when finished
        self.process.destroy()
        logging.debug("HTTP server stopped")

    def create_server(self):
        # TODO: Implement server creation logic
        server_host = "Local Host" if self.local_host_radio.isChecked() else "Ngrok"
        self.server_console.append(f"{self.server_type_combo.currentText()} Server created with {server_host} and port {self.port_input.text()}!")
        if self.server_type_combo.currentText() == "HTTP" and server_host == "Local Host":
            print("HI")
            self.start_http_server()
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
