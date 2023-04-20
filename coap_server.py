import sys
import asyncio
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import QObject, pyqtSignal
from aiocoap.resource import Resource
from aiocoap import Context, Message, Code, CONTENT

class CoapResource(Resource):
    def __init__(self, name="CoapResource"):
        super().__init__()
        self.name = name
        self.payload = b'Hello, CoAP from PyQt6!'

    async def render_get(self, request):
        response = Message(code=CONTENT, payload=self.payload)
        return response

class Ui_MainWindow(QObject):
    coap_signal = pyqtSignal(str)

    def setupUi(self, main_window):
        self.main_window = main_window

        self.centralwidget = QWidget(self.main_window)
        self.centralwidget.setObjectName("centralwidget")

        self.ip_label = QLabel(self.centralwidget)
        self.ip_label.setGeometry(50, 50, 100, 30)
        self.ip_label.setText("IP address:")

        self.ip_edit = QLineEdit(self.centralwidget)
        self.ip_edit.setGeometry(150, 50, 150, 30)

        self.port_label = QLabel(self.centralwidget)
        self.port_label.setGeometry(50, 100, 100, 30)
        self.port_label.setText("Port number:")

        self.port_edit = QLineEdit(self.centralwidget)
        self.port_edit.setGeometry(150, 100, 150, 30)

        self.resource_label = QLabel(self.centralwidget)
        self.resource_label.setGeometry(50, 150, 100, 30)
        self.resource_label.setText("Resource name:")

        self.resource_edit = QLineEdit(self.centralwidget)
        self.resource_edit.setGeometry(150, 150, 150, 30)

        self.start_button = QPushButton(self.centralwidget)
        self.start_button.setGeometry(100, 200, 100, 30)
        self.start_button.setText("Start server")
        self.start_button.clicked.connect(self.start_server)

        self.coap_signal.connect(self.handle_request)

        self.main_window.setCentralWidget(self.centralwidget)

    async def start_server(self):
        ip = self.ip_edit.text()
        port = int(self.port_edit.text())
        resource_name = self.resource_edit.text()

        root = Resource()
        root.add_resource((resource_name,), CoapResource())

        site = Context().create_server_context(root)

        await site.listen(('::', port))

    def handle_request(self, request):
        self.coap_signal.emit(request.payload.decode('utf-8'))

app = QApplication(sys.argv)

# create a QMainWindow instance
main_window = QMainWindow()

# create an instance of the Ui_MainWindow class and set its user interface to the QMainWindow instance
ui = Ui_MainWindow()
ui.setupUi(main_window)

# show the QMainWindow instance
main_window.show()

sys.exit(await app.exec())
