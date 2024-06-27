# flash_cert.py

import os
import subprocess
import configparser
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlashCert:
    def __init__(self, status_label):
        self.status_label = status_label

    def get_certId(self):
        try:
            with open('device_data.txt', 'r') as file:
                for line in file:
                    if 'Matter Cert ID:' in line:
                        certId = line.split('Matter Cert ID: ')[1].split(',')[0].strip()
                        return certId
                self.log_message("No certId found in the text file.")
                return None
        except IOError as e:
            self.log_message(f"Error reading cert info from file: {e}")
            return None

    def create_folder(self):
        sn = self.get_serial_number()
        if sn:
            directory = os.path.join(os.path.dirname(__file__), sn)
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.log_message(f"Directory {directory} created.")
            else:
                self.log_message(f"Directory {directory} already exists.")
        else:
            self.log_message("No serial number found.")

    def save_cert_id_to_ini(self, directory, certId):
        config = configparser.ConfigParser()
        config['CERT'] = {'certId': certId}
        config['SN'] = {'serialNumber': self.get_serial_number()}
        with open(os.path.join(directory, 'cert_info.ini'), 'w') as configfile:
            config.write(configfile)
        self.log_message(f"CertId {certId} saved to {os.path.join(directory, 'cert_info.ini')}")

    def certify(self, bin_path, selected_port):
        try:
            subprocess.run(["esptool.py", "-p", selected_port, "write_flash", "0x10000", bin_path], check=True)
        except subprocess.CalledProcessError as e:
            self.log_message(f"Error flashing cert: {e}")

    def update_status(self, certId):
        try:
            with open('device_data.txt', 'r') as file:
                lines = file.readlines()
            
            with open('device_data.txt', 'w') as file:
                for line in lines:
                    if f'Matter Cert ID: {certId}' in line:
                        line = line.replace('Status: None', 'Status: 0')
                    file.write(line)
            
            self.log_message(f"Status updated to '0' for certId {certId} in cert_info.txt.")
        except IOError as e:
            self.log_message(f"Error updating status in file: {e}")

    def flash_cert(self, port_var):
        certId = self.get_certId()
        selected_port = port_var.get()  # Retrieve the selected port from the Combobox
        if certId:
            bin_path = self.get_bin_path(certId)
            if bin_path:
                if selected_port:
                    self.log_message(f"Flashing cert {certId} on port {selected_port}...")
                    self.certify(bin_path, selected_port)
                    self.update_status(certId)
                    self.create_folder()
                    self.save_cert_id_to_ini(os.path.join(os.path.dirname(__file__), self.get_serial_number()), certId)
                    self.log_message(f"Cert {certId} flashed successfully.")
                    self.update_status_label("Completed")
                else:
                    self.log_message("No port selected. Please select a port before flashing.")
                    self.update_status_label("Failed")
            else:
                self.log_message(f"No .bin file found for certId {certId}.")
                self.update_status_label("Failed")
        else:
            self.log_message("No available certId found in the text file.")
            self.update_status_label("Failed")

    def get_bin_path(self, certId):
        for root, dirs, files in os.walk("/"):
            for file in files:
                if file.endswith(".bin") and certId in file:
                    return os.path.join(root, file)  # Return the path of the .bin file
        return None  # Return None if no .bin file with the certId is found

    def get_serial_number(self):
        return "DummySerialNumber"  # Replace with actual logic to retrieve serial number

    def log_message(self, message):
        logger.info(message)  # Replace this with your preferred logging mechanism
        # self.log_message_callback(message)

    def update_status_label(self, message):
        self.status_label.config(text=message)
