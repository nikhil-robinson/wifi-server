import platform
import os
import tkinter as tk

# Create a tkinter window
root = tk.Tk()
root.title('Hotspot Creator')

# Detect the operating system
os_name = platform.system()

# Function to create a hotspot
def create_hotspot():
    ssid = ssid_entry.get()
    password = password_entry.get()
    
    if os_name == 'Windows':
        os.system(f'netsh wlan set hostednetwork mode=allow ssid={ssid} key={password}')
        os.system('netsh wlan start hostednetwork')
        hotspot_label.config(text='Hotspot enabled on Windows')
    
    elif os_name == 'Darwin':
        os.system(f'sudo networksetup -setairportnetwork en0 {ssid} {password}')
        hotspot_label.config(text='Hotspot enabled on Mac')
    
    elif os_name == 'Linux':
        os.system(f'sudo  ./home/nikhil/Desktop/Nikhil/wifi-server/lnxrouter --ap wlan0 {ssid} -p {password}')
        hotspot_label.config(text='Hotspot enabled on Linux')
    
    else:
        hotspot_label.config(text='Unsupported operating system')
        
# Create input fields and button
ssid_label = tk.Label(root, text='SSID:')
ssid_entry = tk.Entry(root)
password_label = tk.Label(root, text='Password:')
password_entry = tk.Entry(root, show='*')
create_button = tk.Button(root, text='Create Hotspot', command=create_hotspot)
hotspot_label = tk.Label(root, text='')

# Grid the input fields and button
ssid_label.grid(row=0, column=0)
ssid_entry.grid(row=0, column=1)
password_label.grid(row=1, column=0)
password_entry.grid(row=1, column=1)
create_button.grid(row=2, column=0, columnspan=2)
hotspot_label.grid(row=3, column=0, columnspan=2)

# Start the tkinter event loop
root.mainloop()
