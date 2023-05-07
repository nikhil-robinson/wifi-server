from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer,QTime
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QFormLayout
import pyqtgraph as pg
from random import randint
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_ploter_button = QPushButton("Open Window", self)
        self.serial_ploter_button.clicked.connect(self.serial_ploter_open_window)
        self.setCentralWidget(self.serial_ploter_button)
        
    def serial_ploter_open_window(self):
        self.serial_ploter_popup = QDialog(self)
        self.serial_ploter_popup.setWindowTitle('Serial Plotter')
        
        self.serial_ploter_widget = pg.PlotWidget()

        # Create combo boxes for line colors and update interval
        self.serial_ploter_color_combo = QComboBox()
        self.serial_ploter_color_combo.addItems(['red', 'green', 'blue', 'black'])
        self.serial_ploter_time_edit = QLineEdit()
        self.serial_ploter_time_edit.setPlaceholderText("Enter time delay in (ms)")

        # Create labels for combo boxes
        self.serial_ploter_color_label = QLabel('Line Color:')
        self.serial_ploter_update_label = QLabel('Update Interval (s):')

        # Create a form layout for the widget
        self.serial_ploter_layout = QFormLayout()
        self.serial_ploter_layout.addRow(self.serial_ploter_color_label, self.serial_ploter_color_combo)
        self.serial_ploter_layout.addRow(self.serial_ploter_update_label, self.serial_ploter_time_edit)
        self.serial_ploter_layout.addRow(self.serial_ploter_widget)


        self.serial_ploter_x = [0,1]  # 100 time points
        self.serial_ploter_y = [0,1]  # 100 data points

        # Create a line series and add it to the plot
        self.serial_ploter_line = pg.PlotCurveItem(pen=pg.mkPen(color='r', width=1))
        self.serial_ploter_widget.addItem(self.serial_ploter_line)

        # Set plot title and axes labels
        self.serial_ploter_widget.setTitle('Auto Plotter')
        self.serial_ploter_widget.setLabel('bottom', 'Time', units='s')
        self.serial_ploter_widget.setLabel('left', 'Value')

        # Connect combo boxes to update line color and interval
        self.serial_ploter_color_combo.currentTextChanged.connect(self.update_line_color)
        self.serial_ploter_time_edit.textChanged.connect(self.update_update_interval)

        # Set initial values for line color and update interval
        self.serial_ploter_line_colour = QColor('red')
        self.serial_ploter_update_interval = 100

        # Set up timer to update the plot
        self.serial_ploter_triger_timer = QTimer()
        self.serial_ploter_triger_timer.timeout.connect(self.serial_ploter_update_plot)
        self.serial_ploter_triger_timer.start(self.serial_ploter_update_interval)

        self.serial_ploter_elapsed_time = QTime(0, 0)


        self.serial_ploter_popup.setLayout(self.serial_ploter_layout)
        
        self.serial_ploter_popup.finished.connect(self.serial_ploter_handle_popup_closed)
        self.serial_ploter_popup.exec()

    def serial_ploter_handle_popup_closed(self, result):
        self.serial_ploter_triger_timer.stop()
        print("Closed")

    def serial_ploter_update_plot(self):
        self.serial_ploter_elapsed_time = self.serial_ploter_elapsed_time.addMSecs(self.serial_ploter_update_interval)

        # self.serial_ploter_x = self.serial_ploter_x[1:]  # Remove the first y element.
        if len(self.serial_ploter_x) > 100:
            self.serial_ploter_x = self.serial_ploter_x[1:]
        self.serial_ploter_x.append(self.serial_ploter_x[-1] + 1)  # Add a new value 1 higher than the last.

        if len(self.serial_ploter_y) > 100:
            self.serial_ploter_y = self.serial_ploter_y[1:]  # Remove the first
        self.serial_ploter_y.append( randint(0,100))  # Add a new random value.

        self.serial_ploter_line.setData(self.serial_ploter_x, self.serial_ploter_y)  # Update the data.


    def update_line_color(self, color):
        # Update the line color based on the selected combo box value
        self.serial_ploter_line_colour = QColor(color)
        self.serial_ploter_line.setPen(pg.mkPen(color=self.serial_ploter_line_colour, width=1))

    def update_update_interval(self, interval):
        # Update the update interval based on the selected combo box value
        self.serial_ploter_update_interval = int(interval) * 1000
        self.serial_ploter_triger_timer.setInterval(self.serial_ploter_update_interval)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
