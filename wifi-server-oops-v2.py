import subprocess
import platform
import time
import qrcode
import netifaces
import tkinter as tk
from tkinter import messagebox

class App:
    def __init__(self, master):
        self.master = master
        master.title("WiFi Hotspot")

        # Labels
        self.ssid_label = tk.Label(master, text="SSID:")
        self.ssid_label.pack()
        self.password_label = tk.Label(master, text="Password:")
        self.password_label.pack()

        # Entry fields
        self.ssid_entry = tk.Entry(master)
        self.ssid_entry.pack()
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack()

        # Buttons
        self.create_button = tk.Button(master, text="Create Hotspot", command=self.create_hotspot)
        self.create_button.pack()
        self.disconnect_button = tk.Button(master, text="Disconnect", command=self.disconnect_hotspot)
        self.disconnect_button.pack()
        self.qr_button = tk.Button(master, text="Show QR Code", command=self.show_qr_code)
        self.qr_button.pack()

    def create_hotspot(self):
        ssid = self.ssid_entry.get()
        password = self.password_entry.get()
        result = ""
        os_name = platform.system()

        if os_name == "Linux":
            interfaces = netifaces.interfaces()
            wifi_interface = None
            for interface in interfaces:
                if interface.startswith("w"):
                    wifi_interface = interface
                    break
            if wifi_interface is None:
                result = "Error: No WiFi interface found"
            else:
                cmd = f'sudo lnxrouter start --ssid {ssid} --password {password} --iface {wifi_interface}'
                try:
                    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                    result = "Hotspot created successfully"
                except subprocess.CalledProcessError as e:
                    result = e.output.decode().strip()
        elif os_name == "Windows":
            cmd = f'netsh wlan set hostednetwork mode=allow ssid={ssid} key={password}'
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                result = "Hotspot created successfully"
            except subprocess.CalledProcessError as e:
                result = e.output.decode().strip()
        else:
            result = "Unsupported OS"

        messagebox.showinfo("Result", result)

    def disconnect_hotspot(self):
        result = ""
        os_name = platform.system()

        if os_name == "Linux":
            cmd = 'sudo lnxrouter stop'
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                result = "Hotspot disconnected successfully"
            except subprocess.CalledProcessError as e:
                result = e.output.decode().strip()
        elif os_name == "Windows":
            cmd = 'netsh wlan stop hostednetwork'
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                result = "Hotspot disconnected successfully"
            except subprocess.CalledProcessError as e:
                result = e.output.decode().strip()
        else:
            result = "Unsupported OS"

        messagebox.showinfo("Result", result)

    def show_qr_code(self):
        ssid = self.ssid_entry.get()
        password = self.password_entry.get()
        data = f"WIFI:T:WPA;S:{ssid};P:{password};;"
        img = qrcode.make(data)
        img.show()

root = tk.Tk()
app = App(root)
root
