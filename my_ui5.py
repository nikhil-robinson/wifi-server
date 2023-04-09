import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, QSplitter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create the left side bar group box
        self.left_bar_group = QGroupBox("Side Bar")
        self.left_bar_group_layout = QVBoxLayout()
        self.left_bar_group.setLayout(self.left_bar_group_layout)
        self.left_bar_layout.setSpacing(0)  # Set the vertical spacing to 0
        self.left_bar_layout.setAlignment(Qt.AlignTop)  # Align the buttons to the top
        
        
        # Create the buttons
        self.button1 = QPushButton("Button 1")
        self.button2 = QPushButton("Button 2")
        self.button3 = QPushButton("Button 3")
        
        # Add the buttons to the left side bar group box
        self.left_bar_group_layout.addWidget(self.button1)
        self.left_bar_group_layout.addWidget(self.button2)
        self.left_bar_group_layout.addWidget(self.button3)
        
        # Connect the buttons to their respective functions
        self.button1.clicked.connect(self.on_button1_clicked)
        self.button2.clicked.connect(self.on_button2_clicked)
        self.button3.clicked.connect(self.on_button3_clicked)
        
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
        self.setGeometry(100, 100, 400, 300)
        self.show()
    
    def on_button1_clicked(self):
        self.right_text.setText("This is text for button 1.")
    
    def on_button2_clicked(self):
        self.right_text.setText("This is text for button 2.")
    
    def on_button3_clicked(self):
        self.right_text.setText("This is text for button 3.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
