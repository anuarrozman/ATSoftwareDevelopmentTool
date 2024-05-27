import os
import tkinter as tk
from tkinter import ttk

def get_hidraw_ports():
    hidraw_ports = []
    for port in os.listdir('/dev'):
        if port.startswith('hidraw'):
            hidraw_ports.append('/dev/' + port)
    return hidraw_ports

def on_select(self):
    selected_port = self.widget.get()
    print("Selected port:", selected_port)

def main():
    # GeIDraw ports
    hidraw_ports = get_hidraw_ports()

    print("HIDraw Ports:")
    for port in hidraw_ports:
        print(port)
        
if __name__ == "__main__":
    main()
