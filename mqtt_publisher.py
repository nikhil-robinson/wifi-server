import paho.mqtt.client as mqtt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("MQTT Publisher")
        self.setGeometry(100, 100, 300, 150)

        # Create the widgets
        self.url_label = QLabel("Broker URL:")
        self.url_edit = QLineEdit()
        self.topic_label = QLabel("Topic:")
        self.topic_edit = QLineEdit()
        self.data_label = QLabel("Data:")
        self.data_edit = QLineEdit()
        self.publish_button = QPushButton("Publish")
        self.publish_button.clicked.connect(self.publish)

        # Create the layout and add the widgets
        layout = QVBoxLayout()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_edit)
        layout.addWidget(self.topic_label)
        layout.addWidget(self.topic_edit)
        layout.addWidget(self.data_label)
        layout.addWidget(self.data_edit)
        layout.addWidget(self.publish_button)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def publish(self):
        # Get the input values
        broker_url = self.url_edit.text()
        if ':' in broker_url:
            ip, port = broker_url.split(':')
            print(port,ip)

        topic = self.topic_edit.text()
        data = self.data_edit.text()

        # Create an MQTT client and connect to the broker
        client = mqtt.Client()
        client.connect(ip,int(port))

        # Publish the message to the topic
        client.publish(topic, data)

        # Disconnect from the broker
        client.disconnect()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
