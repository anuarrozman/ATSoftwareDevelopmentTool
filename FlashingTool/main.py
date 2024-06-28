import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinter.filedialog import askopenfilename
import serial.tools.list_ports
import os
from tkinter import messagebox
from cryptography.fernet import Fernet
import configparser
import time
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
from components.updateDB.updateDB import UpdateDB
# from components.servoControl.servoControl import ServoController

class SerialCommunicationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Communication App")
        self.root.attributes('-zoomed', True)

        # Serial port configuration
        self.serial_port = None
        self.read_thread = None
        self.selected_port = ""

        # Create GUI elements
        self.initialize_gui()

        # Initialize components
        self.initialize_components()

        # Store reference to the Manual Test menu item
        self.manual_test_menu = None

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
        self.serialCom = SerialCom(self.result_factory_mode_label) #self.atbeam_sensor_temp_update) #(self.receive_text)
        
        self.sendEntry = WriteDeviceInfo(self.send_command) #, self.log_message)
        self.dmmReader = DeviceSelectionApp(self.dmm_frame)
        self.multimeter = Multimeter()
        self.aht20Sensor = SensorLogger()
        # self.servo_controller = ServoController()

    def read_temp_aht20(self):
        ext_sensor = self.aht20Sensor.read_temp_sensor()
        logger.debug(f"External Temperature: {ext_sensor}")
        self.get_atbeam_temp()
        time.sleep(3)
        self.compare_temp(ext_sensor, self.serialCom.sensor_temp_variable)

    def get_atbeam_temp(self):
        command = "FF:3;sensorTemp?\r\n"
        self.send_command(command)

    def read_humid_aht20(self):
        ext_sensor = self.aht20Sensor.read_humid_sensor()
        logger.debug(f"External Humidity: {ext_sensor}")
        self.get_atbeam_sensor()
        time.sleep(3)
        self.compare_humid(ext_sensor, self.serialCom.sensor_humid_variable)

    def get_atbeam_sensor(self):
        command = "FF:3;sensorHumi?\r\n"
        self.send_command(command)

    def compare_temp(self, ext_sensor, atbeam_temp):
        # add more checking
        try:
            with open('sensor.txt', 'r') as file:
                for line in file:
                    if "ATBeam Temperature:" in line:
                        atbeam_temp = line.split(":")[1].strip()
                        logger.info(f"ATBeam Temperature: {atbeam_temp}")
                        if ext_sensor == atbeam_temp:
                            logger.info("Temperature matches")
                            self.status_atbeam_temp.config(text=f"Sensor Temperature: Pass")
                        else:
                            logger.error("Temperature does not match")
                            self.status_atbeam_temp.config(text=f"Sensor Temperature: Failed")
        except FileNotFoundError:
            logger.error("File not found")

    def compare_humid(self, ext_sensor, atbeam_humid):
        # add more checking
        try:
            with open('sensor.txt', 'r') as file:
                for line in file:
                    if "ATBeam Humidity:" in line:
                        atbeam_humid = line.split(":")[1].strip()
                        logger.info(f"ATBeam Humidity: {atbeam_humid}")
                        if ext_sensor == atbeam_humid:
                            logger.info("Humidity matches")
                            self.status_atbeam_humidity.config(text=f"Sensor Humidity: Pass")
                        else:
                            logger.error("Humidity does not match")
                            self.status_atbeam_humidity.config(text=f"Sensor Humidity: Failed")
        except FileNotFoundError:
            logger.error("File not found")

    def refresh_dmm_devices(self):
        self.dmmReader.refresh_devices()

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
        
    def load_test_script(self):
        ini_file_path = askopenfilename(title="Select .ini file", filetypes=[("INI files", "*.ini")])
        if not ini_file_path:
            return
        
        self.loadtTestScript = LoadTestScript(ini_file_path)
        with open(ini_file_path, 'r') as file:
            content = file.read()
            print(content)

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

    def create_widgets(self):
        self.serial_baud_frame = tk.Frame(self.root)
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

        text_frame = tk.Frame(self.root)
        text_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.send_entry_frame = ttk.Entry(text_frame, width=50)
        self.send_entry_frame.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.send_button = ttk.Button(text_frame, text="Send", command=lambda: self.sendEntry.send_entry_command(self.send_entry_frame))
        self.send_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

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

        self.load_config = ttk.Button(self.servo_frame, text="Load Config", command=None)
        self.load_config.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        self.press_button = ttk.Button(self.servo_frame, text="Press Button", command=self.press_button)
        self.press_button.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)

        self.dmm_frame = tk.Frame(self.root)
        self.dmm_frame.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        self.upload_report_button = ttk.Button(self.dmm_frame, text="Upload Report", command=self.upload_report)
        self.upload_report_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        self.read_temp_aht20_button = ttk.Button(self.dmm_frame, text="Read Temperature Sensor", command=self.read_temp_aht20)
        self.read_temp_aht20_button.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        self.read_humid_aht20_button = ttk.Button(self.dmm_frame, text="Read Humidity Sensor", command=self.read_humid_aht20)
        self.read_humid_aht20_button.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
        
        # test check
        self.status_frame = tk.Frame(self.root)
        self.status_frame.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        
        self.status_flashing_fw = tk.Label(self.status_frame, text="Flashing Firmware: ")
        self.status_flashing_fw.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_flashing_fw_label = tk.Label(self.status_frame, text="")
        self.result_flashing_fw_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_flashing_cert = tk.Label(self.status_frame, text="Flashing Cert: ")
        self.status_flashing_cert.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.result_flashing_cert_label = tk.Label(self.status_frame, text="")
        self.result_flashing_cert_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_factory_mode = tk.Label(self.status_frame, text="Factory Mode: ")
        self.status_factory_mode.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_factory_mode_label = tk.Label(self.status_frame, text="")
        self.result_factory_mode_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_read_device_mac = tk.Label(self.status_frame, text="Read Device MAC: ")
        self.status_read_device_mac.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        self.result_read_device_mac_label = tk.Label(self.status_frame, text="")
        self.result_read_device_mac_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.status_write_device_sn = tk.Label(self.status_frame, text="Write Device S/N: ")
        self.status_write_device_sn.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.status_write_device_mtqr = tk.Label(self.status_frame, text="Write Device MTQR: ")
        self.status_write_device_mtqr.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.status_3_3v_test = tk.Label(self.status_frame, text="3.3V Test: ")
        self.status_3_3v_test.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.status_5v_test = tk.Label(self.status_frame, text="5V Test: ")
        self.status_5v_test.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)

        self.status_atbeam_temp = tk.Label(self.status_frame, text="Sensor Temperature: ")
        self.status_atbeam_temp.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)

        self.status_atbeam_humidity = tk.Label(self.status_frame, text="Sensor Humidity: ")
        self.status_atbeam_humidity.grid(row=9, column=0, padx=5, pady=5, sticky=tk.W)

    def press_button(self):
        angle = float(self.angle_entry.get())
        pressing_duration = float(self.duration_entry.get())
        pressing_time = int(self.pressing_time_entry.get())

        for i in range(pressing_time):
            logger.info(f"Pressing button {i+1} time")
            self.servo_controller.set_angle(angle)
            time.sleep(pressing_duration)
            self.servo_controller.set_angle(0)
            time.sleep(0.5)

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
