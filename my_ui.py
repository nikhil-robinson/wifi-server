import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, QSplitter

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
        
        # Create the main layout
        self.main_layout = QHBoxLayout()
        
        # Create a splitter to separate the sidebar from the main window
        self.splitter = QSplitter()
        self.splitter.addWidget(self.left_bar_group)
        self.splitter.addWidget(self.right_text)
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
