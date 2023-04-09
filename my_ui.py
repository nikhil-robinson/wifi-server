import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QButtonGroup, QHBoxLayout, QRadioButton
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, QSplitter


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
        
        # Create the left side bar group box
        self.left_bar_group = QGroupBox("Tools")
        self.left_bar_group_layout = QVBoxLayout()
        self.left_bar_group.setLayout(self.left_bar_group_layout)

        
        
        # Create the buttons
        self.serverButton = QPushButton("Server")
        self.clientButton = QPushButton("Client")
        self.serialButton = QPushButton("Button 3")
        self.networkButton = QPushButton("Button 4")
        self.securityButton = QPushButton("Button 5")
        self.aboutButton = QPushButton("Button 6")
        
        # Add the buttons to the left side bar group box
        self.left_bar_group_layout.addWidget(self.serverButton)
        self.left_bar_group_layout.addWidget(self.clientButton)
        self.left_bar_group_layout.addWidget(self.serialButton)

        self.left_bar_group_layout.addWidget(self.networkButton)
        self.left_bar_group_layout.addWidget(self.securityButton)
        self.left_bar_group_layout.addWidget(self.aboutButton)
        
        # Connect the buttons to their respective functions
        self.serverButton.clicked.connect(self.on_serverButton_clicked)
        self.clientButton.clicked.connect(self.on_clientButton_clicked)
        self.serialButton.clicked.connect(self.on_serialButton_clicked)
        
        # Create the right side text
        self.right_text = QLabel("This is the default text.")
        self.serverConf()
        
        # Create the main layout
        self.main_layout = QHBoxLayout()
        
        # Create a splitter to separate the sidebar from the main window
        self.splitter = QSplitter()
        self.splitter.addWidget(self.left_bar_group)
        self.splitter.addWidget(self.form_widget)
        self.splitter.setSizes([100, 300])
        self.main_layout.addWidget(self.splitter)
        
        # Set the main layout as the central widget
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        
        # Set the window properties
        self.setWindowTitle("PyQt6 App")
        self.setGeometry(100, 100, 500, 300)
        self.show()

    def serverConf(self):
        # Create the layout for the form
        self.form_widget = QWidget()
        self.form_layout = QFormLayout()
        self.form_widget.setLayout(self.form_layout)

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
        self.form_layout.addRow(QLabel(""), self.console)



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

    
    def on_serverButton_clicked(self):
        self.right_text.setText("This is text for button 1.")
    
    def on_clientButton_clicked(self):
        self.right_text.setText("This is text for button 2.")
    
    def on_serialButton_clicked(self):
        self.right_text.setText("This is text for button 3.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
