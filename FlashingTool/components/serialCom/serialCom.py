import serial
import serial.tools.list_ports
from threading import Thread
import tkinter as tk
import logging

from components.updateDB.updateDB import UpdateDB

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SerialCom:
    def __init__(self):
        self.update_db = UpdateDB()
        self.sensor_temp_variable = None
    
    def open_serial_port(self, selected_port, selected_baud):
        try:
            self.serial_port = serial.Serial(selected_port, baudrate=selected_baud, timeout=1)
            logger.info(f"Opened port {selected_port} at {selected_baud} baud")
            
            # Store the selected port in the class variable
            self.selected_port = selected_port

            # Start a thread to continuously read data from the serial port
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
            
    def get_sensor_temp_variable(self):
        print(self.sensor_temp_variable)
        return self.sensor_temp_variable        

    def read_serial_data(self):
        while self.serial_port.is_open:
            try:
                raw_data = self.serial_port.readline()
                decoded_data = raw_data.decode("utf-8", errors='replace').strip()

                if decoded_data:
                    logger.debug(f"Received: {decoded_data}")
                    
                    if "." in decoded_data:
                        logger.debug("Entering Factory Mode")
                        self.send_data_auto()
                    
                    if "3:MAC? = " in decoded_data:
                        mac_address = decoded_data.split("=")[1].strip()
                        self.mac_address_variable = mac_address
                        logger.info(f"MAC Address: {mac_address}")
                        
                        # self.update_db.update_database(self.mac_address_variable)
                        self.update_db.update_text_file(self.mac_address_variable)
                        self.mac_address_variable = ""

                    if "3:sensorTemp? = " in decoded_data:
                        sensor_temp = decoded_data.split("=")[1].strip()
                        self.sensor_temp_variable = sensor_temp
                        logger.info(f"Sensor Temperature: {self.sensor_temp_variable} C")
                        with open("sensor.txt", "w") as file:
                            file.write("ATBeam Temperature: ", self.sensor_temp_variable)

            except UnicodeDecodeError as decode_error:
                logger.error(f"Error decoding data: {decode_error}")
            except Exception as e:
                pass

    def send_data_auto(self):
        auto_data = "polyaire&ADT\r\n"
        if self.serial_port.is_open:
            self.serial_port.write(auto_data.encode())
            logger.debug(f"Entering Password: {auto_data}")
        else:
            logger.debug("Serial port not open.")

