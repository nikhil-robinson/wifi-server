from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QGroupBox, QHBoxLayout

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the main window
        main_layout = QHBoxLayout()

        # Create a group box for the left sidebar
        left_bar_group = QGroupBox("Tools")
        left_bar_group_layout = QVBoxLayout()
        left_bar_group.setLayout(left_bar_group_layout)

        # Create buttons for the left sidebar
        server_button = QPushButton("Server")
        client_button = QPushButton("Client")
        serial_button = QPushButton("Serial")
        network_button = QPushButton("Network")
        security_button = QPushButton("Security")
        about_button = QPushButton("About")

        # Add buttons to the left sidebar group box
        left_bar_group_layout.addWidget(server_button)
        left_bar_group_layout.addWidget(client_button)
        left_bar_group_layout.addWidget(serial_button)
        left_bar_group_layout.addWidget(network_button)
        left_bar_group_layout.addWidget(security_button)
        left_bar_group_layout.addWidget(about_button)

        # Create a label for the right side text
        right_text = QLabel("This is the default text.")

        # Add the left sidebar and right text to the main layout
        main_layout.addWidget(left_bar_group)
        main_layout.addWidget(right_text)

        # Set the main layout as the central widget
        central_widget.setLayout(main_layout)

        # Connect the buttons to their respective functions
        server_button.clicked.connect(self.on_serverButton_clicked)
        client_button.clicked.connect(self.on_clientButton_clicked)
        serial_button.clicked.connect(self.on_serialButton_clicked)

        # Set the window properties
        self.setWindowTitle("PyQt6 App")
        self.setGeometry(100, 100, 1000, 600)
        self.show()

    def on_serverButton_clicked(self):
        print("Server button clicked")

    def on_clientButton_clicked(self):
        print("Client button clicked")

    def on_serialButton_clicked(self):
        print("Serial button clicked")

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
