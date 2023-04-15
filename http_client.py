from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

class HttpClientApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set up UI components
        self.method_label = QLabel('Method:')
        self.method_combobox = QComboBox()
        self.method_combobox.addItem('GET')
        self.method_combobox.addItem('POST')

        self.url_label = QLabel('Server Link:')
        self.url_edit = QLineEdit()

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_request)

        # Set up layout
        self.layout = QVBoxLayout()

        method_layout = QHBoxLayout()
        method_layout.addWidget(self.method_label)
        method_layout.addWidget(self.method_combobox)

        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_edit)

        self.layout.addLayout(method_layout)
        self.layout.addLayout(url_layout)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)

        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.handle_reply)

    def send_request(self):
        method = self.method_combobox.currentText()
        url = self.url_edit.text()

        request = QNetworkRequest()
        request.setUrl(url)

        if method == 'GET':
            self.manager.get(request)
        elif method == 'POST':
            self.manager.post(request, b'')

    def handle_reply(self, reply):
        if reply.error():
            print(f'Request failed: {reply.errorString()}')
        else:
            print(f'Response: {reply.readAll().data().decode()}')

if __name__ == '__main__':
    app = QApplication([])
    window = HttpClientApp()
    window.show()
    app.exec()
