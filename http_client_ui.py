import sys
import requests
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit


class HttpClient(QDialog):
    def __init__(self, parent=None):
        super(HttpClient, self).__init__(parent)

        # Create UI elements
        self.url_label = QLabel("URL:")
        self.url_edit = QLineEdit()
        self.get_button = QPushButton("GET")
        self.post_button = QPushButton("POST")
        self.response_label = QLabel("Response:")
        self.response_edit = QTextEdit()

        # Create layout
        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_edit)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.get_button)
        button_layout.addWidget(self.post_button)

        response_layout = QVBoxLayout()
        response_layout.addWidget(self.response_label)
        response_layout.addWidget(self.response_edit)

        main_layout = QVBoxLayout()
        main_layout.addLayout(url_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(response_layout)

        self.setLayout(main_layout)

        # Connect signals to slots
        self.get_button.clicked.connect(self.get_request)
        self.post_button.clicked.connect(self.post_request)

    def get_request(self):
        url = self.url_edit.text()
        response = requests.get(url)
        self.response_edit.setText(response.text)

    def post_request(self):
        url = self.url_edit.text()
        # params = self.param_edit.text()
        response = requests.post(url, data=url)
        self.response_edit.setText(response.text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = HttpClient()
    client.show()
    sys.exit(app.exec_())
