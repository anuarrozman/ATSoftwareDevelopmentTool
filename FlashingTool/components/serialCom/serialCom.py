import serial
import logging
from threading import Thread
from components.updateDB.updateDB import UpdateDB
from threading import Lock
import time

logger = logging.getLogger(__name__)

class SerialCom:
    def __init__(self, status_label, status_label1, status_label2, status_label3):
        self.status_label = status_label
        self.status_label1 = status_label1
        self.status_label2 = status_label2
        self.status_label3 = status_label3
        self.update_db = UpdateDB()
        self.sensor_temp_variable = None
        self.mac_address_variable = None
        self.serial_port = None
        self.read_thread = None
        self.factory_flag = False
        self.factory_flag_lock = Lock()  # Add a lock for factory_flag
    
    def open_serial_port(self, port_var, baud_var):
        selected_port = port_var
        selected_baud = baud_var
        logger.debug(f"Opening port {selected_port} at {selected_baud} baud")
        try:
            self.serial_port = serial.Serial(selected_port, selected_baud, timeout=1)
            logger.info(f"Opened port {selected_port} at {selected_baud} baud")
            
            self.read_thread = Thread(target=self.read_serial_data)
            self.read_thread.start()
        except serial.SerialException as e:
            logger.error(f"Error opening serial port: {e}")

    def close_serial_port(self):
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                logger.debug("Closed port")
            else:
                logger.debug("Port is not open.")
        except serial.SerialException as e:
            logger.debug(f"Error closing serial port: {e}") 

    def read_serial_data(self):
        while self.serial_port.is_open:
            try:
                raw_data = self.serial_port.readline()
                decoded_data = raw_data.decode("utf-8", errors='replace').strip()

                if decoded_data:
                    logger.debug(f"Received: {decoded_data}")
                    
                    if "." in decoded_data:
                        logger.debug("Data contains '.'")
                        self.send_data_auto()
                    
                    if "3:MAC? = " in decoded_data:
                        self.process_mac_address(decoded_data)
                        
                    if "3:sensorTemp? = " in decoded_data:
                        self.process_sensor_temperature(decoded_data)
                    
                    if "3:sensorHumi? = " in decoded_data:
                        self.process_sensor_humidity(decoded_data)

            except UnicodeDecodeError as decode_error:
                logger.error(f"Error decoding data: {decode_error}")
            except Exception as e:
                logger.error(f"Exception in read_serial_data: {e}")
        
    def process_mac_address(self, decoded_data):
        mac_address = decoded_data.split("=")[1].strip()
        self.mac_address_variable = mac_address
        logger.info(f"MAC Address: {mac_address}")
        
        self.update_db.update_text_file(self.mac_address_variable)
        self.status_label3.config(text="Success")
        self.mac_address_variable = ""

    def process_sensor_temperature(self, decoded_data):
        sensor_temp = decoded_data.split("=")[1].strip()
        self.sensor_temp_variable = sensor_temp
        logger.info(f"{self.sensor_temp_variable} C")
        self.save_sensor_temp_variable()

    def process_sensor_humidity(self, decoded_data):
        sensor_humid = decoded_data.split("=")[1].strip()
        self.sensor_humid_variable = sensor_humid
        logger.info(f"{sensor_humid} %")
        self.save_sensor_humid_variable()

    def save_sensor_temp_variable(self):
        try:
            with open('sensor.txt', 'w') as file:
                file.write(f"ATBeam Temperature: {self.sensor_temp_variable}\n")
                self.status_label1.config(text=f"{self.sensor_temp_variable} C")
            logger.debug(f"Value '{self.sensor_temp_variable}' written to file 'sensor.txt'")
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            self.status_label1.config(text="Failed")

    def save_sensor_humid_variable(self):
        try:
            with open('sensor.txt', 'a') as file:
                file.write(f"ATBeam Humidity: {self.sensor_humid_variable}\n")
                self.status_label2.config(text=f"{self.sensor_humid_variable} %")
            logger.debug(f"Value '{self.sensor_humid_variable}' written to file 'sensor.txt'")
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            self.status_label2.config(text="Failed")

    def send_data_auto(self):
        auto_data = "polyaire&ADT\r\n"
        self.status_label.config(text="Success")
        if self.serial_port.is_open:
            self.serial_port.write(auto_data.encode())
            logger.debug(f"Sending automatic data: {auto_data}")
            time.sleep(5)
        else:
            self.status_label.config(text="Failed")

