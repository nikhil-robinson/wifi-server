import platform
import subprocess
import tkinter as tk
import qrcode
from PIL import ImageTk
import psutil
import os
import signal

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WiFi Hotspot Creator")
        

        self.subprocs = []
        self.threads = []

        # Create input fields
        ssid_label = tk.Label(self, text="SSID:")
        ssid_label.grid(row=0, column=0)
        self.ssid_entry = tk.Entry(self)
        self.ssid_entry.grid(row=0, column=1)

        password_label = tk.Label(self, text="Password:")
        password_label.grid(row=1, column=0)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1)

        # Create button to start hotspot
        start_button = tk.Button(self, text="Start Hotspot", command=self.start_hotspot)
        start_button.grid(row=2, column=0, columnspan=2)
    def __del__(self):
        self.lxpro.send_signal(signal.SIGINT)
        self.lxpro.wait()
        # Terminate any running subprocesses or threads
        for proc in self.subprocs:
            proc.terminate()
        for thread in self.threads:
            thread.join()
        
        
        
    def start_hotspot(self):
        # Get operating system
        system = platform.system()

        # Get available Wi-Fi interfaces
        if system == "Linux":
            process = subprocess.Popen(["iwconfig"], stdout=subprocess.PIPE)
            self.subprocs.append(process)
            output, error = process.communicate()
            interfaces = [line.split()[0] for line in output.decode().split("\n") if "IEEE" in line]
            if len(interfaces) == 1:
                wifi_interface = interfaces[len(interfaces)-1]
            else:
                wifi_interface = tk.simpledialog.askstring("Select Wi-Fi Interface", "Enter the name of the Wi-Fi interface to use:", initialvalue=interfaces[0])
        elif system == "Darwin":
            
            process = subprocess.Popen(["networksetup", "-listallhardwareports"], stdout=subprocess.PIPE)
            self.subprocs.append(process)
            output, error = process.communicate()
            interfaces = [line.split()[-1] for line in output.decode().split("\n") if "Wi-Fi" in line]
            wifi_interface = interfaces[0]
        elif system == "Windows":
            process = subprocess.Popen(["netsh", "wlan", "show", "drivers"], stdout=subprocess.PIPE)
            self.subprocs.append(process)
            output, error = process.communicate()
            if "Hosted network supported  : Yes" in output.decode():
                process = subprocess.Popen(["netsh", "wlan", "show", "interfaces"], stdout=subprocess.PIPE)
                self.subprocs.append(process)
                output, error = process.communicate()
                interfaces = [line.split(":")[-1].strip() for line in output.decode().split("\n") if "Name" in line]
                wifi_interface = interfaces[0]
            else:
                tk.messagebox.showerror("Error", "This computer does not support creating a hotspot")
                return
        else:
            tk.messagebox.showerror("Error", "Operating system not supported")
            return

        # Get input values
        ssid = self.ssid_entry.get()
        password = self.password_entry.get()

        # Create hotspot
        if system == "Linux":
            command = f"sudo ifconfig {wifi_interface} down"
            process = subprocess.Popen(command.split())
            self.subprocs.append(process)
            command = f"sudo bash lnxrouter.sh --ap  {wifi_interface} {ssid} -p {password} --virt-name server"
            self.lxpro =subprocess.Popen(command.split())
            self.subprocs.append(self.lxpro)
            command = f"sudo ifconfig {wifi_interface} up"
            subprocess.Popen(command.split())
        elif system == "Darwin":
            command = f"sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -z && sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -P createNetwork {ssid} {password} -I {wifi_interface}"
            process =subprocess.Popen(command, shell=True)
            self.subprocs.append(process)
        elif system == "Windows":
            command = f"netsh wlan set hostednetwork mode=allow ssid={ssid} key={password}"
            process = subprocess.Popen(command.split())
            self.subprocs.append(process)
            command = f"netsh wlan start hostednetwork"
            process = subprocess.Popen(command.split())
            self.subprocs.append(process)
            

if __name__ == "__main__":
    app = App()
    
    app.mainloop()
