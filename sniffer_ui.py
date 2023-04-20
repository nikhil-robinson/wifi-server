import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore
import scapy.all as scapy

class SnifferUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the main window
        self.setWindowTitle("Packet Sniffer")
        self.setGeometry(200, 200, 500, 500)
        
        # Create a combo box to select the interface
        self.interface_combo = QtWidgets.QComboBox(self)
        self.interface_combo.setGeometry(10, 10, 200, 30)
        self.interface_combo.addItem("-- Select Interface --")

        # Add available interfaces to the combo box
        for iface in os.listdir('/sys/class/net/'):
            if iface != 'lo':
                self.interface_combo.addItem(iface)

        # Create a button to start capturing packets
        self.start_button = QtWidgets.QPushButton("Start", self)
        self.start_button.setGeometry(220, 10, 100, 30)
        self.start_button.clicked.connect(self.start_sniffing)

        # Create a text box to display captured packets
        self.packets_textbox = QtWidgets.QTextEdit(self)
        self.packets_textbox.setGeometry(10, 50, 480, 440)

    def start_sniffing(self):
        # Get the selected interface
        selected_iface = self.interface_combo.currentText()

        # Check if an interface is selected
        if selected_iface == "-- Select Interface --":
            QtWidgets.QMessageBox.warning(self, "Error", "Please select an interface.")
            return

        # Create a sniffing filter
        sniff_filter = "not port 22"

        # Start sniffing packets
        self.packets_textbox.clear()
        self.sniff_thread = SniffThread(selected_iface, sniff_filter)
        self.sniff_thread.packet_signal.connect(self.display_packet)
        self.sniff_thread.start()

    def display_packet(self, packet):
        # Display the packet in the text box
        self.packets_textbox.insertPlainText(str(packet) + "\n")

    def closeEvent(self, event):
        # Stop the sniff thread before closing the window
        self.sniff_thread.stop_sniffing()
        event.accept()

class SniffThread(QtCore.QThread):
    packet_signal = QtCore.pyqtSignal(str)

    def __init__(self, iface, sniff_filter):
        super().__init__()
        self.iface = iface
        self.sniff_filter = sniff_filter
        self.stop_sniffing_flag = False

    def run(self):
        while not self.stop_sniffing_flag:
            scapy.sniff(iface=self.iface, filter=self.sniff_filter, prn=self.packet_signal.emit)

    def stop_sniffing(self):
        self.stop_sniffing_flag = True
        self.wait()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    sniffer = SnifferUI()
    sniffer.show()
    sys.exit(app.exec())
