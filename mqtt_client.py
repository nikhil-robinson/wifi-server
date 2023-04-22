import sys
import paho.mqtt.client as mqtt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QTextEdit


class MQTTClient(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the user interface
        self.setWindowTitle("MQTT Client")
        self.resize(400, 300)

        # Broker settings
        broker_label = QLabel("Broker:")
        self.broker_input = QLineEdit()
        self.broker_input.setPlaceholderText("Enter broker address")

        port_label = QLabel("Port:")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter broker port")
        self.port_input.setText("1883")

        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.connect_to_broker)

        broker_layout = QHBoxLayout()
        broker_layout.addWidget(broker_label)
        broker_layout.addWidget(self.broker_input)
        broker_layout.addWidget(port_label)
        broker_layout.addWidget(self.port_input)
        broker_layout.addWidget(connect_button)

        broker_group = QWidget()
        broker_group.setLayout(broker_layout)

        # Subscription settings
        topic_label = QLabel("Topic:")
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Enter topic")

        subscribe_button = QPushButton("Subscribe")
        subscribe_button.clicked.connect(self.subscribe_to_topic)

        subscription_layout = QHBoxLayout()
        subscription_layout.addWidget(topic_label)
        subscription_layout.addWidget(self.topic_input)
        subscription_layout.addWidget(subscribe_button)

        subscription_group = QWidget()
        subscription_group.setLayout(subscription_layout)

        # Received message display
        message_label = QLabel("Received messages:")
        self.message_display = QTextEdit()

        message_layout = QVBoxLayout()
        message_layout.addWidget(message_label)
        message_layout.addWidget(self.message_display)

        message_group = QWidget()
        message_group.setLayout(message_layout)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(broker_group)
        main_layout.addWidget(subscription_group)
        main_layout.addWidget(message_group)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

        # Initialize the MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect_to_broker(self):
        broker = self.broker_input.text()
        port = int(self.port_input.text())
        self.client.connect(broker, port=port)
        self.client.loop_start()

    def subscribe_to_topic(self):
        topic = self.topic_input.text()
        self.client.subscribe(topic)
        self.message_display.append(f"Subscribed to topic '{topic}'")

    def on_connect(self, client, userdata, flags, rc):
        self.message_display.append(f"Connected with result code {str(rc)}")

    def on_message(self, client, userdata, message):
        self.message_display.append(f"Received message '{str(message.payload)}' on topic '{message.topic}'")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = MQTTClient()
    client.show()
    sys.exit(app.exec())
