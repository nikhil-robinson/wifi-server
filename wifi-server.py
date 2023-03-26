import tkinter as tk
from tkinter import messagebox
import subprocess
import platform
import signal
from time import sleep
from tkinter import simpledialog
import os

class HotspotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Hotspot App")
        self.geometry("300x250")
        self.create_widgets()
        self.subprocs = []
        self.threads = []
        self.hotspot = False
        self.wifi = False
    def __del__(self):

        self.lnproc.send_signal(signal.SIGINT)
        self.lnproc.wait()
        # Terminate any running subprocesses or threads
        for proc in self.subprocs:
            proc.terminate()
        for thread in self.threads:
            thread.join()
    
    def create_widgets(self):
        self.toggle_var = tk.BooleanVar()
        self.toggle_switch = tk.Label(
            self, text="Create Hotspot", font=("Helvetica", 16, "bold"),
            fg="green", pady=20
        )
        self.toggle_switch.pack()
        self.toggle_switch.bind("<Button-1>", self.toggle_command)
        
        self.ssid_label = tk.Label(self, text="SSID:")
        self.ssid_label.pack(pady=5)
        self.ssid_entry = tk.Entry(self)
        self.ssid_entry.pack(pady=5)
        
        self.password_label = tk.Label(self, text="Password:")
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)
        
        self.connect_button = tk.Button(
            self, text="Create Hotspot", command=self.connect_command, state="normal"
        )
        self.connect_button.pack(pady=10)
        
        # self.quit_button = tk.Button(self, text="Quit", command=self.quit)
        # self.quit_button.pack(pady=10)
    
        # self.protocol("WM_DELETE_WINDOW", self.quit)
    
    def toggle_command(self, event):
        if self.toggle_var.get():
            self.toggle_var.set(False)
            self.toggle_switch.config(fg="green", text="Create Hotspot")
            self.connect_button.config(text="Create Hotspot", state="normal")
        else:
            self.toggle_var.set(True)
            self.toggle_switch.config(fg="red", text="Connect to Wi-Fi")
            self.connect_button.config(text="Connect to Wi-Fi", state="normal")
    
    def connect_command(self):
        self.ssid = self.ssid_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if self.toggle_var.get():
            if self.ssid == "":
                messagebox.showerror("Error", "Please enter the SSID.")
            else:
                self.connect_to_wifi(self.ssid)
        else:
            if self.ssid == "" or password == "":
                messagebox.showerror("Error", "Please enter the SSID and password.")
            else:
                if self.hotspot:
                    self.hotspot =False
                    self.stop_hotspot()
                    self.connect_button.config(text="Create Hotspot", state="normal")
                else:
                    self.hotspot =True
                    self.start_hotspot()
                    self.connect_button.config(text="Stop Hotspot", state="normal")

    
    # def create_hotspot(self, ssid, password):
    #     cmd = f"command to create hotspot {ssid} {password}".split()
    #     if subprocess.run(cmd).returncode == 0:
    #         messagebox.showinfo("Success", "Hotspot created successfully!")
    #     else:
    #         messagebox.showerror("Error", "Failed to create hotspot.")
    def check_hotspot_status(self):
        if self.lnproc.poll() is None:
            # subprocess is still running
            # self.hotspot =True

            self.after(5000, self.check_hotspot_status)
        else:
            # subprocess has finished
            # self.hotspot =False
            output, error = self.lnproc.communicate()
            self.connect_button.config(state="normal")
            self.toggle_switch.config(state="normal")
            self.ssid_entry.config(state="normal")
            self.password_entry.config(state="normal")
            # self.toggle_var.set(not self.toggle_var.get())
            if error:
                messagebox.showerror("Error", error.decode("utf-8"))
            else:
                messagebox.showinfo("Success", output.decode("utf-8"))
    def start_hotspot(self):
        self.connect_button.config(state="disabled")
        self.toggle_switch.config(state="disabled")
        self.ssid_entry.config(state="disabled")
        self.password_entry.config(state="disabled")
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
                wifi_interface = simpledialog.askstring("Select Wi-Fi Interface", "Enter the name of the Wi-Fi interface to use:", initialvalue=interfaces[0])
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
        ssid = self.ssid_entry.get().strip()
        password = self.password_entry.get().strip()
        self.i = wifi_interface

        # Create hotspot
        if system == "Linux":
            command = f"sudo ifconfig {wifi_interface} down"
            process = subprocess.Popen(command.split())
            output, error = process.communicate()
            sleep(5)
            print(f"Stoping {wifi_interface}")
            self.subprocs.append(process)
            output, error = process.communicate()
            command = f"sudo bash lnxrouter.sh --ap  {wifi_interface} {ssid} -p {password} --virt-name server"
            # self.lnproc = subprocess.call(command.split())
            # self.subprocs.append(self.lnproc)
            self.lnproc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("lnxrouter started")
            sleep(5)
            command = f"sudo ifconfig {wifi_interface} up"
            process = subprocess.Popen(command.split())
            output, error = process.communicate()
            self.subprocs.append(process)
            print(f"Starting {wifi_interface}")
            

            self.after(5000, self.check_hotspot_status)
            
        elif system == "Darwin":
            command = f"sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -z && sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -P createNetwork {ssid} {password} -I {wifi_interface}"
            process =subprocess.Popen(command, shell=True)
            self.subprocs.append(process)
            output, error = process.communicate()
        elif system == "Windows":
            command = f"netsh wlan set hostednetwork mode=allow ssid={ssid} key={password}"
            process = subprocess.Popen(command.split())
            output, error = process.communicate()
            self.subprocs.append(process)
            command = f"netsh wlan start hostednetwork"
            process = subprocess.Popen(command.split())
            output, error = process.communicate()
            self.subprocs.append(process)
            
    def stop_hotspot(self):
        # self.lnproc.send_signal(signal.SIGINT)
        # self.lnproc.wait()
        os.kill(self.lnproc.pid,signal.SIGINT)
        # os.killpg(os.getpgid(self.lnproc.pid), signal.SIGINT)
        self.lnproc.terminate()
        print("terminated")
        command = f"sudo ifconfig {self.i} down"
        process = subprocess.Popen(command.split())
        command = f"sudo ifconfig server down"
        process = subprocess.Popen(command.split())
        command = f"sudo bash lnxrouter.sh --stop {self.i}"
        process = subprocess.Popen(command.split())
        command = f"sudo bash lnxrouter.sh --stop server"
        process = subprocess.Popen(command.split())
        command = f"sudo ifconfig {self.i} up"
        process = subprocess.Popen(command.split())
        self.connect_button.config(text="Create Hotspot", state="normal")
        self.connect_button.config(state="normal")
        self.toggle_switch.config(state="normal")
        self.ssid_entry.config(state="normal")
        self.password_entry.config(state="normal")
        print("done")
    
    def connect_to_wifi(self, ssid):
        cmd = f"command to connect to wifi {ssid}".split()
        if subprocess.run(cmd).returncode == 0:
            messagebox.showinfo("Success", "Connected to Wi-Fi successfully!")
        else:
            messagebox.showerror("Error", "Failed to connect to Wi-Fi.")
            
if __name__ == "__main__":
    app = HotspotApp()
    app.mainloop()
