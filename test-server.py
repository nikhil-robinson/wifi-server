import os
import subprocess
import threading
import webbrowser
from tkinter import *
from tkinter import messagebox

class ServerThread(threading.Thread):
    def __init__(self, server_type):
        threading.Thread.__init__(self)
        self.server_type = server_type

    def run(self):
        # Start the server process using the appropriate command for the platform
        if os.name == 'nt':  # Windows
            if self.server_type == 'UDP':
                subprocess.call(['python', '-m', 'udp_server'])
            elif self.server_type == 'HTTP':
                subprocess.call(['python', '-m', 'http.server'])
            elif self.server_type == 'HTTPS':
                subprocess.call(['python', '-m', 'http.server', '--bind', 'localhost', '--cgi', '--certfile', 'server.pem', '--ssl'])
            elif self.server_type == 'TCP':
                subprocess.call(['python', '-m', 'http.server', '8000'])
        else:  # Linux or macOS
            if self.server_type == 'UDP':
                subprocess.call(['python3', '-m', 'udp_server'])
            elif self.server_type == 'HTTP':
                subprocess.call(['python3', '-m', 'http.server'])
            elif self.server_type == 'HTTPS':
                subprocess.call(['python3', '-m', 'http.server', '--bind', 'localhost', '--cgi', '--certfile', 'server.pem', '--ssl'])
            elif self.server_type == 'TCP':
                subprocess.call(['python3', '-m', 'http.server', '8000'])

class App(Tk):
    def __init__(self):
        super().__init__()

        # Create the GUI
        self.title('Server App')
        self.geometry('300x200')

        protocol_label = Label(self, text='Select protocol:')
        protocol_label.pack()

        self.protocol_var = StringVar()
        self.protocol_var.set('UDP')

        protocol_menu = OptionMenu(self, self.protocol_var, 'UDP', 'HTTP', 'HTTPS', 'TCP')
        protocol_menu.pack()

        self.start_button = Button(self, text='Start Server', command=self.start_server)
        self.start_button.pack(pady=10)

        ip_label = Label(self, text='IP Address:')
        ip_label.pack()

        self.ip_text = Text(self, height=1, width=20, state='disabled')
        self.ip_text.pack()

        self.protocol_var.trace('w', self.update_ip_address)

    def update_ip_address(self, *args):
        # Update the IP address when the protocol is changed
        ip_address = self.get_ip_address()
        self.ip_text.config(state='normal')
        self.ip_text.delete('1.0', END)
        self.ip_text.insert(END, ip_address)
        self.ip_text.config(state='disabled')

    def get_ip_address(self):
        # Get the IP address of the Wi-Fi hotspot
        if os.name == 'nt':  # Windows
            output = subprocess.check_output(['netsh', 'wlan', 'show', 'hostednetwork'])
            lines = output.decode().split('\n')
            for line in lines:
                if 'IP Address' in line:
                    ip_address = line.split(':')[1].strip()
                    return ip_address
        else:  # Linux or macOS
            output = subprocess.check_output(['ip', 'addr', 'show', 'wlan0'])
            lines = output.decode().split('\n')
            for line in lines:
                if 'inet ' in line:
                    ip_address = line.split()[1]
                    return ip_address

    def start_server
