import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinter.filedialog import askopenfilename
import serial.tools.list_ports
import os
from tkinter import messagebox
from cryptography.fernet import Fernet
import configparser
import time
import threading
import logging

from components.settingWindow.settingWindow import SettingApp
from components.toolsBar.toolsBar import ToolsBar
from components.flashFirmware.flashFirmware import FlashFirmware
from components.flashCert.flashCert import FlashCert
from components.serialCom.serialCom import SerialCom
from components.writeDevInfo.writeDeviceInfo import WriteDeviceInfo
from components.dmmReader.multimeter import Multimeter
from components.dmmReader.dmmReader import DeviceSelectionApp
from components.dmmReader.ut61eplus import UT61EPLUS
from components.adminLoginWindow.adminLoginWindow import AdminLoginApp
from components.manualTest.manualTest import ManualTestApp
from components.uploadReport import uploadReport
from components.loadTestScript.loadTestScript import LoadTestScript
from components.aht20Sensor.aht20Sensor import SensorLogger
# from components.servoControl.servoControl import ServoController

class SerialCommunicationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Communication App")
        self.root.attributes('-zoomed', True)
        self.root.resizable(True, True)

        # Serial port configuration
        self.serial_port = None
        self.task2_thread = None
        self.task1_thread = None
        self.selected_port = ""
        self.step_delay = 3
        self.long_delay = 5

        # Create GUI elements
        self.initialize_gui()

        # Initialize components
        self.initialize_components()

        # Store reference to the Manual Test menu item
        self.manual_test_menu = None
        self.task1_completed = threading.Event()

    def initialize_gui(self):
        self.create_menubar()
        self.create_widgets()
        # self.create_text_widgets()

        version = self.read_version_from_file("version.txt")  # Read version from file
        self.add_version_label(version)  # Add version number here

    def initialize_components(self):
        self.toolsBar = ToolsBar()
        self.flashFw = FlashFirmware(self.result_flashing_fw_label) #(self.receive_text)
        self.flashCert = FlashCert(self.result_flashing_cert_label) #(self.log_message)
        self.serialCom = SerialCom(self.result_factory_mode_label, self.atbeam_temp_value, self.atbeam_humid_value, self.result_read_device_mac, self.result_button_label, self.result_ir_def) #self.atbeam_sensor_temp_update) #(self.receive_text)
        
        self.sendEntry = WriteDeviceInfo(self.send_command, self.result_write_serialnumber, self.result_write_mtqr) #, self.log_message)
        self.dmmReader = DeviceSelectionApp(self.dmm_frame, self.result_3_3v_test, self.result_5v_test)
        self.multimeter = Multimeter()
        # self.aht20Sensor = SensorLogger()
        # self.servo_controller = ServoController()

    def read_temp_aht20(self):
        # ext_sensor = self.aht20Sensor.read_temp_sensor()
        ext_sensor = 25.0
        logger.debug(f"External Temperature: {ext_sensor}")
        self.ext_temp_value.config(text=f"{ext_sensor} °C")
        # self.get_atbeam_temp()
        # time.sleep(3)
        self.compare_temp(ext_sensor, self.serialCom.sensor_temp_variable)
        # pass

    def get_atbeam_temp(self):
        command = "FF:3;sensorTemp?\r\n"
        self.send_command(command)

    def compare_temp(self, ext_sensor, atbeam_temp):
        try:
            with open('sensor.txt', 'r') as file:
                for line in file:
                    if "ATBeam Temperature:" in line:
                        atbeam_temp = line.split(":")[1].strip()
                        logger.info(f"ATBeam Temperature: {atbeam_temp}")
                        if ext_sensor == atbeam_temp:
                            logger.info("Temperature matches")
                            self.result_temp_label.config(text=f"Pass", fg="green", font=("Helvetica", 12, "bold"))
                        else:
                            logger.error("Temperature does not match")
                            self.result_temp_label.config(text=f"Failed", fg="red", font=("Helvetica", 12, "bold"))
        except FileNotFoundError:
            logger.error("File not found")
    
    def read_humid_aht20(self):
        # ext_sensor = self.aht20Sensor.read_humid_sensor()
        ext_sensor = 50.5
        logger.debug(f"External Humidity: {ext_sensor}")
        self.ext_humid_value.config(text=f"{ext_sensor} %")
        # self.get_atbeam_humid()
        # time.sleep(3)
        self.compare_humid(ext_sensor, self.serialCom.sensor_humid_variable)
        # pass

    def get_atbeam_humid(self):
        command = "FF:3;sensorHumi?\r\n"
        self.send_command(command)

    def compare_humid(self, ext_sensor, atbeam_humid):
        try:
            with open('sensor.txt', 'r') as file:
                for line in file:
                    if "ATBeam Humidity:" in line:
                        atbeam_humid = line.split(":")[1].strip()
                        logger.info(f"ATBeam Humidity: {atbeam_humid}")
                        ext_sensor = float(ext_sensor)
                        atbeam_humid = float(atbeam_humid)
                        if ext_sensor == atbeam_humid:
                            logger.info("Humidity matches")
                            self.result_humid_label.config(text=f"Pass", fg="green", font=("Helvetica", 12, "bold"))
                        elif abs(ext_sensor - atbeam_humid) <= 10:
                            logger.info("Humidity is within ±10 range")
                            self.result_humid_label.config(text="Pass", fg="green", font=("Helvetica", 12, "bold"))
                        else:
                            logger.error("Humidity does not match")
                            self.result_humid_label.config(text=f"Failed", fg="red", font=("Helvetica", 12, "bold"))
        except FileNotFoundError:
            logger.error("File not found")

    def dmm_reader_3_3V_value_manual(self, dmm_value):
        dmm_manual_input = dmm_value.get()
        logger.debug(f"Manual 3.3V DMM Value: {dmm_manual_input}")
        self.dmm_3_3V_reader.config(text=f"{dmm_manual_input} V", fg="black", font=("Helvetica", 12, "bold"))
        
        if 2.9 <= float(dmm_manual_input) <= 3.3:
            self.result_3_3v_test.config(text="Pass", fg="green", font=("Helvetica", 12, "bold"))
        else:
            self.result_3_3v_test.config(text="Failed", fg="red", font=("Helvetica", 12, "bold"))
    
    def dmm_reader_5V_value_manual(self, dmm_value):
        dmm_manual_input = dmm_value.get()
        logger.debug(f"Manual 5V DMM Value: {dmm_manual_input}")
        self.dmm_5V_reader.config(text=f"{dmm_manual_input} V", fg="black", font=("Helvetica", 12, "bold"))
        
        if 4.9 <= float(dmm_manual_input) <= 5.1:
            self.result_5v_test.config(text="Pass", fg="green", font=("Helvetica", 12, "bold"))
        else:
            self.result_5v_test.config(text="Failed", fg="red", font=("Helvetica", 12, "bold"))

    def refresh_dmm_devices(self):
        self.dmmReader.refresh_devices()

    def flash_tool_checking(self):
        self.toolsBar.flash_tool_checking()

    def download_list(self):
        self.toolsBar.download_list()

    def flash_firmware(self, port_var, baud_var):
        # self.flashFw.flash_firmware(self.port_var, self.baud_var)
        self.flashFw.flash_firmware(port_var, baud_var)

    def flash_cert(self, port_var):
        # self.flashCert.flash_cert(self.port_var)
        self.flashCert.flash_cert(port_var)

    def open_serial_port(self):
        selected_port = self.port_var1.get()
        selected_baud = int(self.baud_var1.get())
        self.serialCom.open_serial_port(selected_port, selected_baud)

    def close_serial_port(self):
        self.serialCom.close_serial_port()
    
    def get_device_mac(self):
        command = "FF:3;MAC?\r\n"
        self.send_command(command)

    def send_command(self, command):
        if self.serialCom.serial_port and self.serialCom.serial_port.is_open:
            self.serialCom.serial_port.write(command.encode())
            logger.debug(f"Sent: {command.strip()}")
        else:
            logger.error("Port is not open. Please open the port before sending commands.")
    
    def send_serial_number(self):
        self.sendEntry.send_serial_number_command()

    def send_mqtr(self):
        self.sendEntry.send_mtqr_command()

    def create_menubar(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Setting", command=self.config_setting)
        file_menu.add_command(label="Run As Admin", command=self.admin_login)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Check Flash Tool", command=self.flash_tool_checking)
        tools_menu.add_command(label="Download List", command=self.download_list)
        tools_menu.add_command(label="Upload Test Script", command=self.load_test_script)
        self.manual_test_menu = tools_menu.add_command(label="Manual Test", command=self.manual_test)
        tools_menu.entryconfig("Manual Test", state=tk.DISABLED)  
        self.tools_menu = tools_menu  
        menubar.add_cascade(label="Tools", menu=tools_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)
        
    def admin_login(self):
        login_window = tk.Toplevel(self.root)
        app = AdminLoginApp(login_window)
        login_window.wait_window(login_window)  # Wait for the login window to close
        if app.result:
            # Decrypt and verify the password
            decrypted_password = self.decrypt_password()
            logger.debug("Decrypted Password: %s", decrypted_password)  # Debugging message
            if decrypted_password == "admin":  # Replace "admin" with the actual password if needed
                messagebox.showinfo("Login Successful", "Admin login successful. Manual Test enabled.")
                # Change the Manual Test from menubar state to Normal
                self.tools_menu.entryconfig("Manual Test", state=tk.NORMAL)
            else:
                messagebox.showerror("Error", "Failed to decrypt password or invalid password!")

    def config_setting(self):
        SettingApp(tk.Toplevel(self.root))

    def manual_test(self):
        ManualTestApp(self.root, self.send_command).open_manual_test_window()

    def decrypt_password(self):
        key_file = "secret.key"
        password_file = "password.txt"
        try:
            with open(key_file, "rb") as kf:
                key = kf.read()
            with open(password_file, "rb") as pf:
                encrypted_password = pf.read()
            fernet = Fernet(key)
            decrypted_password = fernet.decrypt(encrypted_password).decode()
            return decrypted_password
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None
        
    def upload_report(self):
        ini_file_path = filedialog.askopenfilename(title="Select .ini file", filetypes=[("INI files", "*.ini")])
        if not ini_file_path:
            return
        
        config = configparser.ConfigParser()
        config.read(ini_file_path)
        
        # Create a single dictionary from the INI file sections
        combined_data = {}
        for section in config.sections():
            combined_data.update(config[section])
        
        # Convert to the desired JSON format: a list of one dictionary
        data = [combined_data]

        # Debugging: Print the data dictionary to verify its contents
        logger.debug("Converted data: %s", data)
        
        api_url = "http://localhost:4000/api/endpoint"   # Replace with actual API endpoint
        
        response = uploadReport.post_report(api_url, data)
        
        if response and response.status_code == 200:
            messagebox.showinfo("Success", "Report uploaded successfully!")
        else:
            messagebox.showerror("Error", "Failed to upload report.")

    def disable_frame(self, frame):
        for child in frame.winfo_children():
            child.configure(state='disabled')

    def create_widgets(self):
        self.serial_baud_frame = tk.Frame(self.root)
        self.serial_baud_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.exit_button = ttk.Button(self.serial_baud_frame, text="Exit", command=self.root.quit)
        self.exit_button.grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)

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
        self.port_dropdown1 = ttk.Combobox(self.serial_baud_frame, textvariable=self.port_var1)
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
        self.read_device_mac_button.grid(row=1, column=6, padx=5, pady=5, sticky=tk.W)

        self.write_device_serialnumber_button = ttk.Button(self.serial_baud_frame, text="Write S/N", command=self.send_serial_number)
        self.write_device_serialnumber_button.grid(row=1, column=7, padx=5, pady=5, sticky=tk.W)

        self.write_device_mtqr_button = ttk.Button(self.serial_baud_frame, text="Write MTQR", command=self.send_mqtr)
        self.write_device_mtqr_button.grid(row=1, column=8, padx=5, pady=5, sticky=tk.W)

        self.read_atbeam_temp_button = ttk.Button(self.serial_baud_frame, text="Read ATBeam Temp", command=self.get_atbeam_temp)
        self.read_atbeam_temp_button.grid(row=1, column=9, padx=5, pady=5, sticky=tk.W)

        self.read_atbeam_humid_button = ttk.Button(self.serial_baud_frame, text="Read ATBeam Humid", command=self.get_atbeam_humid)
        self.read_atbeam_humid_button.grid(row=1, column=10, padx=5, pady=5, sticky=tk.W)

        self.disable_frame(self.serial_baud_frame)

        self.text_frame = tk.Frame(self.root)
        self.text_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.send_entry_frame = ttk.Entry(self.text_frame, width=50)
        self.send_entry_frame.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.send_button = ttk.Button(self.text_frame, text="Send", command=lambda: self.sendEntry.send_entry_command(self.send_entry_frame))
        self.send_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.disable_frame(self.text_frame)

        self.servo_frame = tk.Frame(self.root)
        self.servo_frame.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

        self.angle_label = tk.Label(self.servo_frame, text="Enter servo angle:")
        self.angle_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.angle_entry = tk.Entry(self.servo_frame)
        self.angle_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.duration_label = tk.Label(self.servo_frame, text="Enter pressing duration:")
        self.duration_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.duration_entry = tk.Entry(self.servo_frame)
        self.duration_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.pressing_time_label = tk.Label(self.servo_frame, text="Enter pressing time:")
        self.pressing_time_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.pressing_time_entry = tk.Entry(self.servo_frame)
        self.pressing_time_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.disable_frame(self.servo_frame)

        self.dmm_frame = tk.Frame(self.root)
        self.dmm_frame.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        self.upload_report_button = ttk.Button(self.dmm_frame, text="Upload Report", command=self.upload_report)
        self.upload_report_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        self.read_temp_aht20_button = ttk.Button(self.dmm_frame, text="Read Temperature Sensor", command=self.read_temp_aht20)
        self.read_temp_aht20_button.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        self.read_humid_aht20_button = ttk.Button(self.dmm_frame, text="Read Humidity Sensor", command=self.read_humid_aht20)
        self.read_humid_aht20_button.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)

        self.disable_frame(self.dmm_frame)

        # Start and Stop buttons
        self.control_frame = tk.Frame(self.root)
        self.control_frame.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        self.start_button = ttk.Button(self.control_frame, text="Start", command=self.combine_tasks)
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=None)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.reset_button = ttk.Button(self.control_frame, text="Reset", command=self.reset_tasks)
        self.reset_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        self.retest_label = tk.Label(self.control_frame, text="Retest MAC:")
        self.retest_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        self.retest_mac_input = tk.Entry(self.control_frame)
        self.retest_mac_input.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

        self.retest_button = ttk.Button(self.control_frame, text="Retest", command=None)
        self.retest_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # Order Number
        self.order_number_frame = tk.Frame(self.root)
        self.order_number_frame.grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)

        self.order_number_label = tk.Label(self.order_number_frame, text="Order Number:")
        self.order_number_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.order_number_input = tk.Entry(self.order_number_frame)
        self.order_number_input.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.submit_order_number = ttk.Button(self.order_number_frame, text="Submit", command=None)
        self.submit_order_number.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # auto test check
        self.auto_status_frame = tk.Frame(self.root, highlightbackground="black", highlightcolor="black", highlightthickness=2, bd=2)
        self.auto_status_frame.grid(row=7, column=0, padx=10, pady=10, sticky=tk.W)

        self.auto_frame_label = tk.Label(self.auto_status_frame, text="Auto Test Status", font=("Helvetica", 12, "bold"))
        self.auto_frame_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.status_flashing_fw = tk.Label(self.auto_status_frame, text="Flashing Firmware: ")
        self.status_flashing_fw.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_flashing_fw_label = tk.Label(self.auto_status_frame, text="Not Yet")
        self.result_flashing_fw_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_flashing_cert = tk.Label(self.auto_status_frame, text="Flashing Cert: ")
        self.status_flashing_cert.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_flashing_cert_label = tk.Label(self.auto_status_frame, text="Not Yet")
        self.result_flashing_cert_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_factory_mode = tk.Label(self.auto_status_frame, text="Factory Mode: ")
        self.status_factory_mode.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_factory_mode_label = tk.Label(self.auto_status_frame, text="Not Yet")
        self.result_factory_mode_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_read_device_mac = tk.Label(self.auto_status_frame, text="Read Device MAC: ")
        self.status_read_device_mac.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_read_device_mac = tk.Label(self.auto_status_frame, text="Not Yet")
        self.result_read_device_mac.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        self.read_device_mac = tk.Label(self.auto_status_frame, text="-")
        self.read_device_mac.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.status_write_device_sn = tk.Label(self.auto_status_frame, text="Write Device S/N: ")
        self.status_write_device_sn.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_write_serialnumber = tk.Label(self.auto_status_frame,text="Not Yet")
        self.result_write_serialnumber.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        self.read_device_sn = tk.Label(self.auto_status_frame, text="-")
        self.read_device_sn.grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.status_write_device_mtqr = tk.Label(self.auto_status_frame, text="Write Device MTQR: ")
        self.status_write_device_mtqr.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_write_mtqr = tk.Label(self.auto_status_frame, text="Not Yet")
        self.result_write_mtqr.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)

        self.read_device_mtqr = tk.Label(self.auto_status_frame, text="-")
        self.read_device_mtqr.grid(row=6, column=2, padx=5, pady=5, sticky=tk.W)

        self.status_ir_def = tk.Label(self.auto_status_frame, text="IR Definition: ")
        self.status_ir_def.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_ir_def = tk.Label(self.auto_status_frame, text="Not Yet")
        self.result_ir_def.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)

        self.status_atbeam_temp = tk.Label(self.auto_status_frame, text="Sensor Temperature: ")
        self.status_atbeam_temp.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_temp_label = tk.Label(self.auto_status_frame, text="Not Yet")
        self.result_temp_label.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)

        self.atbeam_temp_value = tk.Label(self.auto_status_frame, text="AT °C")
        self.atbeam_temp_value.grid(row=8, column=2, padx=5, pady=5, sticky=tk.W)

        self.ext_temp_value = tk.Label(self.auto_status_frame, text="Ext °C")
        self.ext_temp_value.grid(row=8, column=3, padx=5, pady=5, sticky=tk.W)

        self.status_atbeam_humidity = tk.Label(self.auto_status_frame, text="Sensor Humidity: ")
        self.status_atbeam_humidity.grid(row=9, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_humid_label = tk.Label(self.auto_status_frame, text="Not Yet")
        self.result_humid_label.grid(row=9, column=1, padx=5, pady=5, sticky=tk.W)

        self.atbeam_humid_value = tk.Label(self.auto_status_frame, text="AT %")
        self.atbeam_humid_value.grid(row=9, column=2, padx=5, pady=5, sticky=tk.W)

        self.ext_humid_value = tk.Label(self.auto_status_frame, text="Ext %")
        self.ext_humid_value.grid(row=9, column=3, padx=5, pady=5, sticky=tk.W)
        

        # manual test check
        self.manual_test_frame = tk.Frame(self.root, highlightbackground="black", highlightcolor="black", highlightthickness=2, bd=2)
        self.manual_test_frame.grid(row=10, column=0, padx=10, pady=10, sticky=tk.W)

        self.manual_test_label = tk.Label(self.manual_test_frame, text="Manual Test Status", font=("Helvetica", 12, "bold"))
        self.manual_test_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.status_5v_test = tk.Label(self.manual_test_frame, text="5V Test: ")
        self.status_5v_test.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_5v_test = tk.Label(self.manual_test_frame, text="Not Yet")
        self.result_5v_test.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.dmm_5V_reader = tk.Label(self.manual_test_frame, text="-")
        self.dmm_5V_reader.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        self.input_5V_dmm = tk.Entry(self.manual_test_frame)
        self.input_5V_dmm.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        self.submit_5V_dmm = ttk.Button(self.manual_test_frame, text="Submit", command=lambda: self.dmm_reader_5V_value_manual(self.input_5V_dmm))
        self.submit_5V_dmm.grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)

        self.status_3_3v_test = tk.Label(self.manual_test_frame, text="3.3V Test: ")
        self.status_3_3v_test.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_3_3v_test = tk.Label(self.manual_test_frame, text="Not Yet")
        self.result_3_3v_test.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.dmm_3_3V_reader = tk.Label(self.manual_test_frame, text="-")
        self.dmm_3_3V_reader.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)

        self.input_3_3V_dmm = tk.Entry(self.manual_test_frame)
        self.input_3_3V_dmm.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)

        self.submit_3_3V_dmm = ttk.Button(self.manual_test_frame, text="Submit", command=lambda: self.dmm_reader_3_3V_value_manual(self.input_3_3V_dmm))
        self.submit_3_3V_dmm.grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)

        self.status_button_label = tk.Label(self.manual_test_frame, text="Button: ")
        self.status_button_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_button_label = tk.Label(self.manual_test_frame, text="Not Yet")
        self.result_button_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        self.status_rgb_red_label = tk.Label(self.manual_test_frame, text="Red LED: ")
        self.status_rgb_red_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_rgb_red_label = tk.Label(self.manual_test_frame, text="Not Yet")
        self.result_rgb_red_label.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        self.yes_button_red = ttk.Button(self.manual_test_frame, text="Yes", command=lambda: self.update_red_label("Pass", fg="green", font=("Helvetica", 12, "bold")))
        self.no_button_red = ttk.Button(self.manual_test_frame, text="No", command=lambda: self.update_red_label("Failed", fg="red", font=("Helvetica", 12, "bold")))
        self.yes_button_red.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
        self.no_button_red.grid(row=4, column=3, padx=5, pady=5, sticky=tk.W)

        self.status_rgb_green_label = tk.Label(self.manual_test_frame, text="Green LED: ")
        self.status_rgb_green_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_rgb_green_label = tk.Label(self.manual_test_frame, text="Not Yet")
        self.result_rgb_green_label.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        self.yes_button_green = ttk.Button(self.manual_test_frame, text="Yes", command=lambda: self.update_green_label("Pass", fg="green", font=("Helvetica", 12, "bold")))
        self.yes_button_green.grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)

        self.no_button_green = ttk.Button(self.manual_test_frame, text="No", command=lambda: self.update_green_label("Failed", fg="red", font=("Helvetica", 12, "bold")))
        self.no_button_green.grid(row=5, column=3, padx=5, pady=5, sticky=tk.W)

        self.status_rgb_blue_label = tk.Label(self.manual_test_frame, text="Blue LED: ")
        self.status_rgb_blue_label.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_rgb_blue_label = tk.Label(self.manual_test_frame, text="Not Yet")
        self.result_rgb_blue_label.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)

        self.yes_button_blue = ttk.Button(self.manual_test_frame, text="Yes", command=lambda: self.update_blue_label("Pass", fg="green", font=("Helvetica", 12, "bold")))
        self.yes_button_blue.grid(row=6, column=2, padx=5, pady=5, sticky=tk.W)

        self.no_button_blue = ttk.Button(self.manual_test_frame, text="No", command=lambda: self.update_blue_label("Failed", fg="red", font=("Helvetica", 12, "bold")))
        self.no_button_blue.grid(row=6, column=3, padx=5, pady=5, sticky=tk.W)

        # self.input_temp = tk.Entry(self.manual_test_frame)
        # self.input_temp.grid(row=8, column=4, padx=5, pady=5, sticky=tk.W)

        # self.submit_temp = ttk.Button(self.manual_test_frame, text="Submit", command=lambda: self.get_sensor_temp(self.input_temp))
        # self.submit_temp.grid(row=8, column=5, padx=5, pady=5, sticky=tk.W)

        # self.input_humid = tk.Entry(self.manual_test_frame)
        # self.input_humid.grid(row=9, column=4, padx=5, pady=5, sticky=tk.W)

        # self.submit_humidity = ttk.Button(self.manual_test_frame, text="Submit", command=lambda: self.get_sensor_humid(self.input_humid))
        # self.submit_humidity.grid(row=9, column=5, padx=5, pady=5, sticky=tk.W)

    def update_red_label(self, text, fg, font):
        self.result_rgb_red_label.config(text=text, fg=fg, font=font)
        if text == "Pass":
            self.no_button_red.config(state='disabled')
            logger.info("Red LED: Pass")
        else:
            self.yes_button_red.config(state='disabled')
            logger.error("Red LED: Failed")

    def update_green_label(self, text, fg, font):
        self.result_rgb_green_label.config(text=text, fg=fg, font=font)
        if text == "Pass":
            self.no_button_green.config(state='disabled')
            logger.info("Green LED: Pass")
        else:
            self.yes_button_green.config(state='disabled')
            logger.error("Green LED: Failed")

    def update_blue_label(self, text, fg, font):
        self.result_rgb_blue_label.config(text=text, fg=fg, font=font)
        if text == "Pass":
            self.no_button_blue.config(state='disabled')
            logger.info("Blue LED: Pass")
        else:
            self.yes_button_blue.config(state='disabled')
            logger.error("Blue LED: Failed")

    def load_test_script(self):
        ini_file_path = askopenfilename(title="Select .ini file", filetypes=[("INI files", "*.ini")])
        if not ini_file_path:
            return
        
        self.loadtTestScript = LoadTestScript(ini_file_path)
        with open(ini_file_path, 'r') as file:
            content = file.read()
            print(content)
    
    def check_factory_flag(self):
        flag_value = self.serialCom.get_factory_flag()
        print(f"Factory Flag: {flag_value}")

    def start_test(self):
        logger.info("Starting test")

        # ini_file_name = "testscript.ini"
        # current_directory = os.getcwd()  # Get current working directory
        
        # # Check in the current directory
        # ini_file_path = os.path.join(current_directory, ini_file_name)
        
        # if not os.path.exists(ini_file_path):
        #     logger.error(f"{ini_file_name} not found in the current directory")
        #     return

        ini_file_name = "testscript.ini"
        # specified_directory = "/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool"  # Specify the directory
        specified_directory = "/home/anuarrozman/FactoryApp_Dev/ATSoftwareDevelopmentTool/FlashingTool"  # Specify the directory

        # Check in the specified directory
        ini_file_path = os.path.join(specified_directory, ini_file_name)

        if not os.path.exists(ini_file_path):
            logger.error(f"{ini_file_name} not found in the specified directory: {specified_directory}")
            return
        
        # Proceed to load and process the INI file
        self.loadTestScript = LoadTestScript(ini_file_path)

        config = configparser.ConfigParser()
        config.read(ini_file_path)

        if "flash" in config:
            logger.info("Flashing firmware and certificate")
            port = config.get("flash", "port")
            baud = config.get("flash", "baud")
            logger.info(f"Port: {port}, Baud: {baud}")
            self.flash_firmware(port, baud)
            self.flash_cert(port) 

        # if "dmm" in config:
        #     logger.info("Reading multimeter")
        #     self.dmmReader.select_device(0)

        if "factory" in config:
            logger.info("Entering factory mode")

            try:
                port = config.get("factory", "port")
                baud = config.get("factory", "baud")
                self.serialCom.open_serial_port(port, baud)
            except configparser.NoOptionError:
                logger.error("Port not found in the INI file")

        # Signal that task 1 is complete
        self.task1_completed.set()

    def start_task1_thread(self):
        self.task1_thread = threading.Thread(target=self.start_test)
        self.task1_thread.start()

    def start_test2(self):
        logger.info("Starting test2")

        # ini_file_name = "testscript.ini"
        # current_directory = os.getcwd()  # Get current working directory
        
        # # Check in the current directory
        # ini_file_path = os.path.join(current_directory, ini_file_name)
        
        # if not os.path.exists(ini_file_path):
        #     logger.error(f"{ini_file_name} not found in the current directory")
        #     return

        ini_file_name = "testscript.ini"
        # specified_directory = "/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool"  # Specify the directory
        specified_directory = "/home/anuarrozman/FactoryApp_Dev/ATSoftwareDevelopmentTool/FlashingTool"  # Specify the directory

        # Check in the specified directory
        ini_file_path = os.path.join(specified_directory, ini_file_name)

        if not os.path.exists(ini_file_path):
            logger.error(f"{ini_file_name} not found in the specified directory: {specified_directory}")
            return
        
        # Wait for task 1 to complete
        self.task1_completed.wait()
        
        # Proceed to load and process the INI file
        self.loadTestScript = LoadTestScript(ini_file_path)

        config = configparser.ConfigParser()
        config.read(ini_file_path)

        if "mac_address" in config:
            logger.info("Reading MAC Address")
            self.get_device_mac()
            time.sleep(self.step_delay)

        if "mac_address" in config:
            logger.info("Reading MAC Address")
            self.get_device_mac()
            time.sleep(self.step_delay)

        if "serial_number" in config:
            logger.info("Writing Serial Number")
            self.send_serial_number()
            time.sleep(self.step_delay)

        if "matter_qr" in config:
            logger.info("Writing Matter QR")
            self.send_mqtr()
            time.sleep(self.step_delay)

        if "irdef" in config:
            logger.info("IR Definition")
            self.send_command("FF:3;irdevconf-B001010FE00FE00FE00F000FE05024001B0ED801000000000F0012000F003001000400860042000A0907000F018100860042001B0220E004000000060220E00400312080AF000006600000800006720B100380840A038084030380840503808407160A045F069006043F0690060C180384880F038488010384880203848803038488040384880500D407010400020D3006050401081A1A0904037378020A1403686C0303686C0403686C0003686C0603686C0212020400144B02090A0800610801900D07021700620009090801908AC0088A0A0A12400A8A060813400A0800610901900D07041D0062000A0A0901908AC0098A0A0A8C400A8A080413400A8C060414400C\r\n")
            time.sleep(self.step_delay)

        if "atbeam_temp" in config:
            logger.info("Reading ATBeam Temperature")
            self.get_atbeam_temp()
            time.sleep(self.step_delay)

        if "atbeam_humid" in config:
            logger.info("Reading ATBeam Humidity")
            self.get_atbeam_humid()
            time.sleep(self.step_delay)

        if "rgb" in config:
            logger.info("LED Test")

            try: 
                red = config.get("rgb", "red", fallback=None)
                green = config.get("rgb", "green", fallback=None)
                blue = config.get("rgb", "blue", fallback=None)
                if red:
                    self.send_command("FF:3;RGB-1\r\n")
                    logger.info("Red LED turned on")
                    time.sleep(self.step_delay)
                if green: 
                    self.send_command("FF:3;RGB-2\r\n")
                    logger.info("Green LED turned on")
                    time.sleep(self.step_delay)
                if blue:
                    self.send_command("FF:3;RGB-3\r\n")
                    logger.info("Blue LED turned on")
                    time.sleep(self.step_delay)
                    # self.send_command("FF:3;reboot\r\n")
                    self.process_reset_device()
                if not (red or green or blue):
                    logger.error("LED colors not found in the INI file")
            except configparser.NoSectionError:
                logger.error("RGB section not found in the INI file")
        
        if "servo" in config:
            logger.info("Pressing Button")

            try:
                pressing_time = config.get("servo", "pressing_time")
                button_angle = config.get("servo", "button_angle")
                pressing_duration = config.get("servo", "pressing_duration")

                float_pressing_duration = float(pressing_duration)
                int_pressing_time = int(pressing_time)
                int_button_angle = int(button_angle)

                logger.info(f"Pressing button {int_pressing_time} times, angle: {int_button_angle}, duration: {float_pressing_duration}")

                # for i in range(int_pressing_time):
                #     logger.info(f"Pressing button {i+1} time")
                #     self.servo_controller.set_angle(int_button_angle)
                #     time.sleep(float_pressing_duration)
                #     self.servo_controller.set_angle(0)
                #     time.sleep(0.5)

            except configparser.NoOptionError:
                logger.error("Servo configuration not found in the INI file")

        if "temp_compare" in config:
            logger.info("Temperature Comparison")
            self.read_temp_aht20()
            # time.sleep(5)
        
        if "humid_compare" in config:
            logger.info("Humidity Comparison")
            self.read_humid_aht20()
            # time.sleep(5)

        # self.serialCom.get_button_flag()
        # print("Button Flag: ", self.serialCom.get_button_flag())
        # if self.serialCom.get_button_flag():
        #     self.process_reset_device()

    def start_task2_thread(self):
        self.task2_thread = threading.Thread(target=self.start_test2)
        self.task2_thread.start()

    def combine_tasks(self):
        self.start_task1_thread()
        self.start_task2_thread()

    def process_reset_device(self):
        logger.info("Resetting device")
        self.send_command("FF:3;factoryRST\r\n")
        logger.info("Test Completed")

    def reset_tasks(self):
        logger.info("Resetting tasks")
        self.serialCom.close_serial_port()
        self.result_flashing_fw_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_flashing_cert_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_factory_mode_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_read_device_mac.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_write_serialnumber.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_write_mtqr.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_3_3v_test.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_5v_test.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_temp_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_humid_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.result_rgb_red_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.yes_button_red.config(state='normal')
        self.no_button_red.config(state='normal')
        self.result_rgb_green_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.yes_button_green.config(state='normal')
        self.no_button_green.config(state='normal')
        self.result_rgb_blue_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.yes_button_blue.config(state='normal')
        self.no_button_blue.config(state='normal')
        self.result_button_label.config(text="Not Yet", fg="black", font=("Helvetica", 10, "normal"))
        self.dmm_3_3V_reader.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.dmm_5V_reader.config(text="-", fg="black", font=("Helvetica", 10, "normal"))
        self.atbeam_temp_value.config(text="AT °C", fg="black", font=("Helvetica", 10, "normal"))
        self.ext_temp_value.config(text="Ext °C", fg="black", font=("Helvetica", 10, "normal"))
        self.atbeam_humid_value.config(text="AT %", fg="black", font=("Helvetica", 10, "normal"))
        self.ext_humid_value.config(text="Ext %", fg="black", font=("Helvetica", 10, "normal"))
        self.input_3_3V_dmm.delete(0, tk.END)
        self.input_5V_dmm.delete(0, tk.END)


    # def press_button(self, angle, pressing_duration, pressing_time):
    #     # angle = float(self.angle_entry.get())
    #     # pressing_duration = float(self.duration_entry.get())
    #     # pressing_time = int(self.pressing_time_entry.get())

    #     angle = None
    #     pressing_duration = None
    #     pressing_time = None

    #     logger.info(f"Pressing button {pressing_time} times, angle: {angle}, duration: {pressing_duration}")

    #     for i in range(pressing_time):
    #         logger.info(f"Pressing button {i+1} time")
    #         self.servo_controller.set_angle(angle)
    #         time.sleep(pressing_duration)
    #         self.servo_controller.set_angle(0)
    #         time.sleep(0.5)

    def read_version_from_file(self, file_name):
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        try:
            with open(file_path, "r") as file:
                version = file.readline().strip()
                return version
        except FileNotFoundError:
            return "Version not found"

    def add_version_label(self, version):
        version_label = tk.Label(self.root, text=f"Version: {version}")
        version_label.grid(row=99, column=99, sticky=tk.SE, padx=10, pady=10)  # Use a high number to ensure it's at the bottom right

        # Configure weight for the grid to ensure the label stays at the bottom right
        self.root.grid_rowconfigure(99, weight=1)
        self.root.grid_columnconfigure(99, weight=1)

    def on_exit(self):
        self.root.destroy()
        self.close_serial_port()

    def update_status_label(self, message, fg, font):
        self.status_label.config(text=message, fg=fg, font=font)  # Update the status label with the message


if __name__ == "__main__":
    # Delete "sensor.txt" file during boot up
    sensor_file = "sensor.txt"
    if os.path.exists(sensor_file):
        os.remove(sensor_file)

    root = tk.Tk()
    app = SerialCommunicationApp(root)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    root.protocol("WM_DELETE_WINDOW", app.on_exit)
    root.mainloop()