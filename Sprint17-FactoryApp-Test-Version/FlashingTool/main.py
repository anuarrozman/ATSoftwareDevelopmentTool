import tkinter as tk
from tkinter import ttk, scrolledtext
import serial.tools.list_ports
import serial
import subprocess
import os
import requests
import mysql.connector
from threading import Thread

from components.settingWindow.settingWindow import SettingApp   # Address Configuration Setting Window for Flashing Tool
from components.toolsBar.toolsBar import ToolsBar   # Flash Tool Checking and Download List
from components.flashFirmware.flashFirmware import FlashFirmware   # Flash Firmware
from components.flashCert.flashCert import FlashCert   # Flash Certificate
from components.serialCom.serialCom import SerialCom   # Serial Communication


class SerialCommunicationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Communication App")
        self.root.minsize(600, 300)  # Set minimum window size

        # Serial port configuration
        self.serial_port = None
        self.read_thread = None  # Thread for reading data
        self.selected_port = ""

        # Create GUI elements
        self.create_widgets()
        self.create_text_widgets()
        self.create_menubar()
        
        self.toolsBar = ToolsBar()
        self.flashFw = FlashFirmware(self.receive_text)
        self.flashCert = FlashCert()
        self.serialCom = SerialCom(self.receive_text)
        
    def flash_tool_checking(self):
        self.toolsBar.flash_tool_checking()
        
    def download_list(self):
        self.toolsBar.download_list()
    
    def flash_firmware(self):
        self.flashFw.flash_firmware(self.port_var, self.baud_var)

    def flash_cert(self):
        self.flashCert.flash_cert(self.port_var)
        
    def open_serial_port(self):
        selected_port = self.port_var1.get()
        selected_baud = int(self.baud_var1.get())
        self.serialCom.open_serial_port(selected_port, selected_baud)

    def close_serial_port(self):
        self.serialCom.close_serial_port()
            
    def update_database(self, mac_address):
        try:
            connection = mysql.connector.connect(
        host="localhost",
        user="anuarrozman2303",
        password="Matter2303!",
        database="device_mac_sn"
            )
            
            cursor = connection.cursor()

            # Check if the MAC address already exists in the database
            cursor.execute("SELECT * FROM device_info WHERE mac_address = %s", (mac_address,))
            result = cursor.fetchone()

            if result:
                print("MAC address already exists in the database.")
            else:
                # Insert the MAC address into the database
                cursor.execute("INSERT INTO device_info (mac_address) VALUES (%s)", (mac_address,))
                connection.commit()
                print("MAC address inserted into the database.")

        except mysql.connector.Error as error:
            print("Failed to update database:", error)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection closed.")
        
    def get_device_mac(self):
        command = "FF:3;MAC?\r\n"
        self.send_command(command)
        
    def send_command(self, command):
        if self.serialCom.serial_port and self.serialCom.serial_port.is_open:
            self.serialCom.serial_port.write(command.encode())
        else:
            self.log_message("Port is not open. Please open the port before sending commands.")
            
    def create_menubar(self):
        menubar = tk.Menu(root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Setting", command=self.config_setting)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Check Flash Tool", command=self.flash_tool_checking)
        file_menu.add_command(label="Setting", command=self.config_setting)
        tools_menu.add_command(label="Download List", command=self.download_list)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=help_menu)

        root.config(menu=menubar)
        
    def config_setting(self):
        SettingApp(tk.Toplevel(self.root))
        # read from config.ini file and pass the addresses to flash_firmware function

    def create_widgets(self):
        self.serial_baud_frame = tk.Frame(root)
        self.serial_baud_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.port_label = tk.Label(self.serial_baud_frame, text="Flash Port:")
        self.port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.port_var = tk.StringVar()
        self.port_dropdown = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var)
        self.port_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown['values'] = [port.device for port in serial.tools.list_ports.comports()]

        self.baud_label = tk.Label(self.serial_baud_frame, text="Baud Rate:")
        self.baud_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        self.baud_var = tk.StringVar()
        self.baud_dropdown = ttk.Combobox(self.serial_baud_frame, textvariable=self.baud_var)
        self.baud_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.baud_dropdown['values'] = ["9600", "115200", "460800"]
        self.baud_dropdown.set("460800")

        self.flash_button = ttk.Button(self.serial_baud_frame, text="Flash FW", command=self.flash_firmware)
        self.flash_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        
        self.cert_flash_button = ttk.Button(self.serial_baud_frame, text="Flash Cert", command=self.flash_cert)
        self.cert_flash_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        self.port_label1 = tk.Label(self.serial_baud_frame, text="Factory Port:")
        self.port_label1.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.port_var1 = tk.StringVar()
        self.port_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var1) ##, state="disabled")
        self.port_dropdown1.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.port_dropdown1['values'] = [port.device for port in serial.tools.list_ports.comports()]
        
        self.baud_label1 = tk.Label(self.serial_baud_frame, text="Baud Rate:")
        self.baud_label1.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.baud_var1 = tk.StringVar()
        self.baud_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.baud_var1)
        self.baud_dropdown1.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        self.baud_dropdown1['values'] = ["9600", "115200", "460800"]
        self.baud_dropdown1.set("115200")
        
        self.open_port_button = ttk.Button(self.serial_baud_frame, text="Open Port", command=self.open_serial_port)
        self.open_port_button.grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)
        
        self.close_port_button = ttk.Button(self.serial_baud_frame, text="Close Port", command=self.close_serial_port)
        self.close_port_button.grid(row=1, column=5, padx=5, pady=5, sticky=tk.W)
        
        self.read_device_mac_button = ttk.Button(self.serial_baud_frame, text="Read Device MAC", command=self.get_device_mac)
        self.read_device_mac_button.grid(row=2, column=6, padx=5, pady=5, sticky=tk.W)

    def create_text_widgets(self):
        text_frame = ttk.Frame(self.root)
        text_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.receive_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, state=tk.DISABLED, height=24, width=48)
        self.receive_text.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W)

        self.clear_button = ttk.Button(text_frame, text="Clear", command=self.clear_received_data)
        self.clear_button.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

    def clear_received_data(self):
        self.receive_text.configure(state=tk.NORMAL)
        self.receive_text.delete(1.0, tk.END)
        self.receive_text.configure(state=tk.DISABLED)

    def log_message(self, message):
        self.receive_text.config(state=tk.NORMAL)
        self.receive_text.insert(tk.END, message + '\n')
        self.receive_text.config(state=tk.DISABLED)
        self.receive_text.see(tk.END)
        
    # Added proper closing of the serial port during exit program
    def on_exit(self):
        self.close_serial_port()
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialCommunicationApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_exit)
    root.mainloop()